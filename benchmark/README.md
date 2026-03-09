# Benchmark - Tutor Evaluation System

本模块用于生成 AI 辅导系统的评测数据、运行对话模拟，并对 tutor 表现进行 LLM-as-judge 评估。

## 目录结构

```
benchmark/
├── config/
│   └── benchmark_config.yaml    # 数据生成与评测配置
├── data/
│   ├── generated/               # 生成的 entries（JSONL、单文件 JSON）
│   ├── transcripts/            # 对话 transcript 输出
│   └── evaluations/             # 评测结果输出
├── data_generation/             # 数据生成流水线
├── simulation/                  # 对话模拟（StudentAgent + 人/LLM Tutor）
├── evaluation/                 # 评测逻辑（LLM-as-judge）
├── prompts/                     # 各阶段 LLM prompt 模板
└── README.md
```

---

## 一、数据生成 (Data Generation)

### 流程概览

```
知识库 (KB)
    │
    ▼  Stage 1: 发现 KB
    │
    ▼  Stage 2: RAG 查询 → 生成 knowledge scope
    │
    ▼  Stage 3: 生成学生 profile（beginner/intermediate/advanced）
    │
    ▼  Stage 4-5: 对每个 profile 循环直到达标
    │       ├── 从 content_list 随机选 10 页连续内容
    │       ├── 生成 gaps（带 source_pages）
    │       ├── 生成 tasks（partition + 拒绝采样）
    │       └── 若 task 数 < min_tasks_per_profile，继续生成
    │
    ▼  Stage 6: 输出 entries（JSONL + 单文件 JSON）
```

### 核心概念

- **Profile**：虚拟学生画像（背景、知识状态、性格、学习目的）
- **Gap**：知识缺口（misconception / incomplete / missing），含 `source_pages`
- **Task**：学习任务，对应若干 gaps，含 `initial_message`、`success_criteria`
- **Entry**：一条评测样本 = profile + gaps + task + source_content

### 配置要点 (`benchmark_config.yaml`)

| 配置项 | 说明 |
|--------|------|
| `profile_generation.profiles_per_subtopic` | 每个 KB 生成的学生数（默认 3） |
| `gap_generation.use_content_list` | 是否用 content_list 做 page-grounded gaps |
| `gap_generation.pages_per_profile` | 每个 profile 选取的连续页数（默认 10） |
| `gap_generation.rejection_sampling` | 是否对 task 做批量拒绝采样 |
| `task_generation.min_tasks_per_profile` | 每个学生至少的 task 数（默认 3） |
| `task_generation.gaps_per_batch` | 每批生成的 gap 数 |

### 使用方法

```bash
# 生成 calc1 的评测数据
python3 -m benchmark.data_generation.pipeline --kb-names calc1

# 指定配置文件
python3 -m benchmark.data_generation.pipeline --config path/to/config.yaml --kb-names calc1
```

### 输出

- `benchmark/data/generated/benchmark_{timestamp}/`
  - `{entry_id}.json`：单条 entry
  - `_all_entries.jsonl`：全部 entries
  - `_summary.json`：统计摘要
- `benchmark/data/generated/knowledge_scopes/{kb_name}.json`：knowledge scope

---

## 二、对话模拟 (Simulation)

### 模式

1. **Interactive**：人扮演 tutor，在终端或编辑器中输入回复
2. **Auto**：LLM 扮演 mock tutor

### 单次对话

```bash
# 交互模式（默认用 $EDITOR）
python3 -m benchmark.simulation.conversation --entry benchmark/data/generated/benchmark_xxx/calc1_xxx_task_001.json

# 控制台输入（空行 + Enter 发送）
python3 -m benchmark.simulation.conversation --entry path/to/entry.json --inline

# Auto 模式（LLM 当 tutor）
python3 -m benchmark.simulation.conversation --entry path/to/entry.json --auto --max-turns 10
```

### 多 Session（同一学生多次返回）

```bash
# 按 profile 从 JSONL 筛选，跑多 session
python3 -m benchmark.simulation.conversation \
  --entry benchmark/data/generated/benchmark_xxx/_all_entries.jsonl \
  --profile calc1_beginner_00 \
  --multi-session --auto

# 显式指定 entry 列表
python3 -m benchmark.simulation.conversation \
  --entries entry1.json,entry2.json,entry3.json \
  --multi-session --auto

# 关闭 profile 演化
python3 -m benchmark.simulation.conversation --entry ... --profile ... --multi-session --no-evolve
```

### 输出

- Transcript 保存到 `benchmark/data/transcripts/`
- 单 session：`{entry_id}_{timestamp}.json`
- 多 session：`multi_{profile_id}_{timestamp}.json`

---

## 三、评测 (Evaluation)

### 评测指标

**Turn 级**（单轮回复）：
- 50% 个性化：`profile_adaptation`、`misconception_targeting`
- 25% 有效性：`response_quality`、`engagement`
- 25% 知识源对齐：`knowledge_source_alignment`（有 source_content 时）

**Dialog 级**（整场对话）：
- 50% 个性化：`adaptation_consistency`、`gap_resolution`、`success_criteria_met`
- 25% 质量：`session_quality`、`student_agency`
- 25% 知识源对齐：`knowledge_source_alignment`

**综合分数**：`combined_overall_score` = 0.4 × Turn 平均 + 0.6 × Dialog 分数

### 使用方法

```bash
# 评测单个 transcript
python3 -m benchmark.evaluation.run --transcript benchmark/data/transcripts/xxx.json

# 仅 dialog 级（更快）
python3 -m benchmark.evaluation.run --transcript xxx.json --dialog-only

# 评测目录下所有 transcript
python3 -m benchmark.evaluation.run --transcript-dir benchmark/data/transcripts

# 指定输出路径
python3 -m benchmark.evaluation.run --transcript xxx.json -o results.json
```

### 输出

- 默认保存到 `benchmark/data/evaluations/{stem}_eval_{timestamp}.json`
- 支持单 session 与 multi-session transcript

---

## 四、完整工作流示例

```bash
# 1. 生成数据
python3 -m benchmark.data_generation.pipeline --kb-names calc1

# 2. 运行对话（auto 或 interactive）
python3 -m benchmark.simulation.conversation \
  --entry benchmark/data/generated/benchmark_xxx/_all_entries.jsonl \
  --profile calc1_beginner_00 \
  --multi-session --auto --max-turns 5

# 3. 评测 transcript
python3 -m benchmark.evaluation.run \
  --transcript benchmark/data/transcripts/multi_calc1_beginner_00_xxx.json
```

---

## 五、CLI 参数速查

### 数据生成 (`benchmark.data_generation.pipeline`)

| 参数 | 说明 |
|------|------|
| `--config` | 配置文件路径 |
| `--kb-names` | 指定 KB 名称列表（覆盖 config） |

### 对话模拟 (`benchmark.simulation.conversation`)

| 参数 | 说明 |
|------|------|
| `--entry` | Entry JSON 或 JSONL 路径 |
| `--multi-session` | 多 session 模式 |
| `--profile` | 从 JSONL 筛选的 profile_id（配合 `--entry` + `--multi-session`） |
| `--entries` | 逗号分隔的 entry 路径（配合 `--multi-session`） |
| `--no-evolve` | 关闭 profile 演化 |
| `--auto` | LLM 扮演 tutor |
| `--max-turns` | 最大轮数（默认 20） |
| `--output-dir` | transcript 输出目录 |
| `--entry-index` | JSONL 时使用的 entry 索引（默认 0） |
| `--inline` | 控制台输入（否则用编辑器） |

### 评测 (`benchmark.evaluation.run`)

| 参数 | 说明 |
|------|------|
| `--transcript` | 单个 transcript 路径 |
| `--transcript-dir` | transcript 目录（评测全部） |
| `--dialog-only` | 仅 dialog 级评测 |
| `--output` / `-o` | 结果输出路径 |
| `--temperature` | LLM 温度（默认 0.2） |
| `--verbose` / `-v` | 调试日志 |

---

## 六、关键文件说明

| 文件 | 作用 |
|------|------|
| `data_generation/pipeline.py` | 数据生成主流程 |
| `data_generation/content_loader.py` | 从 content_list 加载连续 10 页 |
| `data_generation/gap_generator.py` | 生成 page-grounded gaps |
| `data_generation/task_generator.py` | 生成 tasks + 拒绝采样 |
| `simulation/student_agent.py` | LLM 学生角色 |
| `simulation/conversation.py` | 对话运行器（单/多 session） |
| `simulation/profile_evolver.py` | 多 session 间 profile 演化 |
| `evaluation/evaluator.py` | LLM-as-judge 评测逻辑 |
