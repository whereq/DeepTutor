# 配置说明

## 配置文件

| 文件 | 用途 |
|:-----|:--------|
| `.env` | API 密钥、端口、服务商 |
| `config/agents.yaml` | LLM 参数（temperature、max_tokens）|
| `config/main.yaml` | 路径、工具、模块设置 |

## 环境变量

### 必需配置

```bash
# LLM
LLM_MODEL=gpt-4o
LLM_API_KEY=your_api_key
LLM_HOST=https://api.openai.com/v1

# Embedding
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_API_KEY=your_api_key
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_DIMENSION=3072
```

### 可选配置

```bash
# 服务端口（默认：8001/3782）
BACKEND_PORT=8001
FRONTEND_PORT=3782

# 远程访问
NEXT_PUBLIC_API_BASE=http://your-server-ip:8001

# 网络搜索（统一 API Key）
SEARCH_PROVIDER=perplexity  # 可选：perplexity, tavily, serper, jina, exa, baidu
SEARCH_API_KEY=your_search_api_key

# TTS 语音合成
TTS_MODEL=
TTS_URL=
TTS_API_KEY=
```

## 🤗 HuggingFace / MinerU（可选：离线/镜像网络）

如果你的环境无法直接访问 `huggingface.co`（比如内网/校园网/离线环境），MinerU 在尝试从 HuggingFace Hub 下载模型时可能会失败。DeepTutor 会读取根目录 `.env`（并且 `docker-compose.yml` 通过 `env_file: .env` 注入到容器），因此你可以在 `.env` 里**按需添加**下面这些变量：

```bash
# ============================================================================
# HuggingFace Hub / MinerU - 可选
# ============================================================================
# 使用 HuggingFace 镜像站点（如果你有可用的镜像域名）
# HF_ENDPOINT=https://your-hf-mirror.example.com

# 缓存目录（容器内路径）。Docker 建议把该目录挂载出来以便复用缓存。
# HF_HOME=/app/data/hf

# 强制离线模式（前提：模型已在本地缓存中）
# HF_HUB_OFFLINE=1
```

## Agent 参数

编辑 `config/agents.yaml`:

```yaml
solve:
  temperature: 0.3
  max_tokens: 8192

research:
  temperature: 0.5
  max_tokens: 12000

question:
  temperature: 0.7
  max_tokens: 4096
```

## 数据存储位置

```text
data/
├── knowledge_bases/    # 你上传的文档
└── user/
    ├── solve/          # 解题输出
    ├── question/       # 生成的题目
    ├── research/       # 研究报告
    ├── guide/          # 学习会话
    └── logs/           # 系统日志
```

---

📖 **完整参考**: [config/README.md](https://github.com/HKUDS/DeepTutor/tree/main/config)
