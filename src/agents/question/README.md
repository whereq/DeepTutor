# Question Module (Refactored)

`src/agents/question` 已重构为**双循环架构**，用于统一处理：

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
│   ├── evaluator.py
│   ├── generator.py
│   └── validator.py
└── prompts/
    ├── en/
    │   ├── idea_agent.yaml
    │   ├── evaluator.yaml
    │   ├── generator.yaml
    │   └── validator.yaml
    └── zh/
        ├── idea_agent.yaml
        ├── evaluator.yaml
        ├── generator.yaml
        └── validator.yaml
```

## 2. 架构概览

### 路径 1：Topic 模式

1. `IdeaAgent` 基于 topic/preference + RAG 生成候选出题创意
2. `Evaluator` 对创意打分并给反馈，必要时继续下一轮
3. 产出 top-k `QuestionTemplate`
4. 对每个 template 进入生成-验证循环：
   - `Generator` 生成 Q-A（可用 `rag_tool` / `web_search` / `write_code`）
   - `Validator` approve/reject，不通过则反馈重生

### 路径 2：Mimic 模式

1. PDF 先经 MinerU 解析（或直接使用已解析目录）
2. 提取参考题（question extractor）
3. 参考题映射为 `QuestionTemplate`
4. 进入与 topic 模式相同的生成-验证循环

## 3. 核心数据模型

定义在 `models.py`：

- `QuestionTemplate`：统一中间表示
  - `question_id`
  - `concentration`
  - `question_type`
  - `difficulty`
  - `source` (`custom`/`mimic`)
- `QAPair`：最终生成结果
  - `question`
  - `correct_answer`
  - `explanation`
  - `validation`

## 4. Coordinator 入口

`AgentCoordinator` 提供两个主入口：

- `generate_from_topic(user_topic, preference, num_questions)`
- `generate_from_exam(exam_paper_path, max_questions, paper_mode)`

## 5. 配置项（main.yaml）

```yaml
question:
  rag_query_count: 3
  max_parallel_questions: 1
  rag_mode: naive
  idea_loop:
    max_rounds: 3
    ideas_per_round: 5
  generation:
    max_retries: 2
    tools:
      web_search: true
      rag_tool: true
      write_code: true
```

## 6. 命令行交互测试

新增脚本：`src/agents/question/cli.py`

从项目根目录运行：

```bash
python src/agents/question/cli.py
```

支持：

- 交互式 Topic 模式测试
- 交互式 Mimic 模式测试（upload/parsed）
- 输出摘要（completed/failed）与题目预览

## 7. 相关工具模块

工具位于 `src/tools/question/`：

- `pdf_parser.py`
- `question_extractor.py`
- `exam_mimic.py`（薄封装，委托 coordinator）

## 8. 注意事项

- 旧版 `retrieve_agent / generate_agent / relevance_analyzer` 已移除
- 旧版 prompt 文件已移除
- 旧文档中的旧接口（如 `generate_questions_custom`）不再适用
