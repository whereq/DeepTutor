<div align="center">

<img src="../../assets/logo-ver2.png" alt="Логотип DeepTutor" width="150" style="border-radius: 15px;">

# DeepTutor: Персональный учебный ассистент на базе ИИ

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](../../LICENSE)

<p align="center">
  <a href="https://discord.gg/eRsjPgMU4t"><img src="https://img.shields.io/badge/Discord-Join_Community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  &nbsp;&nbsp;
  <a href="../../Communication.md"><img src="https://img.shields.io/badge/Feishu-Join_Group-00D4AA?style=for-the-badge&logo=feishu&logoColor=white" alt="Feishu"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/HKUDS/DeepTutor/issues/78"><img src="https://img.shields.io/badge/WeChat-Join_Group-07C160?style=for-the-badge&logo=wechat&logoColor=white" alt="WeChat"></a>
</p>



[**Быстрый старт**](#-быстрый-старт) · [**Основные модули**](#-основные-модули) · [**Часто задаваемые вопросы**](#-часто-задаваемые-вопросы)

[🇬🇧 English](../../README.md) · [🇨🇳 中文](README_CN.md) · [🇯🇵 日本語](README_JA.md) · [🇪🇸 Español](README_ES.md) · [🇫🇷 Français](README_FR.md) · [🇸🇦 العربية](README_AR.md) · [🇮🇳 हिन्दी](README_HI.md) · [🇵🇹 Português](README_PT.md)

</div>

<div align="center">

📚 **Q&A по знаниям из массивов документов** &nbsp;•&nbsp; 🎨 **Интерактивная визуализация обучения**<br>
🎯 **Укрепление знаний** &nbsp;•&nbsp; 🔍 **Глубокие исследования и генерация идей**

</div>

---
### 📰 Новости

> **[2026.1.1]** С Новым годом! Присоединяйтесь к нашему [Discord-сообществу](https://discord.gg/zpP9cssj), [WeChat-сообществу](https://github.com/HKUDS/DeepTutor/issues/78) или [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — формируйте будущее DeepTutor! 💬

> **[2025.12.30]** Посетите наш [официальный сайт](https://hkuds.github.io/DeepTutor/) для получения дополнительной информации!

> **[2025.12.29]** DeepTutor уже в сети! ✨

### 📦 Релизы

> **[2026.1.23]** Релиз [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) - Сохранение сеансов интерфейса, полная поддержка китайского языка, обновления развертывания Docker и исправления незначительных ошибок -- Спасибо всем за обратную связь!

<details>
<summary>История релизов</summary>

> **[2026.1.18]** Релиз [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.1) - Улучшение конвейера RAG с поддержкой Docling и улучшение рабочих процессов CI/CD с исправлением нескольких незначительных ошибок -- Спасибо всем за отзывы!


> **[2026.1.15]** Релиз [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) - Унифицированные службы LLM и встраивания, выбор конвейера RAG и значительные улучшения модулей Home, History, QuestionGen и Settings -- Спасибо всем участникам!

> **[2026.1.9]** Релиз [v0.4.1](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.1) с полной переработкой системы провайдера LLM, улучшением надежности генерации вопросов и очисткой кодовой базы - Спасибо всем участникам!

> **[2026.1.9]** Релиз [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) с новой структурой кода, поддержкой нескольких llm и встраиваний - Спасибо всем участникам!

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) - Унифицированная архитектура PromptManager, автоматизация CI/CD и предварительно собранные образы Docker на GHCR

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) - Развертывание Docker, обновление до Next.js 16 и React 19, исправления безопасности WebSocket и критических уязвимостей

</details>

---

## Ключевые особенности DeepTutor

### 📚 Q&A по знаниям из массивов документов
• **Интеллектуальная база знаний**: Загружайте учебники, научные статьи, технические руководства и документы, специфичные для области. Создавайте исчерпывающий репозиторий знаний на основе ИИ для мгновенного доступа.<br>
• **Решение проблем с несколькими агентами**: Двухконтурная архитектура рассуждений с RAG, веб-поиском и выполнением кода — предоставление пошаговых решений с точными цитатами.

### 🎨 Интерактивная визуализация обучения
• **Упрощение знаний и объяснения**: Преобразование сложных концепций, знаний и алгоритмов в понятные визуальные пособия, подробные пошаговые разборы и увлекательные интерактивные демонстрации.<br>
• **Персонализованный Q&A**: Контекстно-зависимые разговоры, адаптирующиеся к вашему прогрессу в обучении, с интерактивными страницами и отслеживанием знаний на основе сеансов.

### 🎯 Укрепление знаний с помощью генератора практических задач
• **Интеллектуальное создание упражнений**: Генерация целевых викторин, практических задач и настраиваемых оценок, адаптированных к вашему текущему уровню знаний и конкретным учебным целям.<br>
• **Имитация подлинного экзамена**: Загрузите контрольные экзамены для генерации практических вопросов, которые идеально соответствуют оригинальному стилю, формату и сложности — обеспечивая реалистичную подготовку к реальному тесту.

### 🔍 Глубокие исследования и генерация идей
• **Комплексные исследования и обзор литературы**: Проведение глубокого изучения тем с систематическим анализом. Выявление закономерностей, соединение связанных концепций в разных дисциплинах и синтез существующих исследовательских находок.<br>
• **Открытие новых идей**: Генерация структурированных учебных материалов и выявление пробелов в знаниях. Определение перспективных новых направлений исследований посредством интеллектуального синтеза знаний между доменами.

---

<div align="center">
  <img src="../../assets/figs/title_gradient.svg" alt="Все-в-одном система обучения" width="70%">
</div>

<!-- ━━━━━━━━━━━━━━━━ Основной учебный опыт ━━━━━━━━━━━━━━━━ -->

<table>
<tr>
<td width="50%" align="center" valign="top">

<h3>📚 Q&A по знаниям из массивов документов</h3>
<a href="#problem-solving-agent">
<img src="../../assets/gifs/solve.gif" width="100%">
</a>
<br>
<sub>Многоагентное решение проблем с точными цитатами</sub>

</td>
<td width="50%" align="center" valign="top">

<h3>🎨 Интерактивная визуализация обучения</h3>
<a href="#guided-learning">
<img src="../../assets/gifs/guided-learning.gif" width="100%">
</a>
<br>
<sub>Пошаговые визуальные объяснения с персональными Q&A</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Практика и укрепление ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🎯 Укрепление знаний</h3>

<table>
<tr>
<td width="50%" valign="top" align="center">

<a href="#question-generator">
<img src="../../assets/gifs/question-1.gif" width="100%">
</a>

**Пользовательские вопросы**
<sub>Генерация практических вопросов с автоматической проверкой</sub>

</td>
<td width="50%" valign="top" align="center">

<a href="#question-generator">
<img src="../../assets/gifs/question-2.gif" width="100%">
</a>

**Имитационные вопросы**
<sub>Клонирование стиля экзамена для подлинной практики</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Исследование и создание ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🔍 Глубокие исследования и генерация идей</h3>

<table>
<tr>
<td width="33%" align="center">

<a href="#deep-research">
<img src="../../assets/gifs/deepresearch.gif" width="100%">
</a>

**Глубокие исследования**
<sub>Расширение знаний из учебника с помощью RAG, веб- и поиска по статьям</sub>

</td>
<td width="33%" align="center">

<a href="#idea-generation">
<img src="../../assets/gifs/ideagen.gif" width="100%">
</a>

**Автоматизированная генерация идей**
<sub>Систематический мозговой штурм и синтез концепций с двухфазным рабочим процессом</sub>

</td>
<td width="33%" align="center">

<a href="#co-writer">
<img src="../../assets/gifs/co-writer.gif" width="100%">
</a>

**Интерактивная генерация идей**
<sub>Совместное написание текстов на основе RAG и веб-поиска с генерацией подкастов</sub>

</td>
</tr>
</table>

<!-- ━━━━━━━━━━━━━━━━ Инфраструктура знаний ━━━━━━━━━━━━━━━━ -->

<h3 align="center">🏗️ Все-в-одном система знаний</h3>

<table>
<tr>
<td width="50%" align="center">

<a href="#dashboard--knowledge-base-management">
<img src="../../assets/gifs/knowledge_bases.png" width="100%">
</a>

**Персональная база знаний**
<sub>Создание и организация собственного репозитория знаний</sub>

</td>
<td width="50%" align="center">

<a href="#notebook">
<img src="../../assets/gifs/notebooks.png" width="100%">
</a>

**Персональный блокнот**
<sub>Ваша контекстная память для учебных сессий</sub>

</td>
</tr>
</table>

<p align="center">
  <sub>🌙 Используйте DeepTutor в <b>темном режиме</b>!</sub>
</p>

---

## 🏛️ Фреймворк DeepTutor

<div align="center">
<img src="../../assets/figs/full-pipe.png" alt="Рабочий процесс DeepTutor Full-Stack" width="100%">
</div>

### 💬 Слой пользовательского интерфейса
• **Интуитивное взаимодействие**: Простой двунаправленный поток запросов-ответов для интуитивного взаимодействия.<br>
• **Структурированный вывод**: Генерация структурированных ответов, организующих сложную информацию в действия.

### 🤖 Модули интеллектуальных агентов
• **Решение проблем и оценка**: Пошаговое решение проблем и генерация настраиваемых оценок.<br>
• **Исследование и обучение**: Глубокие исследования для изучения тем и руководство обучением с визуализацией.<br>
• **Генерация идей**: Автоматизированное и интерактивное развитие концепций с инсайтами из нескольких источников.

### 🔧 Слой интеграции инструментов
• **Поиск информации**: Гибридное извлечение RAG, поиск в реальном времени и базы данных научных статей.<br>
• **Обработка и анализ**: Выполнение кода Python, поиск элементов запроса и анализ документов в формате PDF.

### 🧠 Основа знаний и памяти
• **Граф знаний**: Сопоставление сущностей и отношений для семантических связей и открытия знаний.<br>
• **Векторное хранилище**: Поиск на основе встраивания для интеллектуального поиска контента.<br>
• **Система памяти**: Управление состоянием сеанса и отслеживание цитат для контекстной непрерывности.

## 📋 Будущие задачи
> 🌟 Поставьте звезду, чтобы следить за нашими будущими обновлениями!
- [x] Поддержка многоязычности
- [x] Сообщество DeepTutor
- [x] Поддержка видео- и аудиофайлов
- [x] Настройка атомарного конвейера RAG
- [ ] Пошаговое редактирование базы знаний
- [ ] Персонализированное рабочее пространство
- [ ] Визуализация базы данных
- [ ] Онлайн-демонстрация

## 🚀 Быстрый старт

### Шаг 1: Предварительная настройка

**① Клонирование репозитория**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**② Настройка переменных окружения**

```bash
cp .env.example .env
# Отредактируйте файл .env с вашими API ключами
```

<details>
<summary>📋 <b>Справочник переменных окружения</b></summary>

| Переменная | Обязательно | Описание |
|:---|:---:|:---|
| `LLM_MODEL` | **Да** | Имя модели (например: `gpt-4o`) |
| `LLM_API_VERSION` | Нет | Версия API для Azure OpenAI (например: `2024-02-15-preview`) |
| `LLM_API_KEY` | **Да** | Ваш API ключ LLM |
| `LLM_HOST` | **Да** | URL конечной точки API |
| `EMBEDDING_MODEL` | **Да** | Имя модели встраивания |
| `EMBEDDING_API_VERSION` | Нет | Версия API для Azure OpenAI Embeddings |
| `EMBEDDING_API_KEY` | **Да** | API ключ встраивания |
| `EMBEDDING_HOST` | **Да** | Конечная точка API встраивания |
| `BACKEND_PORT` | Нет | Порт backend (по умолчанию: `8001`) |
| `FRONTEND_PORT` | Нет | Порт frontend (по умолчанию: `3782`) |
| `NEXT_PUBLIC_API_BASE` | Нет | **URL API для фронтенда** — установите для удаленного/LAN-доступа (например: `http://192.168.1.100:8001`) |
| `TTS_*` | Нет | Настройки синтеза речи |
| `SEARCH_PROVIDER` | Нет | Провайдер поиска (варианты: `perplexity`, `tavily`, `serper`, `jina`, `exa`, `baidu`, по умолчанию: `perplexity`) |
| `SEARCH_API_KEY` | Нет | Единый API-ключ для поиска |

> 💡 **Удаленный доступ**: если вы заходите с другого устройства (например: `192.168.31.66:3782`), добавьте в `.env`:
> ```bash
> NEXT_PUBLIC_API_BASE=http://192.168.31.66:8001
> ```

</details>

**③ Настроить Порты и LLM** *(Опционально)*

- **Порты**: Настройте в `.env` → `BACKEND_PORT` / `FRONTEND_PORT` (по умолчанию: 8001/3782)
- **LLM**: Отредактируйте `config/agents.yaml` → `temperature` / `max_tokens` для каждого модуля
- См. [Документацию по конфигурации](../../config/README.md) для подробностей

**④ Попробовать демо базы знаний** *(Опционально)*

<details>
<summary>📚 <b>Доступные демо</b></summary>

- **Исследовательские Статьи** — 5 статей из нашей лаборатории ([AI-Researcher](https://github.com/HKUDS/AI-Researcher), [LightRAG](https://github.com/HKUDS/LightRAG), и т.д.)
- **Учебник по Науке о Данных** — 8 глав, 296 страниц ([Ссылка на Книгу](https://ma-lab-berkeley.github.io/deep-representation-learning-book/))

</details>

1. Скачать с [Google Drive](https://drive.google.com/drive/folders/1iWwfZXiTuQKQqUYb5fGDZjLCeTUP6DA6?usp=sharing)
2. Распаковать в каталог `data/`

> Демо БЗ используют `text-embedding-3-large` с `dimensions = 3072`

**⑤ Создать собственную базу знаний** *(После Запуска)*

1. Перейдите на http://localhost:3782/knowledge
2. Нажмите "New Knowledge Base" → Введите имя → Загрузите файлы PDF/TXT/MD
3. Следите за прогрессом в терминале

---

### Шаг 2: Выберите метод установки

#### 🐳 Вариант A: Установка через Docker

> Установка Python/Node.js не требуется

**Требования**: [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

**Быстрый старт** — Сборка из исходного кода:

```bash
docker compose up                  # Сборка и запуск (~11 мин при первом запуске на mac mini M4)
docker compose build --no-cache    # Очистка кэша и пересборка после обновления репозитория
```

**Или использовать предварительно собранный образ** (быстрее):

```bash
# Работает на всех платформах — Docker автоматически определяет архитектуру
docker run -d --name deeptutor \
  -p 8001:8001 -p 3782:3782 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config:ro \
  ghcr.io/hkuds/deeptutor:latest

# Windows PowerShell: используйте ${PWD} вместо $(pwd)
```

**Общие команды**:

```bash
docker compose up -d      # Запуск
docker compose down       # Остановка
docker compose logs -f    # Просмотр логов
docker compose up --build # Пересборка после изменений
```

<details>
<summary>📋 <b>Дополнительные параметры Docker</b> (предварительно собранные образы, облачная установка, пользовательские порты)</summary>

**Теги предварительно собранных образов:**

| Тег | Архитектуры | Описание |
|:----|:--------------|:------------|
| `:latest` | AMD64 + ARM64 | Последний стабильный выпуск (автоопределение архитектуры) |
| `:v0.5.x` | AMD64 + ARM64 | Конкретная версия (автоопределение архитектуры) |
| `:v0.5.x-amd64` | Только AMD64 | Явный образ AMD64 |
| `:v0.5.x-arm64` | Только ARM64 | Явный образ ARM64 |

> 💡 Тег `:latest` является **мультиархитектурным образом** — Docker автоматически загружает правильную версию для вашей системы (Intel/AMD или Apple Silicon/ARM)

**Облачная установка** — Необходимо установить внешний URL-адрес API:

```bash
docker run -d --name deeptutor \
  -p 8001:8001 -p 3782:3782 \
  -e NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:8001 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

**Пример пользовательских портов:**

```bash
docker run -d --name deeptutor \
  -p 9001:9001 -p 3000:3000 \
  -e BACKEND_PORT=9001 \
  -e FRONTEND_PORT=3000 \
  -e NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:9001 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

</details>

---

#### 💻 Вариант B: Ручная установка

> Для разработки или сред без Docker

**Требования**: Python 3.10+, Node.js 18+

**1. Настройка окружения**:

```bash
# Использование conda (Рекомендуется)
conda create -n deeptutor python=3.10 && conda activate deeptutor

# Или использование venv
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
```

**2. Установка зависимостей**:

```bash
# Установка в один клик (Рекомендуется)
python scripts/install_all.py
# Или: bash scripts/install_all.sh

# Или ручная установка
pip install -r requirements.txt
npm install --prefix web
```

**3. Запуск**:

```bash
python scripts/start_web.py    # Запуск интерфейса и бэкенда
# Или: python scripts/start.py  # Только CLI
# Остановка: Ctrl+C
```

<details>
<summary>🔧 <b>Запуск интерфейса и бэкенда отдельно</b></summary>

**Бэкенд** (FastAPI):
```bash
python -m deeptutor.api.run_server
# Или: uvicorn deeptutor.api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Интерфейс** (Next.js):
```bash
cd web && npm install && npm run dev -- -p 3782
```

**Примечание**: Создайте `web/.env.local`:
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

| Сервис | Порт по умолчанию |
|:---:|:---:|
| Бэкенд | `8001` |
| Интерфейс | `3782` |

</details>

### URLs Доступа

| Сервис | URL | Описание |
|:---:|:---|:---|
| **Frontend** | http://localhost:3782 | Основной веб-интерфейс |
| **Документация API** | http://localhost:8001/docs | Интерактивная документация API |

---

## 📂 Хранение данных

Все пользовательские данные и системные данные хранятся в каталоге `data/`:

```
data/
├── knowledge_bases/              # Хранилище базы знаний
└── user/                         # Данные пользовательской активности
    ├── solve/                    # Результаты решения проблем и артефакты
    ├── question/                 # Сгенерированные вопросы
    ├── research/                 # Отчеты об исследованиях и кэш
    ├── co-writer/                # Интерактивные документы IdeaGen и аудиофайлы
    ├── notebook/                 # Записи блокнотов и метаданные
    ├── guide/                    # Сеансы руководства обучением
    ├── logs/                     # Системные логи
    └── run_code_workspace/       # Рабочее пространство выполнения кода
```

Результаты автоматически сохраняются во время всех действий. Каталоги создаются автоматически по мере необходимости.

## 📦 Основные модули

<details>
<summary><b>🧠 Умный решатель</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура умного решателя](../../assets/figs/solve.png)

</details>

> **Интеллектуальная система решения проблем** на основе двухконтурной архитектуры **Анализ + Решение**, поддерживающая многорежимные рассуждения и динамическое извлечение знаний.

**Основные особенности**

| Feature | Description |
|:---:|:---|
| Двухконтурная архитектура | **Контур анализа**: InvestigateAgent → NoteAgent<br>**Контур решения**: PlanAgent → ManagerAgent → SolveAgent → CheckAgent → Format |
| Совместная работа нескольких агентов | Специализированные агенты: InvestigateAgent, NoteAgent, PlanAgent, ManagerAgent, SolveAgent, CheckAgent |
| Потоковая передача в реальном времени | Передача через WebSocket с отображением процесса рассуждения в реальном времени |
| Интеграция инструментов | RAG (наивный/гибридный), веб-поиск, элемент запроса, выполнение кода |
| Постоянная память | Файлы памяти на основе JSON для сохранения контекста |
| Управление цитированием | Структурированные цитаты с отслеживанием ссылок |

**Использование**

1. Перейдите на http://localhost:{frontend_port}/solver
2. Выберите базу знаний
3. Введите свой вопрос, нажмите "Solve"
4. Наблюдайте за процессом рассуждения в реальном времени и окончательный ответ

<details>
<summary><b>Python API</b></summary>

```python
import asyncio
from deeptutor.agents.solve import MainSolver

async def main():
    solver = MainSolver(kb_name="ai_textbook")
    result = await solver.solve(
        question="Calculate the linear convolution of x=[1,2,3] and h=[4,5]",
        mode="auto"
    )
    print(result['formatted_solution'])

asyncio.run(main())
```

</details>

<details>
<summary><b>Местоположение вывода</b></summary>

```
data/user/solve/solve_YYYYMMDD_HHMMSS/
├── investigate_memory.json    # Память контура анализа
├── solve_chain.json           # Шаги контура решения и записи инструментов
├── citation_memory.json       # Управление цитированием
├── final_answer.md            # Окончательное решение (Markdown)
├── performance_report.json    # Мониторинг производительности
└── artifacts/                 # Вывод выполнения кода
```

</details>

</details>

---

<details>
<summary><b>📝 Генератор вопросов</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура генератора вопросов](../../assets/figs/question-gen.png)

</details>

> **Система генерации вопросов в двух режимах**, поддерживающая **пользовательскую генерацию на основе знаний** и **имитацию эталонных экзаменационных работ** с автоматической проверкой.

**Основные особенности**

| Feature | Description |
|:---:|:---|
| Пользовательский режим | **Фоновые знания** → **Планирование вопросов** → **Генерация** → **Однократная проверка**<br>Анализирует релевантность вопросов без логики отклонения |
| Режим имитации | **Загрузка PDF** → **Парсинг MinerU** → **Извлечение вопросов** → **Имитация стиля**<br>Генерирует вопросы на основе структуры эталонного экзамена |
| Движок ReAct | QuestionGenerationAgent с автономным принятием решений (think → act → observe) |
| Анализ проверки | Однократный анализ релевантности с `kb_coverage` и `extension_points` |
| Типы вопросов | Multiple choice, fill-in-the-blank, calculation, written response, etc. |
| Пакетная генерация | Parallel processing with progress tracking |
| Complete Persistence | All intermediate files saved (background knowledge, plan, individual results) |
| Timestamped Output | Mimic mode creates batch folders: `mimic_YYYYMMDD_HHMMSS_{pdf_name}/` |

**Использование**

**Пользовательский режим:**
1. Перейдите на http://localhost:{frontend_port}/question
2. Заполните требования (topic, difficulty, question type, count)
3. Нажмите "Generate Questions"
4. Просмотрите сгенерированные вопросы с отчетами о проверке

**Режим имитации:**
1. Перейдите на http://localhost:{frontend_port}/question
2. Переключитесь на вкладку "Mimic Exam"
3. Загрузите PDF или укажите каталог разобранного экзамена
4. Дождитесь разбора → извлечения → генерации
5. Просмотрите сгенерированные вопросы рядом с оригинальными ссылками

<details>
<summary><b>Python API</b></summary>

**Пользовательский режим - Полный конвейер:**
```python
import asyncio
from deeptutor.agents.question import AgentCoordinator

async def main():
    coordinator = AgentCoordinator(
        kb_name="ai_textbook",
        output_dir="data/user/question"
    )

    # Генерация нескольких вопросов из текстового требования
    result = await coordinator.generate_questions_custom(
        requirement_text="Generate 3 medium-difficulty questions about deep learning basics",
        difficulty="medium",
        question_type="choice",
        count=3
    )

    print(f"✅ Generated {result['completed']}/{result['requested']} questions")
    for q in result['results']:
        print(f"- Relevance: {q['validation']['relevance']}")

asyncio.run(main())
```

**Режим имитации - Загрузка PDF:**
```python
from deeptutor.agents.question.tools.exam_mimic import mimic_exam_questions

result = await mimic_exam_questions(
    pdf_path="exams/midterm.pdf",
    kb_name="calculus",
    output_dir="data/user/question/mimic_papers",
    max_questions=5
)

print(f"✅ Generated {result['successful_generations']} questions")
print(f"Output: {result['output_file']}")
```

</details>

<details>
<summary><b>Местоположение вывода</b></summary>

**Пользовательский режим:**
```
data/user/question/custom_YYYYMMDD_HHMMSS/
├── background_knowledge.json      # Результаты извлечения RAG
├── question_plan.json              # Планирование вопросов
├── question_1_result.json          # Индивидуальные результаты вопросов
├── question_2_result.json
└── ...
```

**Режим имитации:**
```
data/user/question/mimic_papers/
└── mimic_YYYYMMDD_HHMMSS_{pdf_name}/
    ├── {pdf_name}.pdf                              # Оригинальный PDF
    ├── auto/{pdf_name}.md                          # Разобранный markdown MinerU
    ├── {pdf_name}_YYYYMMDD_HHMMSS_questions.json  # Извлеченные вопросы
    └── {pdf_name}_YYYYMMDD_HHMMSS_generated_questions.json  # Сгенерированные вопросы
```

</details>

</details>

---

<details>
<summary><b>🎓 Руководство по обучению</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура руководства по обучению](../../assets/figs/guide.png)

</details>

> **Персонализированная система обучения** на основе содержимого блокнота, автоматически генерирующая прогрессивные учебные пути через интерактивные страницы и умный Q&A.

**Основные особенности**

| Feature | Description |
|:---:|:---|
| Многоагентная архитектура | **LocateAgent**: Определяет 3-5 прогрессивных точек знаний<br>**InteractiveAgent**: Преобразует в визуальные HTML-страницы<br>**ChatAgent**: Обеспечивает контекстный Q&A<br>**SummaryAgent**: Генерирует сводки обучения |
| Умное определение знаний | Автоматический анализ содержимого блокнота |
| Интерактивные страницы | Генерация HTML-страниц с исправлением ошибок |
| Умный Q&A | Ответы с учетом контекста с объяснениями |
| Отслеживание прогресса | Статус в реальном времени с сохранением сеанса |
| Поддержка нескольких блокнотов | Выбор записей из нескольких блокнотов |

**Рабочий процесс использования**

1. **Выбор блокнота(ов)** — Выберите один или несколько блокнотов (cross-notebook selection supported)
2. **Генерация учебного плана** — LocateAgent определяет 3-5 основных точек знаний
3. **Начало обучения** — InteractiveAgent генерирует визуализацию HTML
4. **Интерактивное обучение** — Задавайте вопросы, нажмите "Next" для продолжения
5. **Завершение обучения** — SummaryAgent генерирует сводку обучения

<details>
<summary><b>Местоположение вывода</b></summary>

```
data/user/guide/
└── session_{session_id}.json    # Полное состояние сеанса, точки знаний, история чата
```

</details>

</details>

---

<details>
<summary><b>✏️ Интерактивная генерация идей (Co-Writer)</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура интерактивной генерации идей](../../assets/figs/co-writer.png)

</details>

> **Интеллектуальный редактор Markdown**, поддерживающий написание с помощью ИИ, автоматическую аннотацию и озвучивание текста.

**Основные особенности**

| Feature | Description |
|:---:|:---|
| Rich Text Editing | Full Markdown syntax support with live preview |
| EditAgent | **Rewrite**: Custom instructions with optional RAG/web context<br>**Shorten**: Compress while preserving key information<br>**Expand**: Add details and context |
| Auto-Annotation | Automatic key content identification and marking |
| NarratorAgent | Script generation, TTS audio, multiple voices (Cherry, Stella, Annie, Cally, Eva, Bella) |
| Context Enhancement | Optional RAG or web search for additional context |
| Multi-Format Export | Markdown, PDF, etc. |

**Использование**

1. Перейдите на http://localhost:{frontend_port}/co_writer
2. Введите или вставьте текст в редактор
3. Используйте функции ИИ: Rewrite, Shorten, Expand, Auto Mark, Narrate
4. Экспорт в Markdown или PDF

<details>
<summary><b>Местоположение вывода</b></summary>

```
data/user/co-writer/
├── audio/                    # Аудиофайлы TTS
│   └── {operation_id}.mp3
├── tool_calls/               # История вызовов инструментов
│   └── {operation_id}_{tool_type}.json
└── history.json              # История редактирования
```

</details>

</details>

---

<details>
<summary><b>🔬 Глубокие исследования</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура глубоких исследований](../../assets/figs/deepresearch.png)

</details>

> **DR-in-KG** (Глубокие исследования в графе знаний) — Систематическая система глубоких исследований на основе архитектуры **Динамическая очередь тем**, позволяющая совместную работу нескольких агентов в три фазы: **Планирование → Исследование → Отчетность**.

**Основные особенности**

| Особенность | Описание |
|:---:|:---|
| Трехфазная архитектура | **Фаза 1 (Планирование)**: RephraseAgent (оптимизация темы) + DecomposeAgent (декомпозиция подтем)<br>**Фаза 2 (Исследование)**: ManagerAgent (планирование очереди) + ResearchAgent (принятие решений об исследованиях) + NoteAgent (сжатие информации)<br>**Фаза 3 (Отчетность)**: Дедупликация → Генерация структуры из трех уровней → Написание отчета с цитатами |
| Динамическая очередь тем | Основная система планирования с управлением состоянием TopicBlock: `PENDING → RESEARCHING → COMPLETED/FAILED`. Поддерживает динамическое обнаружение тем во время исследования |
| Режимы выполнения | **Последовательный режим**: Последовательная обработка тем<br>**Параллельный режим**: Одновременная обработка нескольких тем с `AsyncCitationManagerWrapper` для потокобезопасных операций |
| Интеграция нескольких инструментов | **RAG** (гибридный/наивный), **Поиск по запросу** (поиск сущностей), **Поиск статей**, **Веб-поиск**, **Выполнение кода** — динамически выбирается ResearchAgent |
| Единая система цитирования | Централизованный CitationManager как единый источник истины для генерации ID цитирования, сопоставления ref_number и дедупликации |
| Предустановленные конфигурации | **quick**: Быстрое исследование (1-2 подтемы, 1-2 итерации)<br>**medium/standard**: Сбалансированная глубина (5 подтем, 4 итерации)<br>**deep**: Тщательное исследование (8 подтем, 7 итераций)<br>**auto**: Агент самостоятельно решает глубину |

**Архитектура системы цитирования**

Система цитирования следует централизованному дизайну с CitationManager как единым источником истины:

```
┌─────────────────────────────────────────────────────────────────┐
│                      CitationManager                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Генерация ID   │  │  Карта ref_number│  │   Дедупликация  │  │
│  │  PLAN-XX        │  │  citation_id →  │  │   (только статьи)│  │
│  │  CIT-X-XX       │  │  ref_number     │  │                 │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
     ┌──────┴──────┐      ┌──────┴──────┐      ┌──────┴──────┐
     │DecomposeAgent│      │ReportingAgent│      │ Раздел     │
     │ ResearchAgent│      │ (inline [N]) │      │ Ссылок     │
     │  NoteAgent   │      └─────────────┘      └────────────┘
     └─────────────┘
```

| Компонент | Описание |
|:---:|:---|
| Формат ID | **PLAN-XX** (запросы RAG на этапе планирования) + **CIT-X-XX** (этап исследований, X=номер блока) |
| Сопоставление ref_number | Последовательные номера, начинающиеся с 1, созданные из отсортированных ID цитирования, с дедупликацией статей |
| Встроенные цитаты | Простой формат `[N]` в выводе LLM, пост-обработка в кликабельные ссылки `[[N]](#ref-N)` |
| Таблица цитирования | Четкая таблица ссылок, предоставленная LLM: `Цитировать как [1] → (RAG) предпросмотр запроса...` |
| Пост-обработка | Автоматическое преобразование формата + проверка для удаления недействительных ссылок на цитаты |
| Параллельная безопасность | Потокобезопасные асинхронные методы (`get_next_citation_id_async`, `add_citation_async`) для параллельного выполнения |

**Архитектура параллельного выполнения**

Когда включено `execution_mode: "parallel"`, несколько блоков тем исследуются одновременно:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Параллельное выполнение исследований                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DynamicTopicQueue                    AsyncCitationManagerWrapper      │
│   ┌─────────────────┐                  ┌─────────────────────────┐      │
│   │ Тема 1 (PENDING)│ ──┐             │  Потокобезопасная       │      │
│   │ Тема 2 (PENDING)│ ──┼──→ asyncio  │  обертка для            │      │
│   │ Тема 3 (PENDING)│ ──┤   Semaphore │                         │      │
│   │ Тема 4 (PENDING)│ ──┤   (max=5)   │  • get_next_citation_   │      │
│   │ Тема 5 (PENDING)│ ──┘             │    id_async()           │      │
│   └─────────────────┘                  │  • add_citation_async() │      │
│            │                           └───────────┬─────────────┘      │
│            ▼                                       │                    │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │              Задачи параллельных ResearchAgent               │      │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │      │
│   │  │ Задача 1│  │ Задача 2│  │ Задача 3│  │ Задача 4│  ...   │      │
│   │  │(Тема 1) │  │(Тема 2) │  │(Тема 3) │  │(Тема 4) │        │      │
│   │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │      │
│   │       │            │            │            │              │      │
│   │       └────────────┴────────────┴────────────┘              │      │
│   │                         │                                    │      │
│   │                         ▼                                    │      │
│   │              AsyncManagerAgentWrapper                        │      │
│   │              (Обновления очереди, безопасные для потоков)    │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

| Компонент | Описание |
|:---:|:---|
| `asyncio.Semaphore` | Ограничивает количество одновременных задач до `max_parallel_topics` (по умолчанию: 5) |
| `AsyncCitationManagerWrapper` | Оборачивает CitationManager с `asyncio.Lock()` для потокобезопасной генерации ID |
| `AsyncManagerAgentWrapper` | Обеспечивает атомарность обновлений состояния очереди в параллельных задачах |
| Отслеживание прогресса в реальном времени | Отображение всех активных задач исследования с индикаторами состояния |

**Обязанности агентов**

| Агент | Фаза | Обязанности |
|:---:|:---:|:---|
| RephraseAgent | Планирование | Оптимизация входной темы пользователя, поддержка многораундового взаимодействия пользователя для уточнения |
| DecomposeAgent | Планирование | Декомпозиция темы на подтемы с контекстом RAG, получение ID цитирования из CitationManager |
| ManagerAgent | Исследование | Управление состоянием очереди, планирование задач, динамическое добавление тем |
| ResearchAgent | Исследование | Проверка достаточности знаний, планирование запросов, выбор инструментов, запрос ID цитирования перед каждым вызовом инструмента |
| NoteAgent | Исследование | Сжатие необработанных выходных данных инструментов в сводки, создание ToolTraces с заранее назначенными ID цитирования |
| ReportingAgent | Отчетность | Построение карты цитирования, генерация структуры из трех уровней, написание разделов отчета с таблицами цитирования, пост-обработка цитирований |

**Конвейер генерации отчетов**

```
1. Построить карту цитирования →  CitationManager.build_ref_number_map()
2. Генерация структуры →  Трехуровневые заголовки (H1 → H2 → H3)
3. Написание разделов →  LLM использует [N] цитирования с предоставленной таблицей цитирования
4. Пост-обработка →  Преобразование [N] → [[N]](#ref-N), проверка ссылок
5. Генерация списка литературы →  Стилизованные академические записи с раскрывающимися деталями источника
```

**Использование**

1. Посетите http://localhost:{frontend_port}/research
2. Введите тему исследования
3. Выберите режим исследования (quick/medium/deep/auto)
4. Наблюдайте за прогрессом в реальном времени с параллельным/последовательным выполнением
5. Просмотрите структурированный отчет с кликабельными встроенными цитатами
6. Экспортируйте в Markdown или PDF (с правильным разделением страниц и поддержкой диаграмм Mermaid)

<details>
<summary><b>CLI</b></summary>

```bash
# Режим быстрого (быстрое исследование)
python -m deeptutor.agents.research.main --topic "Основы глубокого обучения" --preset quick

# Режим среднего (сбалансированный)
python -m deeptutor.agents.research.main --topic "Архитектура Transformer" --preset medium

# Режим глубокого (тщательное исследование)
python -m deeptutor.agents.research.main --topic "Графовые нейронные сети" --preset deep

# Режим авто (агент решает глубину)
python -m deeptutor.agents.research.main --topic "Обучение с подкреплением" --preset auto
```

</details>

<details>
<summary><b>Python API</b></summary>

```python
import asyncio
from deeptutor.agents.research import ResearchPipeline
from deeptutor.core.core import get_llm_config, load_config_with_main

async def main():
    # Загрузка конфигурации (main.yaml объединяется с любыми модульными переопределениями)
    config = load_config_with_main("research_config.yaml")
    llm_config = get_llm_config()

    # Создание конвейера (параметры агента загружаются из agents.yaml автоматически)
    pipeline = ResearchPipeline(
        config=config,
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"],
        kb_name="ai_textbook"  # Необязательно: переопределить базу знаний
    )

    # Запуск исследования
    result = await pipeline.run(topic="Механизмы внимания в глубоком обучении")
    print(f"Отчет сохранен в: {result['final_report_path']}")

asyncio.run(main())
```

</details>

<details>
<summary><b>Местоположение вывода</b></summary>

```
data/user/research/
├── reports/                          # Окончательные отчеты о исследованиях
│   ├── research_YYYYMMDD_HHMMSS.md   # Markdown-отчет с кликабельными цитатами [[N]](#ref-N)
│   └── research_*_metadata.json      # Метаданные и статистика исследований
└── cache/                            # Кэш процесса исследования
    └── research_YYYYMMDD_HHMMSS/
        ├── queue.json                # Состояние DynamicTopicQueue (TopicBlocks + ToolTraces)
        ├── citations.json            # Реестр цитирования с ID-счетчиками и сопоставлением ref_number
        │                             #   - citations: {citation_id: citation_info}
        │                             #   - counters: {plan_counter, block_counters}
        ├── step1_planning.json       # Результаты фазы планирования (подтемы + PLAN-XX цитаты)
        ├── planning_progress.json    # События прогресса планирования
        ├── researching_progress.json # События прогресса исследования
        ├── reporting_progress.json   # События прогресса отчетности
        ├── outline.json              # Трехуровневая структура отчета
        └── token_cost_summary.json   # Статистика использования токенов
```

**Структура файла цитирования** (`citations.json`):
```json
{
  "research_id": "research_20241209_120000",
  "citations": {
    "PLAN-01": {"citation_id": "PLAN-01", "tool_type": "rag_hybrid", "query": "...", "summary": "..."},
    "CIT-1-01": {"citation_id": "CIT-1-01", "tool_type": "paper_search", "papers": [...], ...}
  },
  "counters": {
    "plan_counter": 2,
    "block_counters": {"1": 3, "2": 2}
  }
}
```

</details>

<details>
<summary><b>Параметры конфигурации</b></summary>

Key configuration in `config/main.yaml` (research section) and `config/agents.yaml`:

```yaml
# config/agents.yaml - Параметры LLM агента
research:
  temperature: 0.5
  max_tokens: 12000

# config/main.yaml - Настройки исследования
research:
  # Режим выполнения
  researching:
    execution_mode: "parallel"    # "series" или "parallel"
    max_parallel_topics: 5        # Максимальное количество одновременных тем
    max_iterations: 5             # Максимальное количество итераций на тему

  # Переключатели инструментов
    enable_rag_hybrid: true       # Извлечение гибридного RAG
    enable_rag_naive: true        # Базовое извлечение RAG
    enable_paper_search: true     # Поиск научных статей
    enable_web_search: true       # Веб-поиск (также контролируется через tools.web_search.enabled)
    enable_run_code: true         # Выполнение кода

  # Ограничения очереди
  queue:
    max_length: 5                 # Максимальное количество тем в очереди

  # Отчетность
  reporting:
    enable_inline_citations: true # Включить кликабельные [N] цитаты в отчете

  # Предустановки: quick, medium, deep, auto

# Глобальные переключатели инструментов в разделе инструментов
tools:
  web_search:
    enabled: true                 # Глобальный переключатель веб-поиска (более высокий приоритет)
```

</details>

</details>

---

<details>
<summary><b>💡 Автоматическая генерация идей</b></summary>

<details>
<summary><b>Диаграмма архитектуры</b></summary>

![Архитектура автоматической генерации идей](../../assets/figs/ideagen.png)

</details>

> **Система генерации исследовательских идей**, извлекающая точки знаний из записей блокнота и генерирующая исследовательские идеи через многоступенчатую фильтрацию.

**Основные особенности**

| Feature | Description |
|:---:|:---|
| MaterialOrganizerAgent | Извлекает точки знаний из записей блокнота |
| Multi-Stage Filtering | **Loose Filter** → **Explore Ideas** (5+ per point) → **Strict Filter** → **Generate Markdown** |
| Idea Exploration | Innovative thinking from multiple dimensions |
| Structured Output | Organized markdown with knowledge points and ideas |
| Progress Callbacks | Real-time updates for each stage |

**Использование**

1. Посетите http://localhost:{frontend_port}/ideagen
2. Выберите блокнот с записями
3. При необходимости укажите мысли/предпочтения пользователя
4. Нажмите "Generate Ideas"
5. Просмотрите сгенерированные исследовательские идеи, организованные по точкам знаний

<details>
<summary><b>Python API</b></summary>

```python
import asyncio
from deeptutor.agents.ideagen import IdeaGenerationWorkflow, MaterialOrganizerAgent
from deeptutor.core.core import get_llm_config

async def main():
    llm_config = get_llm_config()

    # Шаг 1: Извлечение точек знаний из материалов
    organizer = MaterialOrganizerAgent(
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"]
    )
    knowledge_points = await organizer.extract_knowledge_points(
        "Ваш учебный материал или содержимое блокнота здесь"
    )

    # Шаг 2: Генерация исследовательских идей
    workflow = IdeaGenerationWorkflow(
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"]
    )
    result = await workflow.process(knowledge_points)
    print(result)  # Идеи исследований в формате Markdown

asyncio.run(main())
```

</details>

</details>

---

<details>
<summary><b>📊 Панель управления + Управление базой знаний</b></summary>

> **Единый вход в систему**, обеспечивающий отслеживание активности, управление базой знаний и мониторинг состояния системы.

**Ключевые особенности**

| Особенность | Описание |
|:---:|:---|
| Статистика активности | Недавние записи решения/генерации/исследования |
| Обзор базы знаний | Список БЗ, статистика, инкрементальные обновления |
| Статистика блокнотов | Количество блокнотов, распределение записей |
| Быстрые действия | Доступ к модулям в один клик |

**Использование**

- **Веб-интерфейс**: Посетите http://localhost:{frontend_port} для просмотра обзора системы
- **Создать KB**: Нажмите "New Knowledge Base", загрузите документы PDF/Markdown
- **Просмотреть активность**: Проверьте последние учебные мероприятия на панели мониторинга

</details>

---

<details>
<summary><b>📓 Блокнот</b></summary>

> **Унифицированное управление учебными записями**, соединяющее выводы из всех модулей для создания персонализированной базы знаний обучения.

**Основные особенности**

| Особенность | Описание |
|:---:|:---|
| Управление несколькими блокнотами | Создание, редактирование, удаление блокнотов |
| Единое хранилище записей | Интеграция записей решения/генерации/исследования/интерактивной генерации идей |
| Теги категоризации | Автоматическая категоризация по типу, базе знаний |
| Пользовательское оформление | Персонализация цвета, значков |

**Использование**

1. Посетите http://localhost:{frontend_port}/notebook
2. Создайте новый блокнот (установите имя, описание, цвет, значок)
3. После выполнения задач в других модулях нажмите "Add to Notebook"
4. Просмотрите и управляйте всеми записями на странице блокнота

</details>

---

### 📖 Документация модуля

<table>
<tr>
<td align="center"><a href="config/README.md">Конфигурация</a></td>
<td align="center"><a href="data/README.md">Каталог данных</a></td>
<td align="center"><a href="deeptutor/api/">API Backend</a></td>
<td align="center"><a href="deeptutor/core/README.md">Основные утилиты</a></td>
</tr>
<tr>
<td align="center"><a href="deeptutor/knowledge/">База знаний</a></td>
<td align="center"><a href="deeptutor/tools/README.md">Инструменты</a></td>
<td align="center"><a href="web/README.md">Веб-интерфейс</a></td>
<td align="center"><a href="deeptutor/agents/solve/">Модуль решения</a></td>
</tr>
<tr>
<td align="center"><a href="deeptutor/agents/question/">Модуль вопросов</a></td>
<td align="center"><a href="deeptutor/agents/research/">Модуль исследования</a></td>
<td align="center"><a href="deeptutor/agents/co_writer/">Модуль интерактивной генерации идей</a></td>
<td align="center"><a href="deeptutor/agents/guide/">Модуль руководства</a></td>
</tr>
<tr>
<td align="center" colspan="4"><a href="deeptutor/agents/ideagen/">Модуль автоматической генерации идей</a></td>
</tr>
</table>

## ❓ Часто задаваемые вопросы

<details>
<summary><b>Не удается запустить backend?</b></summary>

**Контрольный список**
- Подтвердите версию Python >= 3.10
- Подтвердите установку всех зависимостей: `pip install -r requirements.txt`
- Проверьте, используется ли порт 8001
- Проверьте конфигурацию файла `.env`

**Решения**
- **Изменить порт**: Установите `BACKEND_PORT=9001` в файле `.env`
- **Проверить логи**: Просмотрите сообщения об ошибках в терминале

</details>

<details>
<summary><b>Порт занят после Ctrl+C?</b></summary>

**Проблема**

После нажатия Ctrl+C во время выполнения задачи (например, глубокое исследование) при повторном запуске появляется ошибка "порт уже используется".

**Причина**

Ctrl+C иногда завершает только процесс frontend, в то время как backend продолжает работать в фоновом режиме.

**Решение**

```bash
# macOS/Linux: Найти и убить процесс
lsof -i :8001
kill -9 <PID>

# Windows: Найти и убить процесс
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

Затем перезапустите сервис с помощью `python scripts/start_web.py`.

</details>

<details>
<summary><b>Ошибка npm: command not found?</b></summary>

**Проблема**

Запуск `scripts/start_web.py` показывает `npm: command not found` или статус выхода 127.

**Контрольный список**
- Проверьте, установлен ли npm: `npm --version`
- Проверьте, установлен ли Node.js: `node --version`
- Подтвердите активацию среды conda (если используется conda)

**Решения**
```bash
# Вариант A: Использование Conda (рекомендуется)
conda install -c conda-forge nodejs

# Вариант B: Использование официального установщика
# Загрузка с https://nodejs.org/

# Вариант C: Использование nvm
nvm install 18
nvm use 18
```

**Проверка установки**
```bash
node --version  # Должно показывать v18.x.x или выше
npm --version   # Должно показывать номер версии
```

</details>

<details>
<summary><b>Проблемы с длинными именами файлов при установке в Windows?</b></summary>

**Проблема**

В Windows вы можете столкнуться с ошибками, связанными с длинными путями файлов во время установки, такими как "Имя файла или расширение слишком длинное" или аналогичные проблемы с длиной пути.

**Причина**

Windows имеет ограничение по умолчанию на длину пути (260 символов), которое может быть превышено из-за вложенной структуры каталогов и зависимостей DeepTutor.

**Решение**

Включите поддержку длинных путей в системе, выполнив следующую команду в командной строке от имени администратора:

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

После выполнения этой команды перезапустите терминал, чтобы изменения вступили в силу.

</details>

<details>
<summary><b>Frontend не может подключиться к backend?</b></summary>

**Контрольный список**
- Подтвердите, что backend запущен (посетите http://localhost:8001/docs)
- Проверьте консоль браузера на наличие сообщений об ошибках

**Решение**

Создайте `.env.local` в каталоге `web`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

</details>

<details>
<summary><b>Docker: Frontend не может подключиться при облачном развертывании?</b></summary>

**Проблема**

При развертывании на облачном сервере интерфейс показывает ошибки подключения, такие как "Не удалось получить данные" или "NEXT_PUBLIC_API_BASE не настроен".

**Причина**

Стандартный URL API - `localhost:8001`, который указывает на локальную машину пользователя в браузере, а не на ваш сервер.

**Решение**

Установите переменную окружения `NEXT_PUBLIC_API_BASE_EXTERNAL` на публичный URL вашего сервера:

```bash
# Использование docker run
docker run -d --name deeptutor \
  -e NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:8001 \
  ... другие параметры ...
  ghcr.io/hkuds/deeptutor:latest

# Или в файле .env
NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:8001
```

**Пример пользовательского порта:**
```bash
# Если используется порт бэкенда 9001
-e BACKEND_PORT=9001 \
-e NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:9001
```

</details>

<details>
<summary><b>Docker: Как использовать пользовательские порты?</b></summary>

**Решение**

Установите как переменные окружения портов, так и сопоставления портов:

```bash
docker run -d --name deeptutor \
  -p 9001:9001 -p 4000:4000 \
  -e BACKEND_PORT=9001 \
  -e FRONTEND_PORT=4000 \
  -e NEXT_PUBLIC_API_BASE_EXTERNAL=http://localhost:9001 \
  ... другие переменные окружения ...
  ghcr.io/hkuds/deeptutor:latest
```

**Важно**: Сопоставление портов `-p` должно соответствовать значениям `BACKEND_PORT`/`FRONTEND_PORT`.

</details>

<details>
<summary><b>Соединение WebSocket не удается?</b></summary>

**Контрольный список**
- Подтвердите, что backend запущен
- Проверьте настройки брандмауэра
- Подтвердите правильность URL-адреса WebSocket

**Решение**
- **Проверьте логи backend**
- **Подтвердите формат URL**: `ws://localhost:8001/api/v1/...`

</details>

<details>
<summary><b>На странице настроек отображается "Ошибка загрузки данных" при использовании HTTPS обратного прокси?</b></summary>

**Проблема**

При развертывании за HTTPS обратным прокси (например, nginx), на странице настроек отображается "Ошибка загрузки данных", и инструменты разработчика браузера показывают, что HTTPS-запросы перенаправляются на HTTP (307 редирект).

**Причина**

Эта проблема была исправлена в версии v0.5.0+. Если вы используете более старую версию, проблема была вызвана автоматическими перенаправлениями с завершающей косой чертой от FastAPI, которые генерировали HTTP URL-адреса вместо сохранения исходного протокола HTTPS.

**Решение (для v0.5.0+)**

Обновитесь до последней версии. Исправление отключает автоматические перенаправления с косой чертой, чтобы предотвратить понижение протокола.

**Рекомендуемая конфигурация nginx**

При использовании nginx в качестве HTTPS обратного прокси используйте следующую конфигурацию:

```nginx
# Фронтенд
location / {
    proxy_pass http://localhost:3782;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# API бэкенда
location /api/ {
    proxy_pass http://localhost:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;  # Важно: сохраняет исходный протокол
}

# Поддержка WebSocket
location /api/v1/ {
    proxy_pass http://localhost:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Переменная окружения**

Установите в `.env`:
```bash
NEXT_PUBLIC_API_BASE=https://your-domain.com:port
```

См.: [GitHub Issue #112](https://github.com/HKUDS/DeepTutor/issues/112)

</details>

<details>
<summary><b>Где хранятся выходные данные модуля?</b></summary>

| Модуль | Путь вывода |
|:---:|:---|
| Решение | `data/user/solve/solve_YYYYMMDD_HHMMSS/` |
| Вопросы | `data/user/question/question_YYYYMMDD_HHMMSS/` |
| Исследование | `data/user/research/reports/` |
| Интерактивная генерация идей | `data/user/co-writer/` |
| Блокнот | `data/user/notebook/` |
| Руководство | `data/user/guide/session_{session_id}.json` |
| Логи | `data/user/logs/` |

</details>

<details>
<summary><b>Как добавить новую базу знаний?</b></summary>

**Веб-интерфейс**
1. Посетите http://localhost:{frontend_port}/knowledge
2. Нажмите "New Knowledge Base"
3. Введите имя базы знаний
4. Загрузите документы PDF/TXT/MD
5. Система будет обрабатывать документы в фоновом режиме

**CLI**
```bash
deeptutor kb create <kb_name> --doc <pdf_path>
```

</details>

<details>
<summary><b>Как постепенно добавлять документы в существующую БЗ?</b></summary>

**CLI (рекомендуется)**
```bash
python -m deeptutor.knowledge.add_documents <kb_name> --docs <new_document.pdf>
```

**Преимущества**
- Обрабатывает только новые документы, экономит время и стоимость API
- Автоматически объединяет с существующим графом знаний
- Сохраняет все существующие данные

</details>

<details>
<summary><b>Ошибка uvloop.Loop при извлечении пронумерованных элементов?</b></summary>

**Проблема**

При инициализации базы знаний вы можете столкнуться с этой ошибкой:
```
ValueError: Can't patch loop of type <class 'uvloop.Loop'>
```

Это происходит потому, что Uvicorn по умолчанию использует цикл событий `uvloop`, который несовместим с `nest_asyncio`.

**Решение**

Используйте один из следующих методов для извлечения нумерованных элементов:

```bash
# Вариант 1: Использование shell-скрипта (рекомендуется)
# Deprecated: numbered-item extraction was removed

# Вариант 2: Прямая команда Python
# Deprecated: numbered-item extraction was removed
```

Это извлечет нумерованные элементы (Определения, Теоремы, Уравнения и т.д.) из вашей базы знаний без повторной инициализации.

</details>


</div>

## ⭐ История звезд

<div align="center">

<p>
  <a href="https://github.com/HKUDS/DeepTutor/stargazers"><img src="../../assets/roster/stargazers.svg" alt="Stargazers"/></a>
  &nbsp;&nbsp;
  <a href="https://github.com/HKUDS/DeepTutor/network/members"><img src="../../assets/roster/forkers.svg" alt="Forkers"/></a>
</p>

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
  </picture>
</a>

</div>

## 🤝 Участие в разработке

<div align="center">

Мы надеемся, что DeepTutor сможет стать подарком для сообщества. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Участники HKUDS/DeepTutor" />
</a>

</div>

## 🔗 Связанные проекты

<div align="center">

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🎨 RAG-Anything](https://github.com/HKUDS/RAG-Anything) | [💻 DeepCode](https://github.com/HKUDS/DeepCode) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) |
|:---:|:---:|:---:|:---:|
| Простой и быстрый RAG | Мультимодальный RAG | Помощник по коду на ИИ | Автоматизация исследований |

**[Лаборатория интеллектуальных данных @ HKU](https://github.com/HKUDS)**

[⭐ Поставьте звезду](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Сообщить об ошибке](https://github.com/HKUDS/DeepTutor/issues) · [💬 Обсуждения](https://github.com/HKUDS/DeepTutor/discussions)

---

Этот проект распространяется под лицензией ***[AGPL-3.0](../../LICENSE)***.

<p align="center">
  <em> Спасибо, что посетили ✨ DeepTutor!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
