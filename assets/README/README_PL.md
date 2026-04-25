<div align="center">

<img src="assets/logo-ver2.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Twój spersonalizowany korepetytor oparty na agentach AI

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/HKUDS/DeepTutor?style=flat-square&color=brightgreen)](https://github.com/HKUDS/DeepTutor/releases)
[![arXiv](https://img.shields.io/badge/arXiv-Coming_Soon-b31b1b?style=flat-square&logo=arxiv&logoColor=white)](#)

[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-00D4AA?style=flat-square&logo=feishu&logoColor=white)](./Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-07C160?style=flat-square&logo=wechat&logoColor=white)](https://github.com/HKUDS/DeepTutor/issues/78)

[Funkcje](#-kluczowe-funkcje) · [Jak zacząć](#-rozpocznij) · [Odkrywaj](#-odkrywaj-deeptutor) · [TutorBoty](#-tutorbot--trwali-autonomiczni-korepetytorzy-ai) · [CLI](#%EF%B8%8F-deeptutor-cli--interfejs-stworzony-dla-agentów) · [Roadmapa](#%EF%B8%8F-harmonogram) · [Społeczność](#-społeczność--ekosystem)

[🇨🇳 中文](assets/README/README_CN.md) · [🇯🇵 日本語](assets/README/README_JA.md) · [🇪🇸 Español](assets/README/README_ES.md) · [🇫🇷 Français](assets/README/README_FR.md) · [🇸🇦 العربية](assets/README/README_AR.md) · [🇷🇺 Русский](assets/README/README_RU.md) · [🇮🇳 हिन्दी](assets/README/README_HI.md) · [🇵🇹 Português](assets/README/README_PT.md) · [🇹🇭 ภาษาไทย](assets/README/README_TH.md) · [🇵🇱 Polski](assets/README/README_PL.md)

</div>

---

> 🤝 **Każda pomoc jest mile widziana!** Zapoznaj się z naszym [Przewodnikiem dla kontrybutorów](CONTRIBUTING.md), aby poznać nasze standardy kodowania, strategię zarządzania gałęziami i dowiedzieć się, jak zacząć.

### 📦 Wydania

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Załączanie dokumentów bezpośrednio na czacie (PDF/DOCX/XLSX/PPTX), podgląd procesu myślowego modelu (reasoning), trzystopniowy przełącznik `send_dimensions` dla wektorów (embeddings), refaktoryzacja rdzenia dostawców LLM, edytor szablonów "Duszy" (Soul), zapisywanie notatek z poziomu Co-Writera, stabilniejsze przeciąganie i upuszczanie (drag & drop) w Bazie Wiedzy oraz lepsze zachowanie języka przy generowaniu pytań.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — Własne Umiejętności (Skills) tworzone przez użytkowników (pełen CRUD i integracja z czatem), potężna optymalizacja wydajności wprowadzania tekstu, automatyczny fallback `response_format` dla niekompatybilnych API, poprawka dla zdalnego dostępu po LAN, oznaczenie wersji na pasku bocznym, wsparcie dla obrazów w trybie Deep Solve, autostart WebSocketów dla TutorBota, nowy interfejs Biblioteki Książek oraz tryb pełnoekranowy dla wizualizacji.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Limity tokenów na etap rozmowy w `agents.yaml` (dla odpowiedzi na 8000 tokenów), opcja regeneracji ostatniej odpowiedzi w CLI / WebSocket / Web UI, naprawa błędu przy braku wektorów (`None`) w RAG, kompatybilność `json_object` dla modeli Gemma oraz lepsza czytelność ciemnych bloków kodu.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Kompilator interaktywnych "żywych książek" oparty na wielu agentach (Book Engine) z 14 typami bloków, przestrzeń robocza Co-Writer do pracy z wieloma dokumentami, interaktywne wizualizacje HTML, oznaczanie (@) Banku Pytań na czacie, faza 2 eksternalizacji promptów oraz całkowicie przeprojektowany pasek boczny.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Zakładka Kanałów oparta na schematach (z ukrywaniem haseł/kluczy), uproszczenie RAG do jednego potoku, poprawa spójności na linii RAG - Baza Wiedzy, eksternalizacja promptów czatu i README w języku tajskim.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — Uniwersalny przycisk "Odpowiedz teraz" dla wszystkich funkcji, synchronizacja przewijania w Co-Writerze, opcja "Zapisz do Notatnika" dla wiadomości, zunifikowany panel ustawień, przycisk zatrzymywania generowania (Stop) i atomowe zapisywanie konfiguracji TutorBota.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Przepisanie parsera bloków matematycznych LaTeX, diagnostyka LLM przez `agents.yaml`, naprawa przekazywania dodatkowych nagłówków HTTP, poprawka UUID przy zapisywaniu notatek oraz nowe wskazówki dla środowisk Docker + lokalne LLM.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Sesje zapisywane w zakładkach na podstawie adresu URL, nowy motyw Śnieg (Snow), heartbeat i automatyczne wznawianie połączeń WebSocket, poprawa wydajności ChatComposera, przebudowa rejestru dostawców wektorów (embeddings) oraz integracja z wyszukiwarką Serper.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Notatnik na pytania z zakładkami i kategoriami, wsparcie dla diagramów Mermaid w Wizualizacjach, wykrywanie niedopasowania wektorów, kompatybilność Qwen/vLLM, wsparcie dla LM Studio i llama.cpp oraz nowy motyw Szkło (Glass).

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Ujednolicenie wyszukiwania z fallbackiem do SearXNG, naprawa przełączania między dostawcami LLM i łatki na wycieki pamięci we frontendzie.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Funkcja Wizualizacji (Chart.js/SVG), zapobieganie powtarzaniu pytań w quizach i obsługa modelu o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Śledzenie postępu wektoryzacji (z automatycznym ponawianiem przy limitach zapytań), wieloplatformowe poprawki zależności i naprawa walidacji typów MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — Przejście na natywne SDK OpenAI i Anthropic (rezygnacja z litellm), obsługa Math Animator dla Windows, niezawodne parsowanie JSON-ów i pełne tłumaczenie na język chiński.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Przeładowywanie ustawień "w locie" (hot-reload), zagnieżdżone wyniki z MinerU, łatki dla WebSocketów i podniesienie wymagań do Pythona 3.11+.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Całkowicie nowa architektura oparta na agentach (~200 tys. linii kodu): System wtyczek dla Narzędzi i Umiejętności, nowe CLI i SDK, TutorBot, Co-Writer, Przewodnik Nauki (Guided Learning) oraz długoterminowa pamięć.

<details>
<summary><b>Poprzednie wydania</b></summary>

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Pamięć sesji, przyrostowe przesyłanie dokumentów, elastyczny import do RAG i pełne wsparcie języka chińskiego.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Integracja z Docling (RAG-Anything), optymalizacja logów i paczka mniejszych poprawek.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Centralna konfiguracja usług, możliwość wyboru potoku RAG dla każdej bazy wiedzy osobno, przebudowa systemu generowania pytań i personalizacja paska bocznego.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Wsparcie dla wielu dostawców LLM i embeddingów, nowa strona główna, wydzielenie modułu RAG i uporządkowanie zmiennych środowiskowych.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Zunifikowana architektura PromptManager, wdrożenie CI/CD przez GitHub Actions i gotowe obrazy Dockera w GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Wdrożenie w Dockerze, aktualizacja do Next.js 16 i React 19, zabezpieczenie WebSocketów i krytyczne łatki bezpieczeństwa.

</details>

### 📰 Aktualności

> **[2026.4.19]** 🎉 20 000 gwiazdek w 111 dni! Dziękujemy za wasze niesamowite wsparcie — pracujemy dalej, aby stworzyć prawdziwie spersonalizowane, inteligentne korepetycje dostępne dla każdego.

> **[2026.4.4]** Doczekaliśmy się! ✨ DeepTutor v1.0.0 jest już dostępny — to nasza ewolucja w kierunku architektury agentowej, przebudowana od podstaw. Wprowadzamy TutorBoty, płynne przełączanie trybów, a to wszystko na licencji Apache-2.0. Zaczynamy nowy rozdział!

> **[2026.2.6]** 🚀 Mamy 10 000 gwiazdek w zaledwie 39 dni! Ogromne podziękowania dla naszej rewelacyjnej społeczności.

> **[2026.1.1]** Szczęśliwego Nowego Roku! Wpadnij na naszego [Discorda](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) lub dołącz do [Dyskusji](https://github.com/HKUDS/DeepTutor/discussions) — twórzmy przyszłość DeepTutora razem!

> **[2025.12.29]** Oficjalnie wystartowaliśmy! Pierwsze wydanie DeepTutor ujrzało światło dzienne.

## ✨ Kluczowe funkcje

- **Zunifikowana przestrzeń czatu** — Sześć trybów, jedna konwersacja. Czat, Deep Solve (Głębokie Rozwiązywanie), Quizy, Deep Research (Głęboki Research), Math Animator (Animacje Matematyczne) oraz Wizualizacje współdzielą ten sam kontekst. Możesz zacząć od zwykłego pytania, poprosić grupę agentów o rozwiązanie złożonego problemu, wygenerować z tego quiz, zobrazować pojęcia, a na koniec przejść do głębokiego researchu – bez utraty wątku.
- **Co-Writer (Twój asystent AI do pisania)** — Przestrzeń robocza Markdown do pracy z wieloma dokumentami, gdzie sztuczna inteligencja jest Twoim partnerem. Zaznacz tekst i poproś o jego przepisanie, rozwinięcie lub streszczenie w oparciu o Twoją bazę wiedzy i internet. Każda stworzona w ten sposób notatka staje się częścią Twojego ekosystemu nauki.
- **Silnik Książek (Book Engine)** — Przekształć swoje notatki i materiały w ustrukturyzowane, interaktywne "żywe książki". Nasz system, oparty na wielu agentach AI, samodzielnie stworzy spis treści, dobierze odpowiednie źródła i wygeneruje bogate strony przy użyciu 14 typów bloków (m.in. quizów, fiszek, osi czasu, grafów czy interaktywnych dem).
- **Centrum Wiedzy (Knowledge Hub)** — Wgrywaj pliki PDF, Markdown i TXT, aby łatwo budować własne bazy wiedzy gotowe do użycia w RAG. Grupuj wnioski w kolorowych notatnikach, wracaj do pytań w Banku Pytań i twórz własne Umiejętności (Skills), które decydują o tym, w jaki sposób DeepTutor Cię uczy. Twoje pliki nie leżą i nie kurzą się na dysku — one aktywnie uczestniczą w każdej konwersacji.
- **Długoterminowa Pamięć** — DeepTutor na bieżąco buduje Twój profil: wie, czego się uczyłeś, jaki styl nauki preferujesz i do czego dążysz. Pamięć ta jest współdzielona przez wszystkie funkcje i TutorBoty, dzięki czemu system staje się mądrzejszy z każdą Waszą interakcją.
- **Osobiste TutorBoty** — To nie są zwykłe chatboty. To autonomiczni nauczyciele. Każdy TutorBot ma własną przestrzeń roboczą, pamięć, osobowość i zestaw umiejętności. Mogą ustawiać przypomnienia, uczyć się nowych rzeczy i ewoluować razem z Tobą. Napędzane przez technologię [nanobot](https://github.com/HKUDS/nanobot).
- **CLI Stworzone dla Agentów** — Dostęp do każdej umiejętności, bazy wiedzy, sesji i TutorBota bezpośrednio z terminala. Otrzymujesz czytelne informacje dla siebie i ustrukturyzowany JSON dla swoich potoków i agentów AI. Daj DeepTutorowi plik [`SKILL.md`](SKILL.md), a agenci zaczną z nim współpracować w pełni autonomicznie.

---

## 🚀 Jak zacząć

### Wymagania

Zanim wystartujesz, upewnij się, że masz zainstalowane:

| Wymaganie                                   | Wersja  | Jak sprawdzić      | Uwagi                                                                        |
| :------------------------------------------ | :------ | :----------------- | :--------------------------------------------------------------------------- |
| [Git](https://git-scm.com/)                 | Dowolna | `git --version`    | Do pobrania repozytorium                                                     |
| [Python](https://www.python.org/downloads/) | 3.11+   | `python --version` | Środowisko uruchomieniowe backendu                                           |
| [Node.js](https://nodejs.org/)              | 18+     | `node --version`   | Do budowy frontendu (nie jest wymagane, jeśli używasz tylko CLI lub Dockera) |
| [npm](https://www.npmjs.com/)               | 9+      | `npm --version`    | Instalowane domyślnie razem z Node.js                                        |

Będziesz również potrzebować **Klucza API** od co najmniej jednego dostawcy modeli (np. [OpenAI](https://platform.openai.com/api-keys), [DeepSeek](https://platform.deepseek.com/), [Anthropic](https://console.anthropic.com/)). Nasz skrypt konfiguracyjny poprosi Cię o jego podanie.

### Opcja A — Interaktywny Przewodnik Konfiguracji (Zalecane)

Jeden prosty skrypt w terminalu, który poprowadzi Cię za rękę od sklonowania repozytorium aż do uruchomienia aplikacji. Żadnego ręcznego wpisywania `pip install` czy `npm install`, żadnej dłubaniny w pliku `.env`. Skrypt w 7 krokach automatycznie wszystko wykryje, zainstaluje i skonfiguruje za Ciebie.

```bash
git clone [https://github.com/HKUDS/DeepTutor.git](https://github.com/HKUDS/DeepTutor.git)
cd DeepTutor

# Utwórz wirtualne środowisko w Pythonie (wybierz jedno z poniższych):
conda create -n deeptutor python=3.11 && conda activate deeptutor  # Anaconda/Miniconda
python -m venv .venv && source .venv/bin/activate                  # macOS/Linux
python -m venv .venv && .venv\Scripts\activate                       # Windows

# Uruchom interaktywny przewodnik
python scripts/start_tour.py
```

Gdy kreator zakończy działanie:

```bash
python scripts/start_web.py
```

> **Codzienne uruchamianie** — Prezentacja jest potrzebna tylko raz. Od tej pory wystarczy uruchomić `python scripts/start_web.py`, aby uruchomić zarówno backend, jak i frontend za pomocą jednego polecenia (adres URL frontendu zostanie wyświetlony w terminalu). Uruchom ponownie `start_tour.py` tylko wtedy, gdy chcesz ponownie skonfigurować dostawców, zmienić porty lub zainstalować brakujące dodatki. Na stronie **Ustawienia** w sieci możesz również kliknąć **Uruchom prezentację**, aby ponownie odtworzyć prezentację interfejsu użytkownika opartą na najważniejszych elementach.

### Opcja B — Ręczna instalacja lokalna

Jeśli wolisz mieć pełną kontrolę, zainstaluj i skonfiguruj wszystko samodzielnie.

**1. Zainstaluj zależności**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

# Utwórz i aktywuj wirtualne środowisko Python (tak samo jak w opcji A)
conda create -n deeptutor python=3.11 && conda activate deeptutor

# Zainstaluj DeepTutor wraz z zależnościami backendu i serwera WWW
pip install -e „.[server]”

# Zainstaluj zależności frontendu (wymagany Node.js 18+)
cd web && npm install && cd ..
```

**2. Skonfiguruj środowisko**

```bash
cp .env.example .env
```

Edytuj plik `.env` i wypełnij przynajmniej wymagane pola:

```dotenv
# LLM (wymagane)
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxx
LLM_HOST=https://api.openai.com/v1

# Embedding (wymagane dla bazy wiedzy)
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_DIMENSION=3072
```

<details>
<summary><b>Obsługiwani dostawcy modeli LLM</b></summary>

| Dostawca               | Interface                | Domyślny bazowy URL                                        |
| :--------------------- | :----------------------- | :--------------------------------------------------------- |
| AiHubMix               | `aihubmix`               | `https://aihubmix.com/v1`                                  |
| Anthropic              | `anthropic`              | `https://api.anthropic.com/v1`                             |
| Azure OpenAI           | `azure_openai`           | —                                                          |
| BytePlus               | `byteplus`               | `https://ark.ap-southeast.bytepluses.com/api/v3`           |
| BytePlus Coding Plan   | `byteplus_coding_plan`   | `https://ark.ap-southeast.bytepluses.com/api/coding/v3`    |
| Custom                 | `custom`                 | —                                                          |
| Custom (Anthropic API) | `custom_anthropic`       | —                                                          |
| DashScope              | `dashscope`              | `https://dashscope.aliyuncs.com/compatible-mode/v1`        |
| DeepSeek               | `deepseek`               | `https://api.deepseek.com`                                 |
| Gemini                 | `gemini`                 | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| GitHub Copilot         | `github_copilot`         | `https://api.githubcopilot.com`                            |
| Groq                   | `groq`                   | `https://api.groq.com/openai/v1`                           |
| llama.cpp              | `llama_cpp`              | `http://localhost:8080/v1`                                 |
| LM Studio              | `lm_studio`              | `http://localhost:1234/v1`                                 |
| MiniMax                | `minimax`                | `https://api.minimaxi.com/v1`                              |
| MiniMax (Anthropic)    | `minimax_anthropic`      | `https://api.minimaxi.com/anthropic`                       |
| Mistral                | `mistral`                | `https://api.mistral.ai/v1`                                |
| Moonshot               | `moonshot`               | `https://api.moonshot.cn/v1`                               |
| Ollama                 | `ollama`                 | `http://localhost:11434/v1`                                |
| OpenAI                 | `openai`                 | `https://api.openai.com/v1`                                |
| OpenAI Codex           | `openai_codex`           | `https://chatgpt.com/backend-api`                          |
| OpenRouter             | `openrouter`             | `https://openrouter.ai/api/v1`                             |
| OpenVINO Model Server  | `ovms`                   | `http://localhost:8000/v3`                                 |
| Qianfan                | `qianfan`                | `https://qianfan.baidubce.com/v2`                          |
| SiliconFlow            | `siliconflow`            | `https://api.siliconflow.cn/v1`                            |
| Step Fun               | `stepfun`                | `https://api.stepfun.com/v1`                               |
| vLLM/Local             | `vllm`                   | —                                                          |
| VolcEngine             | `volcengine`             | `https://ark.cn-beijing.volces.com/api/v3`                 |
| VolcEngine Coding Plan | `volcengine_coding_plan` | `https://ark.cn-beijing.volces.com/api/coding/v3`          |
| Xiaomi MIMO            | `xiaomi_mimo`            | `https://api.xiaomimimo.com/v1`                            |
| Zhipu AI               | `zhipu`                  | `https://open.bigmodel.cn/api/paas/v4`                     |

</details>

<details>
<summary><b>Wspierani dostawcy Embedding</b></summary>

| Dostawca                      | Binding        | Przykład modelu          | Domyślne przyciemnienie |
| :---------------------------- | :------------- | :----------------------- | :---------------------- |
| OpenAI                        | `openai`       | `text-embedding-3-large` | 3072                    |
| Azure OpenAI                  | `azure_openai` | nazwa wdrożenia          | —                       |
| Cohere                        | `cohere`       | `embed-v4.0`             | 1024                    |
| Jina                          | `jina`         | `jina-embeddings-v3`     | 1024                    |
| Ollama                        | `ollama`       | `nomic-embed-text`       | 768                     |
| vLLM / LM Studio              | `vllm`         | Dowolny model osadzania  | —                       |
| Dowolny model zgodny z OpenAI | `custom`       | —                        | —                       |

Dostawcy zgodni z OpenAI (DashScope, SiliconFlow itp.) działają poprzez powiązanie `custom` lub `openai`.

</details>

<details>
<summary><b>Obsługiwani dostawcy wyszukiwarek internetowych</b></summary>

| Dostawca   | Klucz środowiska     | Uwagi                                               |
| :--------- | :------------------- | :-------------------------------------------------- |
| Brave      | `BRAVE_API_KEY`      | Zalecany, dostępny bezpłatny                        |
| Tavily     | `TAVILY_API_KEY`     |                                                     |
| Serper     | `SERPER_API_KEY`     | Wyniki wyszukiwania Google za pośrednictwem Serper  |
| Jina       | `JINA_API_KEY`       |                                                     |
| SearXNG    | —                    | Hostowanie samodzielne, klucz API nie jest wymagany |
| DuckDuckGo | —                    | Klucz API nie jest wymagany                         |
| Perplexity | `PERPLEXITY_API_KEY` | Wymagany klucz API                                  |

</details>

**3. Uruchom usługi**

Najszybszy sposób na uruchomienie wszystkiego:

```bash
python scripts/start_web.py
```

Spowoduje to uruchomienie zarówno backendu, jak i frontendu oraz automatyczne otwarcie przeglądarki.

Alternatywnie, uruchom każdą usługę ręcznie w oddzielnych terminalach:

```bash
# Backend (FastAPI)
python -m deeptutor.api.run_server

# Frontend (Next.js) — w oddzielnym terminalu
cd web && npm run dev -- -p 3782
```

|  Usługa  | Port domyślny |
| :------: | :-----------: |
| Backend  |    `8001`     |
| Frontend |    `3782`     |

Otwórz [http://localhost:3782](http://localhost:3782) i gotowe.

### Opcja C — Wdrożenie w Dockerze

Docker łączy backend i frontend w jednym kontenerze — nie jest wymagana lokalna instalacja Pythona ani Node.js. Potrzebujesz jedynie [Docker Desktop](https://www.docker.com/products/docker-desktop/) (lub Docker Engine + Compose w systemie Linux).

**1. Skonfiguruj zmienne środowiskowe** (wymagane dla obu poniższych opcji)

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
cp .env.example .env
```

Edytuj plik `.env` i wypełnij przynajmniej wymagane pola (tak samo jak w [opcji B](#option-b--manual-local-install) powyżej).

**2a. Pobierz oficjalny obraz (zalecane)**

Oficjalne obrazy są publikowane w [GitHub Container Registry](https://github.com/HKUDS/DeepTutor/pkgs/container/deeptutor) przy każdym wydaniu, skompilowane dla `linux/amd64` i `linux/arm64`.

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

Aby przypiąć konkretną wersję, edytuj tag obrazu w pliku `docker-compose.ghcr.yml`:

```yaml
image: ghcr.io/hkuds/deeptutor:1.0.0 # or :latest
```

**2b. Kompilacja ze źródeł**

```bash
docker compose up -d
```

Spowoduje to skompilowanie obrazu lokalnie z pliku `Dockerfile` i uruchomienie kontenera.

**3. Weryfikacja i zarządzanie**

Po upewnieniu się, że kontener działa poprawnie, otwórz stronę [http://localhost:3782](http://localhost:3782).

```bash
docker compose logs -f   # wyświetlaj logi
docker compose down       # zatrzymaj i usuń kontener
```

<details>
<summary><b>Wdrażanie w chmurze / na serwerze zdalnym</b></summary>

Podczas wdrażania na serwerze zdalnym przeglądarka musi znać publiczny adres URL interfejsu API zaplecza. Dodaj jeszcze jedną zmienną do pliku `.env`:

```dotenv
# Ustaw na publiczny adres URL, pod którym dostępne jest zaplecze
NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:8001
```

Skrypt uruchamiający frontend stosuje tę wartość w czasie wykonywania — nie jest wymagana kompilacja.

</details>

<details>
<summary><b>Tryb programowania (hot-reload)</b></summary>

Dodaj warstwę nadpisującą dla programistów, aby zamontować kod źródłowy i włączyć hot-reload dla obu usług:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Zmiany w katalogach `deeptutor/`, `deeptutor_cli/`, `scripts/` i `web/` są odzwierciedlane natychmiast.

</details>

<details>
<summary><b>Niestandardowe porty</b></summary>

Zastąp domyślne porty w pliku `.env`:

```dotenv
BACKEND_PORT=9001
FRONTEND_PORT=4000
```

Następnie uruchom ponownie:

```bash
docker compose up -d     # lub docker compose -f docker-compose.ghcr.yml up -d
```

</details>

<details>
<summary><b>Trwałość danych</b></summary>

Dane użytkowników i bazy wiedzy są przechowywane w woluminach Docker przypisanych do lokalnych katalogów:

| Ścieżka kontenera           | Ścieżka hosta            | Zawartość                                       |
| :-------------------------- | :----------------------- | :---------------------------------------------- |
| `/app/data/user`            | `./data/user`            | Ustawienia, pamięć, obszar roboczy, sesje, logi |
| `/app/data/knowledge_bases` | `./data/knowledge_bases` | Przesłane dokumenty i indeksy wektorowe         |

Katalogi te pozostają nienaruszone po wykonaniu polecenia `docker compose down` i są ponownie wykorzystywane przy następnym uruchomieniu `docker compose up`.

</details>

<details>
<summary><b>Opis zmiennych środowiskowych</b></summary>

| Zmienna                         | Wymagana | Opis                                                                  |
| :------------------------------ | :------: | :-------------------------------------------------------------------- |
| `LLM_BINDING`                   | **Tak**  | Dostawca LLM (`openai`, `anthropic` itp.)                             |
| `LLM_MODEL`                     | **Tak**  | Nazwa modelu (np. `gpt-4o`)                                           |
| `LLM_API_KEY`                   | **Tak**  | Twój klucz API LLM                                                    |
| `LLM_HOST`                      | **Tak**  | Adres URL punktu końcowego API                                        |
| `EMBEDDING_BINDING`             | **Tak**  | Dostawca osadzania                                                    |
| `EMBEDDING_MODEL`               | **Tak**  | Nazwa modelu osadzania                                                |
| `EMBEDDING_API_KEY`             | **Tak**  | Klucz API osadzania                                                   |
| `EMBEDDING_HOST`                | **Tak**  | Punkt końcowy osadzania                                               |
| `EMBEDDING_DIMENSION`           | **Tak**  | Wymiar wektora                                                        |
| `SEARCH_PROVIDER`               |   Nie    | Dostawca wyszukiwania (`tavily`, `jina`, `serper`, `perplexity` itp.) |
| `SEARCH_API_KEY`                |   Nie    | Klucz API wyszukiwania                                                |
| `BACKEND_PORT`                  |   Nie    | Port zaplecza (domyślnie `8001`)                                      |
| `FRONTEND_PORT`                 |   Nie    | Port interfejsu użytkownika (domyślnie `3782`)                        |
| `NEXT_PUBLIC_API_BASE_EXTERNAL` |   Nie    | Publiczny adres URL zaplecza dla wdrożenia w chmurze                  |
| `DISABLE_SSL_VERIFY`            |   Nie    | Wyłącz weryfikację SSL (domyślnie `false`)                            |

</details>

### Opcja D — Tylko CLI

Jeśli chcesz tylko CLI bez interfejsu użytkownika:

```bash
pip install -e „.[cli]”
```

Nadal musisz skonfigurować dostawcę LLM. Najszybszy sposób:

```bash
cp .env.example .env   # następnie edytuj plik .env, aby wprowadzić swoje klucze API
```

Po skonfigurowaniu wszystko jest gotowe do działania:

```bash
deeptutor chat                                   # Interaktywny REPL
deeptutor run chat „Explain Fourier transform”   # Funkcja jednorazowa
deeptutor run deep_solve „Solve x^2 = 4”         # Rozwiązywanie problemów przez wielu agentów
deeptutor kb create my-kb --doc textbook.pdf     # Utwórz bazę wiedzy
```

> Pełny przewodnik po funkcjach i opis poleceń znajdziesz w [DeepTutor CLI](#%EF%B8%8F-deeptutor-cli--agent-native-interface).

---

## 📖 Poznaj DeepTutor

<div align="center">
<img src="assets/figs/deeptutor-architecture.png" alt="Architektura DeepTutor" width="800">
</div>

### 💬 Czat — ujednolicone inteligentne środowisko pracy

<div align="center">
<img src="assets/figs/dt-chat.png" alt="Środowisko pracy czatu" width="800">
</div>

W jednym obszarze roboczym współistnieje sześć różnych trybów, połączonych **ujednoliconym systemem zarządzania kontekstem**. Historia rozmów, bazy wiedzy i odniesienia są zachowywane we wszystkich trybach — przełączaj się między nimi swobodnie w ramach tego samego tematu, kiedy tylko zajdzie taka potrzeba.

| Tryb                      | Co robi                                                                                                                                                                                                   |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Czat**                  | Płynna rozmowa wspomagana narzędziami. Wybieraj spośród wyszukiwania RAG, wyszukiwania w sieci, wykonywania kodu, głębokiego rozumowania, burzy mózgów i wyszukiwania artykułów — łącz je według potrzeb. |
| **Deep Solve**            | Wielopodmiotowe rozwiązywanie problemów: planuj, badaj, rozwiązuj i weryfikuj — z precyzyjnymi cytatami źródeł na każdym etapie.                                                                          |
| **Generowanie quizów**    | Generuj testy oparte na Twojej bazie wiedzy, z wbudowaną walidacją.                                                                                                                                       |
| **Głębokie badania**      | Rozbij temat na podtematy, wyślij równoległe agenty badawcze do RAG, sieci i artykułów naukowych oraz stwórz w pełni cytowany raport.                                                                     |
| **Animator matematyczny** | Zamień pojęcia matematyczne w animacje wizualne i scenariusze oparte na Manim.                                                                                                                            |
| **Wizualizacja**          | Generuj interaktywne diagramy SVG, wykresy Chart.js, wykresy Mermaid lub samodzielne strony HTML na podstawie opisów w języku naturalnym.                                                                 |

Narzędzia są **oddzielone od przepływów pracy** — w każdym trybie sam decydujesz, które narzędzia włączyć, ile z nich użyć lub czy w ogóle z nich korzystać. Przepływ pracy koordynuje proces wnioskowania; narzędzia możesz dowolnie komponować.

> Zacznij od szybkiego pytania na czacie, przejdź do Deep Solve, gdy sprawa się skomplikuje, wizualizuj koncepcję, generuj pytania quizowe, aby sprawdzić swoją wiedzę, a następnie uruchom Deep Research, aby zagłębić się w temat — wszystko w jednym ciągłym wątku.

### ✍️ Co-Writer — środowisko pracy z obsługą wielu dokumentów i sztuczną inteligencją

<div align="center">
<img src="assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer przenosi inteligencję Chat bezpośrednio do obszaru roboczego. Twórz i zarządzaj wieloma dokumentami, z których każdy jest przechowywany w osobnym obszarze roboczym — nie jest to zwykły, jednorazowy notatnik, ale w pełni funkcjonalny edytor Markdown obsługujący wiele dokumentów, w którym sztuczna inteligencja pełni rolę pierwszorzędnego współpracownika.

Zaznacz dowolny tekst i wybierz opcję **Przepisz**, **Rozwiń** lub **Skróć** — opcjonalnie czerpiąc kontekst z bazy wiedzy lub sieci. Proces edycji jest nieniszczący, z pełną funkcją cofania/ponawiania, a każdy fragment, który napiszesz, może zostać zapisany bezpośrednio w twoich notatnikach, zasilając twój ekosystem nauki.

### 📖 Book Engine — interaktywne „żywe książki”

<div align="center">
<img src="assets/figs/dt-book-0.png" alt="Biblioteka książek" width="270"><img src="assets/figs/dt-book-1.png" alt="Czytnik książek" width="270"><img src="assets/figs/dt-book-2.png" alt="Animacja książki" width="270">
</div>

Podaj DeepTutor temat, wskaż swoją bazę wiedzy, a program stworzy uporządkowaną, interaktywną książkę — nie statyczny eksport, ale żywy dokument, który możesz czytać, sprawdzać swoją wiedzę i omawiać w kontekście.

Za kulisami potężny potok wieloagentowy zajmuje się ciężką pracą: proponuje zarys, pobiera odpowiednie źródła z Twojej bazy wiedzy, syntetyzuje drzewo rozdziałów, planuje każdą stronę i kompiluje każdy blok. Ty zachowujesz kontrolę — przeglądasz propozycję, zmieniasz kolejność rozdziałów i rozmawiasz na czacie przy dowolnej stronie.

Strony są tworzone z 14 typów bloków — tekst, ramka, quiz, fiszki, kod, rysunek, zagłębienie, animacja, interaktywne demo, oś czasu, wykres koncepcyjny, sekcja, notatka użytkownika i symbol zastępczy — z których każdy jest renderowany z własnym interaktywnym komponentem. Oś czasu postępu w czasie rzeczywistym pozwala obserwować, jak kompilacja przebiega w miarę jak książka nabiera kształtu.

### 📚 Zarządzanie wiedzą — Twoja infrastruktura edukacyjna

<div align="center">
<img src="assets/figs/dt-knowledge.png" alt="Zarządzanie wiedzą" width="800">
</div>

W sekcji „Wiedza” tworzysz i zarządzasz zbiorami dokumentów, notatkami oraz profilami nauczycielskimi, które napędzają wszystkie pozostałe funkcje DeepTutor.

- **Bazy wiedzy** — Przesyłaj pliki PDF, TXT lub Markdown, aby tworzyć kolekcje z możliwością wyszukiwania, gotowe do RAG. Dodawaj dokumenty stopniowo, w miarę jak Twoja biblioteka się powiększa.
- **Notatniki** — Organizuj zapisy z nauki z różnych sesji. Zapisuj spostrzeżenia z Czat, Współautora, Książki lub Głębokich badań w skategoryzowanych, oznaczonych kolorami notatnikach.
- **Bank pytań** — Przeglądaj i wracaj do wszystkich wygenerowanych pytań quizowych. Dodawaj wpisy do zakładek i oznaczaj je @ bezpośrednio na czacie, aby analizować dotychczasowe wyniki.
- **Umiejętności** — Twórz niestandardowe persony nauczycielskie za pomocą plików `SKILL.md`. Każda umiejętność definiuje nazwę, opis, opcjonalne wyzwalacze oraz treść w formacie Markdown, która jest wstawiana do podpowiedzi systemu czatu, gdy jest aktywna — zamieniając DeepTutor w nauczyciela stosującego metodę sokratejską, partnera do nauki, asystenta badawczego lub dowolną rolę, którą zaprojektujesz.

Twoja baza wiedzy nie jest biernym magazynem — aktywnie uczestniczy w każdej rozmowie, każdej sesji badawczej i każdej ścieżce nauki, którą tworzysz.

### 🧠 Pamięć — DeepTutor uczy się razem z Tobą

<div align="center">
<img src="assets/figs/dt-memory.png" alt="Pamięć" width="800">
</div>

DeepTutor utrzymuje trwałe, ewoluujące zrozumienie Ciebie poprzez dwa uzupełniające się wymiary:

- **Podsumowanie** — bieżące podsumowanie Twoich postępów w nauce: czego się uczyłeś, jakie tematy zgłębiałeś i jak rozwijało się Twoje zrozumienie.
- **Profil** — Twoja tożsamość jako ucznia: preferencje, poziom wiedzy, cele i styl komunikacji — automatycznie udoskonalane podczas każdej interakcji.

Pamięć jest wspólna dla wszystkich funkcji i wszystkich Twoich TutorBotów. Im częściej korzystasz z DeepTutor, tym bardziej spersonalizowany i skuteczny staje się on.

---

### 🦞 TutorBot — Trwali, autonomiczni nauczyciele AI

<div align="center">
<img src="assets/figs/tutorbot-architecture.png" alt="Architektura TutorBota" width="800">
</div>

TutorBot nie jest chatbotem — to **trwały, wieloinstancyjny agent** zbudowany na bazie [nanobota](https://github.com/HKUDS/nanobot). Każdy TutorBot uruchamia własną pętlę agenta z niezależnym obszarem roboczym, pamięcią i osobowością. Stwórz sokratejskiego korepetytora matematyki, cierpliwego trenera pisania i rygorystycznego doradcę naukowego — wszyscy działają jednocześnie, a każdy z nich ewoluuje razem z Tobą.

<div align="center">
<img src="assets/figs/tb.png" alt="TutorBot" width="800">
</div>

- **Szablony duszy** — Zdefiniuj osobowość, ton i filozofię nauczania swojego korepetytora za pomocą edytowalnych plików duszy. Wybierz spośród wbudowanych archetypów (sokratyczny, zachęcający, rygorystyczny) lub stwórz własny — dusza kształtuje każdą odpowiedź.
- **Niezależna przestrzeń robocza** — Każdy bot ma swój własny katalog z oddzielną pamięcią, sesjami, umiejętnościami i konfiguracją — w pełni odizolowany, ale z dostępem do wspólnej warstwy wiedzy DeepTutor.
- **Proaktywny Heartbeat** — Boty nie tylko odpowiadają — one inicjują. Wbudowany system Heartbeat umożliwia cykliczne sprawdzanie postępów w nauce, przypomnienia o powtórkach i zaplanowane zadania. Twój tutor pojawia się nawet wtedy, gdy Ciebie nie ma.
- **Pełny dostęp do narzędzi** — Każdy bot ma dostęp do pełnego zestawu narzędzi DeepTutor: wyszukiwanie RAG, wykonywanie kodu, wyszukiwanie w sieci, wyszukiwanie artykułów naukowych, głębokie rozumowanie i burza mózgów.
- **Nauka umiejętności** — Naucz swojego bota nowych umiejętności, dodając pliki umiejętności do jego obszaru roboczego. Wraz z ewolucją Twoich potrzeb ewoluują również możliwości Twojego tutora.
- **Obecność w wielu kanałach** — Połącz boty z Telegramem, Discordem, Slackiem, Feishu, WeChat Work, DingTalk, e-mailem i innymi platformami. Twój korepetytor spotyka się z Tobą, gdziekolwiek jesteś.
- **Zespoły i podagenci** — Twórz podagentów działających w tle lub koordynuj zespoły wieloagentowe w ramach jednego bota do złożonych, długotrwałych zadań.

```bash
deeptutor bot create math-tutor --persona „Sokratyczny nauczyciel matematyki, który zadaje dociekliwe pytania”
deeptutor bot create writing-coach --persona „Cierpliwy, zwracający uwagę na szczegóły mentor pisania”
deeptutor bot list                  # Zobacz wszystkich aktywnych tutorów
```

---

### ⌨️ DeepTutor CLI — Interfejs natywny dla agentów

<div align="center">
<img src="assets/figs/cli-architecture.png" alt="Architektura DeepTutor CLI" width="800">
</div>

DeepTutor jest w pełni natywny dla CLI. Każda funkcja, baza wiedzy, sesja, pamięć i TutorBot są dostępne za pomocą jednego polecenia — nie jest wymagana przeglądarka. CLI obsługuje zarówno ludzi (dzięki bogatemu renderowaniu terminala), jak i agentów AI (dzięki ustrukturyzowanemu wyjściu JSON).

Przekaż plik [`SKILL.md`](SKILL.md) znajdujący się w katalogu głównym projektu dowolnemu agentowi korzystającemu z narzędzi ([nanobot](https://github.com/HKUDS/nanobot) lub dowolnemu LLM z dostępem do narzędzi), a będzie on mógł samodzielnie skonfigurować i obsługiwać DeepTutor.

**Wykonanie jednokrotne** — Uruchom dowolną funkcję bezpośrednio z terminala:

```bash
deeptutor run chat „Wyjaśnij transformację Fouriera” -t rag --kb textbook
deeptutor run deep_solve „Udowodnij, że √2 jest liczbą niewymierną” -t reason
deeptutor run deep_question „Algebra liniowa” --config num_questions=5
deeptutor run deep_research „Mechanizmy uwagi w transformatorach”
deeptutor run visualize „Narysuj architekturę transformatora”
```

**Interaktywny REPL** — Trwała sesja czatu z przełączaniem trybów na żywo:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# W REPL: /cap, /tool, /kb, /history, /notebook, /config do przełączania w locie
```

**Cykl życia bazy wiedzy** — Twórz, przeszukuj i zarządzaj kolekcjami gotowymi do RAG całkowicie z terminala:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # Utwórz z dokumentu
deeptutor kb add my-kb --docs-dir ./papers/         # Dodaj folder z artykułami
deeptutor kb search my-kb „gradient descent”        # Wyszukaj bezpośrednio
deeptutor kb set-default my-kb                      # Ustaw jako domyślną dla wszystkich poleceń
```

**Podwójny tryb wyjściowy** — Bogate renderowanie dla ludzi, ustrukturyzowany JSON dla potoków:

```bash
deeptutor run chat „Summarize chapter 3” -f rich    # Kolorowe, sformatowane wyjście
deeptutor run chat „Summarize chapter 3” -f json    # Zdarzenia JSON rozdzielone liniami
```

**Ciągłość sesji** — Wznów dowolną rozmowę dokładnie tam, gdzie ją przerwałeś:

```bash
deeptutor session list                              # Wyświetl listę wszystkich sesji
deeptutor session open <id>                         # Wznów w REPL
```

<details>
<summary><b>Pełna dokumentacja poleceń CLI</b></summary>

**Najwyższy poziom**

| Polecenie                              | Opis                                                                                                                          |
| :------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| `deeptutor run <capability> <message>` | Uruchom dowolną funkcję w jednej turze (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat`                       | Interaktywny REPL z opcjonalnymi parametrami `--capability`, `--tool`, `--kb`, `--language`                                   |
| `deeptutor serve`                      | Uruchom serwer API DeepTutor                                                                                                  |

**`deeptutor bot`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor bot list` | Wyświetl listę wszystkich instancji TutorBot |

| `deeptutor bot create <id>` | Utwórz i uruchom nowego bota (`--name`, `--persona`, `--model`) |

| `deeptutor bot start <id>` | Uruchom bota |

| `deeptutor bot stop <id>` | Zatrzymaj bota |

**`deeptutor kb`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor kb list` | Wyświetl listę wszystkich baz wiedzy |

| `deeptutor kb info <name>` | Pokaż szczegóły bazy wiedzy |

| `deeptutor kb create <nazwa>` | Utwórz na podstawie dokumentów (`--doc`, `--docs-dir`) |

| `deeptutor kb add <nazwa>` | Dodaj dokumenty stopniowo |

| `deeptutor kb search <nazwa> <zapytanie>` | Przeszukaj bazę wiedzy |

| `deeptutor kb set-default <nazwa>` | Ustaw jako domyślną bazę wiedzy |

| `deeptutor kb delete <nazwa>` | Usuń bazę wiedzy (`--force`) |

**`deeptutor memory`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor memory show [plik]` | Wyświetl pamięć (`summary`, `profile` lub `all`) |

| `deeptutor memory clear [plik]` | Wyczyść pamięć (`--force`) |

**`deeptutor session`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor session list` | Wyświetl listę sesji (`--limit`) |

| `deeptutor session show <id>` | Wyświetl komunikaty sesji |

| `deeptutor session open <id>` | Wznow sesję w REPL |

| `deeptutor session rename <id>` | Zmień nazwę sesji (`--title`) |

| `deeptutor session delete <id>` | Usuń sesję |

**`deeptutor notebook`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor notebook list` | Wyświetl listę notatników |

| `deeptutor notebook create <name>` | Utwórz notatnik (`--description`) |

| `deeptutor notebook show <id>` | Wyświetl rekordy notatnika |

| `deeptutor notebook add-md <id> <path>` | Importuj markdown jako rekord |

| `deeptutor notebook replace-md <id> <rec> <path>` | Zastąp rekord w formacie Markdown |

| `deeptutor notebook remove-record <id> <rec>` | Usuń rekord |

**`deeptutor book`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor book list` | Wyświetl listę wszystkich książek w obszarze roboczym |

| `deeptutor book health <book_id>` | Sprawdź odchylenie KB i stan książki |

| `deeptutor book refresh-fingerprints <book_id>` | Odśwież odciski palców KB i wyczyść nieaktualne strony |

**`deeptutor config` / `plugin` / `provider`**

| Polecenie | Opis |

|:---|:---|

| `deeptutor config show` | Wyświetl podsumowanie bieżącej konfiguracji |

| `deeptutor plugin list` | Wyświetl listę zarejestrowanych narzędzi i funkcji |

| `deeptutor plugin info <name>` | Wyświetl szczegóły narzędzia lub funkcji |

| `deeptutor provider login <provider>` | Uwierzytelnianie dostawcy (logowanie OAuth `openai-codex`; `github-copilot` weryfikuje istniejącą sesję uwierzytelniającą Copilot) |

</details>

## 🗺️ Plan działania

| Status | Kamień milowy |

|:---:|:---|

| 🎯 | **Uwierzytelnianie i logowanie** — Opcjonalna strona logowania dla wdrożeń publicznych z obsługą wielu użytkowników |

| 🎯 | **Motywy i wygląd** — Różnorodne opcje motywów i konfigurowalny wygląd interfejsu użytkownika |

| 🎯 | **Ulepszenie interakcji** — optymalizacja projektu ikon i szczegółów interakcji |

| 🔜 | **Lepsze pamięci** — integracja lepszego zarządzania pamięcią |

| 🔜 | **Integracja LightRAG** — Integracja [LightRAG](https://github.com/HKUDS/LightRAG) jako zaawansowanego silnika bazy wiedzy |

| 🔜 | **Strona dokumentacji** — Kompleksowa strona dokumentacji zawierająca przewodniki, opis API i samouczki |

> Jeśli uważasz, że DeepTutor jest przydatny, [przyznaj nam gwiazdkę](https://github.com/HKUDS/DeepTutor/stargazers) — to pomoże nam dalej działać!

---

## 🌐 Społeczność i ekosystem

DeepTutor opiera się na wybitnych projektach open source:

| Projekt | Rola w DeepTutor |

|:---|:---|

| [**nanobot**](https://github.com/HKUDS/nanobot) | Ultralekki silnik agenta zasilający TutorBot |

| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Potok RAG i szkielet indeksowania dokumentów |

| [**ManimCat**](https://github.com/Wing900/ManimCat) | Generowanie animacji matematycznych oparte na sztucznej inteligencji dla Math Animator |

**Z ekosystemu HKUDS:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |

|:---:|:---:|:---:|:---:|

| Prosty i szybki RAG | Framework agenta bez kodowania | Zautomatyzowane badania | Ultralekki agent AI |

## 🤝 Współtworzenie

<div align="center">

Mamy nadzieję, że DeepTutor stanie się prezentem dla społeczności. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">

<img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Współtwórcy" />

</a>

</div>

Zobacz [CONTRIBUTING.md](CONTRIBUTING.md), aby zapoznać się z wytycznymi dotyczącymi konfiguracji środowiska programistycznego, standardów kodowania oraz procesu składania pull requestów.

## ⭐ Historia gwiazdek

<div align="center">

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">

<picture>

<source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />

<source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />

<img alt="Wykres historii gwiazd" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />

</picture>

</a>

</div>

<p align="center">

<a href="https://www.star-history.com/hkuds/deeptutor">

<picture>

<source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor&theme=dark" />

<source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />

<img alt="Ranking historii gwiazdek" src="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />

</picture>

</a>

</p>

<div align="center">

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ Oznacz nas gwiazdką](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Zgłoś błąd](https://github.com/HKUDS/DeepTutor/issues) · [💬 Dyskusje](https://github.com/HKUDS/DeepTutor/discussions)

---

Na licencji [Apache License 2.0](LICENSE).

<p>

<img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Widoki">

</p>

</div>
