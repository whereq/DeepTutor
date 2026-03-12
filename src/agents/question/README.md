# Question Module

`src/agents/question` 当前采用**批量模板 + 单次生成**架构，统一处理：

- 主题驱动出题（topic + preference）
- 试卷驱动出题（PDF/已解析试卷）

## 1. 目录结构

```text
src/agents/question/
├── __init__.py
├── coordinator.py
├── models.py
├── cli.py
├── agents/
│   ├── idea_agent.py
│   └── generator.py
└── prompts/
    ├── en/
    │   ├── idea_agent.yaml
    │   └── generator.yaml
    └── zh/
        ├── idea_agent.yaml
        └── generator.yaml
```

## 2. 架构概览

### 路径 1：Topic 模式

1. `IdeaAgent` 基于 topic/preference + 可选 RAG 生成模板
2. 每批最多生成 5 个 `QuestionTemplate`
3. 若题量超过 5，则继续下一批模板生成，并尽量避开前批次考察点
4. `Generator` 对每个 template 单次生成最终 Q-A

### 路径 2：Mimic 模式

1. PDF 先经 MinerU 解析（或直接使用已解析目录）
2. 提取参考题（question extractor）
3. 参考题映射为 `QuestionTemplate`
4. 进入与 topic 模式相同的单次生成流程

## 3. 核心数据模型

定义在 `models.py`：

- `QuestionTemplate`：统一中间表示
  - `question_id`
  - `concentration`
  - `question_type`
  - `difficulty`
  - `source` (`custom` / `mimic`)
- `QAPair`：最终生成结果
  - `question`
  - `correct_answer`
  - `explanation`

## 4. Coordinator 入口

`AgentCoordinator` 提供两个主入口：

- `generate_from_topic(user_topic, preference, num_questions)`
- `generate_from_exam(exam_paper_path, max_questions, paper_mode)`

## 5. 配置项

```yaml
question:
  rag_mode: naive
  generation:
    tools:
      web_search: true
      rag: true
      code_execution: true
```

## 6. 命令行交互测试

脚本位于 `src/agents/question/cli.py`。

从项目根目录运行：

```bash
python src/agents/question/cli.py
```

支持：

- 交互式 Topic 模式测试
- 交互式 Mimic 模式测试（upload / parsed）
- 输出摘要（completed / failed）与题目预览

## 7. 相关工具模块

工具位于 `src/tools/question/`：

- `pdf_parser.py`
- `question_extractor.py`
- `exam_mimic.py`（薄封装，委托 coordinator）

## 8. 注意事项

- Topic 模式默认每批最多 5 个模板
- 当前实现优先追求吞吐和响应速度，而非多轮精筛
- 旧版双循环 `Evaluator / Validator` 已移除
