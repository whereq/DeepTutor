# Simulator Tools 使用指南

## 概述

三个异步工具，供学生 Agent 调用，完整覆盖 **解题 → 出题 → 做答** 流程，并自动集成 Memory 系统。

每个学生通过独立的 `workspace` 路径实现数据隔离——所有产出文件（解题记录、出题批次、trace、memory 文档）均保存在该路径下，Memory Agent 也只读取该路径内的历史数据。

## Workspace 目录结构

```
workspace/
├── memory/                        # 记忆系统
│   ├── traces/                    # trace 森林
│   │   ├── index.json
│   │   ├── embeddings.json
│   │   └── {trace_id}.json
│   ├── logs/                      # memory agent 日志
│   ├── memory.md                  # 学习总结 (SummaryAgent)
│   ├── weakness.md                # 薄弱点 (WeaknessAgent)
│   └── reflection.md              # 反思 (ReflectionAgent)
├── solve/                         # 解题输出
│   └── solve_YYYYMMDD_HHMMSS/
│       ├── scratchpad.json
│       ├── final_answer.md
│       └── cost_report.json
└── question/                      # 出题输出
    └── batch_YYYYMMDD_HHMMSS/
        ├── templates.json
        ├── summary.json
        └── q_X_result.json
```

## 工具 API

### 1. `solve_question` — 解题

```python
from benchmark.simulation import solve_question

result = await solve_question(
    workspace="/path/to/student_001",
    kb_name="ai-textbook",
    question="什么是拉格朗日乘数法？",
    language="zh",            # 可选，默认 "en"
)
```

**输入参数**

| 参数 | 类型 | 说明 |
|---|---|---|
| `workspace` | `str` | 学生 workspace 根路径 |
| `kb_name` | `str` | 知识库名称 |
| `question` | `str` | 学生提出的问题 |
| `language` | `str` | 语言（`en` / `zh`），默认 `en` |

**返回值**

```python
{
    "question": "什么是拉格朗日乘数法？",
    "answer": "拉格朗日乘数法是一种...",       # 完整解答
    "output_dir": "/path/to/.../solve_20260220_143022",
    "steps": 3,
    "completed_steps": 3,
    "citations": ["source-1", "source-2"],
}
```

**内部流程**: Plan → ReAct → Write → 构建 trace → 注册到 trace forest → 运行三个 Memory Agent 更新 memory.md / weakness.md / reflection.md。

---

### 2. `generate_questions` — 出题

```python
from benchmark.simulation import generate_questions

result = await generate_questions(
    workspace="/path/to/student_001",
    kb_name="ai-textbook",
    topic="线性代数中的特征值分解",
    preferences="侧重应用和计算",   # 可选
    num_questions=3,               # 可选，默认 3
    language="zh",                 # 可选，默认 "en"
)
```

**输入参数**

| 参数 | 类型 | 说明 |
|---|---|---|
| `workspace` | `str` | 学生 workspace 根路径 |
| `kb_name` | `str` | 知识库名称 |
| `topic` | `str` | 出题主题 |
| `preferences` | `str` | 个人偏好/要求，可为空 |
| `num_questions` | `int` | 题目数量，默认 3 |
| `language` | `str` | 语言，默认 `en` |

**返回值**

```python
{
    "batch_id": "batch_20260220_150000",
    "batch_dir": "/path/to/.../batch_20260220_150000",
    "num_generated": 3,
    "questions": [
        {
            "question_id": "q_1",
            "question": "下列关于特征值的说法，正确的是？",
            "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
            "question_type": "choice",
        },
        # ...
    ],
}
```

> **注意**: 返回的 `questions` 中 **不含正确答案**，防止学生 Agent "作弊"。正确答案存储在 `summary.json` 中，由 `submit_answers` 在判分时读取。

---

### 3. `submit_answers` — 做答

```python
from benchmark.simulation import submit_answers

result = await submit_answers(
    workspace="/path/to/student_001",
    batch_id="batch_20260220_150000",  # 来自 generate_questions 的返回
    answers=[
        {"question_id": "q_1", "answer": "A"},
        {"question_id": "q_2", "answer": "C"},
        {"question_id": "q_3", "answer": "B"},
    ],
    language="zh",
)
```

**输入参数**

| 参数 | 类型 | 说明 |
|---|---|---|
| `workspace` | `str` | 学生 workspace 根路径 |
| `batch_id` | `str` | `generate_questions` 返回的 `batch_id` |
| `answers` | `list[dict]` | `[{"question_id": "q_1", "answer": "A"}, ...]` |
| `language` | `str` | 语言，默认 `en` |

**返回值**

```python
{
    "results": [
        {
            "question_id": "q_1",
            "user_answer": "A",
            "correct_answer": "A",
            "judged_result": "correct",   # correct / wrong / skipped
            "explanation": "因为...",
        },
        # ...
    ],
    "score": {
        "total": 3,
        "correct": 2,
        "wrong": 1,
        "accuracy": 0.6667,
    },
}
```

**内部流程**: 从 `summary.json` 读取正确答案 → 自动判分 → 将答题节点写入 trace → 运行三个 Memory Agent 更新记忆。

---

## 典型调用流程

```python
import asyncio
from benchmark.simulation import solve_question, generate_questions, submit_answers

WS = "/data/eval/student_001"
KB = "ai-textbook"

async def main():
    # ① 解题（自动带 memory）
    solve_result = await solve_question(
        workspace=WS, kb_name=KB,
        question="什么是梯度下降？", language="zh",
    )
    print(solve_result["answer"])

    # ② 出题
    gen_result = await generate_questions(
        workspace=WS, kb_name=KB,
        topic="反向传播算法", num_questions=3, language="zh",
    )

    # ③ 学生 Agent 思考后做答
    answers = []
    for q in gen_result["questions"]:
        answer = student_agent_think(q)  # 你自己的学生 Agent 逻辑
        answers.append({"question_id": q["question_id"], "answer": answer})

    # ④ 提交答案（自动判分 + 更新 memory）
    ans_result = await submit_answers(
        workspace=WS, batch_id=gen_result["batch_id"],
        answers=answers, language="zh",
    )
    print(f"得分: {ans_result['score']['correct']}/{ans_result['score']['total']}")

asyncio.run(main())
```

## 多学生并行模拟

不同学生使用不同的 `workspace` 路径，即可完全隔离。可通过 `asyncio.gather` 并行运行多个学生：

```python
async def simulate_student(student_id: str):
    ws = f"/data/eval/student_{student_id}"
    # ... 调用 solve_question / generate_questions / submit_answers ...

await asyncio.gather(
    simulate_student("001"),
    simulate_student("002"),
    simulate_student("003"),
)
```

## 依赖

使用前确保项目根目录的 `.env` 或 `DeepTutor.env` 中配置了 LLM API 凭证，且目标知识库已在 `data/knowledge_bases/` 中构建完成。
