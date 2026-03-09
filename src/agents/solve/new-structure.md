# Solve Agent 重构：Plan → ReAct → Write

## 设计原则

- **一条流水线**：不分路由、不分路径，所有问题走同一个流程
- **宏观 Plan**：先规划解题步骤，给 Agent 全局视野（解决纯 ReAct 局部最优问题）
- **微观 ReAct**：每个步骤内通过 think→act→observe 迭代获取信息
- **Plan 自适应**：简单问题自然产生 1 步计划，复杂问题产生多步计划——复杂度由 LLM 判断，不由系统硬编码
- **去中间摘要**：Agent 直接看原始检索结果，不经过独立的摘要 Agent

---

## 总体流程

```
用户问题
    │
    ▼
┌─────────────────────────────────────────────┐
│  Phase 1: PLAN                              │
│  PlannerAgent 分析问题，生成有序步骤列表       │
│  [S1, S2, S3, ...]                          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Phase 2: SOLVE                             │
│                                             │
│  for each step Si:                          │
│    SolverAgent (ReAct Loop):                │
│      THINK  → 当前步骤还缺什么信息？          │
│      ACT    → rag / web / code / done       │
│      OBSERVE → 工具返回结果写入 Scratchpad    │
│      ... 重复直到 done ...                   │
│                                             │
│  (可选) 步骤间 replan：                      │
│    如果新信息表明原计划需调整，               │
│    SolverAgent 可输出 replan 信号，           │
│    触发 PlannerAgent 修订剩余步骤             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Phase 3: WRITE                             │
│  WriterAgent 基于完整 Scratchpad 生成答案     │
│  结构化 Markdown + LaTeX + 内联引用          │
└─────────────────────────────────────────────┘
```

---

## Agent 定义（共 3 个）

### PlannerAgent

职责：将用户问题分解为有序解题步骤。

输入：
- 用户问题
- 知识库元信息（可选，帮助判断可用资源）
- 已有 Scratchpad 内容（replan 场景下非空）

输出：
```
{
  "analysis": "对问题的简要分析",
  "steps": [
    { "id": "S1", "goal": "明确线性卷积的数学定义", "tools_hint": ["rag"] },
    { "id": "S2", "goal": "推导卷积的计算过程", "tools_hint": ["rag", "code"] },
    { "id": "S3", "goal": "举例验证", "tools_hint": ["code"] }
  ]
}
```

设计要点：
- 步骤粒度为"一个可验证的子目标"，不是"一个工具调用"
- `tools_hint` 仅为提示，SolverAgent 可自行决定实际用什么工具
- 简单问题（如"X 的定义是什么"）自然只产生 1 个步骤
- 复杂问题自然产生 3-6 个步骤
- 不需要 Router——Plan 本身就是自适应机制

### SolverAgent

职责：针对当前步骤，通过 ReAct 迭代获取和验证所需信息。

每轮迭代输出：
```
{
  "thought": "当前步骤需要卷积定义，我先在教材中检索...",
  "action": "rag_search",          // rag_search | web_search | code_execute | done | replan
  "action_input": "线性卷积 定义 公式",
  "self_note": "找到了精确定义和公式，信息充足"   // 简短自注，用于后续上下文压缩
}
```

设计要点：
- 一个 Agent 兼具检索决策、查询改写、信息评估能力
- `done` 表示当前步骤信息已充足，推进到下一步
- `replan` 表示发现原计划有问题（如发现问题理解有误、知识库缺少关键信息），触发 PlannerAgent 修订
- `self_note` 是 Agent 对本轮结果的一句话总结，服务于上下文压缩（不是独立的摘要 Agent）
- 工具执行本身是纯函数调用，不消耗 LLM
- 原始检索结果直接截断写入 Scratchpad 的 observation 字段，不做 LLM 摘要

### WriterAgent

职责：基于完整 Scratchpad 生成最终答案。

输入：
- 用户问题
- 完整 Scratchpad（含 plan + 所有 ReAct 条目）
- 用户偏好（语言、详细程度等）

输出：
- 结构化 Markdown 答案
- 内联引用（直接映射 Scratchpad 条目中的 sources）

设计要点：
- 融合原 ResponseAgent + PrecisionAnswerAgent 的能力
- 可以回溯任意 observation 的原始内容来确保公式/数据准确
- 引用不需要独立系统，直接从 Scratchpad entries 的 sources 提取

---

## 统一记忆：Scratchpad

一个数据结构，替代原来的 InvestigateMemory + SolveMemory + CitationMemory。

```
Scratchpad
│
├── question: str                          # 用户原始问题
│
├── plan: {                                # PlannerAgent 输出
│     analysis: str,
│     steps: [ { id, goal, tools_hint, status } ]
│   }
│
├── entries: [                             # ReAct 循环所有条目（按时间顺序）
│     {
│       step_id: "S1",                     # 属于哪个 plan step
│       round: 1,                          # 该 step 内的第几轮
│       thought: str,
│       action: str,
│       action_input: str,
│       observation: str,                  # 原始工具返回（截断，不做 LLM 摘要）
│       self_note: str,                    # Agent 自注（1 句话）
│       sources: [ { type, file, page, url, chunk_id } ],
│       timestamp: str
│     }
│   ]
│
└── metadata: {
      total_llm_calls: int,
      total_tokens: int,
      start_time: str,
      plan_revisions: int                  # replan 次数
    }
```

### Scratchpad 的上下文管理

ReAct 迭代多了之后 Scratchpad 会膨胀，需要主动管理（借鉴 MemoBrain 思想）：

**分层压缩策略：**

```
┌─────────────────────────────────────────────┐
│ 当前步骤的条目：完整保留                       │
│   thought + action + observation（原始）      │
├─────────────────────────────────────────────┤
│ 已完成步骤的条目：压缩为精要                   │
│   thought + action + self_note（替代 obs）    │
├─────────────────────────────────────────────┤
│ 更早的步骤：极度压缩                          │
│   仅保留 self_note 拼接为 1 段摘要             │
└─────────────────────────────────────────────┘
```

- 触发时机：传入 SolverAgent 的上下文 token 超过窗口 60%
- 原始 observation 始终完整保存在磁盘 JSON 中（WriterAgent 可按需回溯）
- 压缩在构建 prompt 时动态进行，不修改 Scratchpad 本体

---

## Replan 机制

不是每次都 replan，仅在 SolverAgent 主动判断需要时触发：

```
SolverAgent 输出 action = "replan"
    │
    ▼
PlannerAgent 接收：
  - 原始问题
  - 当前 Scratchpad（已执行的步骤和结果）
  - SolverAgent 的 replan 理由
    │
    ▼
输出修订后的 steps（可增删改剩余步骤）
    │
    ▼
继续 Solve Phase
```

典型触发场景：
- 检索发现问题前提有误，需要重新理解问题
- 发现知识库中缺少关键信息，需要转向 web_search
- 已完成的步骤覆盖了后续步骤的目标，可以合并/删除

---

## 工具层

纯执行函数，不涉及 LLM 调用。SolverAgent 通过 `action` + `action_input` 调度：

| action | 功能 | 返回 |
|--------|------|------|
| `rag_search` | 知识库检索 | 检索片段 + 来源元信息 |
| `web_search` | 网络搜索 | 搜索结果 + URL |
| `code_execute` | 沙箱执行 Python | 执行结果 + 产物路径 |
| `done` | 当前步骤完成 | — |
| `replan` | 请求修订计划 | — |

工具返回结果直接截断到合理长度（如 2000 token），写入 observation 字段。

---

## 与现有架构的映射

| 原架构 | 新架构 | 变化 |
|--------|--------|------|
| InvestigateAgent | SolverAgent | 合并 |
| NoteAgent | 删除 | self_note 替代 |
| ManagerAgent | PlannerAgent | 简化 |
| SolveAgent | SolverAgent | 合并 |
| ToolAgent（LLM 摘要） | 删除 | Agent 直接看原始结果 |
| SolveNoteAgent | 删除 | replan 机制替代 |
| ResponseAgent | WriterAgent | 简化 |
| PrecisionAnswerAgent | WriterAgent | 合并 |
| InvestigateMemory | Scratchpad | 统一 |
| SolveMemory | Scratchpad | 统一 |
| CitationMemory | Scratchpad.sources | 内嵌 |
| CitationManager | 删除 | 不需要独立管理 |

LLM 调用估算对比（中等复杂度问题）：

| | 原架构 | 新架构 |
|--|--------|--------|
| 规划 | 1 次 ManagerAgent | 1 次 PlannerAgent |
| 检索决策 | ~5 次 InvestigateAgent + ~5 次 SolveAgent | ~6 次 SolverAgent |
| 中间摘要 | ~5 次 NoteAgent + ~5 次 ToolAgent | 0 |
| Todo 管理 | ~3 次 SolveNoteAgent | 0（偶尔 1 次 replan） |
| 答案生成 | ~3 次 ResponseAgent | 1 次 WriterAgent |
| **总计** | **~27 次** | **~8 次** |

---

## 附加建议

**流式输出**：SolverAgent 每轮的 thought 可实时推送前端，用户可看到推理过程。WriterAgent 支持流式生成答案。

**与 Research Agent 复用**：PlannerAgent + SolverAgent + WriterAgent 的三段式结构可复用于 research 模块，仅需切换 prompt 和可用工具。

**Query Rewriting 内置**：SolverAgent 在 thought 步骤中自然包含查询改写推理，不需要独立模块。

**观测截断策略**：RAG 返回多个片段时，按相关性分数排序后截断到 top-K 片段（如 top-3），保留最相关内容在有限 token 预算内。
