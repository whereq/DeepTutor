# Solve 模块 — 上下文工程审计

> 本文档从 **上下文工程 (Context Engineering)** 的视角，逐模块、逐 Agent 梳理当前 `src/agents/solve/` 中每次 LLM 调用的输入上下文组成，分析信息流转路径与压缩策略，并标注可改进点。

---

## 0. 架构总览

```
Pipeline: Plan → ReAct → Write

Phase 1 — PlannerAgent.process()         → Plan (steps)
Phase 2 — SolverAgent.process()  × N     → Entry (thought/action/observation/self_note)
Phase 3 — WriterAgent.process()          → final_answer (Markdown)
          WriterAgent.process_iterative() → detailed + concise answer

Memory:   Scratchpad (统一记忆体：Plan + Entries + Sources + Metadata)
```

---

## 1. PlannerAgent — 规划阶段

### 1.1 调用时机
- Phase 1 开始时（首次规划）
- Phase 2 中 SolverAgent 返回 `replan` 动作时（重新规划）

### 1.2 LLM 调用上下文

| 上下文槽位 | 来源 | 内容描述 | 动态/静态 |
|-----------|------|---------|----------|
| **system_prompt** | `prompts/en/planner_agent.yaml → system` | 角色定义 + 规则 + 输出格式 (JSON) | 静态 |
| **user_prompt → {question}** | `MainSolver.solve(question)` 传入 | 用户原始问题，完整文本 | 动态 |
| **user_prompt → {tools_description}** | `ToolRegistry.build_planner_description()` 动态组合 | 根据注册的工具生成描述 (默认: rag_search / web_search / code_execute) | 动态 |
| **user_prompt → {scratchpad_summary}** | `Scratchpad` 状态 | 首次："(initial plan — no progress yet)"；replan 时：各步骤状态 + self_note 汇总 + replan reason | 动态 |

### 1.3 Prompt 模板

```yaml
# user_template
## Question
{question}

## Available Tools
{tools_description}

## Progress So Far
{scratchpad_summary}
```

### 1.4 scratchpad_summary 的组装逻辑（replan 时）

```python
# planner_agent.py → _build_user_prompt()
for step in scratchpad.plan.steps:
    entries = scratchpad.get_entries_for_step(step.id)
    notes = " | ".join(e.self_note for e in entries if e.self_note)
    → "[S1] (COMPLETED) 步骤目标"
    → "    Notes: note1 | note2"

# 追加最后一条 replan entry 的 action_input 作为 replan reason
```

### 1.5 上下文特征分析

- **优点**：首次调用上下文极简，LLM 聚焦规划任务。
- **缺失**：
  - 无用户历史对话上下文（多轮 Q&A 场景缺失）
  - 无知识库元信息（不知道 KB 里有什么内容、什么格式）
  - 无用户个性化偏好（风格/难度/语言偏好未注入规划阶段）
  - replan 时 `scratchpad_summary` 只有 self_note 压缩摘要，丢失了具体 observation 细节

---

## 2. SolverAgent — ReAct 求解阶段

### 2.1 调用时机
- Phase 2 中对每个 PlanStep 的每轮 ReAct 迭代（最多 `max_react_iterations` 轮/步骤）

### 2.2 LLM 调用上下文

| 上下文槽位 | 来源 | 内容描述 | 动态/静态 |
|-----------|------|---------|----------|
| **system_prompt** | `prompts/en/solver_agent.yaml → system` | 角色定义 + 5 个 action 说明表 + 指南 + 输出格式 (JSON) | 静态 |
| **user_prompt → {question}** | 原始问题全文 | 用户原始问题 | 动态（但跨调用不变） |
| **user_prompt → {plan}** | `Scratchpad._format_plan()` | 完整计划概览（含分析 + 各步骤状态标记 [x]/[>]/[ ]） | 动态 |
| **user_prompt → {current_step}** | `PlanStep` 对象 | 当前步骤 ID + 目标文本 | 动态 |
| **user_prompt → {step_history}** | `Scratchpad.build_solver_context()` | 当前步骤的所有历史 round：thought + action + observation（**完整**） + self_note | 动态（增长） |
| **user_prompt → {previous_knowledge}** | `Scratchpad.build_solver_context()` | 已完成步骤的 self_note 汇总（压缩形式） | 动态（增长） |

### 2.3 Prompt 模板

```yaml
# user_template
## Original Question
{question}

## Plan
{plan}

## Current Step
{current_step}

## Previous Actions for This Step
{step_history}

## Knowledge from Previous Steps
{previous_knowledge}
```

### 2.4 上下文压缩策略 — `build_solver_context()`

```
Scratchpad.build_solver_context(current_step_id, max_tokens=6000):

1. plan_text         = 完整计划（analysis + 各步骤带状态标记）
2. current_step_text = "[S2] 步骤目标"
3. step_history      = 当前步骤所有 round 的 FULL observation（不压缩）
4. previous_knowledge:
   - 正常：[S1] 步骤目标: note1 note2 note3（self_note 拼接）
   - 超预算(>6000 tokens)：仅保留 "[S1]: note1 | note2"（管道分隔）

压缩只在 previous_knowledge 上执行，step_history 始终保留完整 observation。
```

### 2.5 上下文特征分析

- **优点**：
  - step_history 保留完整 observation，SolverAgent 能看到当前步骤的全部工具返回
  - previous_knowledge 有 token 预算控制，避免上下文爆炸
  - self_note 作为信息压缩机制，跨步骤传递关键发现
- **缺失/风险**：
  - **step_history 无压缩上限**：如果某步骤迭代多轮，observation 可能非常长（每个 observation 最大 `obs_max * 4` 字符）
  - **question 每轮重复**：原始问题全文在每次调用中重复传入
  - **plan 每轮重复**：完整 plan 在每次调用中重复传入（步骤多时可观）
  - **无 few-shot 示例**：system prompt 有输出格式示例但仅 1 个
  - **code_execute 的 observation 包含完整代码**：`Code:\n```python\n{code}\n```\n\n{output}`，代码可能很长

---

## 3. WriterAgent — 写作阶段

WriterAgent 有 **3 种调用模式**，共涉及 **5 个不同的 LLM 调用**：

### 3.1 Simple 模式 — `process()`

**单次 LLM 调用生成完整答案。**

| 上下文槽位 | 来源 | 内容描述 |
|-----------|------|---------|
| **system_prompt** | `writer_agent.yaml → system` | 角色 + Markdown/LaTeX 格式规则 + 结构要求 + 引用规则 |
| **user → {question}** | 原始问题 | 用户问题全文 |
| **user → {scratchpad_content}** | `Scratchpad.build_writer_context()` | 所有步骤的 plan + entries 详情 |
| **user → {sources}** | `Scratchpad.format_sources_markdown()` | 去重后的引用来源列表 (Markdown) |
| **user → {preference}** | `MemoryReader.get_writer_context()` | 用户学习记忆上下文（reflection + weakness，可为空） |
| **user → {language}** | `config.system.language` | 输出语言代码 (en/zh) |

### 3.2 Iterative 模式 — `process_iterative()`

**多次 LLM 调用，逐步累积 draft，最后生成 concise answer。**

#### 3.2.1 Draft 迭代 — `_write_draft()` × N

| 上下文槽位 | 来源 | 内容描述 |
|-----------|------|---------|
| **system_prompt** | `writer_agent.yaml → iterative_system` | 增量写作角色 + 格式规则 |
| **user → {question}** | 原始问题 | 用户问题全文 |
| **user → {previous_draft}** | 上一轮 draft 输出 / 首轮为占位文本 | 累积的答案草稿（**可能很长**） |
| **user → {new_evidence}** | `_format_step_evidence(step, entries)` | 当前步骤的 action + observation（完整） |
| **user → {sources}** | `Scratchpad.format_sources_markdown()` | 引用来源列表 |
| **user → {language}** | 配置 | 输出语言 |

**Draft 迭代逻辑**：
```
Iter 1: evidence(S1) + evidence(S2) → draft_1    # 首轮合并前两步
Iter 2: draft_1 + evidence(S3) → draft_2          # 后续每步增量
Iter N: draft_{N-1} + evidence(S_{N+1}) → draft_N
```

#### 3.2.2 Concise 生成 — `_write_concise()`

| 上下文槽位 | 来源 | 内容描述 |
|-----------|------|---------|
| **system_prompt** | `writer_agent.yaml → concise_system` | 简洁回答角色 + 规则 |
| **user → {question}** | 原始问题 | 用户问题全文 |
| **user → {detailed_answer}** | 最终 draft | 完整详细答案（**可能非常长**） |
| **user → {language}** | 配置 | 输出语言 |

### 3.3 `build_writer_context()` 上下文组装逻辑

```
Scratchpad.build_writer_context(max_tokens=12000):

1. Plan 概览（带状态标记）
2. 每个 completed/in_progress 步骤：
   正常：
     ### Step S1: 目标
     **Round 0** — Action: rag_search(query)
     Note: self_note
     Observation: <完整 observation>

   超预算(>12000 tokens)时压缩：
     前 N-2 步 → 仅保留 "Round 0: self_note"（丢弃 observation）
     最后 2 步 → 保留完整 observation
```

### 3.4 上下文特征分析

- **优点**：
  - `build_writer_context` 有 token 预算和渐进压缩策略
  - Iterative 模式通过分步投喂 evidence 降低单次上下文压力
  - 个性化偏好注入（虽然仅在 Simple 模式）
- **缺失/风险**：
  - **Iterative 模式的 previous_draft 持续增长**：每次迭代 draft 只增不减，后期可能超出上下文窗口
  - **Iterative 模式缺少 preference**：`_write_draft()` 和 `_write_concise()` 未注入用户偏好
  - **sources 在每次 draft 迭代中重复传入**：完整引用列表每轮重复
  - **_format_step_evidence 无长度限制**：observation 完整传入，单步证据可能很大

---

## 4. Code Generation — 隐式 LLM 调用

### 4.1 调用时机
- SolverAgent 返回 `code_execute` 动作时，`MainSolver._generate_code()` 发起额外 LLM 调用

### 4.2 LLM 调用上下文

| 上下文槽位 | 来源 | 内容描述 |
|-----------|------|---------|
| **system_prompt** | 硬编码字符串 | "You are a Python code generator..." + 库提示 + 输出规则 |
| **user_prompt** | SolverAgent 的 `action_input` | 自然语言意图描述（如 "compute the convolution of x=[1,2,3] and h=[1,1]"） |

### 4.3 上下文特征分析

- **缺失严重**：
  - 无原始问题上下文（代码生成不知道整体问题背景）
  - 无当前步骤目标（不知道这段代码要验证什么）
  - 无先前步骤的知识（可能需要用到之前检索的公式）
  - 仅靠 SolverAgent 在 `action_input` 中的描述传递意图

---

## 5. Scratchpad — 统一记忆体

### 5.1 数据结构

```
Scratchpad
├── question: str                    # 原始问题
├── plan: Plan                       # 规划
│   ├── analysis: str               # 问题分析
│   └── steps: [PlanStep]           # 步骤列表
│       ├── id: str                 #   步骤 ID (S1, S2, ...)
│       ├── goal: str               #   步骤目标
│       ├── tools_hint: [str]       #   工具提示（未实际使用）
│       └── status: str             #   状态 (pending/in_progress/completed/skipped)
├── entries: [Entry]                 # ReAct 迭代记录
│   ├── step_id: str                #   所属步骤
│   ├── round: int                  #   轮次号
│   ├── thought: str                #   思考
│   ├── action: str                 #   动作
│   ├── action_input: str           #   动作输入
│   ├── observation: str            #   工具返回结果
│   ├── self_note: str              #   自我总结（压缩用）
│   ├── sources: [Source]           #   来源引用
│   └── timestamp: str              #   时间戳
└── metadata: dict                   # 元数据
    ├── total_llm_calls: int
    ├── total_tokens: int
    ├── start_time: str
    └── plan_revisions: int
```

### 5.2 信息压缩层级

| 压缩级别 | 使用场景 | 保留内容 | 丢弃内容 |
|---------|---------|---------|---------|
| **L0 完整** | step_history（SolverAgent 当前步骤） | 全部字段 | 无 |
| **L1 结构化** | build_writer_context 正常模式 | plan + action + observation + self_note | thought |
| **L2 摘要** | previous_knowledge 正常模式 | step_goal + self_note 拼接 | observation, thought, action_input |
| **L3 极简** | previous_knowledge 超预算 / writer_context 超预算 | self_note 管道分隔 | 其余全部 |

### 5.3 Token 预算

| 场景 | 预算 | 来源 |
|------|------|------|
| `build_solver_context` | 6,000 tokens | 硬编码默认值 |
| `build_writer_context` | 12,000 tokens | 硬编码默认值 |
| observation 截断 | `obs_max * 4` 字符 ≈ 2,000 × 4 = 8,000 字符 | config `solve.observation_max_tokens` |

---

## 6. 外部上下文来源

### 6.1 工具返回 (observation)

| 工具 | 返回格式 | 最大长度 | 附带 Source |
|------|---------|---------|------------|
| `rag_search` | RAG answer 文本 | `obs_max * 4` 字符 | Source(type="rag", file=kb_name, chunk_id=query[:50]) |
| `web_search` | Web answer 文本 | `obs_max * 4` 字符 | Source(type="web", url=..., file=title) × 最多 5 个 |
| `code_execute` | `Code:\n```python\n{code}\n```\n\n{stdout/stderr/artifacts}` | `obs_max * 4` 字符 (output 部分) | Source(type="code", file=artifact_name) |

### 6.2 个性化 (Personalization)

| 注入点 | 内容 | 条件 |
|--------|------|------|
| WriterAgent.process() → `{preference}` | `MemoryReader.get_writer_context()` | reflection + weakness 摘要；服务可用时 |
| PlannerAgent — **未注入** | — | — |
| SolverAgent — **未注入** | — | — |
| WriterAgent Iterative — **未注入** | — | — |

### 6.3 配置参数 (agents.yaml)

| 参数 | 值 | 影响 |
|------|-----|------|
| `solve.temperature` | 0.3 | 所有 3 个 Agent 共用 |
| `solve.max_tokens` | 8192 | 所有 3 个 Agent 共用（Writer 调用时覆盖为 8192 / 1024） |

---

## 7. 完整信息流图

```
用户问题 (question)
    │
    ▼
┌─────────────────────────────────────────────────┐
│ PlannerAgent                                     │
│                                                  │
│  system: 静态角色 prompt                          │
│  user:   question                                │
│         + tools_description (静态)               │
│         + scratchpad_summary (首次为空/replan时有) │
│                                                  │
│  输出: Plan { analysis, steps[] }                │
└───────────────────┬─────────────────────────────┘
                    │ 写入 Scratchpad.plan
                    ▼
┌─────────────────────────────────────────────────┐
│ SolverAgent (循环: 每步骤 × 每轮)                 │
│                                                  │
│  system: 静态角色 prompt                          │
│  user:   question (每轮重复)                      │
│         + plan (每轮重复, 含状态标记)              │
│         + current_step (当前步骤目标)              │
│         + step_history (当前步骤完整历史, L0)      │
│         + previous_knowledge (已完成步骤摘要, L2)  │
│                                                  │
│  输出: { thought, action, action_input, self_note }│
│         │                                        │
│         ├─ action=rag_search  → _tool_rag()      │
│         ├─ action=web_search  → _tool_web()      │
│         ├─ action=code_execute → _generate_code() │
│         │                       → run_code()     │
│         ├─ action=done → 标记步骤完成              │
│         └─ action=replan → 回到 PlannerAgent      │
│                                                  │
│  observation + sources → 写入 Scratchpad.entries  │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ WriterAgent                                      │
│                                                  │
│ [Simple 模式]                                    │
│  system: 格式规则 prompt                          │
│  user:   question                                │
│         + scratchpad_content (L1, 预算12k)        │
│         + sources (引用列表)                      │
│         + preference (个性化, 可为空)              │
│         + language                               │
│                                                  │
│ [Iterative 模式]                                 │
│  Draft × N:                                      │
│    system: 增量写作 prompt                        │
│    user:   question + previous_draft + new_evidence│
│           + sources + language                   │
│  Concise × 1:                                    │
│    system: 简洁回答 prompt                        │
│    user:   question + detailed_answer + language  │
│                                                  │
│  输出: final_answer (Markdown)                   │
└─────────────────────────────────────────────────┘
```

---

## 8. 关键问题与改进方向

### 8.1 上下文冗余

| 问题 | 位置 | 影响 |
|------|------|------|
| question 在 SolverAgent 每轮调用中完整重复 | solver_agent user_prompt | 浪费 tokens，尤其问题很长时 |
| plan 在 SolverAgent 每轮调用中完整重复 | solver_agent user_prompt | 步骤多时占用可观 |
| sources 在 Writer Iterative 每轮重复 | _write_draft user_prompt | 引用列表持续膨胀 |
| system_prompt 每次调用完整传入 | 所有 Agent | 协议限制，但可考虑缩短 |

### 8.2 上下文缺失

| 缺失 | 影响 | 严重度 |
|------|------|--------|
| **Code Generation 缺乏上下文** | 代码生成仅凭 action_input，不知道问题背景和已有知识 | 🔴 高 |
| **Planner 无 KB 元信息** | 不知道知识库中有什么，可能规划不切实际的步骤 | 🟡 中 |
| **Planner 无个性化偏好** | 规划不考虑用户偏好的难度/风格 | 🟡 中 |
| **Writer Iterative 无个性化** | 仅 Simple 模式注入 preference，Iterative 模式遗漏 | 🟡 中 |
| **无多轮对话历史** | 追问场景下无法理解上下文 | 🟡 中（取决于场景） |
| **Solver 无 observation 质量反馈** | 不知道 RAG 返回的是高质量精确匹配还是模糊泛化 | 🟢 低 |

### 8.3 压缩策略风险

| 风险 | 位置 | 说明 |
|------|------|------|
| **step_history 无上限** | `build_solver_context` | 当前步骤 observation 完整保留，多轮后可能超出窗口 |
| **Iterative draft 持续增长** | `_write_draft` | previous_draft 只增不减，后期可能超出模型上下文窗口 |
| **压缩粒度粗** | `build_writer_context` | 超预算时前 N-2 步直接丢弃 observation，可能丢失关键信息 |
| **token 估算不精确** | `_estimate_tokens` | tiktoken 不可用时退化为 `len/4`，非英语文本误差大 |

### 8.4 self_note 作为压缩中枢

`self_note` 是整个系统**唯一的跨步骤信息传递机制**（从 SolverAgent 到 PlannerAgent-replan、后续 SolverAgent 步骤）。其质量直接决定：
- PlannerAgent 是否能做出正确的 replan 决策
- 后续步骤的 SolverAgent 是否有足够的先验知识
- 信息在多步推理中的保真度

当前 self_note 由 SolverAgent 自行在每轮末尾生成（1 句话），**没有质量验证或格式约束**。

---

## 9. Token 消耗估算（典型场景）

假设：3 步计划，每步平均 2 轮 ReAct，每个 observation ≈ 1500 tokens

| 调用 | system | user | 合计估算 |
|------|--------|------|---------|
| Planner (首次) | ~300 | ~200 (Q) + ~100 (tools) + ~50 (empty progress) = ~350 | ~650 |
| Solver S1 R1 | ~400 | ~200 (Q) + ~150 (plan) + ~50 (step) + ~50 (no history) + ~50 (no prev) = ~500 | ~900 |
| Solver S1 R2 | ~400 | ~200 + ~150 + ~50 + ~1600 (R1 full obs) + ~50 = ~2050 | ~2450 |
| Solver S2 R1 | ~400 | ~200 + ~150 + ~50 + ~50 (no history) + ~100 (S1 notes) = ~550 | ~950 |
| Solver S2 R2 | ~400 | ~200 + ~150 + ~50 + ~1600 + ~100 = ~2100 | ~2500 |
| Solver S3 R1 | ~400 | ~200 + ~150 + ~50 + ~50 + ~200 (S1+S2 notes) = ~650 | ~1050 |
| Solver S3 R2 | ~400 | ~200 + ~150 + ~50 + ~1600 + ~200 = ~2200 | ~2600 |
| CodeGen (如有) | ~50 | ~100 | ~150 |
| Writer (Simple) | ~300 | ~200 + ~5000 (writer_context) + ~200 (sources) + ~100 (pref) = ~5500 | ~5800 |

**总输入约：~17,000 tokens**（不含 LLM 输出 tokens）

---

*最后更新：2026-02-10*
