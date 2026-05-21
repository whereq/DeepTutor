<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Агент-нативное персонализированное обучение

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-CDCFD4"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-CDCFD4"></a>&nbsp;
  <a href="README_FR.md"><img alt="Français" height="40" src="https://img.shields.io/badge/Français-CDCFD4"></a>&nbsp;
  <a href="README_AR.md"><img alt="Arabic" height="40" src="https://img.shields.io/badge/Arabic-CDCFD4"></a>&nbsp;
  <a href="README_RU.md"><img alt="Русский" height="40" src="https://img.shields.io/badge/Русский-BCDCF7"></a>&nbsp;
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

[Возможности](#key-features) · [Начало работы](#get-started) · [Обзор](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [Многопользовательский режим](#multi-user) · [Сообщество](#community)

</div>

---

> 🤝 **Мы приветствуем любые виды вклада!** Стратегия ветвления, стандарты кода и руководство по началу работы — в [Руководстве по вкладу](../../CONTRIBUTING.md).
>
> 🗺️ **Дорожная карта** ведётся в открытом виде на [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — комментируйте, чтобы голосовать за пункты или предлагать новые.

### 📦 Релизы

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — Трёхслойный верстак Memory (L1/L2/L3), все возможности чата перестроены на едином агентном движке, RAG исключительно на LlamaIndex и единый интерфейс Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Восстановление CORS для удалённого Docker, `DISABLE_SSL_VERIFY` для SDK-провайдеров, более безопасные цитаты в блоках кода и опциональное дополнение Matrix E2EE.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — Поддержка Zulip и NVIDIA NIM для TutorBot, более безопасная маршрутизация моделей рассуждения, `deeptutor start`, подсказки в боковой панели и согласованность хранилища сессий.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Опциональные многопользовательские развёртывания с изолированными рабочими пространствами, права администратора, маршруты аутентификации и ограниченный доступ во время выполнения.

<details>
<summary><b>Предыдущие релизы (более 2 недель назад)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Исправления моделей рассуждения/провайдеров, видимая история индексов Knowledge, более безопасные очистка и редактирование шаблонов в Co-Writer.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Выбор моделей на основе каталога для чата и TutorBot, более безопасная переиндексация RAG, исправления лимита токенов OpenAI Responses, валидация редактора Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Более гладкие настройки локального запуска, более безопасные RAG-запросы, чище аутентификация локальных эмбеддингов, полировка тёмного режима настроек.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Сохранение чата на страницах книг и потоки восстановления, ссылки чат-книга, усиленная обработка языка/рассуждения, упрочнение извлечения документов RAG.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — Поддержка эмбеддингов NVIDIA NIM + Gemini, единый контекст Space (история чата/skills/память), снимки сессий, устойчивость переиндексации RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — Прозрачные URL эндпоинтов эмбеддингов, устойчивость переиндексации RAG для невалидных персистентных векторов, очистка памяти от вывода моделей рассуждения, исправление выполнения Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Стабильность: более безопасная маршрутизация RAG и валидация эмбеддингов, персистентность Docker, ввод с поддержкой IME, надёжность в Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Версионированные индексы KB с рабочим процессом переиндексации, перестроенное рабочее пространство Knowledge, авто-определение эмбеддингов с новыми адаптерами, хаб Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Сохраняемые вложения чата с панелью предпросмотра файлов, конвейеры возможностей с учётом вложений, экспорт TutorBot в Markdown.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — Текстовые/кодовые/SVG вложения, Setup Tour одной командой, экспорт чата в Markdown, компактный UI управления KB.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Вложения документов (PDF/DOCX/XLSX/PPTX), отображение блоков рассуждения, редактор шаблонов Soul, сохранение Co-Writer в notebook.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — Пользовательская система Skills, переработка производительности ввода чата, авто-запуск TutorBot, UI библиотеки книг, полноэкранная визуализация.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Лимиты токенов по этапам, регенерация ответа во всех точках входа, исправления совместимости с RAG и Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Компилятор «живых книг» Book Engine, многодокументный Co-Writer, интерактивные HTML-визуализации, @-упоминание Question Bank.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Вкладка Channels на основе схемы, консолидация в единый RAG-конвейер, вынесенные prompt чата.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — Универсальный «Ответить сейчас», синхронизация прокрутки Co-Writer, единая панель настроек, кнопка Stop для стриминга.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Переработка блочной математики LaTeX, диагностический зонд LLM, руководство по Docker + локальной LLM.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Сессии с закладками URL, тема Snow, heartbeat WebSocket и автопереподключение, переработка реестра эмбеддингов.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Тетрадь вопросов с закладками и категориями, Mermaid в Visualize, обнаружение несоответствия эмбеддингов, совместимость Qwen/vLLM, поддержка LM Studio и llama.cpp, тема Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Консолидация поиска с резервом SearXNG, исправление переключения провайдера, исправления утечек ресурсов фронтенда.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Возможность Visualize (Chart.js/SVG), предотвращение дубликатов в quiz и поддержка модели o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Отслеживание прогресса эмбеддингов с повтором при превышении лимита, кросс-платформенные исправления зависимостей, исправление валидации MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — Нативный SDK OpenAI/Anthropic (без litellm), поддержка Windows Math Animator, надёжный парсинг JSON и полная китайская i18n.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Горячая перезагрузка настроек, вложенный вывод MinerU, исправление WebSocket и минимум Python 3.11+.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Переписывание агент-нативной архитектуры (~200к строк): плагин-модель Tools + Capabilities, CLI и SDK, TutorBot, Co-Writer, Guided Learning и постоянная память.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Постоянство сессий, инкрементальная загрузка документов, гибкий импорт RAG-конвейера и полная китайская локализация.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Поддержка Docling для RAG-Anything, оптимизация системы логирования и исправления ошибок.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Единая конфигурация сервисов, выбор RAG-конвейера на базу знаний, переработка генерации вопросов и настройка боковой панели.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Поддержка многопровайдерных LLM и эмбеддингов, новая домашняя страница, развязка модуля RAG и рефакторинг переменных окружения.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Единая архитектура PromptManager, CI/CD на GitHub Actions и предсобранные Docker-образы на GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Развёртывание в Docker, обновление до Next.js 16 и React 19, усиление безопасности WebSocket и исправления критических уязвимостей.

</details>

### 📰 Новости

> **[2026.4.19]** 🎉 Мы достигли 20 тысяч звёзд за 111 дней! Спасибо за невероятную поддержку — мы привержены непрерывной итерации к по-настоящему персонализированному, разумному обучению для каждого.

> **[2026.4.10]** 📄 Наша статья теперь доступна на arXiv! Прочитайте [препринт](https://arxiv.org/abs/2604.26962), чтобы узнать больше о замысле и идеях, стоящих за DeepTutor.

> **[2026.4.4]** Давно не виделись! ✨ DeepTutor v1.0.0 наконец-то здесь — агент-нативная эволюция с полным переписыванием архитектуры с нуля, TutorBot и гибким переключением режимов под лицензией Apache-2.0. Начинается новая глава!

> **[2026.2.6]** 🚀 Мы достигли 10 тысяч звёзд всего за 39 дней! Огромное спасибо нашему невероятному сообществу за поддержку!

> **[2026.1.1]** С Новым годом! Присоединяйтесь к нашему [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) или [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — давайте вместе формировать будущее DeepTutor!

> **[2025.12.29]** DeepTutor официально выпущен!


<a id="key-features"></a>
## ✨ Ключевые возможности

**Рабочие поверхности**

- Chat — Chat, Solve, Quiz, Research и Visualize разделяют одну сессию, базу знаний и историю цитирования, что позволяет вам эскалировать в середине разговора без потери контекста.
- Co-Writer — Markdown-рабочее пространство с разделённым видом, где любое выделение можно переписать, расширить или сократить, опционально с привязкой к вашей KB или вебу. Черновики сохраняются прямо в notebooks.
- Book Engine — мультиагентный конвейер компилирует ваши материалы в интерактивные «живые книги» с 13 типами блоков: викторины, флэш-карты, временные шкалы, графы концепций, встроенный просмотрщик GeoGebra, анимации и многое другое. Страницы маркируются отпечатком KB, что позволяет обнаруживать дрейф.

**Ваша библиотека**

- Knowledge Bases — версионированные RAG-готовые коллекции, end-to-end на LlamaIndex. Каждая (пере)индексация отслеживается, сравнима и откатываема.
- Space — личная библиотека для повторения, объединяющая историю чата, notebooks, банк вопросов и пользовательские skills (`SKILL.md`), которые переключают личность DeepTutor.
- Трёхслойная память — append-only трассы L1, L2 факты, курируемые по поверхности с цитированием, и L3 межповерхностный синтез. Инспектируемый верстак и граф памяти позволяют вам аудировать *почему* DeepTutor знает то, что он знает.

**Расширяемость и контроль**

- Композируемые инструменты — RAG, веб-поиск, выполнение кода, рассуждение, мозговой штурм, поиск статей, анализ GeoGebra и помощники чата (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). Серверы MCP подключаются наряду со встроенными.
- Персональные TutorBots — постоянные, автономные тьюторы, каждый со своим рабочим пространством, soul, skills и каналами (Telegram, Discord, Slack, Matrix, Zulip, …). Построены на [nanobot](https://github.com/HKUDS/nanobot).
- Единые Settings — один черновик / Apply верстак для внешнего вида, моделей, эмбеддингов, поиска, возможностей, памяти, MCP-серверов и инструментов, с общим отслеживанием стоимости по вызову.
- Агент-нативная CLI — каждая возможность, KB, сессия и TutorBot в одной команде; богатый вывод для людей, структурированный JSON для агентов. Передайте [`SKILL.md`](../../SKILL.md) любому LLM с доступом к инструментам, и он сможет управлять DeepTutor автономно.
- Опциональная аутентификация — отключена по умолчанию; включите для многопользовательских развёртываний с bcrypt + JWT, панелью администратора и опциональным sidecar PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 Начало работы

DeepTutor теперь имеет четыре параллельных пути установки. Все они используют один и тот же макет конфигурации времени выполнения:

- Настройки находятся в `data/user/settings/` под вашим текущим рабочим пространством или под `DEEPTUTOR_HOME` / `deeptutor start --home`, когда вы выбираете его явно.
- `model_catalog.json` хранит профили провайдеров моделей, базовые URL, API-ключи, активные модели, настройки эмбеддингов и поиска.
- `system.json` хранит порты запуска, публичную базу API, CORS, TLS и параметры вложений.
- `auth.json` хранит опциональный переключатель аутентификации и хеш загрузочных учётных данных.
- `integrations.json` хранит опциональные sidecar, такие как PocketBase.
- Корневой `.env` проекта больше не используется как файл конфигурации приложения.

Для полного локального приложения рекомендуемый порядок: **выберите рабочее пространство → установите → `deeptutor init` → `deeptutor start`**.

### Вариант 1 — Установить DeepTutor

Используйте, когда вам нужно полное локальное веб-приложение и CLI без клонирования репозитория.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **Пробуете v1.4.0 beta?** PyPI нормализует `1.4.0-beta` в `1.4.0b0`, так что `pip install -U deeptutor` останется на последней стабильной версии. Включите пре-релиз с помощью:
>
> ```bash
> pip install --pre -U deeptutor      # последний пре-релиз
> pip install -U deeptutor==1.4.0b0   # точно зафиксировать на v1.4.0-beta
> ```

`deeptutor init` записывает конфигурацию в `data/user/settings/` в каталоге, где вы её запускаете. Он спрашивает:

- Порт backend, по умолчанию `8001`
- Порт frontend, по умолчанию `3782`
- Провайдер LLM, базовый URL, API-ключ и имя модели
- Опциональный провайдер эмбеддингов для Knowledge Base / RAG

После `deeptutor start` откройте URL frontend, напечатанный в терминале. С портами по умолчанию это URL [http://127.0.0.1:3782](http://127.0.0.1:3782).

Держите терминал `deeptutor start` открытым. Нажмите `Ctrl+C` в этом терминале, чтобы остановить и backend, и frontend.

Примечания:

- `deeptutor start` запускает FastAPI backend и упакованный Next.js frontend вместе.
- Упакованное веб-приложение не требует `git clone` или `npm install`, но ему всё ещё нужен локальный Node.js 20+ для выполнения автономного сервера Next.js.

### Вариант 2 — Установить из исходного кода

Используйте, когда разрабатываете DeepTutor или хотите запускать прямо из checkout.
Используйте Python 3.11+ и Node.js 22 LTS для наилучшего соответствия CI и Docker.

**1. Клонировать репозиторий**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Создать окружение Python**

macOS / Linux с `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell с `venv`:

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

**3. Установить локальный пакет и зависимости frontend**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

**4. Настроить и запустить**

```bash
deeptutor init
deeptutor start
```

Если `deeptutor start` сообщает о существующем frontend, который не отвечает, удалите устаревшие файлы блокировки и запустите снова:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

Полезные дополнения для разработчиков:

```bash
pip install -e ".[dev]"             # инструменты тестов/lint
pip install -e ".[tutorbot]"        # движок TutorBot + SDK каналов
pip install -e ".[matrix]"          # канал Matrix без E2EE/libolm
pip install -e ".[matrix-e2e]"      # Matrix E2EE; требует libolm
pip install -e ".[math-animator]"   # дополнение Manim; требует LaTeX/ffmpeg/системные библиотеки
```

### Вариант 3 — Docker

Используйте, когда вам нужно полное веб-приложение в одном контейнере. Образы публикуются в GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — стабильный релиз
- `ghcr.io/hkuds/deeptutor:pre` — пре-релиз, когда доступен

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Затем откройте [http://127.0.0.1:3782](http://127.0.0.1:3782). Конфигурация, API-ключи, логи, файлы рабочего пространства, память и базы знаний хранятся в томе `deeptutor-data` под `/app/data`.

#### Подключение к Ollama или другим хост-сервисам

Внутри Docker-контейнера `localhost` ссылается на сам контейнер, а не на ваш хост. Если вы запускаете Ollama, LM Studio, llama.cpp, vLLM или другой сервис моделей на хосте, используйте один из этих подходов.

Вариант A — host gateway, рекомендуется для обычных запусков Docker:

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Затем в **DeepTutor Settings → Models** установите базовый URL провайдера на `host.docker.internal`:

- Ollama LLM endpoint: `http://host.docker.internal:11434/v1`
- Ollama embedding endpoint: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

Вариант B — host networking, только Linux:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Для запуска в фоне:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

### Вариант 4 — Только CLI

Используйте, когда вам не нужен веб-интерфейс.

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

`deeptutor init --cli` использует тот же макет `data/user/settings/`, что и полное приложение, но меняет поведение мастера:

- Пропускает запросы портов backend/frontend, потому что использование только CLI не запускает веб-приложение.
- По-прежнему записывает файлы по умолчанию `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml` и `agents.yaml`.
- По-прежнему запрашивает активный провайдер и модель LLM.
- Спрашивает, настраивать ли эмбеддинги; ответ по умолчанию — `Нет`; выберите `Да`, если планируете использовать `deeptutor kb ...` или RAG-инструменты.

Распространённые команды CLI:

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "Объясните преобразование Фурье"
deeptutor run deep_solve "Решите x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
deeptutor config show
```

### Справочник конфигурации

| Файл | Назначение |
|:---|:---|
| `data/user/settings/model_catalog.json` | Профили провайдеров LLM, эмбеддингов и поиска; API-ключи; активные модели |
| `data/user/settings/system.json` | Порты backend/frontend, публичная база API, CORS, проверка SSL, каталог вложений |
| `data/user/settings/auth.json` | Опциональный переключатель аутентификации, имя пользователя, хеш пароля, настройки токенов/cookies |
| `data/user/settings/integrations.json` | Настройки интеграции PocketBase и опциональных sidecar |
| `data/user/settings/interface.json` | Настройки языка/темы/боковой панели UI |
| `data/user/settings/main.yaml` | Значения по умолчанию поведения времени выполнения и инъекция путей |
| `data/user/settings/agents.yaml` | Настройки температуры и токенов возможностей/инструментов |

<a id="explore-deeptutor"></a>
## 📖 Обзор DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

Рефакторинг v1.4.0-beta реорганизует DeepTutor вокруг **пяти основных поверхностей** — Chat, Co-Writer, Book, Knowledge, Space — плюс **трёхслойная Memory**, которая находится под ними всеми, и единый верстак **Settings**, открывающий все параметры. Возможности (Solve / Quiz / Research / Visualize) и инструменты (RAG, веб, код, рассуждение, мозговой штурм, поиск статей, `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) свободно компонуются поверх.

### 💬 Chat — Единое интеллектуальное рабочее пространство

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Один поток, пять режимов, любой инструмент. Выбор возможности находится в композиторе; одна и та же сессия, база знаний, вложения и ссылки путешествуют с вами между режимами — переключайтесь с непринуждённого вопроса на многоагентное решение, на викторину, на полный исследовательский отчёт, не теряя контекста.

| Режим | Что делает | Построен на |
|:---|:---|:---|
| **Chat** | Гибкий разговор с любым инструментом; выбирайте из RAG, веб-поиска, выполнения кода, глубокого рассуждения, мозгового штурма, поиска статей, анализа GeoGebra. | RAG на LlamaIndex + реестр инструментов |
| **Solve** | Многошаговый план → исследовать → решить → проверить, с точными цитатами источников. | Агентный движок (`deep_solve`) |
| **Quiz** | Автоматически валидируемая генерация вопросов, привязанная к вашей KB; создаёт композитор чата для каждого вопроса. | Агентный движок (`deep_question`) |
| **Research** | Разлагает тему на подтемы, отправляет параллельные агенты через RAG / веб / arXiv и производит цитируемый отчёт с итеративными доработками в режиме append. | Перестроенный `pipeline.py` (~45% меньше, цитаты + итеративные отчёты сохранены) |
| **Visualize** | Генерирует SVG-диаграммы, диаграммы Chart.js, графы Mermaid, интерактивные HTML-страницы **или** видео/раскадровки Manim — анализатор выбирает правильный `render_type`. | Конвейер Visualize (Animator интегрирован) |

**Новые инструменты чата**, выпущенные с рефакторингом: `ask_user` (задаёт структурированный уточняющий вопрос в середине хода), `web_fetch` (втягивает конкретный URL в контекст), `write_note` / `list_notebook` (сохраняет и перечисляет записи notebook с поверхности чата) и `github_query` (поиск по issue / PR / репозиториям). Инструменты остаются **развязанными от рабочих процессов** — каждый режим позволяет вам включать или отключать инструменты по ходу.

Сессия также несёт **накопленный инвентарь источников** между ходами, так что цитаты из ранних RAG / веб-обращений остаются повторно используемыми позже в том же разговоре.

### ✍️ Co-Writer — Многодокументное рабочее пространство ИИ-письма

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer — это верстак Markdown с разделённым видом (необработанный редактор слева, живое превью справа) для заметок, отчётов, руководств и черновиков с помощью ИИ. Каждый документ живёт в своём собственном рабочем пространстве с автосохранением, скачиваемым Markdown и **Сохранить в Notebook** одним кликом.

Выделите любой текст и выберите **Переписать**, **Расширить** или **Сократить** — каждое действие выполняется как отслеживаемое редактирование агента, которое опционально может извлекать из базы знаний или веба.

### 📖 Book Engine — Интерактивные «живые книги»

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

Дайте DeepTutor тему, укажите ему вашу базу знаний, и он произведёт структурированную, интерактивную книгу — не статический экспорт, а живой документ, который вы можете читать, проверять себя по нему и обсуждать в контексте.

За кулисами многоагентный конвейер занимается тяжёлой работой: предлагает план, извлекает соответствующие источники из вашей KB, синтезирует дерево глав, планирует каждую страницу и компилирует каждый блок. Вы остаётесь под контролем — просмотрите предложение, переупорядочите главы и общайтесь рядом с любой страницей.

Страницы собираются из 13 типов блоков — текст, выноска, викторина, флэш-карты, код, рисунок, глубокое погружение, анимация, интерактивное демо (теперь включающее **просмотрщик GeoGebra**), временная шкала, граф концепций, секция и пользовательская заметка.

### 📚 Knowledge Bases — Готовые для RAG библиотеки документов

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

Выделенное рабочее пространство для коллекций документов, питающих RAG. Каждая база знаний имеет четыре вкладки:

- **Files** — просматривайте загруженные источники, просматривайте PDF-файлы встроенно и видите размер/статус по файлу.
- **Add documents** — добавляйте PDF, файлы Office (DOCX / XLSX / PPTX), Markdown, обычный текст и широкий спектр типов файлов кода/данных. Документы автоматически маршрутизируются к подходящему экстрактору.
- **Index versions** — каждая (пере)индексация — это отслеживаемая версия. Откатывайтесь к более раннему индексу, сравнивайте модели эмбеддингов или инспектируйте статистику chunking, не теряя предыдущую сборку.
- **Settings** — выбирайте провайдера/модель эмбеддингов, параметры chunking и reranker для KB.

Индексация построена на **LlamaIndex** end-to-end, с переиндексацией с защитой от повторов, обнаружением несоответствия эмбеддингов и устойчивой обработкой повреждённых персистентных векторов.

### 🌐 Space — Ваша персональная библиотека обучения

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space — это аналог **чтения / повторения** активных поверхностей. Там, где Chat / Co-Writer / Book — это где вы *производите*, Space — это место, где живёт всё, что вы производите, доступное для поиска и воспроизведения.

- **Chat History** — каждый разговор по каждому режиму, с переименованием заголовка, удалением и возобновлением.
- **Notebooks** — сохраняйте вывод из Chat, Research и Co-Writer в категоризированные, цветокодированные notebooks.
- **Question Bank** — каждый автоматически сгенерированный вопрос викторины, доступный для добавления в закладки и @-упоминания в чате.
- **Skills** — пользовательские файлы `SKILL.md`, определяющие персоны обучения (имя, описание, триггеры, тело). Когда skill активен, он внедряется в системный prompt чата.

### 🧠 Memory — Трёхслойная архитектура

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

Память DeepTutor теперь — это **трёхслойный конвейер** с инспектируемым верстаком на `/memory`.

| Слой | Роль | Хранение |
|:---|:---|:---|
| **L1 · Зеркало рабочего пространства** (LIVE) | Append-only трасса каждого взаимодействия, по поверхности, по дню. Беспотерьная запись того, что действительно произошло. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Сводки по поверхностям** (CURATED) | Специфичные для поверхности факты, извлечённые консолидатором. Каждый факт несёт цитаты-сноски обратно к трассам L1. | `L2/<surface>.md` |
| **L3 · Межповерхностное знание** (SYNTHESIS) | Межповерхностный синтез: ваш `profile`, временная шкала `recent`, `scope` знаний и `preferences`. Хеджированные утверждения, каждое поддержано доказательствами L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

Семь поверхностей питают конвейер: **chat, notebook, quiz, kb, book, tutorbot, cowriter**.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

**Memory Graph** (`/memory/graph`) отрисовывает все три слоя одновременно: синтез L3 в центре, факты L2 в среднем кольце, трассы L1 снаружи, сгруппированные по поверхности.

### ⚙️ Settings — Единый центр управления

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

Поверхность настроек была унифицирована в v1.4 и разделена по областям, с моделью черновика / **Apply**, чтобы изменения были атомарными и могли быть отменены до сохранения:

- **Appearance** — язык UI и тема (Cream, Snow, Dark, Glass).
- **Status** — живой зонд здоровья LLM, эмбеддингов, поиска и хранилищных бэкендов.
- **LLM**, **Embedding**, **Search** — каталог провайдеров, базовые URL, API-ключи и выбор активных моделей.
- **Capabilities** — настройки для каждой возможности (chunking, бюджет LLM, политики дедупликации и ссылок, максимум итераций) для Chat, Solve, Quiz, Research, Visualize и Co-Writer. Поддерживается единым конвертом `emit_capability_result` и общим `UsageTracker`, который показывает стоимость по вызову.
- **Memory** — переключайте запуски консолидатора, настраивайте частоту и бюджет и переходите в верстак памяти.
- **MCP servers** — регистрируйте внешние серверы Model Context Protocol; их инструменты появляются рядом с встроенными инструментами.
- **Tools** — инспектируйте каждый встроенный инструмент, его параметры, статус (включён / скоро) и i18n-статус.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — Постоянные, автономные ИИ-тьюторы

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot — это не чатбот, это **постоянный, многоэкземплярный агент**, построенный на [nanobot](https://github.com/HKUDS/nanobot). Каждый TutorBot выполняет свой собственный цикл агента с независимым рабочим пространством, памятью и личностью.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Шаблоны Soul** — определите личность, тон и философию обучения вашего тьютора через редактируемые файлы Soul.
- **Независимое рабочее пространство** — у каждого бота есть свой каталог с отдельной памятью, сессиями, skills и конфигурацией.
- **Проактивный Heartbeat** — боты не только отвечают — они инициируют. Встроенная система Heartbeat включает повторяющиеся учебные напоминания, проверки повторения и запланированные задачи.
- **Полный доступ к инструментам** — каждый бот обращается к полному набору инструментов DeepTutor: извлечение RAG, выполнение кода, веб-поиск, поиск академических статей, глубокое рассуждение и мозговой штурм.
- **Обучение Skills** — обучите вашего бота новым способностям, добавляя файлы skills в его рабочее пространство.
- **Многоканальное присутствие** — подключайте ботов к Telegram, Discord, Slack, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, Email и многому другому.
- **Команды и суб-агенты** — порождайте фоновых суб-агентов или оркеструйте многоагентные команды внутри одного бота.

```bash
deeptutor bot create math-tutor --persona "Сократический учитель математики, использующий наводящие вопросы"
deeptutor bot create writing-coach --persona "Терпеливый, внимательный к деталям наставник по письму"
deeptutor bot list                  # Просмотреть всех ваших активных тьюторов
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — Агент-нативный интерфейс

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor полностью CLI-нативен. Каждая возможность, база знаний, сессия, память и TutorBot — на расстоянии одной команды, без необходимости в браузере.

**Одноразовое выполнение**:

```bash
deeptutor run chat "Объясните преобразование Фурье" -t rag --kb textbook
deeptutor run deep_solve "Докажите, что √2 иррационально" -t reason
deeptutor run deep_question "Линейная алгебра" --config num_questions=5
deeptutor run deep_research "Механизмы внимания в трансформерах"
deeptutor run visualize "Нарисуйте архитектуру трансформера"
```

**Интерактивный REPL**:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Внутри REPL: /cap, /tool, /kb, /history, /notebook, /config для переключения на лету
```

**Жизненный цикл базы знаний**:

```bash
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb add my-kb --docs-dir ./papers/
deeptutor kb search my-kb "градиентный спуск"
deeptutor kb set-default my-kb
```

**Двойной режим вывода**:

```bash
deeptutor run chat "Резюмируйте главу 3" -f rich    # Цветной, форматированный вывод
deeptutor run chat "Резюмируйте главу 3" -f json    # JSON-события с разделителями строк
```

**Непрерывность сессий**:

```bash
deeptutor session list
deeptutor session open <id>
```

<details>
<summary><b>Полный справочник команд CLI</b></summary>

**Верхний уровень**

| Команда | Описание |
|:---|:---|
| `deeptutor run <capability> <message>` | Запустить любую возможность за один ход (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | Интерактивный REPL с опциональными `--capability`, `--tool`, `--kb`, `--language` |
| `deeptutor serve` | Запустить API-сервер DeepTutor |

**`deeptutor bot`**

| Команда | Описание |
|:---|:---|
| `deeptutor bot list` | Список всех экземпляров TutorBot |
| `deeptutor bot create <id>` | Создать и запустить нового бота (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Запустить бота |
| `deeptutor bot stop <id>` | Остановить бота |

**`deeptutor kb`**

| Команда | Описание |
|:---|:---|
| `deeptutor kb list` | Список всех баз знаний |
| `deeptutor kb info <name>` | Показать детали базы знаний |
| `deeptutor kb create <name>` | Создать из документов (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Добавлять документы инкрементально |
| `deeptutor kb search <name> <query>` | Искать в базе знаний |
| `deeptutor kb set-default <name>` | Установить как KB по умолчанию |
| `deeptutor kb delete <name>` | Удалить базу знаний (`--force`) |

**`deeptutor memory`**

| Команда | Описание |
|:---|:---|
| `deeptutor memory show [file]` | Просмотр памяти (`summary`, `profile` или `all`) |
| `deeptutor memory clear [file]` | Очистить память (`--force`) |

**`deeptutor session`**

| Команда | Описание |
|:---|:---|
| `deeptutor session list` | Список сессий (`--limit`) |
| `deeptutor session show <id>` | Просмотреть сообщения сессии |
| `deeptutor session open <id>` | Возобновить сессию в REPL |
| `deeptutor session rename <id>` | Переименовать сессию (`--title`) |
| `deeptutor session delete <id>` | Удалить сессию |

**`deeptutor notebook`**

| Команда | Описание |
|:---|:---|
| `deeptutor notebook list` | Список notebooks |
| `deeptutor notebook create <name>` | Создать notebook (`--description`) |
| `deeptutor notebook show <id>` | Просмотреть записи notebook |
| `deeptutor notebook add-md <id> <path>` | Импортировать markdown как запись |
| `deeptutor notebook replace-md <id> <rec> <path>` | Заменить запись markdown |
| `deeptutor notebook remove-record <id> <rec>` | Удалить запись |

**`deeptutor book`**

| Команда | Описание |
|:---|:---|
| `deeptutor book list` | Список всех книг в рабочем пространстве |
| `deeptutor book health <book_id>` | Проверить дрейф KB и здоровье книги |
| `deeptutor book refresh-fingerprints <book_id>` | Обновить отпечатки KB и очистить устаревшие страницы |

**`deeptutor config` / `plugin` / `provider`**

| Команда | Описание |
|:---|:---|
| `deeptutor config show` | Напечатать сводку текущей конфигурации |
| `deeptutor plugin list` | Список зарегистрированных инструментов и возможностей |
| `deeptutor plugin info <name>` | Показать детали инструмента или возможности |
| `deeptutor provider login <provider>` | Аутентификация провайдера |

</details>

---

<a id="multi-user"></a>
### 👥 Многопользовательский режим — Совместные развёртывания с рабочими пространствами на пользователя

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Включите аутентификацию, и DeepTutor превратится в многотенантное развёртывание с **изолированными рабочими пространствами на пользователя** и **курируемыми администратором ресурсами**. Первый зарегистрировавшийся становится администратором и настраивает модели, API-ключи и базы знаний от имени всех остальных.

**Быстрый старт (5 шагов):**

```bash
# 1. Включите auth в data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Перезапустите веб-стек.
deeptutor start

# 3. Откройте http://localhost:3782/register и создайте первый аккаунт.
#    Первая регистрация — единственная публичная; этот пользователь становится admin,
#    и endpoint /register автоматически закрывается после.

# 4. Как admin, перейдите в /admin/users → "Add user", чтобы создать товарищей по команде.

# 5. Для каждого пользователя нажмите на иконку слайдера → назначьте профили LLM,
#    базы знаний и skills. Сохраните.
```

**Что видит администратор:**

- **Полная страница Settings** на `/settings` — управляйте провайдерами LLM / эмбеддингов / поиска, API-ключами, каталогами моделей и runtime "Apply".
- **Управление пользователями** на `/admin/users` — создавайте, повышайте, понижайте и удаляйте аккаунты.
- **Редактор грантов** — для каждого не-администратора выбирайте профили моделей, базы знаний и skills, которыми они могут пользоваться.
- **Аудит-журнал** — каждое изменение грантов добавляется в `multi-user/_system/audit/usage.jsonl`.

**Что получают обычные пользователи:**

- **Изолированное рабочее пространство** под `multi-user/<uid>/` — собственная история чата (`chat_history.db`), память, notebooks и личные базы знаний.
- **Доступ только для чтения** к назначенным администратором базам знаний и skills.
- **Отредактированная страница Settings** — только тема, язык и сводка предоставленных моделей.
- **LLM с областью** — ходы чата маршрутизируются через назначенную администратором модель.

**Макет рабочего пространства:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Хешированные учётные данные, роли
│   ├── auth/auth_secret         # Секрет подписи JWT (автогенерируется)
│   ├── grants/<uid>.json        # Гранты ресурсов на пользователя (управляются admin)
│   └── audit/usage.jsonl        # Аудит-журнал
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Справочник конфигурации:**

| Настройка | Обязательно | Описание |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Да | Установите `true` для включения многопользовательской auth. По умолчанию `false` (однопользовательский режим). |
| `multi-user/_system/auth/auth_secret` | Рекомендуется | Секрет подписи JWT. Автогенерируется при первой аутентифицированной загрузке, если отсутствует. |
| `data/user/settings/auth.json: token_expire_hours` | Нет | Время жизни JWT; по умолчанию `24`. |
| `data/user/settings/auth.json: username/password_hash` | Нет | Опциональные учётные данные загрузки одного пользователя без головы. |
| `data/user/settings/system.json` | Нет | `deeptutor start` выводит флаги auth frontend из runtime-настроек. |

> ⚠️ **Режим PocketBase (`integrations.pocketbase_url` установлен) только для одного пользователя.** Многопользовательские развёртывания должны оставлять `integrations.pocketbase_url` пустым и использовать бэкенд JSON/SQLite по умолчанию.

> ⚠️ **Рекомендация одного процесса.** Повышение первого пользователя до администратора защищено внутрипроцессным `threading.Lock`. Развёртывания с несколькими воркерами должны провизировать первого администратора офлайн или поддерживать хранилище пользователей внешней системой.

<a id="community"></a>
## 🌐 Сообщество и экосистема

DeepTutor стоит на плечах выдающихся open-source проектов:

| Проект | Роль в DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Ультралёгкий агентный движок, питающий TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Конвейер RAG и хребет индексации документов |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | ИИ-генерация математических анимаций для Math Animator |

**Из экосистемы HKUDS:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| Простой и быстрый RAG | Фреймворк агентов без кода | Автоматизированное исследование | Ультралёгкий ИИ-агент |


## 🤝 Вклад

<div align="center">

Мы надеемся, что DeepTutor станет подарком для сообщества. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

См. [CONTRIBUTING.md](../../CONTRIBUTING.md) для руководства по настройке окружения разработки, стандартам кода и рабочему процессу pull request.

## ⭐ История звёзд

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

[⭐ Поставьте звезду](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Сообщить об ошибке](https://github.com/HKUDS/DeepTutor/issues) · [💬 Обсуждения](https://github.com/HKUDS/DeepTutor/discussions)

---

Лицензировано под [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
