<div align="center">

<img src="../../assets/logo-ver2.png" alt="DeepTutor Logo" width="150" style="border-radius: 15px;">

# DeepTutor: Seu Assistente Pessoal de Aprendizado

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](../../LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join-7289DA?style=flat&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-blue?style=flat)](../../Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-green?style=flat&logo=wechat)](https://github.com/HKUDS/DeepTutor/issues/78)



[**Início Rápido**](#início-rápido) · [**Módulos Principais**](#módulos-principais) · [**Perguntas Frequentes**](#perguntas-frequentes)

[🇬🇧 English](../../README.md) · [🇨🇳 中文](README_CN.md) · [🇯🇵 日本語](README_JA.md) · [🇪🇸 Español](README_ES.md) · [🇫🇷 Français](README_FR.md) · [🇸🇦 العربية](README_AR.md) · [🇷🇺 Русский](README_RU.md) · [🇮🇳 हिन्दी](README_HI.md) · [🇵🇹 Português](README_PT.md)

</div>

<div align="center">

| ⚡ **Q&A de Conhecimento de Documentos Massivos**  |  📈 **Visualização de Aprendizado Interativo**  | <br>
| 🧠 **Reforço de Conhecimento**  |  🔬 **Pesquisa Profunda e Geração de Ideias** |

</div>

---
> **[2026.1.1]** Feliz Ano Novo! Junte-se à nossa [Comunidade no Discord](https://discord.gg/zpP9cssj), à [Comunidade no WeChat](https://github.com/HKUDS/DeepTutor/issues/78), ou ao [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — molde o futuro do DeepTutor! 💬

> **[2025.12.30]** Visite nosso [Site Oficial](https://hkuds.github.io/DeepTutor/) para mais detalhes!

> **[2025.12.29]** DeepTutor já está disponível! ✨
---

## Características Principais do DeepTutor

### 📚 Q&A de Conhecimento de Documentos Massivos
• **Base de Conhecimento Inteligente**: Faça upload de livros didáticos, artigos de pesquisa, manuais técnicos e documentos específicos do domínio. Construa um repositório de conhecimento abrangente alimentado por IA para acesso instantâneo.<br>
• **Resolução de Problemas Multi-Agente**: Arquitetura de raciocínio de duplo loop com RAG, busca na web, busca de artigos e execução de código—fornecendo soluções passo a passo com citações precisas.

### 🎨 Visualização de Aprendizado Interativo
• **Simplificação e Explicações do Conhecimento**: Transforme conceitos complexos, conhecimento e algoritmos em auxílios visuais fáceis de entender, decomposições detalhadas passo a passo e demonstrações interativas envolventes.<br>
• **Q&A Personalizado**: Conversas conscientes do contexto que se adaptam ao seu progresso de aprendizado, com páginas interativas e rastreamento de conhecimento baseado em sessões.

### 🎯 Reforço de Conhecimento com Gerador de Problemas de Prática
• **Criação de Exercícios Inteligentes**: Gere questionários direcionados, problemas de prática e avaliações personalizadas adaptadas ao seu nível atual de conhecimento e objetivos de aprendizado específicos.<br>
• **Simulação de Exame Autêntica**: Faça upload de exames de referência para gerar questões de prática que correspondem perfeitamente ao estilo, formato e dificuldade originais—fornecendo preparação realista para o teste real.

### 🔍 Pesquisa Profunda e Geração de Ideias
• **Pesquisa Abrangente e Revisão de Literatura**: Realize exploração profunda de tópicos com análise sistemática. Identifique padrões, conecte conceitos relacionados entre disciplinas e sintetize descobertas de pesquisa existentes.<br>
• **Descoberta de Insights Inovadores**: Gere materiais de aprendizado estruturados e descubra lacunas de conhecimento. Identifique novas direções de pesquisa promissoras através de síntese inteligente de conhecimento entre domínios.

---

<div align="center">
  <img src="../../assets/figs/title_gradient.svg" alt="All-in-One Tutoring System" width="70%">
</div>

<br>

<!-- ━━━━━━━━━━━━━━━━ Core Learning Experience ━━━━━━━━━━━━━━━━ -->

<table>
<tr>
<td width="50%" align="center" valign="top">

<h3>📚 Q&A de Conhecimento de Documentos Massivos</h3>
<a href="#problem-solving-agent">
<img src="../../assets/gifs/solve.gif" width="100%">
</a>
<br>
<sub>Resolução de Problemas Multi-Agente com Citações Exatas</sub>

</td>
<td width="50%" align="center" valign="top">

<h3>🎨 Visualização de Aprendizado Interativo</h3>
<a href="#guided-learning">
<img src="../../assets/gifs/guided-learning.gif" width="100%">
</a>
<br>
<sub>Explicações Visuais Passo a Passo com Q&A Personalizado</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Practice & Reinforcement ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🎯 Reforço de Conhecimento</h3>

<table>
<tr>
<td width="50%" valign="top" align="center">

<a href="#question-generator">
<img src="../../assets/gifs/question-1.gif" width="100%">
</a>

**Questões Personalizadas**  
<sub>Geração de Questões de Prática Auto-Validadas</sub>

</td>
<td width="50%" valign="top" align="center">

<a href="#question-generator">
<img src="../../assets/gifs/question-2.gif" width="100%">
</a>

**Questões de Imitação**  
<sub>Clonar Estilo de Exame para Prática Autêntica</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Research & Creation ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🔍 Pesquisa Profunda e Geração de Ideias</h3>

<table>
<tr>
<td width="33%" align="center">

<a href="#deep-research">
<img src="../../assets/gifs/deepresearch.gif" width="100%">
</a>

**Pesquisa Profunda**  
<sub>Extensão do Conhecimento do Livro Didático com RAG, Web e Busca de Artigos</sub>

</td>
<td width="33%" align="center">

<a href="#idea-generation">
<img src="../../assets/gifs/ideagen.gif" width="100%">
</a>

**IdeaGen Automatizado**  
<sub>Brainstorming Sistemático e Síntese de Conceitos com Fluxo de Trabalho de Duplo Filtro</sub>

</td>
<td width="33%" align="center">

<a href="#co-writer">
<img src="../../assets/gifs/co-writer.gif" width="100%">
</a>

**IdeaGen Interativo**  
<sub>Co-Writer Alimentado por RAG e Busca Web com Geração de Podcasts</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Knowledge Infrastructure ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🏗️ Sistema de Conhecimento Tudo-em-Um</h3>

<table>
<tr>
<td width="50%" align="center">

<a href="#dashboard--knowledge-base-management">
<img src="../../assets/gifs/knowledge_bases.png" width="100%">
</a>

**Base de Conhecimento Pessoal**  
<sub>Construa e Organize Seu Próprio Repositório de Conhecimento</sub>

</td>
<td width="50%" align="center">

<a href="#notebook">
<img src="../../assets/gifs/notebooks.png" width="100%">
</a>

**Caderno Pessoal**  
<sub>Sua Memória Contextual para Sessões de Aprendizado</sub>

</td>
</tr>
</table>

<p align="center">
  <sub>🌙 Use DeepTutor no <b>Modo Escuro</b>!</sub>
</p>

<details>
<summary><b>Arquitetura do Sistema</b></summary>
<br>

![DeepTutor Full-Stack Workflow](../../assets/figs/full-pipe.png)

</details>

## 📋 Tarefas Pendentes

> Siga-nos para nossas futuras atualizações!
- [ ] Suporte para serviços LLM locais (ex. ollama)
- [ ] Refatoração do módulo RAG (ver [Discussions](https://github.com/HKUDS/DeepTutor/discussions))
- [ ] Codificação profunda a partir da geração de ideias
- [ ] Interação personalizada com o caderno

## 🚀 Início Rápido

### Passo 1: Pré-configuração

**① Clonar Repositório**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**② Configurar Variáveis de Ambiente**

```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

<details>
<summary>📋 <b>Referência de Variáveis de Ambiente</b></summary>

| Variável | Obrigatório | Descrição |
|:---|:---:|:---|
| `LLM_MODEL` | **Sim** | Nome do modelo (ex: `gpt-4o`) |
| `LLM_API_VERSION` | Não | Versão da API para Azure OpenAI (ex: `2024-02-15-preview`) |
| `LLM_API_KEY` | **Sim** | Sua chave API LLM |
| `LLM_HOST` | **Sim** | URL do endpoint da API |
| `EMBEDDING_MODEL` | **Sim** | Nome do modelo de incorporação |
| `EMBEDDING_API_VERSION` | Não | Versão da API para Azure OpenAI Embeddings |
| `EMBEDDING_API_KEY` | **Sim** | Chave API de incorporação |
| `EMBEDDING_HOST` | **Sim** | Endpoint da API de incorporação |
| `BACKEND_PORT` | Não | Porta do backend (padrão: `8001`) |
| `FRONTEND_PORT` | Não | Porta do frontend (padrão: `3782`) |
| `NEXT_PUBLIC_API_BASE` | Não | **URL da API do frontend** (defina para acesso remoto/LAN, ex: `http://192.168.1.100:8001`) |
| `TTS_*` | Não | Configurações de texto para voz |
| `SEARCH_PROVIDER` | Não | Provedor de busca (opções: `perplexity`, `tavily`, `serper`, `jina`, `exa`, `baidu`, padrão: `perplexity`) |
| `SEARCH_API_KEY` | Não | Chave API unificada para busca |

> 💡 **Acesso remoto**: se estiver acessando de outro dispositivo (ex.: `192.168.31.66:3782`), adicione ao `.env`:
> ```bash
> NEXT_PUBLIC_API_BASE=http://192.168.31.66:8001
> ```

</details>

**③ Configurar Portas e LLM** *(Opcional)*

- **Portas**: Configure no `.env` → `BACKEND_PORT` / `FRONTEND_PORT` (padrão: 8001/3782)
- **LLM**: Edite `config/agents.yaml` → `temperature` / `max_tokens` por módulo
- Consulte [Documentação de Configuração](../../config/README.md) para detalhes

**④ Experimentar Bases de Conhecimento Demo** *(Opcional)*

<details>
<summary>📚 <b>Demos Disponíveis</b></summary>

- **Artigos de Pesquisa** — 5 artigos do nosso laboratório ([AI-Researcher](https://github.com/HKUDS/AI-Researcher), [LightRAG](https://github.com/HKUDS/LightRAG), etc.)
- **Livro Didático de Ciência de Dados** — 8 capítulos, 296 páginas ([Link do Livro](https://ma-lab-berkeley.github.io/deep-representation-learning-book/))

</details>

1. Baixar de [Google Drive](https://drive.google.com/drive/folders/1iWwfZXiTuQKQqUYb5fGDZjLCeTUP6DA6?usp=sharing)
2. Extrair para o diretório `data/`

> Os KBs demo usam `text-embedding-3-large` com `dimensions = 3072`

**⑤ Criar Sua Própria Base de Conhecimento** *(Após o Início)*

1. Ir para http://localhost:3782/knowledge
2. Clicar em "New Knowledge Base" → Inserir nome → Fazer upload de arquivos PDF/TXT/MD
3. Monitorar o progresso no terminal

---

### Passo 2: Escolha seu Método de Instalação

<table>
<tr>
<td width="50%" valign="top">

<h3 align="center">🐳 Implantação Docker</h3>
<p align="center"><b>Recomendado</b> — Sem configuração Python/Node.js</p>

---

**Pré-requisitos**: [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)

<details open>
<summary><b>🚀 Opção A: Imagem Pré-construída (Mais Rápido)</b></summary>

```bash
# Funciona em todas as plataformas — Docker detecta sua arquitetura automaticamente
docker run -d --name deeptutor \
  -p 8001:8001 -p 3782:3782 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config:ro \
  ghcr.io/hkuds/deeptutor:latest

# Windows PowerShell: use ${PWD} em vez de $(pwd)
```

Ou usar arquivo `.env`:

```bash
docker run -d --name deeptutor \
  -p 8001:8001 -p 3782:3782 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config:ro \
  ghcr.io/hkuds/deeptutor:latest
```

</details>

<details>
<summary><b>🔨 Opção B: Construir do Código Fonte</b></summary>

```bash
# Construir e iniciar (~5-10 min primeira execução)
docker compose up --build -d

# Ver logs
docker compose logs -f
```

</details>

**Comandos**:

```bash
docker compose up -d      # Iniciar
docker compose logs -f    # Logs
docker compose down       # Parar
docker compose up --build # Reconstruir
docker pull ghcr.io/hkuds/deeptutor:latest  # Atualizar imagem
```

> **Modo Dev**: Adicionar `-f docker-compose.dev.yml`

</td>
<td width="50%" valign="top">

<h3 align="center">💻 Instalação Manual</h3>
<p align="center">Para desenvolvimento ou ambientes não Docker</p>

---

**Pré-requisitos**: Python 3.10+, Node.js 18+

**Configurar Ambiente**:

```bash
# Usando conda (Recomendado)
conda create -n deeptutor python=3.10
conda activate deeptutor

# Ou usando venv
python -m venv venv
source venv/bin/activate
```

**Instalar Dependências**:

```bash
# Instalação com um clique (Recomendado)
python scripts/install_all.py
# Ou: bash scripts/install_all.sh

# Ou instalação manual
pip install -r requirements.txt
npm install --prefix web
```

**Iniciar**:

```bash
# Iniciar interface web
python scripts/start_web.py

# Ou apenas CLI
python scripts/start.py

# Parar: Ctrl+C
```

</td>
</tr>
</table>

### URLs de Acesso

| Serviço | URL | Descrição |
|:---:|:---|:---|
| **Frontend** | http://localhost:3782 | Interface web principal |
| **Documentação API** | http://localhost:8001/docs | Documentação de API interativa |

---

## 📂 Armazenamento de Dados

Todo o conteúdo gerado pelo usuário e os dados do sistema são armazenados na pasta `data/`:

```
data/
├── knowledge_bases/              # Armazenamento da base de conhecimento
└── user/                         # Dados de atividade do usuário
    ├── solve/                    # Resultados de resolução de problemas e artefatos
    ├── question/                 # Questões geradas
    ├── research/                 # Relatórios de pesquisa e cache
    ├── co-writer/                # Documentos Co-Writer e arquivos de áudio
    ├── notebook/                 # Registros de caderno e metadados
    ├── guide/                    # Sessões de aprendizado guiado
    ├── logs/                     # Logs do sistema
    └── run_code_workspace/       # Espaço de trabalho de execução de código
```

Todos os resultados são automaticamente salvos quando você realiza qualquer atividade. As pastas são criadas automaticamente se não existirem.

---

## 📖 Documentação dos Módulos

<table>
<tr>
<td align="center"><a href="../../config/README.md">Configuração</a></td>
<td align="center"><a href="../../data/README.md">Repositório de Dados</a></td>
<td align="center"><a href="../../deeptutor/api/README.md">Backend API</a></td>
<td align="center"><a href="../../deeptutor/core/README.md">Utilitários Principais</a></td>
</tr>
<tr>
<td align="center"><a href="../../deeptutor/knowledge/README.md">Base de Conhecimento</a></td>
<td align="center"><a href="../../deeptutor/tools/README.md">Ferramentas</a></td>
<td align="center"><a href="../../web/README.md">Frontend Web</a></td>
<td align="center"><a href="../../deeptutor/agents/solve/README.md">Módulo de Resolução</a></td>
</tr>
<tr>
<td align="center"><a href="../../deeptutor/agents/question/README.md">Módulo de Questões</a></td>
<td align="center"><a href="../../deeptutor/agents/research/README.md">Módulo de Pesquisa</a></td>
<td align="center"><a href="../../deeptutor/agents/co_writer/README.md">Módulo Co-Writer</a></td>
<td align="center"><a href="../../deeptutor/agents/guide/README.md">Módulo de Guia</a></td>
</tr>
<tr>
<td align="center" colspan="4"><a href="../../deeptutor/agents/ideagen/README.md">Módulo de Geração de Ideias</a></td>
</tr>
</table>

---

## ❓ Perguntas Frequentes

<details>
<summary><b>O backend não inicia?</b></summary>

**Lista de Verificação**
- Confirme que a versão Python >= 3.10
- Confirme que todas as dependências estão instaladas: `pip install -r requirements.txt`
- Verifique se a porta 8001 está em uso
- Verifique a configuração do arquivo `.env`

**Soluções**
- **Mudar porta**: Defina `BACKEND_PORT=9001` no arquivo `.env`
- **Verificar logs**: Revise as mensagens de erro do terminal

</details>

<details>
<summary><b>Porta ocupada após Ctrl+C?</b></summary>

**Problema**

Após pressionar Ctrl+C durante uma tarefa em execução (por exemplo, pesquisa profunda), reiniciar mostra erro "porta já em uso".

**Causa**

Ctrl+C às vezes termina apenas o processo frontend enquanto o backend continua executando em segundo plano.

**Solução**

```bash
# macOS/Linux: Encontrar e matar o processo
lsof -i :8001
kill -9 <PID>

# Windows: Encontrar e matar o processo
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

Depois reinicie o serviço com `python scripts/start_web.py`.

</details>

<details>
<summary><b>Erro "npm: command not found"?</b></summary>

**Problema**

Executar `scripts/start_web.py` mostra `npm: command not found` ou código de saída 127.

**Lista de Verificação**
- Verifique se npm está instalado: `npm --version`
- Verifique se Node.js está instalado: `node --version`
- Confirme que o ambiente conda está ativado (se estiver usando conda)

**Soluções**
```bash
# Opção A: Usar Conda (Recomendado)
conda install -c conda-forge nodejs

# Opção B: Usar instalador oficial
# Baixar de https://nodejs.org/

# Opção C: Usar nvm
nvm install 18
nvm use 18
```

**Verificar Instalação**
```bash
node --version  # Deve mostrar v18.x.x ou superior
npm --version   # Deve mostrar o número da versão
```

</details>

<details>
<summary><b>O frontend não consegue conectar ao backend?</b></summary>

**Lista de Verificação**
- Confirme que o backend está em execução (visite http://localhost:8001/docs)
- Verifique o console do navegador para mensagens de erro

**Solução**

Crie `.env.local` no diretório `web`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

</details>

<details>
<summary><b>Falha na conexão WebSocket?</b></summary>

**Lista de Verificação**
- Confirme que o backend está em execução
- Verifique as configurações do firewall
- Confirme que a URL WebSocket está correta

**Solução**
- **Verifique os logs do backend**
- **Confirme o formato da URL**: `ws://localhost:8001/api/v1/...`

</details>

<details>
<summary><b>Onde as saídas do módulo são armazenadas?</b></summary>

| Módulo | Caminho de Saída |
|:---:|:---|
| Resolver | `data/user/solve/solve_YYYYMMDD_HHMMSS/` |
| Questão | `data/user/question/question_YYYYMMDD_HHMMSS/` |
| Pesquisa | `data/user/research/reports/` |
| Co-Writer | `data/user/co-writer/` |
| Caderno | `data/user/notebook/` |
| Guia | `data/user/guide/session_{session_id}.json` |
| Logs | `data/user/logs/` |

</details>

<details>
<summary><b>Como adicionar uma nova base de conhecimento?</b></summary>

**Interface Web**
1. Visite http://localhost:{frontend_port}/knowledge
2. Clique em "New Knowledge Base"
3. Digite o nome da base de conhecimento
4. Faça upload de documentos PDF/TXT/MD
5. O sistema processará os documentos em segundo plano

**CLI**
```bash
deeptutor kb create <kb_name> --doc <pdf_path>
```

</details>

<details>
<summary><b>Como adicionar documentos incrementalmente a uma BC existente?</b></summary>

**CLI (Recomendado)**
```bash
python -m deeptutor.knowledge.add_documents <kb_name> --docs <new_document.pdf>
```

**Benefícios**
- Processa apenas novos documentos, economiza tempo e custo da API
- Fusão automática com o grafo de conhecimento existente
- Preserva todos os dados existentes

</details>

<details>
<summary><b>Erro uvloop.Loop ao extrair elementos numerados?</b></summary>

**Problema**

Ao inicializar uma base de conhecimento, você pode encontrar este erro:
```
ValueError: Can't patch loop of type <class 'uvloop.Loop'>
```

Isso ocorre porque Uvicorn usa o loop de eventos `uvloop` por padrão, que é incompatível com `nest_asyncio`.

**Solução**

Use um dos seguintes métodos para extrair elementos numerados:

```bash
# Opção 1: Usar script shell (recomendado)
# Deprecated: numbered-item extraction was removed

# Opção 2: Comando Python direto
# Deprecated: numbered-item extraction was removed
```

Isso extrairá elementos numerados (Definições, Teoremas, Equações, etc.) da sua base de conhecimento sem reinicializá-la.

</details>

<br>

---

## 📄 Licença

Este projeto está licenciado sob **[AGPL-3.0](../../LICENSE)**.


## ⭐ Histórico de Stars

<div align="center">
<a href="https://star-history.com/#HKUDS/DeepTutor&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=Date" />
 </picture>
</a>
</div>


## 🤝 Contribuição

Acolhemos contribuições da comunidade! Para garantir qualidade e consistência do código, siga as diretrizes abaixo.

<details>
<summary><b>Configuração de Desenvolvimento</b></summary>

### Configuração dos Pre-commit Hooks

Este projeto usa **pre-commit hooks** para formatar automaticamente o código e verificar problemas antes de fazer commit.

**Passo 1: Instalar pre-commit**
```bash
# Usar pip
pip install pre-commit

# Ou usar conda
conda install -c conda-forge pre-commit
```

**Passo 2: Instalar os hooks do Git**
```bash
cd DeepTutor
pre-commit install
```

**Passo 3: (Opcional) Executar verificações em todos os arquivos**
```bash
pre-commit run --all-files
```

Sempre que você executar `git commit`, os pre-commit hooks executarão automaticamente:
- Formatar o código Python com Ruff
- Formatar o código frontend com Prettier
- Verificar erros de sintaxe
- Validar arquivos YAML/JSON
- Detectar problemas de segurança potenciais

### Ferramentas de Qualidade de Código

| Ferramenta | Objetivo | Configuração |
|:---:|:---|:---:|
| **Ruff** | Verificação e formatação do código Python | `pyproject.toml` |
| **Prettier** | Formatação do código frontend | `web/.prettierrc.json` |
| **detect-secrets** | Verificação de segurança | `.secrets.baseline` |

> **Nota**: O projeto usa **Ruff format** em vez de Black para evitar conflitos de formatação.

### Comandos Comuns

```bash
# Commit normal (os hooks são executados automaticamente)
git commit -m "Sua mensagem de commit"

# Verificar manualmente todos os arquivos
pre-commit run --all-files

# Atualizar os hooks para as versões mais recentes
pre-commit autoupdate

# Ignorar os hooks (não recomendado, apenas para emergências)
git commit --no-verify -m "Correção de emergência"
```

</details>

### Diretrizes de Contribuição

1. **Fork e Clone**: Faça fork do repositório e clone-o
2. **Criar uma Branch**: Crie uma branch de funcionalidade a partir de `main`
3. **Instalar Pre-commit**: Siga as etapas de configuração acima
4. **Fazer Modificações**: Escreva código seguindo o estilo do projeto
5. **Testar**: Certifique-se de que suas modificações funcionam corretamente
6. **Commit**: Os pre-commit hooks formatarão automaticamente seu código
7. **Push e PR**: Faça push para seu fork e crie uma Pull Request

### Reportar Problemas

- Use GitHub Issues para reportar bugs ou sugerir funcionalidades
- Forneça informações detalhadas sobre o problema
- Se for um bug, inclua as etapas para reproduzi-lo

<div align="center">
<br>
❤️ Agradecemos a todos os nossos contribuidores por suas valiosas contribuições.

</div>

## 🔗 Projetos Relacionados

<div align="center">

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🎨 RAG-Anything](https://github.com/HKUDS/RAG-Anything) | [💻 DeepCode](https://github.com/HKUDS/DeepCode) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) |
|:---:|:---:|:---:|:---:|
| RAG Simples e Rápido | RAG Multimodal | Assistente de Código IA | Automação de Pesquisa |

**[Laboratório de Inteligência de Dados @ HKU](https://github.com/HKUDS)**

[⭐ Siga-nos](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Reportar um bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussões](https://github.com/HKUDS/DeepTutor/discussions)

---
*✨ Obrigado por visitar **DeepTutor**!*

<img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">

</div>
