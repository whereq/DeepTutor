# iso_solve

`iso_solve` 用于隔离评估 DeepTutor 解题能力，支持同一套评估主流程在多个 benchmark 上复用：

- `direct`：直接调用 LLM 解题
- `pipeline`：调用 DeepTutor 的 Plan -> ReAct -> Write 解题链路

评估逻辑统一为两步：

1. 基于题目 + 模型输出（`output.md` / `final_answer.md` 内容）使用 LLM 抽取最终答案
2. 基于抽取答案 + GT 使用 LLM 判分（正确/错误）

---

## 目录结构

```text
benchmark/iso_solve/
├── run_benchmark.py          # 统一 CLI 入口
├── config.yaml               # 统一配置
├── core/                     # 通用评估框架
│   ├── types.py
│   ├── extractor.py
│   ├── judge.py
│   ├── pipeline.py
│   └── runner.py
├── eval/                     # benchmark 适配层
│   ├── base.py
│   ├── math.py
│   ├── gpqa.py
│   ├── aime25.py
│   ├── gaia.py
│   ├── hle.py
│   ├── livebench.py
│   └── scorers/
└── results/                  # 所有评估产物
```

---

## 核心设计

- `core/runner.py`
  - 统一并发调度、结果落盘、report 汇总
  - 与 benchmark 无关
- `eval/*.py`
  - 只负责数据加载、过滤、prompt/metadata 差异
  - 每个 benchmark 通过 adapter 接入
- `core/extractor.py` + `core/judge.py`
  - 统一的 LLM 抽取与 LLM 判分能力
  - 全局配置由 `config.yaml` 的 `evaluation` 控制

---

## 配置说明

全局评估开关（单一真值来源）：

```yaml
evaluation:
  llm_extract: true
  llm_judge: true
  extract_model: null
  extract_max_tokens: 256
  judge_model: null
  judge_max_tokens: 128
```

说明：

- `extract_model` / `judge_model` 为 `null` 时使用默认 LLM 配置
- `extract_max_tokens` / `judge_max_tokens` 控制抽取和判分模型的输出长度
- benchmark 子配置不再单独控制 extract/judge 的模型和开关

---

## 运行方式

从项目根目录执行：

### MATH（config 默认 500 题，Level 3-5）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark math --mode direct --config benchmark/iso_solve/config.yaml --limit 5
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark math --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark math --mode pipeline --config benchmark/iso_solve/config.yaml --limit 5
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark math --mode pipeline --config benchmark/iso_solve/config.yaml
```

### GPQA-Diamond（共 198 题）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark gpqa --mode direct --config benchmark/iso_solve/config.yaml --limit 5
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark gpqa --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark gpqa --mode pipeline --config benchmark/iso_solve/config.yaml --limit 5
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark gpqa --mode pipeline --config benchmark/iso_solve/config.yaml
```

### AIME 2025（共 30 题，Part I + II）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark aime25 --mode direct --config benchmark/iso_solve/config.yaml --limit 5
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark aime25 --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark aime25 --mode pipeline --config benchmark/iso_solve/config.yaml --limit 5
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark aime25 --mode pipeline --config benchmark/iso_solve/config.yaml
```

### HLE（config 默认 100 题）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark hle --mode direct --config benchmark/iso_solve/config.yaml --limit 5
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark hle --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark hle --mode pipeline --config benchmark/iso_solve/config.yaml --limit 5
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark hle --mode pipeline --config benchmark/iso_solve/config.yaml
```

### GAIA（config 默认 10 题，需 `huggingface-cli login`）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark gaia --mode direct --config benchmark/iso_solve/config.yaml --limit 3
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark gaia --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark gaia --mode pipeline --config benchmark/iso_solve/config.yaml --limit 3
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark gaia --mode pipeline --config benchmark/iso_solve/config.yaml
```

### LiveBench（共 ~1436 题）

```bash
# direct 少量
python -m benchmark.iso_solve.run_benchmark --benchmark livebench --mode direct --config benchmark/iso_solve/config.yaml --limit 20
# direct 全量
python -m benchmark.iso_solve.run_benchmark --benchmark livebench --mode direct --config benchmark/iso_solve/config.yaml
# pipeline 少量
python -m benchmark.iso_solve.run_benchmark --benchmark livebench --mode pipeline --config benchmark/iso_solve/config.yaml --limit 20
# pipeline 全量
python -m benchmark.iso_solve.run_benchmark --benchmark livebench --mode pipeline --config benchmark/iso_solve/config.yaml
```

### 常见参数

| 参数 | 说明 |
|------|------|
| `--benchmark` | `math \| gpqa \| aime25 \| hle \| gaia \| livebench` |
| `--mode` | `direct \| pipeline` |
| `--limit N` | 限制样本数（覆盖 config.yaml 中的 `filter.limit`） |
| `--seed N` | 采样随机种子 |
| `--output DIR` | 自定义结果根目录（默认 `benchmark/iso_solve/results`） |
| `--dry-run` | 仅验证数据加载与过滤，不触发 LLM 调用 |
| `-v` | 开启 DEBUG 日志 |

---

## 结果目录规范

每次实验按 benchmark / mode / run 分层：

```text
results/{benchmark}/{mode}/{model}_{YYYYMMDD_HHMMSS}/
├── report.json
├── summary.txt
└── outputs/
    ├── 0000/
    │   ├── output.md
    │   ├── meta.json
    │   ├── scratchpad.json      # pipeline 模式由 solver 生成
    │   ├── cost_report.json     # pipeline 模式由 solver 生成
    │   ├── task.log             # pipeline 模式由 solver 生成
    │   └── code_runs/           # pipeline+code_execute 产生
    │       └── exec_*/...
    └── 0001/
```

---

## 关于 code_execute 产物落盘

`pipeline` 模式下如果调用 `code_execute`，其执行目录会写入当前题目的 solve 输出目录下（`code_runs/exec_*`），而不是全局 `run_code_workspace`。

这使得单次实验目录具备完整可复现性：题目输出、推理轨迹、开销和代码执行产物全部在同一条目录树内。
