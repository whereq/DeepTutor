<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor：智能体原生的个性化辅导

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-BCDCF7"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-CDCFD4"></a>&nbsp;
  <a href="README_FR.md"><img alt="Français" height="40" src="https://img.shields.io/badge/Français-CDCFD4"></a>&nbsp;
  <a href="README_AR.md"><img alt="Arabic" height="40" src="https://img.shields.io/badge/Arabic-CDCFD4"></a>&nbsp;
  <a href="README_RU.md"><img alt="Русский" height="40" src="https://img.shields.io/badge/Русский-CDCFD4"></a>&nbsp;
  <a href="README_HI.md"><img alt="Hindi" height="40" src="https://img.shields.io/badge/Hindi-CDCFD4"></a>&nbsp;
  <a href="README_PT.md"><img alt="Português" height="40" src="https://img.shields.io/badge/Português-CDCFD4"></a>&nbsp;
  <a href="README_TH.md"><img alt="Thai" height="40" src="https://img.shields.io/badge/Thai-CDCFD4"></a>&nbsp;
  <a href="README_PL.md"><img alt="Polski" height="40" src="https://img.shields.io/badge/Polski-CDCFD4"></a>
</p>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](../../LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/HKUDS/DeepTutor?style=flat-square&color=brightgreen)](https://github.com/HKUDS/DeepTutor/releases)
[![arXiv](https://img.shields.io/badge/arXiv-2604.26962-b31b1b?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2604.26962)

[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-00D4AA?style=flat-square&logo=feishu&logoColor=white)](../../Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-07C160?style=flat-square&logo=wechat&logoColor=white)](https://github.com/HKUDS/DeepTutor/issues/78)

[核心亮点](#key-features) · [快速开始](#get-started) · [探索 DeepTutor](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [多用户](#multi-user) · [社区](#community)

</div>

---

> 🤝 **欢迎各种形式的贡献!** 分支策略、编码规范与上手方式见 [贡献指南](../../CONTRIBUTING.md)。
>
> 🗺️ **路线图** 在 [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) 公开追踪 —— 在那里为已有条目投票或提出新想法。

### 📦 版本发布

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — 三层 Memory 工作台(L1/L2/L3)、所有聊天能力基于单一智能体引擎重建、RAG 全面切换至 LlamaIndex,以及统一的 Settings + Capabilities 入口。

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — 修复远程 Docker CORS、SDK Provider 的 `DISABLE_SSL_VERIFY`、更安全的代码块引用,并将 Matrix E2EE 改为可选扩展。

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — TutorBot 支持 Zulip 与 NVIDIA NIM,思考模型路由更安全,新增 `deeptutor start`、侧栏提示与会话存储一致性提升。

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — 可选多用户部署,具备隔离的用户工作区、管理员授权、认证路由与作用域运行时访问。

<details>
<summary><b>更早发布(两周以前)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — 思考模型/提供商修复,知识索引历史可见,Co-Writer 清空与模板编辑更安全。

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — 聊天与 TutorBot 基于目录的模型选择,更安全的 RAG 重建索引,OpenAI Responses token 上限修复,Skills 编辑器校验。

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — 本地启动设置更顺滑、RAG 查询更安全、本地嵌入鉴权更清晰,Settings 深色模式打磨。

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Book 页对话持久化与重建流程、聊天到 Book 引用、更强的语言/推理处理、RAG 文档抽取加固。

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — NVIDIA NIM 与 Gemini 嵌入支持,统一 Space 上下文(聊天历史/技能/记忆),会话快照,RAG 重建索引韧性。

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — 嵌入端点 URL 透明可读,无效持久化向量时 RAG 重建索引韧性,思考模型输出记忆清理,Deep Solve 运行时修复。

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — 稳定性:更安全的 RAG 路由与嵌入校验、Docker 持久化、输入法友好输入、Windows/GBK 健壮性。

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — 版本化 KB 索引与重建工作流、Knowledge 工作区重构、嵌入自动发现与新适配器、Space 中心。

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — 聊天附件持久化与文件预览抽屉,感知附件的能力流水线,TutorBot Markdown 导出。

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — 文本/代码/SVG 附件、一键 Setup Tour、Markdown 聊天导出、紧凑 KB 管理界面。

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — 文档附件(PDF/DOCX/XLSX/PPTX)、推理思维块展示、Soul 模板编辑器、Co-Writer 保存至笔记本。

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — 用户自建 Skills 体系、聊天输入性能重构、TutorBot 自动启动、Book Library UI、可视化全屏。

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — 分阶段 token 上限、各入口重新生成回复、RAG 与 Gemma 兼容性修复。

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Book Engine「活书」编译器、多文档 Co-Writer、交互式 HTML 可视化、题库 @ 提及。

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — 基于 Schema 的 Channels 标签页、RAG 单一流水线收敛、聊天提示词外置。

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — 通用「立即回答」、Co-Writer 滚动同步、统一设置面板、流式停止按钮。

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — LaTeX 块级公式重构、LLM 诊断探测、Docker 与本地 LLM 说明。

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — 可收藏会话、Snow 主题、WebSocket 心跳与自动重连、嵌入注册表重构。

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — 题目笔记本(书签与分类)、Visualize 支持 Mermaid、嵌入不匹配检测、Qwen/vLLM 兼容、LM Studio 与 llama.cpp,以及 Glass 主题。

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — 搜索整合与 SearXNG 回退、提供商切换修复、前端资源泄漏修复。

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Visualize 能力(Chart.js/SVG)、测验去重、o4-mini 模型支持。

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — 嵌入进度跟踪与限流重试、跨平台依赖修复、MIME 校验修复。

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — 原生 OpenAI/Anthropic SDK(移除 litellm)、Windows 数学动画、健壮 JSON 解析、完整中文 i18n。

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — 设置热重载、MinerU 嵌套输出、WebSocket 修复、最低 Python 3.11+。

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — 智能体原生架构重写(约 20 万行):Tools + Capabilities 插件模型、CLI 与 SDK、TutorBot、Co-Writer、引导学习与持久记忆。

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — 会话持久化、文档增量上传、灵活 RAG 流水线导入、完整中文本地化。

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — RAG-Anything 支持 Docling、日志系统优化与缺陷修复。

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — 统一服务配置、按知识库选择 RAG 流水线、出题改版,以及侧栏定制。

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — 多提供商 LLM 与嵌入支持、新首页、RAG 模块解耦、环境变量重构。

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — 统一 PromptManager 架构、GitHub Actions CI/CD、GHCR 预构建 Docker 镜像。

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Docker 部署、Next.js 16 与 React 19 升级、WebSocket 安全加固、关键漏洞修复。

</details>

### 📰 动态

> **[2026.4.19]** 🎉 111 天内突破 20k star!感谢一路以来的支持 —— 我们将持续迭代,致力于为每个人打造真正个性化的智能辅导。

> **[2026.4.10]** 📄 论文已在 arXiv 上线!阅读[预印本](https://arxiv.org/abs/2604.26962)了解 DeepTutor 背后的设计与理念。

> **[2026.4.4]** 好久不见!✨ DeepTutor v1.0.0 终于上线 —— 智能体原生演进,基于 Apache-2.0 许可证完成自下而上的架构重写,带来 TutorBot 与灵活的模式切换。新篇章已经开启,故事仍在继续!

> **[2026.2.6]** 🚀 39 天内突破 10k star!衷心感谢社区的支持!

> **[2026.1.1]** 新年快乐!欢迎加入 [Discord](https://discord.gg/eRsjPgMU4t)、[微信](https://github.com/HKUDS/DeepTutor/issues/78) 或 [Discussions](https://github.com/HKUDS/DeepTutor/discussions),一起塑造 DeepTutor 的未来!

> **[2025.12.29]** DeepTutor 正式发布!


<a id="key-features"></a>
## ✨ 核心亮点

**工作面**

- Chat —— Chat、Solve、Quiz、Research、Visualize 共享同一会话、知识库与引用历史,可在对话中逐级升级而不丢失上下文。
- Co-Writer —— 分栏 Markdown 工作区,任意选区都可改写、扩写或缩写,可选择由 KB 或网络支撑。草稿可一键存入笔记本。
- Book Engine —— 多智能体流水线把你的材料编译成交互式「活书」,包含 13 种块类型:测验、闪卡、时间线、概念图、内嵌的 GeoGebra 浏览器、动画等。页面对 KB 做指纹标记,任何漂移都可检测。

**你的资料库**

- Knowledge Bases —— 版本化、可用于 RAG 的文档集合,端到端基于 LlamaIndex。每次(重新)索引都被追踪、可比较、可回滚。
- Space —— 个人复习库,聚合聊天历史、笔记本、题库与用户自建的 Skills(`SKILL.md`),后者可切换 DeepTutor 的人格。
- 三层 Memory —— 仅追加的 L1 轨迹、L2 按工作面整理且带引用的事实、L3 跨工作面的综合。可审查的工作台与 Memory Graph 让你审视 DeepTutor「为什么知道」这些信息。

**可扩展性与可控性**

- 可组合的工具 —— RAG、网络搜索、代码执行、推理、头脑风暴、论文搜索、GeoGebra 分析,以及聊天助手(`ask_user`、`web_fetch`、`write_note`、`list_notebook`、`github_query`)。MCP 服务器与内置工具并列接入。
- 个人 TutorBot —— 持续、自主的导师,各自拥有工作区、Soul、Skills 与频道(Telegram、Discord、Slack、Matrix、Zulip 等)。基于 [nanobot](https://github.com/HKUDS/nanobot) 构建。
- 统一 Settings —— 唯一的草稿 / Apply 工作台,统管外观、模型、嵌入、搜索、能力、记忆、MCP 服务器与工具,并共享按调用计费的成本跟踪。
- 智能体原生 CLI —— 每个能力、KB、会话与 TutorBot 一条命令搞定;人类看富文本,智能体看结构化 JSON。把根目录的 [`SKILL.md`](../../SKILL.md) 交给任意可调用工具的 LLM,它就能自己驾驭 DeepTutor。
- 可选身份认证 —— 默认关闭;启用后即可部署多用户场景,具备 bcrypt + JWT、管理员面板,以及可选的 PocketBase / OAuth 侧车。

---

<a id="get-started"></a>
## 🚀 快速开始

DeepTutor 现在提供四条并行的安装路径,所有方式共享同一份运行时配置布局:

- 设置保存在当前工作区下的 `data/user/settings/`,或当你显式指定时位于 `DEEPTUTOR_HOME` / `deeptutor start --home` 所指目录。
- `model_catalog.json` 存放模型提供商档案、Base URL、API Key、激活模型、嵌入设置与搜索设置。
- `system.json` 存放启动端口、公共 API base、CORS、TLS 与附件选项。
- `auth.json` 存放可选的认证开关与引导凭证哈希。
- `integrations.json` 存放可选侧车(如 PocketBase)的设置。
- 项目根目录的 `.env` 不再作为应用配置文件使用。

要使用完整本地应用,推荐顺序是 **选择工作区 → 安装 → `deeptutor init` → `deeptutor start`**。`deeptutor start` 可作为安全网回填缺失的默认文件,但正常首次配置应当先通过 `deeptutor init` 明确写入端口与模型设置,再启动 Web 应用。

### 方案 1 —— 安装 DeepTutor

适用于希望获得完整本地 Web 应用与 CLI、但不想克隆仓库的用户。

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **想尝鲜 v1.4.0 beta?** PyPI 会把 `1.4.0-beta` 规范化为 `1.4.0b0`,所以 `pip install -U deeptutor` 仍会停留在最新稳定版。可用以下任意一条命令选择预发布版本:
>
> ```bash
> pip install --pre -U deeptutor      # 最新预发布版本
> pip install -U deeptutor==1.4.0b0   # 精确锁定到 v1.4.0-beta
> ```

`deeptutor init` 会在执行目录下的 `data/user/settings/` 写入配置,会询问:

- 后端端口,默认 `8001`
- 前端端口,默认 `3782`
- LLM 提供商绑定、Base URL、API Key 与模型名
- 可选的嵌入提供商(用于 Knowledge Base / RAG)

`deeptutor start` 完成后,打开终端中输出的前端 URL。默认端口下该 URL 是 [http://127.0.0.1:3782](http://127.0.0.1:3782)。如果你在 `deeptutor init` 中或之后编辑 `data/user/settings/system.json` 修改了 `frontend_port`,请使用配置后的端口。

请保持 `deeptutor start` 的终端窗口打开。在该终端按 `Ctrl+C` 即可同时停止后端与前端。

注意:

- `deeptutor start` 会同时启动 FastAPI 后端与打包好的 Next.js 前端。
- 打包好的 Web 应用不需要 `git clone` 或 `npm install`,但仍需要本地的 Node.js 20+ 运行时来执行内置的 Next.js 独立服务器。
- 如果你为了快速试用刻意跳过了 `deeptutor init`,应用会以安全的默认端口与空模型设置启动;启动后再到 **Settings → Models** 中配置模型即可。

### 方案 2 —— 从源码安装

适用于参与 DeepTutor 开发或希望从代码检出直接运行的用户。请使用 Python 3.11+ 与 Node.js 22 LTS,以贴近 CI 与 Docker 环境。

**1. 克隆仓库**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. 创建 Python 环境**

macOS / Linux 下使用 `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell 下使用 `venv`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Conda / Miniconda:

```bash
conda create -n deeptutor python=3.11
conda activate deeptutor
python -m pip install --upgrade pip
```

**3. 安装本地包与前端依赖**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

如果你有意修改了前端依赖,请使用 `npm install --legacy-peer-deps` 刷新 `web/package-lock.json`,然后同时提交 `web/package.json` 与 `web/package-lock.json`。

**4. 配置并启动**

```bash
deeptutor init
deeptutor start
```

源码安装会使用本地 `web/` 目录作为前端,并以 Next.js 开发模式启动。使用过程中请保持 `deeptutor start` 的终端窗口打开。这种方式刻意面向开发者友好,不会向 `.env` 写入配置;直接编辑 `data/user/settings/*.json` 或使用 Web Settings 页面即可。

如果 `deeptutor start` 报告已有但无响应的前端,请停掉提示中打印的 PID。若没有正在运行的 Next.js 进程,请删除残留的锁文件后重新启动:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

实用的开发者扩展:

```bash
pip install -e ".[dev]"             # 测试/lint 工具
pip install -e ".[tutorbot]"        # TutorBot 引擎 + 频道 SDK
pip install -e ".[matrix]"          # Matrix 频道(不含 E2EE/libolm)
pip install -e ".[matrix-e2e]"      # Matrix E2EE;需要 libolm
pip install -e ".[math-animator]"   # Manim 扩展;需要 LaTeX/ffmpeg/系统库
```

### 方案 3 —— Docker

适用于希望一个容器内拥有完整 Web 应用的用户。镜像发布在 GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` —— 稳定版本
- `ghcr.io/hkuds/deeptutor:pre` —— 预发布版本(若可用)

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

然后访问 [http://127.0.0.1:3782](http://127.0.0.1:3782)。配置、API Key、日志、工作区文件、记忆与知识库都保存在 `deeptutor-data` 卷中,挂载于 `/app/data`。

容器在首次启动时会自动创建 `/app/data/user/settings/*.json`。你可以直接在 Web Settings 页面里配置模型提供商,无需手动准备本地 JSON 文件。

如需使用不同的宿主端口,只需修改 `-p` 映射的左侧。例如 `-p 127.0.0.1:8088:3782` 会让 Web UI 在 `http://127.0.0.1:8088` 暴露,而容器内仍监听 `3782`。如果你在 `/app/data/user/settings/system.json` 中修改了容器端口,请重启容器,并让每个 `-p 宿主:容器` 映射的右侧与配置后的容器端口一致。

#### 连接到 Ollama 或其他宿主服务

在 Docker 容器内部,`localhost` 指向容器自身,不是你的宿主机。如果你在宿主机上运行 Ollama、LM Studio、llama.cpp、vLLM 或其他模型服务,可以使用以下方式之一。

方案 A —— host gateway(常规 Docker 运行推荐方式):

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

然后在 **DeepTutor Settings → Models** 中,将提供商的 Base URL 设为 `host.docker.internal`:

- Ollama LLM 端点:`http://host.docker.internal:11434/v1`
- Ollama 嵌入端点:`http://host.docker.internal:11434/api/embed`
- LM Studio:`http://host.docker.internal:1234/v1`
- llama.cpp:`http://host.docker.internal:8080/v1`

在 macOS / Windows 上的 Docker Desktop 中,即便不加 `--add-host`,`host.docker.internal` 通常也可用。在 Linux 上,`--add-host=host.docker.internal:host-gateway` 是在现代 Docker Engine 上创建该主机名的可移植方式。

方案 B —— host networking(仅 Linux):

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

host-network 模式下无需 `-p` 映射。容器直接共享宿主网络,所以默认访问 [http://127.0.0.1:3782](http://127.0.0.1:3782),或访问 `/app/data/user/settings/system.json` 中配置的 `frontend_port`。这种模式下,宿主服务通常可以用普通的 localhost URL 访问,例如 `http://127.0.0.1:11434/v1`。host networking 会把容器端口直接暴露在宿主上,可能与已有服务冲突。

如需后台运行,加上 `-d` 并按名称查看日志:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

如需停止前台运行的 Docker,按 `Ctrl+C`。如果使用了上面带名字的后台容器,运行 `docker stop deeptutor`。在用相同名称启动新容器之前,请用 `docker rm deeptutor` 移除已停止的容器;`deeptutor-data` 卷会保留你的设置与工作区。

### 方案 4 —— 仅 CLI

适用于不需要 Web UI 的场景。仅 CLI 的包从本地源码检出安装,而非 PyPI。

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

python3 -m venv .venv-cli
source .venv-cli/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./packaging/deeptutor-cli
deeptutor init --cli
deeptutor chat
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ./packaging/deeptutor-cli
deeptutor init --cli
deeptutor chat
```

`deeptutor init --cli` 使用与完整应用相同的 `data/user/settings/` 布局,但会调整向导行为:

- 跳过后端/前端端口提示,因为纯 CLI 使用不会启动 Web 应用。
- 仍会写入默认的 `system.json`、`auth.json`、`integrations.json`、`model_catalog.json`、`main.yaml` 与 `agents.yaml`,确保运行时布局完整。
- 仍会询问激活的 LLM 提供商与模型。
- 询问是否配置嵌入,默认答案为 `No`;如果计划使用 `deeptutor kb ...` 或 RAG 工具,请选择 `Yes`。

常用 CLI 命令:

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "Explain Fourier transform"
deeptutor run deep_solve "Solve x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
deeptutor config show
```

本地的 `deeptutor-cli` 安装不包含 Web 资源与服务器依赖。请保留源码检出目录,因为可编辑安装指向它。如果你之后想要 Web 应用,可以在同一份检出中改用方案 2,或者卸载本地 CLI 包,通过 `pip install -U deeptutor` 安装完整 PyPI 包,需要 Web 端口时再运行 `deeptutor init`,然后在同一工作区运行 `deeptutor start`。

### 配置参考

Web Settings 页面是推荐的编辑器,但底层文件都是普通 JSON/YAML,也可以直接管理:

| 文件 | 用途 |
|:---|:---|
| `data/user/settings/model_catalog.json` | LLM、嵌入与搜索提供商档案;API Key;激活模型 |
| `data/user/settings/system.json` | 后端/前端端口、公共 API base、CORS、SSL 校验、附件目录 |
| `data/user/settings/auth.json` | 可选认证开关、用户名、密码哈希、token/cookie 设置 |
| `data/user/settings/integrations.json` | 可选的 PocketBase 与侧车集成设置 |
| `data/user/settings/interface.json` | UI 语言/主题/侧栏偏好 |
| `data/user/settings/main.yaml` | 运行时行为默认值与路径注入 |
| `data/user/settings/agents.yaml` | 能力/工具的 temperature 与 token 设置 |

模型的最简配置可在浏览器中完成:打开 **Settings → Models**,新增一个 LLM 档案,填写 Base URL / API Key / 模型名后保存。仅在你打算使用 Knowledge Base / RAG 功能时再添加嵌入档案。

<a id="explore-deeptutor"></a>
## 📖 探索 DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

v1.4.0-beta 的重构将 DeepTutor 重新组织为 **五个核心工作面** —— Chat、Co-Writer、Book、Knowledge、Space —— 加上位于它们之下的 **三层 Memory**,以及暴露所有旋钮的统一 **Settings** 工作台。能力(Solve / Quiz / Research / Visualize)与工具(RAG、网络、代码、推理、头脑风暴、论文搜索、`ask_user`、`web_fetch`、`write_note`、`list_notebook`、`github_query`)可以在它们之上自由组合。

### 💬 Chat —— 统一的智能工作区

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

一个线程,五种模式,任意工具。能力选择器就在输入框中;同一会话、同一知识库、同一份附件与引用会随着你在模式之间切换 —— 从一个随手的问题,跨入多智能体解题、出题、完整研究报告,而不丢失上下文。

| 模式 | 用途 | 底层 |
|:---|:---|:---|
| **Chat** | 灵活对话,可调用任意工具:RAG、网络搜索、代码执行、深度推理、头脑风暴、论文搜索、GeoGebra 分析。 | LlamaIndex 驱动的 RAG + 工具注册表 |
| **Solve** | 多步规划 → 调研 → 解答 → 校验,附精准来源引用。 | 智能体引擎(`deep_solve`) |
| **Quiz** | 基于你的 KB 自动校验的出题;为每道题派生后续聊天输入框。 | 智能体引擎(`deep_question`) |
| **Research** | 将主题拆分为子主题,跨 RAG / 网络 / arXiv 派发并行智能体,产出带引用的报告,并支持迭代式追加修订。 | 重写的 `pipeline.py`(代码缩减约 45%,引用与迭代式撰写完整保留) |
| **Visualize** | 生成 SVG 图、Chart.js 图表、Mermaid 图、交互式 HTML 页面,**或** Manim 视频 / 故事板 —— 分析器会选择合适的 `render_type`。 | Visualize 流水线(已合并 Animator) |

本次重构随之上线的 **新聊天工具**:`ask_user`(在中途提出结构化追问)、`web_fetch`(把指定 URL 拉入上下文)、`write_note` / `list_notebook`(在聊天面里保存与列出笔记本记录),以及 `github_query`(查询 issue / PR / 仓库)。工具与工作流保持 **解耦** —— 每个模式都允许你按回合自主启用或禁用工具。

会话还会跨回合维护一份 **累积来源清单**,先前 RAG / 网络的命中结果在同一对话后续仍然可被重复引用。

### ✍️ Co-Writer —— 多文档 AI 写作工作区

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer 是一个分栏 Markdown 工作台(左侧原文编辑器,右侧实时预览),适合写笔记、报告、教程,以及 AI 辅助的初稿。每个文档拥有独立工作区,支持自动保存、Markdown 下载,以及一键 **Save to Notebook**。

选中任意文本即可选择 **Rewrite**、**Expand** 或 **Shorten** —— 每个动作都作为可追踪的智能体编辑执行,并可选择从知识库或网络获取支持。Co-Writer 渲染标准 Markdown / CommonMark / GFM(表格、代码、数学公式、流程图、时序图),支持 HTML 标签的逃逸出口(`<sub>`、`<sup>`、`<abbr>`、`<mark>`),并附带为 DeepTutor 产品文档与学习笔记调好的初始模板。

### 📖 Book Engine —— 交互式「活书」

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

给 DeepTutor 一个主题,把它指向你的知识库,它就能产出一本结构化、可交互的书 —— 不是静态导出,而是一份你可以阅读、自测、在上下文中讨论的活文档。

幕后,多智能体流水线承担繁重任务:提出大纲、从 KB 检索相关来源、综合成章节树、规划每页内容,并编译每一个块。你始终掌握主动 —— 审阅提案、重排章节,并能在任何一页旁边继续对话。

页面由 13 种块类型组装而成 —— 文本、callout、测验、闪卡、代码、图、深度剖析、动画、交互演示(现在包含 **GeoGebra 浏览器**)、时间线、概念图、章节与用户笔记 —— 每一种都用自己的交互组件渲染。Book 页面会对源 KB 做指纹标记;`deeptutor book health` 报告漂移,`deeptutor book refresh-fingerprints` 在源变化后清理过期页面。

### 📚 Knowledge Bases —— RAG 就绪的文档库

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

为支撑 RAG 的文档集合准备的专属工作区。每个知识库有四个标签页:

- **Files** —— 浏览上传过的来源、就地预览 PDF,并查看每个文件的大小 / 状态。
- **Add documents** —— 上传 PDF、Office 文件(DOCX / XLSX / PPTX)、Markdown、纯文本,以及种类丰富的代码 / 数据文件。文档会被自动路由到合适的抽取器。
- **Index versions** —— 每次(重新)索引都是一个被追踪的版本。你可以回滚到更早的索引、比较嵌入模型,或者检查分块统计,而不会丢失之前的构建。
- **Settings** —— 为该 KB 选择嵌入提供商 / 模型、分块参数与重排器。默认值继承自你的全局 LLM 与嵌入档案。

索引端到端基于 **LlamaIndex**(此前的双流水线拆分已在 v1.4 重构中合并),具备重试安全的重建索引、嵌入不匹配检测,以及对受损的持久化向量的健壮处理。

### 🌐 Space —— 个人学习库

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space 是与活跃工作面相对的 **阅读 / 复习** 一侧。Chat / Co-Writer / Book 是你*产出*的地方,Space 则是你产出的一切的归宿,可搜索、可回放。

- **Chat History** —— 跨所有模式的全部对话,支持重命名、删除与恢复;每个入口均支持删除单条回合。
- **Notebooks** —— 把 Chat、Research 与 Co-Writer 的输出保存到按类别与配色组织的笔记本;每条记录都链回它的源会话与工作面。
- **Question Bank** —— 每一道自动生成的测验题,可加书签,也可在聊天中通过 @ 提及来对过往表现进行推理。
- **Skills** —— 用户自建的 `SKILL.md` 文件,定义教学人格(名称、描述、触发条件、正文)。激活后,某个 skill 会被注入聊天系统提示 —— 把 DeepTutor 变成一名苏格拉底式导师、一位研究助理,或任何你设计的角色。

### 🧠 Memory —— 三层架构

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

DeepTutor 的记忆现在是一条 **三层流水线**,并在 `/memory` 提供一个可审查的工作台。v1 的双文件 `SUMMARY.md` / `PROFILE.md` 模型已经退役;首次启动时会把所有内容迁移到新布局。

| 层 | 角色 | 存储 |
|:---|:---|:---|
| **L1 · Workspace mirror**(LIVE) | 按工作面、按天追加的交互轨迹。是真实发生过事情的无损记录。 | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Per-surface summaries**(CURATED) | 由整合器抽取的、面向具体工作面的事实。每条事实都带有指回 L1 轨迹的脚注引用。支持按文档的 **Update / Audit / Dedup** 任务。 | `L2/<surface>.md` |
| **L3 · Cross-surface knowledge**(SYNTHESIS) | 跨工作面的综合:你的 `profile`、`recent` 时间线、知识 `scope` 与 `preferences`。每条带保留语气的论断都由 L2 证据支撑。 | `L3/<recent\|profile\|scope\|preferences>.md` |

七个工作面为该流水线供数据:**chat、notebook、quiz、kb、book、tutorbot、cowriter**。整合器由 LLM 驱动,并异步运行(`POST /memory/runs/start`)—— 你可以从工作台触发它,看着 L1 → L2 → L3 一路传播,并手动编辑任意层。

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

**Memory Graph**(`/memory/graph`)同时呈现三层:L3 综合位于中心,L2 事实位于中环,L1 轨迹位于外圈,按工作面分组。悬停任意节点查看内联预览;点击可锁定高亮,沿 L3 → L2 → L1 向内追溯引用,让你审视 DeepTutor「为什么知道」你的这些信息。

### ⚙️ Settings —— 统一控制中心

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

设置入口在 v1.4 完成统一并按关注点拆分,采用草稿 / **Apply** 模型 —— 修改是原子化的,在保存前可撤回:

- **Appearance** —— UI 语言与主题(Cream、Snow、Dark、Glass)。
- **Status** —— 跨 LLM、嵌入、搜索与存储后端的实时健康探测。
- **LLM**、**Embedding**、**Search** —— 提供商目录、Base URL、API Key 与激活模型选择。激活模型从目录中挑选,使每个工作面保持同步。
- **Capabilities** —— 为 Chat、Solve、Quiz、Research、Visualize 与 Co-Writer 提供按能力的可调项(分块、LLM 预算、去重与引用策略、最大迭代次数)。背后由统一的 `emit_capability_result` 信封与共享的 `UsageTracker` 支撑,后者揭示按调用计费的成本。
- **Memory** —— 切换整合器运行,配置节奏与预算,并跳转到 Memory 工作台。
- **MCP servers** —— 注册外部的 Model Context Protocol 服务器;它们的工具与内置工具并列展示。
- **Tools** —— 查看每个内置工具、它的参数、状态(已启用 / 即将上线)与 i18n 状态文案。

「Tour」启动器会带新用户走完整页,每个能力都附带规范的 `capabilities/prompts/{en,zh}/<name>.yaml`,以保证状态消息在英文与中文之间保持一致。

---

<a id="tutorbot"></a>
### 🦞 TutorBot —— 持久、自主的 AI 导师

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot 不是聊天机器人 —— 它是 **持久的、多实例的智能体**,基于 [nanobot](https://github.com/HKUDS/nanobot) 构建。每个 TutorBot 都跑着自己的智能体循环,拥有独立的工作区、记忆与人格。你可以创建一个苏格拉底式数学导师、一位耐心的写作教练,以及一名严谨的研究顾问 —— 它们同时运行,各自与你一同成长。

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Soul 模板** —— 通过可编辑的 Soul 文件定义导师的人格、语气与教学哲学。从内置原型(苏格拉底式、鼓励式、严谨式)中选用,或者自行打造 —— soul 塑造每一次回复。
- **独立工作区** —— 每个 bot 拥有自己的目录,以及隔离的记忆、会话、Skills 与配置 —— 完全隔离,但仍可访问 DeepTutor 的共享知识层。
- **主动心跳** —— bot 不只是回应 —— 它会主动发起。内置的心跳系统支持周期性学习打卡、复习提醒与定时任务。即便你没找它,你的导师也会准时出现。
- **完整工具访问** —— 每个 bot 都能调用 DeepTutor 的完整工具箱:RAG 检索、代码执行、网络搜索、学术论文搜索、深度推理与头脑风暴。
- **技能学习** —— 通过向 bot 工作区添加 skill 文件来教它新本领。随着你的需求演进,你的导师能力也跟着扩展。
- **多频道存在** —— 把 bot 接入 Telegram、Discord、Slack、飞书、企业微信、钉钉、Matrix、QQ、WhatsApp、邮件等。你在哪里,导师就在哪里。
- **团队与子智能体** —— 在单个 bot 内派生后台子智能体,或编排多智能体团队,以承接复杂、长时间运行的任务。

```bash
deeptutor bot create math-tutor --persona "Socratic math teacher who uses probing questions"
deeptutor bot create writing-coach --persona "Patient, detail-oriented writing mentor"
deeptutor bot list                  # 查看所有活跃的导师
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI —— 智能体原生接口

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor 完全 CLI 原生。每个能力、知识库、会话、记忆与 TutorBot 都可以通过一条命令操作 —— 无需浏览器。CLI 同时服务人类(富文本终端渲染)与 AI 智能体(结构化 JSON 输出)。

把项目根目录的 [`SKILL.md`](../../SKILL.md) 交给任何可调用工具的智能体([nanobot](https://github.com/HKUDS/nanobot),或者任何有工具访问能力的 LLM),它就能自主配置并操作 DeepTutor。

**一次性执行** —— 直接在终端运行任意能力:

```bash
deeptutor run chat "Explain the Fourier transform" -t rag --kb textbook
deeptutor run deep_solve "Prove that √2 is irrational" -t reason
deeptutor run deep_question "Linear algebra" --config num_questions=5
deeptutor run deep_research "Attention mechanisms in transformers"
deeptutor run visualize "Draw the architecture of a transformer"
```

**交互式 REPL** —— 支持实时切换模式的持久聊天会话:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# 在 REPL 内:/cap、/tool、/kb、/history、/notebook、/config 即可即时切换
```

**知识库生命周期** —— 完全在终端中构建、查询并管理 RAG 就绪的集合:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # 从文档创建
deeptutor kb add my-kb --docs-dir ./papers/         # 添加一批论文
deeptutor kb search my-kb "gradient descent"        # 直接搜索
deeptutor kb set-default my-kb                      # 设为所有命令的默认 KB
```

**双输出模式** —— 给人看的富文本,给流水线用的结构化 JSON:

```bash
deeptutor run chat "Summarize chapter 3" -f rich    # 彩色、格式化输出
deeptutor run chat "Summarize chapter 3" -f json    # 行分隔的 JSON 事件
```

**会话连续性** —— 在任何一次对话中断的位置接着继续:

```bash
deeptutor session list                              # 列出所有会话
deeptutor session open <id>                         # 在 REPL 中恢复
```

<details>
<summary><b>完整 CLI 命令参考</b></summary>

**顶层**

| 命令 | 说明 |
|:---|:---|
| `deeptutor run <capability> <message>` | 单轮运行任意能力(`chat`、`deep_solve`、`deep_question`、`deep_research`、`math_animator`、`visualize`) |
| `deeptutor chat` | 交互式 REPL,可选 `--capability`、`--tool`、`--kb`、`--language` |
| `deeptutor serve` | 启动 DeepTutor API 服务 |

**`deeptutor bot`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor bot list` | 列出所有 TutorBot 实例 |
| `deeptutor bot create <id>` | 创建并启动新 bot(`--name`、`--persona`、`--model`) |
| `deeptutor bot start <id>` | 启动一个 bot |
| `deeptutor bot stop <id>` | 停止一个 bot |

**`deeptutor kb`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor kb list` | 列出所有知识库 |
| `deeptutor kb info <name>` | 显示知识库详情 |
| `deeptutor kb create <name>` | 从文档创建(`--doc`、`--docs-dir`) |
| `deeptutor kb add <name>` | 增量添加文档 |
| `deeptutor kb search <name> <query>` | 搜索知识库 |
| `deeptutor kb set-default <name>` | 设为默认 KB |
| `deeptutor kb delete <name>` | 删除知识库(`--force`) |

**`deeptutor memory`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor memory show [file]` | 查看记忆(`summary`、`profile` 或 `all`) |
| `deeptutor memory clear [file]` | 清空记忆(`--force`) |

**`deeptutor session`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor session list` | 列出会话(`--limit`) |
| `deeptutor session show <id>` | 查看会话消息 |
| `deeptutor session open <id>` | 在 REPL 中恢复会话 |
| `deeptutor session rename <id>` | 重命名会话(`--title`) |
| `deeptutor session delete <id>` | 删除会话 |

**`deeptutor notebook`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor notebook list` | 列出笔记本 |
| `deeptutor notebook create <name>` | 创建笔记本(`--description`) |
| `deeptutor notebook show <id>` | 查看笔记本记录 |
| `deeptutor notebook add-md <id> <path>` | 导入 markdown 作为记录 |
| `deeptutor notebook replace-md <id> <rec> <path>` | 替换 markdown 记录 |
| `deeptutor notebook remove-record <id> <rec>` | 移除一条记录 |

**`deeptutor book`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor book list` | 列出工作区中的所有书 |
| `deeptutor book health <book_id>` | 检查 KB 漂移与书的健康状态 |
| `deeptutor book refresh-fingerprints <book_id>` | 刷新 KB 指纹并清理过期页面 |

**`deeptutor config` / `plugin` / `provider`**

| 命令 | 说明 |
|:---|:---|
| `deeptutor config show` | 打印当前配置摘要 |
| `deeptutor plugin list` | 列出已注册的工具与能力 |
| `deeptutor plugin info <name>` | 显示工具或能力详情 |
| `deeptutor provider login <provider>` | 提供商认证(`openai-codex` 走 OAuth 登录;`github-copilot` 校验已有的 Copilot 认证会话) |

</details>

---

<a id="multi-user"></a>
### 👥 多用户 —— 共享部署 + 用户级工作区

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

打开身份认证后,DeepTutor 就变成一个多租户部署,具备 **按用户隔离的工作区** 与 **管理员集中管理的资源**。首位注册者成为管理员,代表所有人配置模型、API Key 与知识库。后续账号由管理员创建(仅邀请制),每位用户都拥有自己作用域内的聊天历史 / 记忆 / 笔记本 / 知识库,并且只看到管理员分配给他们的 LLM、KB 与 skills。

**快速开始(5 步):**

```bash
# 1. 在 data/user/settings/auth.json 中启用认证:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. 重启 Web 栈。
deeptutor start

# 3. 打开 http://localhost:3782/register 创建首个账号。
#    首次注册是唯一公开的;该用户成为管理员,
#    之后 /register 端点会自动关闭。

# 4. 以管理员身份打开 /admin/users → 「Add user」为团队成员开账号。

# 5. 对每位用户点击 slider 图标 → 分配 LLM 档案、知识库与 skills。
#    保存。该用户即可登录并开始使用。
```

**管理员看到的:**

- **完整 Settings 页面**(`/settings`)—— 管理 LLM / 嵌入 / 搜索提供商、API Key、模型目录与运行时「Apply」。
- **用户管理**(`/admin/users`)—— 创建、提升、降级与删除账号。一旦首位管理员出现,公开的 `/register` 端点会自动关闭;后续账号通过 `POST /api/v1/auth/users`(仅管理员)创建。
- **授权编辑器** —— 对每位非管理员用户,挑选他们可使用的模型档案、知识库与 skills。授权仅携带 **逻辑 ID**;API Key 永远不会跨过授权边界。
- **审计追踪** —— 每一次授权变更与对所授资源的访问都会追加到 `multi-user/_system/audit/usage.jsonl`。

**普通用户得到的:**

- **隔离工作区** 位于 `multi-user/<uid>/` —— 自己的聊天历史(`chat_history.db`)、记忆(`SUMMARY.md` / `PROFILE.md`)、笔记本与个人知识库。默认彼此不共享。
- **只读访问** 管理员所分配的知识库与 skills,在他们自己的资源旁内嵌展示,并带有「Assigned by admin」标签。
- **脱敏 Settings 页面** —— 只显示主题、语言与已授权模型的摘要。非管理员请求永远不会返回 API Key、Base URL 与提供商端点。
- **作用域 LLM** —— 聊天回合通过管理员所分配的模型进行路由。如果没有授权 LLM,该回合会被前置拒绝(不会静默回退到管理员的 Key)。

**工作区布局:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # 哈希后的凭证、角色
│   ├── auth/auth_secret         # JWT 签名密钥(自动生成)
│   ├── grants/<uid>.json        # 按用户的资源授权(管理员管理)
│   └── audit/usage.jsonl        # 审计追踪
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**配置参考:**

| 设置 | 必填 | 说明 |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | 是 | 设为 `true` 开启多用户认证。默认 `false`(单用户模式 —— 全程走管理员路径)。 |
| `multi-user/_system/auth/auth_secret` | 推荐 | JWT 签名密钥。若缺失,会在首次启用认证启动时自动生成。 |
| `data/user/settings/auth.json: token_expire_hours` | 否 | JWT 有效期;默认 `24`。 |
| `data/user/settings/auth.json: username/password_hash` | 否 | 可选的无界面单用户引导凭证。使用浏览器注册时留空即可。 |
| `data/user/settings/system.json` | 否 | `deeptutor start` 会从运行时设置推导前端认证开关与 API base。 |

> ⚠️ **PocketBase 模式(`integrations.pocketbase_url` 已设)仅支持单用户。** 默认 PocketBase schema 在 `users` 上没有 `role` 字段(每次登录都解析为 `role=user`,无法创建管理员),并且 `sessions` / `messages` / `turns` 的查询没有按 `user_id` 过滤。多用户部署必须保持 `integrations.pocketbase_url` 为空,使用默认的 JSON/SQLite 后端。

> ⚠️ **建议单进程部署。** 首位用户晋升管理员的逻辑由进程内的 `threading.Lock` 保护。多 worker 部署应当离线开通首位管理员(以 `auth.json.enabled=false` 启动,通过引导流程注册管理员,然后再把 `auth.json.enabled` 设为 `true`),或者使用外部系统承载用户存储。

<a id="community"></a>
## 🌐 社区与生态

DeepTutor 立足于一系列出色的开源项目:

| 项目 | 在 DeepTutor 中的角色 |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | 驱动 TutorBot 的超轻量智能体引擎 |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | RAG 流水线与文档索引主干 |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | Math Animator 的 AI 驱动数学动画生成 |

**来自 HKUDS 生态:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| 简洁高速的 RAG | 零代码智能体框架 | 自动化研究 | 超轻量 AI 智能体 |


## 🤝 贡献

<div align="center">

希望 DeepTutor 能成为送给社区的一份礼物。 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

开发环境搭建、代码规范与 PR 流程见 [CONTRIBUTING.md](../../CONTRIBUTING.md)。

## ⭐ Star 历史

<div align="center">

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
  </picture>
</a>

</div>

<p align="center">
 <a href="https://www.star-history.com/hkuds/deeptutor">
  <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
   <img alt="Star History Rank" src="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
  </picture>
 </a>
</p>

<div align="center">

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ Star 我们](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 报告 bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussions](https://github.com/HKUDS/DeepTutor/discussions)

---

基于 [Apache License 2.0](../../LICENSE) 开源。

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
