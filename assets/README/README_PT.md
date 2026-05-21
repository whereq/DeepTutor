<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: tutoria personalizada nativa para agentes

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-CDCFD4"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-CDCFD4"></a>&nbsp;
  <a href="README_FR.md"><img alt="Français" height="40" src="https://img.shields.io/badge/Français-CDCFD4"></a>&nbsp;
  <a href="README_AR.md"><img alt="Arabic" height="40" src="https://img.shields.io/badge/Arabic-CDCFD4"></a>&nbsp;
  <a href="README_RU.md"><img alt="Русский" height="40" src="https://img.shields.io/badge/Русский-CDCFD4"></a>&nbsp;
  <a href="README_HI.md"><img alt="Hindi" height="40" src="https://img.shields.io/badge/Hindi-CDCFD4"></a>&nbsp;
  <a href="README_PT.md"><img alt="Português" height="40" src="https://img.shields.io/badge/Português-BCDCF7"></a>&nbsp;
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

[Recursos](#key-features) · [Começar](#get-started) · [Explorar](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [Multi-usuário](#multi-user) · [Comunidade](#community)

</div>

---

> 🤝 **Aceitamos todo tipo de contribuição!** Veja o [Guia de contribuição](../../CONTRIBUTING.md) para estratégia de branches, padrões de código e como começar.
>
> 🗺️ **O roteiro** é mantido aberto em [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — comente lá para votar em itens ou propor novos.

### 📦 Lançamentos

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — Workbench de Memory de três camadas (L1/L2/L3), todas as capacidades de chat reconstruídas sobre um único motor agentic, RAG só com LlamaIndex e uma superfície unificada de Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Recuperação de CORS em Docker remoto, `DISABLE_SSL_VERIFY` em provedores SDK, citações mais seguras em blocos de código e add-on opcional Matrix E2EE.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — Suporte a Zulip e NVIDIA NIM no TutorBot, roteamento mais seguro para modelos de raciocínio, `deeptutor start`, tooltips na barra lateral e paridade do store de sessões.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Implantações multiusuário opcionais com workspaces isolados por usuário, concessões de administrador, rotas de autenticação e acesso ao runtime com escopo.

<details>
<summary><b>Lançamentos anteriores (mais de 2 semanas atrás)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Correções de modelos de raciocínio/provedores, histórico visível do índice de Knowledge e edição de templates / limpeza do Co-Writer mais seguros.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Seleção de modelos baseada em catálogo para chat e TutorBot, reindexação RAG mais segura, correções de limite de tokens em OpenAI Responses e validação do editor de Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Configurações de lançamento local mais fluidas, consultas RAG mais seguras, autenticação de embedding local mais limpa e polimento do modo escuro em Settings.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Persistência de chat em página de livro e fluxos de reconstrução, referências de chat para livro, melhor tratamento de linguagem/raciocínio e endurecimento da extração de documentos RAG.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — Suporte a embeddings NVIDIA NIM + Gemini, contexto Space unificado para histórico de chat / Skills / Memory, snapshots de sessão, resiliência de reindexação RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — URLs transparentes de endpoint de embedding, resiliência de reindexação RAG para vetores persistidos inválidos, limpeza de Memory para saída de modelos de raciocínio, correção de runtime do Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Estabilidade: roteamento RAG mais seguro e validação de embedding, persistência Docker, entrada segura com IME, robustez Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Índices de KB versionados com fluxo de reindexação, workspace de Knowledge reconstruído, auto-descoberta de embedding com novos adaptadores, hub Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Anexos de chat persistentes com gaveta de pré-visualização de arquivos, pipelines de capacidade cientes de anexos, exportação Markdown do TutorBot.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — Anexos de texto/código/SVG, Setup Tour de um comando, exportação Markdown do chat, UI compacta de gestão de KB.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Anexos de documentos (PDF/DOCX/XLSX/PPTX), exibição de bloco de pensamento em raciocínio, editor de templates Soul, salvar-no-notebook a partir do Co-Writer.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — Sistema de Skills criados pelo usuário, revisão de desempenho do input de chat, início automático do TutorBot, UI da Book Library, visualização em tela cheia.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Limites de tokens por etapa, Regenerar resposta em todos os pontos de entrada, correções de compatibilidade RAG e Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Compilador Book Engine de "living books", Co-Writer multidocumento, visualizações HTML interativas, menção @ ao banco de questões.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Aba Channels orientada por schema, consolidação RAG em pipeline único, prompts de chat externalizados.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — "Responder agora" universal, sincronização de rolagem do Co-Writer, painel de Settings unificado, botão Stop em streaming.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Revisão de matemática LaTeX em bloco, sonda de diagnóstico LLM, guia Docker + LLM local.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Sessões marcáveis, tema Snow, heartbeat WebSocket e reconexão automática, revisão do registro de embeddings.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Question Notebook com favoritos e categorias, Mermaid no Visualize, detecção de incompatibilidade de embedding, compatibilidade Qwen/vLLM, suporte LM Studio e llama.cpp, e tema Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Consolidação da busca com fallback SearXNG, correção da troca de provedor e correções de vazamento de recursos no frontend.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Capacidade Visualize (Chart.js/SVG), prevenção de duplicatas em quiz e suporte ao modelo o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Acompanhamento de progresso de embedding com nova tentativa sob limite de taxa, correções de dependência multiplataforma e correção de validação MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — SDK nativo OpenAI/Anthropic (abandono do litellm), suporte ao Math Animator no Windows, parsing JSON robusto e i18n chinês completo.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Recarga a quente de configurações, saída aninhada do MinerU, correção WebSocket e Python 3.11+ como mínimo.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Reescrita de arquitetura nativa de agentes (~200k linhas): modelo de plugins Tools + Capabilities, CLI e SDK, TutorBot, Co-Writer, aprendizado guiado e Memory persistente.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Persistência de sessão, upload incremental de documentos, importação flexível de pipeline RAG e localização completa em chinês.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Suporte a Docling para RAG-Anything, otimização do sistema de logs e correção de bugs.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Configuração de serviço unificada, seleção de pipeline RAG por base de conhecimento, revisão da geração de questões e personalização da barra lateral.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Suporte multi-provedor LLM e embedding, nova página inicial, desacoplamento do módulo RAG e refatoração de variáveis de ambiente.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Arquitetura PromptManager unificada, CI/CD com GitHub Actions e imagens Docker pré-construídas no GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Implantação Docker, atualização para Next.js 16 e React 19, endurecimento de segurança WebSocket e correções críticas de vulnerabilidades.

</details>

### 📰 Notícias

> **[2026.4.19]** 🎉 Atingimos 20 mil estrelas em 111 dias! Obrigado pelo apoio incrível — seguimos comprometidos em iterar continuamente rumo a um ensino verdadeiramente personalizado e inteligente para todos.

> **[2026.4.10]** 📄 Nosso artigo já está no arXiv! Leia o [preprint](https://arxiv.org/abs/2604.26962) para saber mais sobre o desenho e as ideias por trás do DeepTutor.

> **[2026.4.4]** Há quanto tempo! ✨ O DeepTutor v1.0.0 finalmente chegou — uma evolução nativa de agentes com reescrita completa da arquitetura, TutorBot e troca flexível de modos sob a licença Apache-2.0. Um novo capítulo começa e nossa história continua!

> **[2026.2.6]** 🚀 Atingimos 10 mil estrelas em apenas 39 dias! Um enorme obrigado à nossa incrível comunidade pelo apoio!

> **[2026.1.1]** Feliz Ano Novo! Junte-se ao nosso [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) ou [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — vamos moldar juntos o futuro do DeepTutor!

> **[2025.12.29]** O DeepTutor é lançado oficialmente!


<a id="key-features"></a>
## ✨ Principais recursos

**Superfícies de trabalho**

- Chat — Chat, Solve, Quiz, Research e Visualize compartilham uma única sessão, base de conhecimento e histórico de citações, para que você possa escalar no meio da conversa sem perder o contexto.
- Co-Writer — workspace Markdown em visão dividida onde qualquer seleção pode ser reescrita, expandida ou encurtada, opcionalmente ancorada em sua KB ou na web. Os rascunhos vão direto para notebooks.
- Book Engine — um pipeline multiagente compila seus materiais em "living books" interativos com 13 tipos de bloco: quizzes, flash cards, linhas do tempo, grafos de conceitos, um visualizador GeoGebra embutido, animações e mais. As páginas levam impressão digital da KB, então o drift é detectável.

**Sua biblioteca**

- Knowledge Bases — coleções versionadas prontas para RAG, ponta a ponta sobre LlamaIndex. Cada (re)indexação é rastreada, comparável e reversível.
- Space — uma biblioteca pessoal de revisão que reúne histórico de chat, notebooks, banco de questões e Skills criados pelo usuário (`SKILL.md`) que trocam a persona do DeepTutor.
- Memory de três camadas — traces L1 somente-append, fatos L2 curados por superfície com citações, e síntese L3 entre superfícies. Um workbench inspecionável e um Memory Graph deixam você auditar *por que* o DeepTutor sabe o que sabe.

**Extensibilidade e controle**

- Ferramentas componíveis — RAG, busca web, execução de código, raciocínio, brainstorming, busca de papers, análise GeoGebra e auxiliares de chat (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). Servidores MCP plugam ao lado das nativas.
- TutorBots pessoais — tutores autônomos e persistentes, cada um com seu próprio workspace, Soul, Skills e canais (Telegram, Discord, Slack, Matrix, Zulip, …). Construídos sobre [nanobot](https://github.com/HKUDS/nanobot).
- Settings unificado — um workbench único de rascunho / Apply para aparência, modelos, embeddings, busca, capacidades, Memory, servidores MCP e ferramentas, com rastreio compartilhado de custo por chamada.
- CLI nativo para agentes — toda capacidade, KB, sessão e TutorBot está a um comando; saída rica para humanos, JSON estruturado para agentes. Entregue o [`SKILL.md`](../../SKILL.md) a qualquer LLM que use ferramentas e ele poderá operar o DeepTutor sozinho.
- Autenticação opcional — desligada por padrão; opt-in para implantações multiusuário com bcrypt + JWT, painel de admin e um sidecar opcional PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 Começar

O DeepTutor agora tem quatro caminhos paralelos de instalação. Todos usam o mesmo layout de configuração em tempo de execução:

- As configurações ficam em `data/user/settings/` sob o seu workspace atual, ou sob `DEEPTUTOR_HOME` / `deeptutor start --home` quando você escolher um explicitamente.
- `model_catalog.json` guarda perfis de provedor de modelo, URLs base, chaves de API, modelos ativos, configurações de embedding e configurações de busca.
- `system.json` guarda portas de lançamento, base pública da API, CORS, TLS e opções de anexos.
- `auth.json` guarda o toggle de autenticação opcional e o hash da credencial de bootstrap.
- `integrations.json` guarda sidecars opcionais como PocketBase.
- O `.env` na raiz do projeto deixou de ser usado como arquivo de configuração da aplicação.

Para o app local completo, a ordem recomendada é **escolher um workspace → instalar → `deeptutor init` → `deeptutor start`**. `deeptutor start` pode preencher arquivos padrão ausentes como rede de segurança, mas o primeiro setup normal deve passar por `deeptutor init` para que portas e configurações de modelo fiquem explícitas antes do app Web iniciar.

### Opção 1 — Instalar o DeepTutor

Use isto quando quiser o app Web local completo e a CLI sem clonar o repositório.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **Experimentando o v1.4.0 beta?** O PyPI normaliza `1.4.0-beta` para `1.4.0b0`, então `pip install -U deeptutor` continuará no último estável. Adote o pre-release com qualquer um destes:
>
> ```bash
> pip install --pre -U deeptutor      # último pre-release
> pip install -U deeptutor==1.4.0b0   # fixar exatamente em v1.4.0-beta
> ```

`deeptutor init` escreve a configuração em `data/user/settings/` no diretório onde você o executa. Ele pergunta:

- Porta do backend, padrão `8001`
- Porta do frontend, padrão `3782`
- Binding de provedor LLM, URL base, chave de API e nome do modelo
- Provedor de embedding opcional para Knowledge Base / RAG

Após `deeptutor start`, abra a URL do frontend impressa no terminal. Com as portas padrão, essa URL é [http://127.0.0.1:3782](http://127.0.0.1:3782). Se você mudou `frontend_port` durante `deeptutor init` ou editou depois `data/user/settings/system.json`, use a porta configurada.

Mantenha o terminal de `deeptutor start` aberto. Pressione `Ctrl+C` nele para parar backend e frontend.

Notas:

- `deeptutor start` inicia o backend FastAPI e o frontend Next.js empacotado juntos.
- O app Web empacotado não exige `git clone` nem `npm install`, mas ainda precisa de um runtime Node.js 20+ local para executar o servidor standalone Next.js embutido.
- Se você deliberadamente pular `deeptutor init` para um teste rápido, o app inicia com portas padrão seguras e configurações de modelo vazias; configure os modelos depois em **Settings → Models**.

### Opção 2 — Instalar a partir do código-fonte

Use isto quando estiver desenvolvendo o DeepTutor ou quiser rodar diretamente de um checkout.
Use Python 3.11+ e Node.js 22 LTS para a maior similaridade com CI e Docker.

**1. Clone o repositório**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Crie um ambiente Python**

macOS / Linux com `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell com `venv`:

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

**3. Instale o pacote local e as dependências do frontend**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

Se você intencionalmente mudar as dependências do frontend, use `npm install --legacy-peer-deps`
para atualizar `web/package-lock.json`, e então faça commit de `web/package.json` e
`web/package-lock.json` juntos.

**4. Configure e inicie**

```bash
deeptutor init
deeptutor start
```

Instalações a partir do código-fonte usam o diretório local `web/` para o frontend e o iniciam com
o modo dev do Next.js. Mantenha o terminal de `deeptutor start` aberto enquanto usar o app.
São intencionalmente amigáveis ao desenvolvedor e não escrevem configuração em
`.env`; edite `data/user/settings/*.json` ou use a página de Settings na Web.

Se `deeptutor start` reportar um frontend existente que não responde, pare o
PID impresso na mensagem. Se nenhum processo Next.js estiver rodando, remova os
arquivos de lock obsoletos e inicie de novo:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

Extras úteis para desenvolvedores:

```bash
pip install -e ".[dev]"             # ferramentas de testes/lint
pip install -e ".[tutorbot]"        # motor TutorBot + SDKs de canal
pip install -e ".[matrix]"          # canal Matrix sem E2EE/libolm
pip install -e ".[matrix-e2e]"      # Matrix E2EE; requer libolm
pip install -e ".[math-animator]"   # addon Manim; requer LaTeX/ffmpeg/libs do sistema
```

### Opção 3 — Docker

Use isto quando quiser o app Web completo em um único contêiner. As imagens são publicadas no GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — release estável
- `ghcr.io/hkuds/deeptutor:pre` — pre-release, quando disponível

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Em seguida, abra [http://127.0.0.1:3782](http://127.0.0.1:3782). Configuração, chaves de API, logs, arquivos do workspace, Memory e Knowledge Bases ficam armazenados no volume `deeptutor-data` sob `/app/data`.

O contêiner cria `/app/data/user/settings/*.json` automaticamente no primeiro boot. Você pode configurar provedores de modelo diretamente na página de Settings na Web sem preparar arquivos JSON locais manualmente.

Para usar portas de host diferentes, mude o lado esquerdo dos mapeamentos `-p`. Por exemplo, `-p 127.0.0.1:8088:3782` faz a UI Web ficar disponível em `http://127.0.0.1:8088` enquanto o contêiner segue escutando em `3782`. Se você mudar as portas internas do contêiner em `/app/data/user/settings/system.json`, reinicie o contêiner e faça o lado direito de cada mapeamento `-p host:contêiner` casar com a porta configurada.

#### Conectando ao Ollama ou outros serviços do host

Dentro de um contêiner Docker, `localhost` se refere ao próprio contêiner, não à sua máquina host. Se você executa Ollama, LM Studio, llama.cpp, vLLM ou outro serviço de modelo no host, use uma destas abordagens.

Opção A — gateway de host, recomendado para execuções normais de Docker:

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Depois em **DeepTutor Settings → Models**, defina a URL base do provedor como `host.docker.internal`:

- Endpoint LLM Ollama: `http://host.docker.internal:11434/v1`
- Endpoint de embedding Ollama: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

No Docker Desktop para macOS/Windows, `host.docker.internal` normalmente está disponível mesmo sem `--add-host`. No Linux, a flag `--add-host=host.docker.internal:host-gateway` é a forma portável de criar esse hostname em versões modernas do Docker Engine.

Opção B — rede do host, somente Linux:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Não é necessário mapeamento `-p` no modo de rede do host. O contêiner compartilha a rede do host diretamente, então abra [http://127.0.0.1:3782](http://127.0.0.1:3782) por padrão, ou a `frontend_port` configurada em `/app/data/user/settings/system.json`. Nesse modo, serviços do host costumam ser alcançáveis com URLs normais de localhost como `http://127.0.0.1:11434/v1`. A rede do host expõe portas do contêiner diretamente no host e pode entrar em conflito com serviços existentes.

Para rodar em background, adicione `-d` e siga logs pelo nome:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

Para parar uma execução Docker em primeiro plano, pressione `Ctrl+C`. Se você usou o
contêiner em background nomeado acima, execute `docker stop deeptutor`. Antes de iniciar outro contêiner
com o mesmo nome, remova o parado com `docker rm deeptutor`; o
volume `deeptutor-data` mantém suas configurações e workspace.

### Opção 4 — Somente CLI

Use isto quando não precisar da UI Web. O pacote somente-CLI é instalado
a partir de um checkout local em vez do PyPI.

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

`deeptutor init --cli` usa o mesmo layout `data/user/settings/` do app completo, mas muda o comportamento do assistente:

- Pula as perguntas de portas backend/frontend porque o uso somente-CLI não inicia o app Web.
- Ainda escreve os padrões `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml` e `agents.yaml` para que o layout de runtime fique completo.
- Ainda pergunta sobre o provedor LLM ativo e o modelo.
- Pergunta se deve configurar embeddings, mas a resposta padrão é `No`; escolha `Yes` se planeja usar `deeptutor kb ...` ou ferramentas RAG.

Comandos comuns da CLI:

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

A instalação local de `deeptutor-cli` não traz assets Web nem dependências de servidor.
Mantenha o checkout do código-fonte por perto, pois a instalação editável aponta para ele. Se
mais tarde você quiser o app Web, siga a Opção 2 no mesmo checkout, ou desinstale
o pacote CLI local, instale o pacote completo do PyPI com `pip install -U
deeptutor`, execute `deeptutor init` se quiser adicionar portas Web e depois execute
`deeptutor start` a partir do mesmo workspace.

### Referência de configuração

A página de Settings na Web é o editor recomendado, mas os arquivos são JSON/YAML simples e podem ser gerenciados diretamente:

| Arquivo | Finalidade |
|:---|:---|
| `data/user/settings/model_catalog.json` | Perfis de provedor de LLM, embedding e busca; chaves de API; modelos ativos |
| `data/user/settings/system.json` | Portas backend/frontend, base pública da API, CORS, verificação SSL, diretório de anexos |
| `data/user/settings/auth.json` | Toggle de autenticação opcional, nome de usuário, hash de senha, configurações de token/cookie |
| `data/user/settings/integrations.json` | Configurações opcionais de PocketBase e integração sidecar |
| `data/user/settings/interface.json` | Preferências de idioma/tema/barra lateral da UI |
| `data/user/settings/main.yaml` | Padrões de comportamento de runtime e injeção de caminhos |
| `data/user/settings/agents.yaml` | Configurações de temperatura e tokens de capability/tool |

O setup mínimo de modelo pode ser feito no navegador: abra **Settings → Models**, adicione um perfil LLM, defina URL base / chave de API / nome do modelo e salve. Adicione um perfil de embedding apenas se planejar usar recursos de Knowledge Base / RAG.

<a id="explore-deeptutor"></a>
## 📖 Explorar o DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

O refactor v1.4.0-beta reorganiza o DeepTutor em torno de **cinco superfícies centrais** — Chat, Co-Writer, Book, Knowledge, Space — mais uma **Memory de três camadas** que está por baixo de todas elas e um workbench unificado de **Settings** que expõe todos os controles. As Capabilities (Solve / Quiz / Research / Visualize) e as tools (RAG, web, code, reason, brainstorm, paper search, `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) se compõem livremente em cima.

### 💬 Chat — Workspace inteligente unificado

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Um thread, cinco modos, qualquer ferramenta. O seletor de capability fica no composer; a mesma sessão, base de conhecimento, anexos e referências viajam com você entre os modos — passe de uma pergunta casual para resolução multiagente, para um quiz, para um relatório de pesquisa completo, sem perder contexto.

| Modo | O que faz | Construído sobre |
|:---|:---|:---|
| **Chat** | Conversa flexível com qualquer tool; escolha entre RAG, busca web, execução de código, raciocínio profundo, brainstorming, busca de papers, análise GeoGebra. | RAG baseado em LlamaIndex + registro de tools |
| **Solve** | Plano multietapa → investigar → resolver → verificar, com citações de fontes precisas. | Motor agentic (`deep_solve`) |
| **Quiz** | Geração de questões auto-validada ancorada em sua KB; gera um composer de chat de follow-up por questão. | Motor agentic (`deep_question`) |
| **Research** | Decompõe um tópico em subtópicos, despacha agentes paralelos por RAG / web / arXiv e produz um relatório citado com revisões iterativas em modo append. | `pipeline.py` reconstruído (~45% menor, citações + relato iterativo preservados) |
| **Visualize** | Gera diagramas SVG, gráficos Chart.js, grafos Mermaid, páginas HTML interativas, **ou** vídeos / storyboards Manim — o analisador escolhe o `render_type` certo. | Pipeline Visualize (Animator fundido) |

**Novas chat tools** lançadas com o refactor: `ask_user` (faz uma pergunta de esclarecimento estruturada no meio do turno), `web_fetch` (puxa uma URL específica para o contexto), `write_note` / `list_notebook` (salva e lista registros de notebook a partir da superfície de chat) e `github_query` (consultas de issue / PR / repo). As tools permanecem **desacopladas dos workflows** — todo modo permite optar por habilitar ou desabilitar tools por turno.

Uma sessão também carrega um **inventário cumulativo de fontes** entre turnos, então citações de hits RAG / web anteriores permanecem reutilizáveis depois na mesma conversa.

### ✍️ Co-Writer — Workspace multidocumento de escrita com IA

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer é um workbench Markdown em visão dividida (editor raw à esquerda, preview ao vivo à direita) para notas, relatórios, tutoriais e rascunhos assistidos por IA. Cada documento vive em seu próprio workspace com autosave, Markdown baixável e **Save to Notebook** em um clique.

Selecione qualquer texto e escolha **Rewrite**, **Expand** ou **Shorten** — toda ação roda como uma edição de agente rastreada que pode opcionalmente puxar de uma base de conhecimento ou da web. Co-Writer renderiza Markdown / CommonMark / GFM padrão (tabelas, código, matemática, fluxogramas, diagramas de sequência), suporta um escape via tags HTML (`<sub>`, `<sup>`, `<abbr>`, `<mark>`) e traz um template inicial ajustado para docs de produto e notas de aprendizado do DeepTutor.

### 📖 Book Engine — "Living books" interativos

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

Dê um tópico ao DeepTutor, aponte-o para sua base de conhecimento, e ele produz um livro estruturado e interativo — não uma exportação estática, mas um documento vivo que você pode ler, sobre o qual pode se autoquestionar e que pode discutir em contexto.

Por trás dos panos, um pipeline multiagente lida com o trabalho pesado: propor um esboço, recuperar fontes relevantes da sua KB, sintetizar uma árvore de capítulos, planejar cada página e compilar cada bloco. Você fica no controle — revise a proposta, reordene capítulos e converse ao lado de qualquer página.

As páginas são montadas a partir de 13 tipos de bloco — texto, callout, quiz, flash cards, código, figura, deep dive, animação, demo interativa (agora incluindo um **GeoGebra viewer**), linha do tempo, grafo de conceitos, seção e nota do usuário — cada um renderizado com seu próprio componente interativo. As páginas de livro são impressas digitalmente contra sua KB de origem; `deeptutor book health` reporta drift e `deeptutor book refresh-fingerprints` limpa páginas obsoletas quando as fontes mudam.

### 📚 Knowledge Bases — Bibliotecas de documentos prontas para RAG

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

Um workspace dedicado às coleções de documentos que alimentam o RAG. Cada Knowledge Base tem quatro abas:

- **Files** — Navegue pelas fontes carregadas, pré-visualize PDFs inline e veja tamanho / status por arquivo.
- **Add documents** — Solte PDFs, arquivos Office (DOCX / XLSX / PPTX), Markdown, texto puro e uma ampla gama de tipos de arquivos de código / dados. Os documentos são roteados pelo extrator apropriado automaticamente.
- **Index versions** — Cada (re)indexação é uma versão rastreada. Reverta para um índice anterior, compare modelos de embedding ou inspecione estatísticas de chunking sem perder o build anterior.
- **Settings** — Escolha provedor / modelo de embedding, parâmetros de chunking e reranker para a KB. Os defaults são herdados dos seus perfis globais de LLM e embedding.

A indexação é construída ponta a ponta sobre **LlamaIndex** (o split anterior em dual-pipeline foi consolidado no refactor v1.4), com reindexação tolerante a retry, detecção de incompatibilidade de embedding e tratamento resiliente de vetores persistidos corrompidos.

### 🌐 Space — Sua biblioteca pessoal de aprendizado

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space é a contraparte de **leitura / revisão** das superfícies ativas. Onde Chat / Co-Writer / Book é onde você *produz*, Space é onde tudo que você produz vive, pesquisável e replayable.

- **Chat History** — Cada conversa em cada modo, com renomeação de título, exclusão e retomada; exclusão de turnos individuais é suportada em todos os pontos de entrada.
- **Notebooks** — Salve saídas de Chat, Research e Co-Writer em notebooks categorizados e coloridos; cada registro liga de volta à sessão e superfície de origem.
- **Question Bank** — Cada questão de quiz auto-gerada, marcável como favorita e endereçável via @-mention no chat para raciocinar sobre desempenho passado.
- **Skills** — Arquivos `SKILL.md` criados pelo usuário que definem personas de ensino (nome, descrição, gatilhos, corpo). Quando ativo, um Skill é injetado no system prompt do chat — transformando o DeepTutor em um tutor Socrático, um assistente de pesquisa ou qualquer papel que você projetar.

### 🧠 Memory — Arquitetura de três camadas

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

A Memory do DeepTutor agora é um **pipeline de três camadas** com um workbench inspecionável em `/memory`. O modelo v1 de dois arquivos `SUMMARY.md` / `PROFILE.md` foi descontinuado; tudo é migrado para o novo layout no primeiro boot.

| Camada | Função | Armazenamento |
|:---|:---|:---|
| **L1 · Workspace mirror** (LIVE) | Trace somente-append de cada interação, por superfície, por dia. Registro sem perdas do que realmente aconteceu. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Resumos por superfície** (CURATED) | Fatos específicos por superfície extraídos pelo consolidator. Cada fato carrega citações em rodapé de volta para os traces L1. Suporta execuções por documento de **Update / Audit / Dedup**. | `L2/<surface>.md` |
| **L3 · Conhecimento entre superfícies** (SYNTHESIS) | Síntese entre superfícies: seu `profile`, linha do tempo `recent`, `scope` de conhecimento e `preferences`. Afirmações hedged, cada uma sustentada por evidência L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

Sete superfícies alimentam o pipeline: **chat, notebook, quiz, kb, book, tutorbot, cowriter**. O consolidator é orientado por LLM e roda de forma assíncrona (`POST /memory/runs/start`) — você pode dispará-lo a partir do workbench, observar L1 → L2 → L3 se propagar e editar qualquer camada manualmente.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

O **Memory Graph** (`/memory/graph`) renderiza as três camadas ao mesmo tempo: a síntese L3 no centro, os fatos L2 no anel do meio, os traces L1 do lado de fora, agrupados por superfície. Passe o cursor sobre qualquer nó para um preview inline; clique para travar o destaque e rastrear as referências L3 → L2 → L1 para dentro, para que você possa auditar *por que* o DeepTutor "sabe" algo sobre você.

### ⚙️ Settings — Centro de controle unificado

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

A superfície de Settings foi unificada na v1.4 e dividida por preocupação, com um modelo de rascunho / **Apply** para que mudanças sejam atômicas e possam ser revertidas antes de salvar:

- **Appearance** — Idioma e tema da UI (Cream, Snow, Dark, Glass).
- **Status** — Sonda de saúde ao vivo entre os backends de LLM, embedding, busca e armazenamento.
- **LLM**, **Embedding**, **Search** — Catálogo de provedores, URLs base, chaves de API e seleção do modelo ativo. Os modelos ativos são escolhidos a partir do catálogo, então toda superfície fica em sincronia.
- **Capabilities** — Ajustes por capability (chunking, orçamento de LLM, políticas de dedup e referência, máximo de iterações) para Chat, Solve, Quiz, Research, Visualize e Co-Writer. Suportado por um envelope unificado `emit_capability_result` e um `UsageTracker` compartilhado que expõe custo por chamada.
- **Memory** — Alterne execuções do consolidator, configure cadência e orçamento e salte para o workbench de Memory.
- **MCP servers** — Registre servidores externos Model Context Protocol; suas tools são expostas ao lado das tools nativas.
- **Tools** — Inspecione cada tool nativa, seus parâmetros, status (habilitada / em breve) e copy de status i18n.

Um launcher "Tour" guia novos usuários pela página, e toda capability traz um canônico `capabilities/prompts/{en,zh}/<name>.yaml` para que as mensagens de status fiquem consistentes em inglês e em 中文.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — Tutores de IA persistentes e autônomos

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot não é um chatbot — é um **agente persistente e multi-instância** construído sobre [nanobot](https://github.com/HKUDS/nanobot). Cada TutorBot roda seu próprio agent loop com workspace, memória e personalidade independentes. Crie um tutor de matemática Socrático, um paciente coach de escrita e um assessor de pesquisa rigoroso — todos rodando simultaneamente, cada um evoluindo com você.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Soul Templates** — Defina a personalidade, o tom e a filosofia pedagógica do seu tutor por meio de arquivos Soul editáveis. Escolha entre arquétipos nativos (Socrático, encorajador, rigoroso) ou crie o seu — o Soul molda cada resposta.
- **Workspace independente** — Cada bot tem seu próprio diretório com memória, sessões, Skills e configuração separadas — totalmente isolados, ainda assim capazes de acessar a camada compartilhada de conhecimento do DeepTutor.
- **Heartbeat proativo** — Bots não apenas respondem — eles iniciam. O sistema Heartbeat nativo viabiliza check-ins recorrentes de estudo, lembretes de revisão e tarefas agendadas. Seu tutor aparece mesmo quando você não.
- **Acesso completo a tools** — Todo bot alcança o toolkit completo do DeepTutor: recuperação RAG, execução de código, busca web, busca acadêmica de papers, raciocínio profundo e brainstorming.
- **Aprendizado de Skills** — Ensine ao seu bot novas habilidades adicionando arquivos de skill ao seu workspace. À medida que suas necessidades evoluem, evolui também a capacidade do seu tutor.
- **Presença multicanal** — Conecte bots a Telegram, Discord, Slack, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, e-mail e mais. Seu tutor te encontra onde você está.
- **Equipe e sub-agentes** — Lance sub-agentes em background ou orquestre equipes multiagente dentro de um único bot para tarefas complexas e de longa duração.

```bash
deeptutor bot create math-tutor --persona "Socratic math teacher who uses probing questions"
deeptutor bot create writing-coach --persona "Patient, detail-oriented writing mentor"
deeptutor bot list                  # Veja todos os seus tutores ativos
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — Interface nativa para agentes

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

O DeepTutor é totalmente nativo de CLI. Toda capability, base de conhecimento, sessão, Memory e TutorBot está a um comando — sem navegador necessário. A CLI atende tanto humanos (com renderização rica no terminal) quanto agentes de IA (com saída JSON estruturada).

Entregue o [`SKILL.md`](../../SKILL.md) na raiz do projeto a qualquer agente que use tools ([nanobot](https://github.com/HKUDS/nanobot) ou qualquer LLM com acesso a tools), e ele pode configurar e operar o DeepTutor autonomamente.

**Execução one-shot** — Rode qualquer capability direto do terminal:

```bash
deeptutor run chat "Explain the Fourier transform" -t rag --kb textbook
deeptutor run deep_solve "Prove that √2 is irrational" -t reason
deeptutor run deep_question "Linear algebra" --config num_questions=5
deeptutor run deep_research "Attention mechanisms in transformers"
deeptutor run visualize "Draw the architecture of a transformer"
```

**REPL interativo** — Uma sessão de chat persistente com troca de modo ao vivo:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Dentro do REPL: /cap, /tool, /kb, /history, /notebook, /config para alternar em tempo real
```

**Ciclo de vida de Knowledge Base** — Construa, consulte e gerencie coleções prontas para RAG inteiramente do terminal:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # Criar a partir de documento
deeptutor kb add my-kb --docs-dir ./papers/         # Adicionar uma pasta de papers
deeptutor kb search my-kb "gradient descent"        # Buscar diretamente
deeptutor kb set-default my-kb                      # Definir como padrão para todos os comandos
```

**Modo de saída dual** — Renderização rica para humanos, JSON estruturado para pipelines:

```bash
deeptutor run chat "Summarize chapter 3" -f rich    # Saída colorida e formatada
deeptutor run chat "Summarize chapter 3" -f json    # Eventos JSON delimitados por linha
```

**Continuidade de sessão** — Retome qualquer conversa exatamente de onde parou:

```bash
deeptutor session list                              # Lista todas as sessões
deeptutor session open <id>                         # Retomar no REPL
```

<details>
<summary><b>Referência completa de comandos da CLI</b></summary>

**Nível superior**

| Command | Description |
|:---|:---|
| `deeptutor run <capability> <message>` | Executa qualquer capability em um único turno (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | REPL interativo com `--capability`, `--tool`, `--kb`, `--language` opcionais |
| `deeptutor serve` | Inicia o servidor API do DeepTutor |

**`deeptutor bot`**

| Command | Description |
|:---|:---|
| `deeptutor bot list` | Lista todas as instâncias TutorBot |
| `deeptutor bot create <id>` | Cria e inicia um novo bot (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Inicia um bot |
| `deeptutor bot stop <id>` | Para um bot |

**`deeptutor kb`**

| Command | Description |
|:---|:---|
| `deeptutor kb list` | Lista todas as Knowledge Bases |
| `deeptutor kb info <name>` | Mostra detalhes da Knowledge Base |
| `deeptutor kb create <name>` | Cria a partir de documentos (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Adiciona documentos incrementalmente |
| `deeptutor kb search <name> <query>` | Busca em uma Knowledge Base |
| `deeptutor kb set-default <name>` | Define como KB padrão |
| `deeptutor kb delete <name>` | Exclui uma Knowledge Base (`--force`) |

**`deeptutor memory`**

| Command | Description |
|:---|:---|
| `deeptutor memory show [file]` | Visualiza Memory (`summary`, `profile` ou `all`) |
| `deeptutor memory clear [file]` | Limpa Memory (`--force`) |

**`deeptutor session`**

| Command | Description |
|:---|:---|
| `deeptutor session list` | Lista sessões (`--limit`) |
| `deeptutor session show <id>` | Visualiza mensagens da sessão |
| `deeptutor session open <id>` | Retoma sessão no REPL |
| `deeptutor session rename <id>` | Renomeia uma sessão (`--title`) |
| `deeptutor session delete <id>` | Exclui uma sessão |

**`deeptutor notebook`**

| Command | Description |
|:---|:---|
| `deeptutor notebook list` | Lista notebooks |
| `deeptutor notebook create <name>` | Cria um notebook (`--description`) |
| `deeptutor notebook show <id>` | Visualiza registros do notebook |
| `deeptutor notebook add-md <id> <path>` | Importa markdown como registro |
| `deeptutor notebook replace-md <id> <rec> <path>` | Substitui um registro markdown |
| `deeptutor notebook remove-record <id> <rec>` | Remove um registro |

**`deeptutor book`**

| Command | Description |
|:---|:---|
| `deeptutor book list` | Lista todos os livros no workspace |
| `deeptutor book health <book_id>` | Verifica drift da KB e saúde do livro |
| `deeptutor book refresh-fingerprints <book_id>` | Atualiza fingerprints da KB e limpa páginas obsoletas |

**`deeptutor config` / `plugin` / `provider`**

| Command | Description |
|:---|:---|
| `deeptutor config show` | Imprime resumo da configuração atual |
| `deeptutor plugin list` | Lista tools e capabilities registradas |
| `deeptutor plugin info <name>` | Mostra detalhes de tool ou capability |
| `deeptutor provider login <provider>` | Auth de provedor (login OAuth `openai-codex`; `github-copilot` valida uma sessão Copilot existente) |

</details>

---

<a id="multi-user"></a>
### 👥 Multi-usuário — Implantações compartilhadas com workspaces por usuário

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Ative a autenticação e o DeepTutor se transforma em uma implantação multi-tenant com **workspaces isolados por usuário** e **recursos curados pelo admin**. A primeira pessoa a se registrar torna-se admin e configura modelos, chaves de API e Knowledge Bases em nome de todos. As contas seguintes são criadas pelo admin (somente por convite), cada uma com seu próprio histórico de chat / Memory / notebooks / Knowledge Bases com escopo, e só veem os LLMs, KBs e Skills que o admin atribuiu a elas.

**Início rápido (5 passos):**

```bash
# 1. Habilite a auth em data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Reinicie o stack web.
deeptutor start

# 3. Abra http://localhost:3782/register e crie a primeira conta.
#    O primeiro registro é o único público; esse usuário torna-se admin
#    e o endpoint /register é fechado automaticamente depois.

# 4. Como admin, navegue até /admin/users → "Add user" para provisionar colegas.

# 5. Para cada usuário, clique no ícone slider → atribua perfis LLM, Knowledge
#    Bases e Skills. Salve. O usuário agora pode entrar e começar a trabalhar.
```

**O que o admin vê:**

- **Página Settings completa** em `/settings` — gerencie provedores LLM / embedding / busca, chaves de API, catálogos de modelo e "Apply" em runtime.
- **Gerenciamento de usuários** em `/admin/users` — criar, promover, rebaixar e excluir contas. O endpoint público `/register` é fechado automaticamente quando o primeiro admin existe; outras contas passam por `POST /api/v1/auth/users` (somente-admin).
- **Editor de concessões** — para cada usuário não-admin, escolha os perfis de modelo, Knowledge Bases e Skills que ele pode usar. As concessões carregam **apenas IDs lógicos**; chaves de API nunca cruzam a fronteira da concessão.
- **Trilha de auditoria** — toda mudança de concessão e acesso a recurso atribuído é registrada em `multi-user/_system/audit/usage.jsonl`.

**O que os usuários comuns recebem:**

- **Workspace isolado** sob `multi-user/<uid>/` — seu próprio histórico de chat (`chat_history.db`), Memory (`SUMMARY.md` / `PROFILE.md`), notebooks e Knowledge Bases pessoais. Nada é compartilhado por padrão.
- **Acesso somente-leitura** a Knowledge Bases e Skills atribuídos pelo admin, exibidos inline ao lado de seus próprios recursos com um badge "Assigned by admin".
- **Página Settings redigida** — apenas tema, idioma e um resumo dos modelos concedidos. Chaves de API, URLs base e endpoints de provedor nunca são retornados para requisições não-admin.
- **LLM com escopo** — turnos de chat são roteados pelo modelo atribuído pelo admin. Se nenhum LLM foi concedido, o turno é rejeitado de antemão (sem fallback silencioso para as chaves do admin).

**Layout do workspace:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Hashed credentials, roles
│   ├── auth/auth_secret         # JWT signing secret (auto-generated)
│   ├── grants/<uid>.json        # Per-user resource grants (admin-managed)
│   └── audit/usage.jsonl        # Audit trail
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Referência de configuração:**

| Configuração | Obrigatório | Descrição |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Sim | Defina como `true` para habilitar auth multiusuário. Padrão `false` (modo single-user — caminhos de admin em todo lugar). |
| `multi-user/_system/auth/auth_secret` | Recomendado | Segredo de assinatura JWT. Gerado automaticamente no primeiro boot autenticado se ausente. |
| `data/user/settings/auth.json: token_expire_hours` | Não | Lifetime do JWT; padrão `24`. |
| `data/user/settings/auth.json: username/password_hash` | Não | Credencial opcional headless de bootstrap single-user. Deixe em branco ao usar registro pelo navegador. |
| `data/user/settings/system.json` | Não | `deeptutor start` deriva flags de auth do frontend e base da API a partir das configurações de runtime. |

> ⚠️ **Modo PocketBase (`integrations.pocketbase_url` definido) é somente single-user.** O schema padrão do PocketBase não tem campo `role` em `users` (todo login resolve para `role=user`, nenhum admin pode ser criado), e as queries de `sessions` / `messages` / `turns` não são filtradas por `user_id`. Implantações multiusuário devem manter `integrations.pocketbase_url` em branco e usar o backend padrão JSON/SQLite.

> ⚠️ **Recomendação de processo único.** A promoção primeiro-usuário-vira-admin é protegida por um `threading.Lock` em processo. Implantações multi-worker devem provisionar o primeiro admin offline (comece com `auth.json.enabled=false`, registre o admin pelo fluxo de bootstrap, depois defina `auth.json.enabled=true`) ou apoiar o user store em um sistema externo.

<a id="community"></a>
## 🌐 Comunidade e ecossistema

O DeepTutor se apoia nos ombros de projetos open-source excelentes:

| Projeto | Papel no DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Motor de agentes ultraleve que alimenta o TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Pipeline RAG e espinha dorsal de indexação de documentos |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | Geração de animações matemáticas guiada por IA para o Math Animator |

**Do ecossistema HKUDS:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| RAG simples e rápido | Framework de agentes sem código | Pesquisa automatizada | Agente de IA ultraleve |


## 🤝 Contribuir

<div align="center">

Esperamos que o DeepTutor seja um presente para a comunidade. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

Veja [CONTRIBUTING.md](../../CONTRIBUTING.md) para diretrizes sobre como configurar seu ambiente de desenvolvimento, padrões de código e fluxo de pull request.

## ⭐ Histórico de estrelas

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

[⭐ Marque uma estrela](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Reporte um bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussões](https://github.com/HKUDS/DeepTutor/discussions)

---

Licenciado sob a [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
