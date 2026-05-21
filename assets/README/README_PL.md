<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Spersonalizowane korepetycje natywne dla agentów

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
  <a href="README_PT.md"><img alt="Português" height="40" src="https://img.shields.io/badge/Português-CDCFD4"></a>&nbsp;
  <a href="README_TH.md"><img alt="Thai" height="40" src="https://img.shields.io/badge/Thai-CDCFD4"></a>&nbsp;
  <a href="README_PL.md"><img alt="Polski" height="40" src="https://img.shields.io/badge/Polski-BCDCF7"></a>
</p>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](../../LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/HKUDS/DeepTutor?style=flat-square&color=brightgreen)](https://github.com/HKUDS/DeepTutor/releases)
[![arXiv](https://img.shields.io/badge/arXiv-2604.26962-b31b1b?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2604.26962)

[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-00D4AA?style=flat-square&logo=feishu&logoColor=white)](../../Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-07C160?style=flat-square&logo=wechat&logoColor=white)](https://github.com/HKUDS/DeepTutor/issues/78)

[Funkcje](#key-features) · [Jak zacząć](#get-started) · [Odkrywaj](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [Multi-użytkownik](#multi-user) · [Społeczność](#community)

</div>

---

> 🤝 **Każda forma współtworzenia jest mile widziana!** Zapoznaj się z naszym [Przewodnikiem dla kontrybutorów](../../CONTRIBUTING.md), w którym opisaliśmy strategię gałęzi, standardy kodu oraz pierwsze kroki.
>
> 🗺️ **Roadmapa** prowadzona jest jawnie pod adresem [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — komentuj, aby głosować na elementy lub proponować nowe.

### 📦 Wydania

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — Trójwarstwowy workbench Memory (L1/L2/L3), każda funkcja czatu przebudowana w oparciu o jeden agentowy silnik, RAG wyłącznie na LlamaIndex oraz zunifikowana powierzchnia Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Naprawa CORS dla zdalnego Dockera, `DISABLE_SSL_VERIFY` w dostawcach SDK, bezpieczniejsze cytaty w blokach kodu oraz opcjonalny dodatek Matrix E2EE.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — Wsparcie Zulip i NVIDIA NIM w TutorBot, bezpieczniejszy routing modeli rozumujących, `deeptutor start`, podpowiedzi w pasku bocznym i spójność magazynu sesji.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Opcjonalne wdrożenia wielu użytkowników z izolowanymi przestrzeniami roboczymi, uprawnienia administratora, trasy uwierzytelniania oraz ograniczony dostęp w trakcie działania.

<details>
<summary><b>Starsze wydania (ponad 2 tygodnie temu)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Poprawki dla modeli/dostawców rozumujących, widoczna historia indeksów Knowledge oraz bezpieczniejsze czyszczenie i edycja szablonów w Co-Writer.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Wybór modeli na podstawie katalogu dla czatu i TutorBot, bezpieczniejsza ponowna indeksacja RAG, poprawki limitów tokenów OpenAI Responses oraz walidacja edytora Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Płynniejsze ustawienia lokalnego uruchamiania, bezpieczniejsze zapytania RAG, schludniejsze uwierzytelnianie lokalnych embeddingów oraz dopracowanie trybu ciemnego w Settings.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Trwałość czatu na stronach książek i przepływy odbudowy, odniesienia z czatu do książek, lepsza obsługa języka i rozumowania, wzmocnienie ekstrakcji dokumentów RAG.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — Wsparcie embeddingów NVIDIA NIM i Gemini, zunifikowany kontekst Space dla historii czatu/skills/memory, migawki sesji oraz odporność na ponowną indeksację RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — Przejrzyste adresy URL endpointów embeddingów, odporność ponownej indeksacji RAG przy nieprawidłowych zapisanych wektorach, sprzątanie pamięci dla wyjścia modeli rozumujących oraz poprawka działania Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Stabilność: bezpieczniejszy routing RAG oraz walidacja embeddingów, trwałość Docker, bezpieczne wejście IME, odporność na Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Wersjonowane indeksy KB z procesem ponownej indeksacji, przebudowana przestrzeń Knowledge, automatyczne wykrywanie embeddingów z nowymi adapterami oraz hub Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Trwałe załączniki czatu z szufladą podglądu plików, potoki funkcji świadome załączników oraz eksport Markdown w TutorBot.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — Załączniki tekstowe/kodu/SVG, Setup Tour jednym poleceniem, eksport czatu do Markdown, kompaktowy interfejs zarządzania KB.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Załączniki dokumentów (PDF/DOCX/XLSX/PPTX), wyświetlanie bloku rozumowania, edytor szablonów Soul, zapis Co-Writer do notatnika.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — System Skills tworzonych przez użytkownika, gruntowna poprawa wydajności wprowadzania w czacie, automatyczny start TutorBot, interfejs Book Library, wizualizacje w trybie pełnoekranowym.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Limity tokenów na etap, regeneracja odpowiedzi we wszystkich punktach wejścia, poprawki kompatybilności RAG i Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Kompilator „żywych książek” Book Engine, wielodokumentowy Co-Writer, interaktywne wizualizacje HTML, @-wzmianki Question Bank.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Zakładka Channels oparta na schemacie, konsolidacja RAG w jeden potok, zewnętrzne prompty czatu.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — Uniwersalne „Odpowiedz teraz”, synchronizacja przewijania Co-Writer, zunifikowany panel ustawień, przycisk Stop dla streamingu.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Przebudowa blokowej matematyki LaTeX, sonda diagnostyczna LLM, wskazówki dla Docker + lokalnego LLM.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Sesje z zakładkami, motyw Snow, heartbeat WebSocket i automatyczne ponowne łączenie, przebudowa rejestru embeddingów.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Notatnik pytań z zakładkami i kategoriami, Mermaid w Visualize, wykrywanie niedopasowania embeddingów, kompatybilność Qwen/vLLM, wsparcie LM Studio i llama.cpp oraz motyw Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Konsolidacja wyszukiwania z fallbackiem do SearXNG, naprawa przełączania dostawców i poprawki wycieków zasobów we frontendzie.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Funkcja Visualize (Chart.js/SVG), zapobieganie duplikatom w quizach oraz wsparcie modelu o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Śledzenie postępu embeddingów z ponawianiem przy rate-limit, międzyplatformowe poprawki zależności oraz naprawa walidacji MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — Natywne SDK OpenAI/Anthropic (rezygnacja z litellm), wsparcie Math Animator dla Windows, odporne parsowanie JSON oraz pełna chińska i18n.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Przeładowywanie ustawień na gorąco, zagnieżdżone wyjście MinerU, poprawka WebSocket oraz minimum Python 3.11+.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Przepisanie architektury natywnej dla agentów (~200 tys. linii): model wtyczek Tools + Capabilities, CLI i SDK, TutorBot, Co-Writer, Guided Learning oraz trwała pamięć.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Trwałość sesji, przyrostowe przesyłanie dokumentów, elastyczny import potoku RAG i pełna lokalizacja chińska.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Wsparcie Docling dla RAG-Anything, optymalizacja systemu logowania oraz poprawki błędów.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Zunifikowana konfiguracja usług, wybór potoku RAG dla każdej bazy wiedzy, przebudowa generowania pytań oraz personalizacja paska bocznego.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Wsparcie wielu dostawców LLM i embeddingów, nowa strona główna, oddzielenie modułu RAG oraz refaktor zmiennych środowiskowych.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Zunifikowana architektura PromptManager, CI/CD oparte na GitHub Actions oraz gotowe obrazy Docker na GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Wdrożenie Docker, aktualizacja Next.js 16 i React 19, wzmocnienie bezpieczeństwa WebSocket oraz krytyczne poprawki luk.

</details>

### 📰 Aktualności

> **[2026.4.19]** 🎉 Osiągnęliśmy 20 tys. gwiazdek po 111 dniach! Dziękujemy za niesamowite wsparcie — zobowiązujemy się do dalszej iteracji w stronę naprawdę spersonalizowanych, inteligentnych korepetycji dla każdego.

> **[2026.4.10]** 📄 Nasz artykuł jest już dostępny na arXiv! Przeczytaj [preprint](https://arxiv.org/abs/2604.26962), aby dowiedzieć się więcej o projekcie i ideach stojących za DeepTutor.

> **[2026.4.4]** Dawno się nie widzieliśmy! ✨ DeepTutor v1.0.0 jest wreszcie tutaj — agentowa ewolucja z przebudowaną od podstaw architekturą, TutorBot oraz elastycznym przełączaniem trybów na licencji Apache-2.0. Zaczyna się nowy rozdział, a nasza historia trwa dalej!

> **[2026.2.6]** 🚀 Osiągnęliśmy 10 tys. gwiazdek w zaledwie 39 dni! Ogromne podziękowania dla naszej niesamowitej społeczności za wsparcie!

> **[2026.1.1]** Szczęśliwego Nowego Roku! Dołącz do naszego [Discorda](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) lub [Dyskusji](https://github.com/HKUDS/DeepTutor/discussions) — wspólnie kształtujmy przyszłość DeepTutor!

> **[2025.12.29]** DeepTutor zostaje oficjalnie wydany!


<a id="key-features"></a>
## ✨ Kluczowe funkcje

**Powierzchnie pracy**

- Chat — Chat, Solve, Quiz, Research oraz Visualize współdzielą jedną sesję, bazę wiedzy i historię cytatów, więc można eskalować w trakcie rozmowy bez utraty kontekstu.
- Co-Writer — przestrzeń Markdown z widokiem podzielonym, w której dowolne zaznaczenie można przepisać, rozwinąć lub skrócić, opcjonalnie zakotwiczone w Twoim KB lub w sieci. Wersje robocze zapisują się prosto do notatników.
- Book Engine — potok wieloagentowy kompiluje Twoje materiały w interaktywne „żywe książki” z 13 typami bloków: quizy, fiszki, osie czasu, grafy pojęć, osadzony viewer GeoGebra, animacje i inne. Strony są oznaczone odciskami palców KB, więc dryf jest wykrywalny.

**Twoja biblioteka**

- Knowledge Bases — wersjonowane zbiory gotowe dla RAG, w całości na LlamaIndex. Każde (ponowne) indeksowanie jest śledzone, porównywalne i można je cofnąć.
- Space — osobista biblioteka powtórek łącząca historię czatu, notatniki, bank pytań oraz Skills tworzone przez użytkownika (`SKILL.md`), które zmieniają personę DeepTutor.
- Trójwarstwowa Memory — append-only ślady L1, kurowane fakty per-powierzchnia L2 z cytatami oraz synteza międzypowierzchniowa L3. Inspektowalny workbench i Memory Graph pozwalają audytować, *dlaczego* DeepTutor wie to, co wie.

**Rozszerzalność i kontrola**

- Komponowalne narzędzia — RAG, wyszukiwanie webowe, wykonanie kodu, rozumowanie, brainstorming, wyszukiwanie artykułów, analiza GeoGebra oraz pomocnicy czatu (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). Serwery MCP podpinają się obok wbudowanych narzędzi.
- Osobiste TutorBoty — trwałe, autonomiczne korepetytorzy, każdy z własnym workspace, Soul, Skills i kanałami (Telegram, Discord, Slack, Matrix, Zulip, …). Zbudowane na [nanobot](https://github.com/HKUDS/nanobot).
- Zunifikowane Settings — jeden workbench draft / Apply dla wyglądu, modeli, embeddingów, wyszukiwania, capabilities, memory, serwerów MCP oraz narzędzi, ze wspólnym śledzeniem kosztu per wywołanie.
- CLI natywne dla agentów — każda funkcja, KB, sesja oraz TutorBot dostępne jednym poleceniem; bogate wyjście dla ludzi, ustrukturyzowany JSON dla agentów. Przekaż dowolnemu LLM-owi z narzędziami plik [`SKILL.md`](../../SKILL.md) i sam pokieruje DeepTutor.
- Opcjonalne uwierzytelnianie — domyślnie wyłączone; włącz dla wdrożeń wieloużytkownikowych z bcrypt + JWT, panelem administratora oraz opcjonalnym sidecarem PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 Jak zacząć

DeepTutor ma teraz cztery równoległe ścieżki instalacji. Wszystkie korzystają z tego samego układu konfiguracji runtime:

- Ustawienia żyją w `data/user/settings/` w bieżącej przestrzeni roboczej lub pod `DEEPTUTOR_HOME` / `deeptutor start --home`, jeśli wybierzesz jedną wprost.
- `model_catalog.json` przechowuje profile dostawców modeli, base URL, klucze API, aktywne modele, ustawienia embeddingów oraz wyszukiwania.
- `system.json` przechowuje porty startowe, publiczny API base, CORS, TLS oraz opcje załączników.
- `auth.json` przechowuje opcjonalny przełącznik auth oraz hash danych startowych.
- `integrations.json` przechowuje opcjonalne sidecary, takie jak PocketBase.
- `.env` w katalogu głównym projektu nie jest już używany jako plik konfiguracyjny aplikacji.

Dla pełnej aplikacji lokalnej zalecana kolejność to **wybierz workspace → zainstaluj → `deeptutor init` → `deeptutor start`**. `deeptutor start` może uzupełnić brakujące domyślne pliki jako siatka bezpieczeństwa, ale normalna konfiguracja pierwszego uruchomienia powinna iść przez `deeptutor init`, aby porty i ustawienia modeli były jawne przed startem aplikacji webowej.

### Opcja 1 — Zainstaluj DeepTutor

Użyj tej opcji, gdy chcesz mieć pełną lokalną aplikację webową i CLI bez klonowania repozytorium.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **Próbujesz wersji v1.4.0 beta?** PyPI normalizuje `1.4.0-beta` do `1.4.0b0`, więc `pip install -U deeptutor` pozostanie na najnowszej wersji stabilnej. Włącz pre-release za pomocą jednego z:
>
> ```bash
> pip install --pre -U deeptutor      # najnowsze pre-release
> pip install -U deeptutor==1.4.0b0   # przypnij dokładnie do v1.4.0-beta
> ```

`deeptutor init` zapisuje konfigurację pod `data/user/settings/` w katalogu, w którym to uruchamiasz. Pyta o:

- Port backendu, domyślnie `8001`
- Port frontendu, domyślnie `3782`
- Powiązanie dostawcy LLM, base URL, klucz API oraz nazwę modelu
- Opcjonalnego dostawcę embeddingów dla Knowledge Base / RAG

Po `deeptutor start` otwórz adres frontendu wypisany w terminalu. Z domyślnymi portami jest to [http://127.0.0.1:3782](http://127.0.0.1:3782). Jeśli zmieniłeś `frontend_port` podczas `deeptutor init` lub później edytowałeś `data/user/settings/system.json`, użyj tego skonfigurowanego portu.

Pozostaw terminal `deeptutor start` otwarty. Naciśnij `Ctrl+C` w tym terminalu, aby zatrzymać backend i frontend.

Uwagi:

- `deeptutor start` uruchamia razem backend FastAPI oraz spakowany frontend Next.js.
- Spakowana aplikacja webowa nie wymaga `git clone` ani `npm install`, ale wciąż potrzebuje lokalnego runtime Node.js 20+ do uruchomienia spakowanego serwera standalone Next.js.
- Jeśli świadomie pominiesz `deeptutor init` dla szybkiego testu, aplikacja startuje z bezpiecznymi domyślnymi portami i pustymi ustawieniami modeli; skonfiguruj modele później w **Settings → Models**.

### Opcja 2 — Instalacja ze źródeł

Użyj tej opcji, gdy rozwijasz DeepTutor lub chcesz uruchomić bezpośrednio z checkoutu.
Użyj Python 3.11+ oraz Node.js 22 LTS dla najbliższego dopasowania do CI i Dockera.

**1. Sklonuj repozytorium**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Utwórz środowisko Python**

macOS / Linux z `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell z `venv`:

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

**3. Zainstaluj lokalny pakiet i zależności frontendu**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

Jeśli celowo zmieniasz zależności frontendu, użyj `npm install --legacy-peer-deps`,
aby odświeżyć `web/package-lock.json`, a następnie zatwierdź zarówno `web/package.json`,
jak i `web/package-lock.json`.

**4. Skonfiguruj i uruchom**

```bash
deeptutor init
deeptutor start
```

Instalacje ze źródeł używają lokalnego katalogu `web/` dla frontendu i uruchamiają go
w trybie deweloperskim Next.js. Pozostaw terminal `deeptutor start` otwarty podczas
korzystania z aplikacji. Są one celowo przyjazne dla deweloperów i nie zapisują konfiguracji do
`.env`; edytuj `data/user/settings/*.json` lub użyj strony Web Settings.

Jeśli `deeptutor start` zgłosi istniejący frontend, który nie odpowiada, zatrzymaj
PID wypisany w komunikacie. Jeśli żaden proces Next.js nie działa, usuń
przestarzałe pliki blokady i uruchom ponownie:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

Przydatne dodatki deweloperskie:

```bash
pip install -e ".[dev]"             # narzędzia tests/lint
pip install -e ".[tutorbot]"        # silnik TutorBot + SDK kanałów
pip install -e ".[matrix]"          # kanał Matrix bez E2EE/libolm
pip install -e ".[matrix-e2e]"      # Matrix E2EE; wymaga libolm
pip install -e ".[math-animator]"   # dodatek Manim; wymaga LaTeX/ffmpeg/bibliotek systemowych
```

### Opcja 3 — Docker

Użyj tej opcji, gdy chcesz mieć pełną aplikację webową w jednym kontenerze. Obrazy są publikowane do GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — stabilne wydanie
- `ghcr.io/hkuds/deeptutor:pre` — pre-release, gdy dostępne

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Następnie otwórz [http://127.0.0.1:3782](http://127.0.0.1:3782). Konfiguracja, klucze API, logi, pliki workspace, pamięć oraz bazy wiedzy są przechowywane w wolumenie `deeptutor-data` pod `/app/data`.

Kontener automatycznie tworzy `/app/data/user/settings/*.json` przy pierwszym starcie. Możesz konfigurować dostawców modeli bezpośrednio na stronie Web Settings bez ręcznego przygotowywania lokalnych plików JSON.

Aby użyć innych portów hosta, zmień lewą stronę mapowań `-p`. Na przykład `-p 127.0.0.1:8088:3782` udostępnia UI webowe pod `http://127.0.0.1:8088`, podczas gdy kontener wciąż nasłuchuje na `3782`. Jeśli zmienisz porty po stronie kontenera w `/app/data/user/settings/system.json`, zrestartuj kontener i dopasuj prawą stronę każdego mapowania `-p host:container` do skonfigurowanego portu kontenera.

#### Łączenie z Ollama lub innymi usługami hosta

Wewnątrz kontenera Docker `localhost` odnosi się do samego kontenera, a nie do Twojej maszyny hosta. Jeśli uruchamiasz Ollama, LM Studio, llama.cpp, vLLM lub inną usługę modelu na hoście, użyj jednego z poniższych podejść.

Opcja A — bramka hosta, zalecana dla normalnych uruchomień Docker:

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Następnie w **DeepTutor Settings → Models** ustaw Base URL dostawcy na `host.docker.internal`:

- Endpoint LLM Ollama: `http://host.docker.internal:11434/v1`
- Endpoint embeddingów Ollama: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

W Docker Desktop dla macOS/Windows `host.docker.internal` jest zwykle dostępny nawet bez `--add-host`. W Linuksie flaga `--add-host=host.docker.internal:host-gateway` jest przenośnym sposobem utworzenia tej nazwy hosta na nowoczesnym Docker Engine.

Opcja B — sieć hosta, tylko Linux:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

W trybie sieci hosta mapowanie `-p` nie jest potrzebne. Kontener współdzieli sieć hosta bezpośrednio, więc otwórz domyślnie [http://127.0.0.1:3782](http://127.0.0.1:3782) lub `frontend_port` skonfigurowany w `/app/data/user/settings/system.json`. W tym trybie usługi hosta są zwykle osiągalne pod normalnymi URL-ami localhost, takimi jak `http://127.0.0.1:11434/v1`. Sieć hosta wystawia porty kontenera bezpośrednio na hoście i może powodować konflikty z istniejącymi usługami.

Aby uruchomić w tle, dodaj `-d` i śledź logi po nazwie:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

Aby zatrzymać uruchomienie Docker pierwszoplanowe, naciśnij `Ctrl+C`. Jeśli użyłeś nazwanego, odłączonego
kontenera powyżej, uruchom `docker stop deeptutor`. Przed uruchomieniem kolejnego kontenera
o tej samej nazwie usuń zatrzymany za pomocą `docker rm deeptutor`; wolumen
`deeptutor-data` zachowuje Twoje ustawienia i workspace.

### Opcja 4 — Tylko CLI

Użyj tej opcji, gdy nie potrzebujesz Web UI. Pakiet CLI-only instaluje się
z lokalnego checkoutu źródeł zamiast z PyPI.

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

`deeptutor init --cli` używa tego samego układu `data/user/settings/` co pełna aplikacja, ale zmienia zachowanie kreatora:

- Pomija pytania o porty backend/frontend, ponieważ użycie CLI-only nie uruchamia aplikacji webowej.
- Nadal zapisuje domyślne `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml` oraz `agents.yaml`, aby układ runtime był kompletny.
- Nadal pyta o aktywnego dostawcę LLM oraz model.
- Pyta, czy skonfigurować embeddingi, ale domyślna odpowiedź to `No`; wybierz `Yes`, jeśli planujesz używać `deeptutor kb ...` lub narzędzi RAG.

Częste komendy CLI:

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

Lokalna instalacja `deeptutor-cli` nie dostarcza zasobów webowych ani zależności serwera.
Pozostaw checkout źródeł w pobliżu, ponieważ instalacja editable wskazuje na niego. Jeśli
później zechcesz aplikację webową, podążaj za Opcją 2 w tym samym checkoutcie albo odinstaluj
lokalny pakiet CLI, zainstaluj pełny pakiet PyPI za pomocą `pip install -U
deeptutor`, uruchom `deeptutor init`, jeśli chcesz dodać porty webowe, a następnie uruchom
`deeptutor start` z tej samej przestrzeni roboczej.

### Referencja konfiguracji

Strona Web Settings jest zalecanym edytorem, ale pliki to zwykły JSON/YAML i można nimi zarządzać bezpośrednio:

| Plik | Cel |
|:---|:---|
| `data/user/settings/model_catalog.json` | Profile dostawców LLM, embeddingów i wyszukiwania; klucze API; aktywne modele |
| `data/user/settings/system.json` | Porty backend/frontend, publiczny API base, CORS, weryfikacja SSL, katalog załączników |
| `data/user/settings/auth.json` | Opcjonalny przełącznik auth, nazwa użytkownika, hash hasła, ustawienia tokenów/cookies |
| `data/user/settings/integrations.json` | Opcjonalne ustawienia PocketBase i integracji sidecar |
| `data/user/settings/interface.json` | Preferencje języka UI / motywu / paska bocznego |
| `data/user/settings/main.yaml` | Domyślne zachowanie runtime i wstrzykiwanie ścieżek |
| `data/user/settings/agents.yaml` | Ustawienia temperatury i tokenów capability/tool |

Minimalna konfiguracja modelu może być wykonana w przeglądarce: otwórz **Settings → Models**, dodaj profil LLM, ustaw Base URL / klucz API / nazwę modelu i zapisz. Dodaj profil embeddingów tylko jeśli planujesz korzystać z funkcji Knowledge Base / RAG.

<a id="explore-deeptutor"></a>
## 📖 Odkrywaj DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

Refaktor v1.4.0-beta reorganizuje DeepTutor wokół **pięciu głównych powierzchni** — Chat, Co-Writer, Book, Knowledge, Space — plus **trójwarstwowa Memory**, która leży pod nimi wszystkimi, oraz zunifikowany workbench **Settings**, który eksponuje każde pokrętło. Capabilities (Solve / Quiz / Research / Visualize) i narzędzia (RAG, web, code, reason, brainstorm, paper search, `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) komponują się swobodnie na wierzchu.

### 💬 Chat — Zunifikowana inteligentna przestrzeń robocza

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Jeden wątek, pięć trybów, dowolne narzędzie. Wybór capability mieszka w okienku tworzenia wiadomości; ta sama sesja, baza wiedzy, załączniki i odniesienia podróżują z Tobą pomiędzy trybami — przełącz się z luźnego pytania w wieloagentowe rozwiązywanie, w quiz, w pełny raport badawczy, bez utraty kontekstu.

| Tryb | Co robi | Zbudowany na |
|:---|:---|:---|
| **Chat** | Elastyczna rozmowa z dowolnym narzędziem; wybierz z RAG, wyszukiwania webowego, wykonania kodu, głębokiego rozumowania, brainstormingu, wyszukiwania artykułów, analizy GeoGebra. | RAG zasilany przez LlamaIndex + rejestr narzędzi |
| **Solve** | Wieloetapowy plan → zbadaj → rozwiąż → zweryfikuj, z precyzyjnymi cytatami źródeł. | Silnik agentowy (`deep_solve`) |
| **Quiz** | Auto-walidowane generowanie pytań ugruntowane w Twoim KB; tworzy okienko follow-up dla każdego pytania. | Silnik agentowy (`deep_question`) |
| **Research** | Dekomponuje temat na podtematy, wysyła równoległych agentów po RAG / web / arXiv i tworzy raport z cytatami z iteracyjnymi rewizjami w trybie append. | Przebudowany `pipeline.py` (~45% mniejszy, cytaty + iteracyjne raportowanie zachowane) |
| **Visualize** | Generuje diagramy SVG, wykresy Chart.js, grafy Mermaid, interaktywne strony HTML **lub** filmy / storyboardy Manim — analizator wybiera odpowiedni `render_type`. | Potok Visualize (włączony Animator) |

**Nowe narzędzia czatu** dostarczone z refaktorem: `ask_user` (zadaje ustrukturyzowane pytanie wyjaśniające w połowie tury), `web_fetch` (pobiera konkretny URL do kontekstu), `write_note` / `list_notebook` (zapisuje i listuje rekordy notatników z powierzchni czatu) oraz `github_query` (wyszukiwanie issue / PR / repo). Narzędzia pozostają **oddzielone od przepływów pracy** — każdy tryb pozwala włączać lub wyłączać narzędzia per tura.

Sesja przenosi również **skumulowany inwentarz źródeł** pomiędzy turami, więc cytaty z wcześniejszych trafień RAG / web pozostają możliwe do ponownego użycia później w tej samej rozmowie.

### ✍️ Co-Writer — Wielodokumentowa przestrzeń pisania AI

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer to workbench Markdown z widokiem podzielonym (surowy edytor po lewej, podgląd na żywo po prawej) dla notatek, raportów, samouczków i wersji roboczych wspomaganych AI. Każdy dokument żyje we własnej przestrzeni roboczej z autozapisem, pobieralnym Markdown i jednym kliknięciem **Save to Notebook**.

Zaznacz dowolny tekst i wybierz **Rewrite**, **Expand** lub **Shorten** — każda akcja działa jako śledzona edycja agenta, która może opcjonalnie czerpać z bazy wiedzy lub sieci. Co-Writer renderuje standardowy Markdown / CommonMark / GFM (tabele, kod, matematyka, diagramy przepływu, diagramy sekwencji), wspiera furtkę tagów HTML (`<sub>`, `<sup>`, `<abbr>`, `<mark>`) i zawiera szablon startowy dostrojony do dokumentów produktowych DeepTutor i notatek do nauki.

### 📖 Book Engine — Interaktywne „żywe książki”

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

Daj DeepTutor temat, wskaż mu Twoją bazę wiedzy, a wyprodukuje strukturalną, interaktywną książkę — nie statyczny eksport, lecz żywy dokument, który możesz czytać, samodzielnie odpytywać i omawiać w kontekście.

Za kulisami potok wieloagentowy zajmuje się ciężką robotą: proponowaniem konspektu, pobieraniem odpowiednich źródeł z Twojego KB, syntezą drzewa rozdziałów, planowaniem każdej strony i kompilowaniem każdego bloku. Ty pozostajesz w kontroli — przejrzyj propozycję, zmień kolejność rozdziałów i rozmawiaj obok dowolnej strony.

Strony są składane z 13 typów bloków — tekst, callout, quiz, fiszki, kod, rysunek, deep dive, animacja, demo interaktywne (teraz włącznie z **GeoGebra viewer**), oś czasu, graf pojęć, sekcja i notatka użytkownika — każdy renderowany ze swoim własnym komponentem interaktywnym. Strony książki są oznaczone odciskami palców względem ich źródłowego KB; `deeptutor book health` raportuje dryf, a `deeptutor book refresh-fingerprints` czyści przestarzałe strony, gdy źródła się zmieniają.

### 📚 Knowledge Bases — Biblioteki dokumentów gotowe dla RAG

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

Dedykowana przestrzeń robocza dla kolekcji dokumentów zasilających RAG. Każda baza wiedzy ma cztery zakładki:

- **Files** — Przeglądaj przesłane źródła, podglądaj PDF-y inline i zobacz rozmiar / status per plik.
- **Add documents** — Wrzucaj PDF-y, pliki Office (DOCX / XLSX / PPTX), Markdown, zwykły tekst oraz szeroki zakres typów plików kodu / danych. Dokumenty są automatycznie kierowane przez odpowiedni ekstraktor.
- **Index versions** — Każde (ponowne) indeksowanie to śledzona wersja. Cofnij się do wcześniejszego indeksu, porównaj modele embeddingów lub zbadaj statystyki chunkingu bez utraty poprzedniej kompilacji.
- **Settings** — Wybierz dostawcę / model embeddingów, parametry chunkingu oraz reranker dla KB. Domyślne wartości są dziedziczone z Twoich globalnych profili LLM i embeddingów.

Indeksowanie zbudowane jest na **LlamaIndex** end-to-end (poprzedni podział na dwa potoki został skonsolidowany w refaktorze v1.4), z bezpieczną ponowną indeksacją, wykrywaniem niedopasowania embeddingów i odporną obsługą uszkodzonych zapisanych wektorów.

### 🌐 Space — Twoja osobista biblioteka nauki

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space jest odpowiednikiem **odczyt / przegląd** dla aktywnych powierzchni. Tam, gdzie Chat / Co-Writer / Book są miejscem, gdzie *produkujesz*, Space jest miejscem, gdzie wszystko, co produkujesz, mieszka, przeszukiwalne i odtwarzalne.

- **Chat History** — Każda rozmowa we wszystkich trybach, ze zmianą nazwy tytułu, usuwaniem i wznawianiem; usuwanie poszczególnych tur jest wspierane w każdym punkcie wejścia.
- **Notebooks** — Zapisuj wyjścia z Chat, Research i Co-Writer w skategoryzowanych, oznaczonych kolorem notatnikach; każdy rekord linkuje z powrotem do źródłowej sesji i powierzchni.
- **Question Bank** — Każde auto-generowane pytanie quizowe, możliwe do dodania do zakładek i wzmiankowania @-em w czacie, aby rozumować nad przeszłą wydajnością.
- **Skills** — Pliki `SKILL.md` tworzone przez użytkownika, które definiują persony nauczania (nazwa, opis, wyzwalacze, treść). Gdy aktywne, skill jest wstrzykiwany w system prompt czatu — zamieniając DeepTutor w sokratejskiego tutora, asystenta badawczego lub dowolną rolę, którą zaprojektujesz.

### 🧠 Memory — Architektura trójwarstwowa

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

Memory DeepTutor jest teraz **trójwarstwowym potokiem** z inspektowalnym workbenchem pod `/memory`. Dwuplikowy model v1 `SUMMARY.md` / `PROFILE.md` zniknął; wszystko jest migrowane do nowego układu przy pierwszym starcie.

| Warstwa | Rola | Magazyn |
|:---|:---|:---|
| **L1 · Lustro przestrzeni roboczej** (LIVE) | Append-only ślad każdej interakcji, per powierzchnia, per dzień. Bezstratny zapis tego, co rzeczywiście się wydarzyło. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Podsumowania per powierzchnia** (CURATED) | Fakty specyficzne dla powierzchni wyekstrahowane przez konsolidator. Każdy fakt niesie cytaty przypisów z powrotem do śladów L1. Wspiera per-doc **Update / Audit / Dedup**. | `L2/<surface>.md` |
| **L3 · Wiedza międzypowierzchniowa** (SYNTHESIS) | Synteza międzypowierzchniowa: Twój `profile`, oś czasu `recent`, `scope` wiedzy oraz `preferences`. Hedgowane stwierdzenia, każde poparte dowodem L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

Siedem powierzchni zasila potok: **chat, notebook, quiz, kb, book, tutorbot, cowriter**. Konsolidator jest sterowany przez LLM i działa asynchronicznie (`POST /memory/runs/start`) — możesz odpalić go z workbencha, obserwować propagację L1 → L2 → L3 i edytować dowolną warstwę ręcznie.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

**Memory Graph** (`/memory/graph`) renderuje wszystkie trzy warstwy naraz: synteza L3 w centrum, fakty L2 w środkowym pierścieniu, ślady L1 na zewnątrz, pogrupowane według powierzchni. Najedź na dowolny węzeł, aby zobaczyć podgląd inline; kliknij, aby zablokować podświetlenie i prześledzić referencje L3 → L2 → L1 do wewnątrz, aby móc audytować, *dlaczego* DeepTutor „wie” coś o Tobie.

### ⚙️ Settings — Zunifikowane centrum kontroli

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

Powierzchnia ustawień została zunifikowana w v1.4 i podzielona według trosk, z modelem draft / **Apply**, więc zmiany są atomowe i można je cofnąć przed zapisem:

- **Appearance** — Język UI i motyw (Cream, Snow, Dark, Glass).
- **Status** — Sonda zdrowia na żywo dla LLM, embeddingów, wyszukiwania i backendów magazynu.
- **LLM**, **Embedding**, **Search** — Katalog dostawców, base URL-e, klucze API i wybór aktywnego modelu. Aktywne modele są wybierane z katalogu, więc każda powierzchnia pozostaje w synchronizacji.
- **Capabilities** — Tunable per-capability (chunking, budżet LLM, polityki dedup i referencji, max iteracji) dla Chat, Solve, Quiz, Research, Visualize oraz Co-Writer. Wsparte przez zunifikowaną kopertę `emit_capability_result` oraz wspólny `UsageTracker`, który eksponuje koszt per wywołanie.
- **Memory** — Przełącz uruchomienia konsolidatora, skonfiguruj rytm i budżet oraz wejdź do workbencha pamięci.
- **MCP servers** — Zarejestruj zewnętrzne serwery Model Context Protocol; ich narzędzia są eksponowane obok wbudowanych.
- **Tools** — Zbadaj każde wbudowane narzędzie, jego parametry, status (włączone / wkrótce) oraz tłumaczenia statusu i18n.

Launcher „Tour” prowadzi nowych użytkowników przez stronę, a każda capability dostarcza kanoniczny `capabilities/prompts/{en,zh}/<name>.yaml`, więc komunikaty statusu pozostają spójne zarówno w języku angielskim, jak i 中文.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — Trwałe, autonomiczne AI-korepetytorzy

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot to nie chatbot — to **trwały, wieloinstancyjny agent** zbudowany na [nanobot](https://github.com/HKUDS/nanobot). Każdy TutorBot uruchamia własną pętlę agenta z niezależną przestrzenią roboczą, pamięcią i osobowością. Utwórz sokratejskiego korepetytora matematyki, cierpliwego trenera pisania i rygorystycznego doradcę badawczego — wszyscy działający jednocześnie, każdy ewoluujący z Tobą.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Soul Templates** — Definiuj osobowość, ton i filozofię nauczania Twojego tutora poprzez edytowalne pliki Soul. Wybierz spośród wbudowanych archetypów (sokratejski, motywujący, rygorystyczny) lub stwórz własne — Soul kształtuje każdą odpowiedź.
- **Niezależny workspace** — Każdy bot ma własny katalog z oddzielną pamięcią, sesjami, Skills i konfiguracją — w pełni izolowany, ale zdolny do dostępu do współdzielonej warstwy wiedzy DeepTutor.
- **Proaktywny Heartbeat** — Boty nie tylko odpowiadają — inicjują. Wbudowany system Heartbeat umożliwia powtarzające się przypomnienia o nauce, przypomnienia o powtórkach i zaplanowane zadania. Twój tutor pojawia się nawet wtedy, gdy Ty nie.
- **Pełny dostęp do narzędzi** — Każdy bot sięga do kompletnego zestawu narzędzi DeepTutor: pobieranie RAG, wykonanie kodu, wyszukiwanie webowe, wyszukiwanie artykułów akademickich, głębokie rozumowanie i brainstorming.
- **Uczenie się Skills** — Naucz Twojego bota nowych zdolności, dodając pliki Skill do jego workspace. W miarę jak Twoje potrzeby się rozwijają, rozwijają się też możliwości Twojego tutora.
- **Obecność wielokanałowa** — Połącz boty z Telegramem, Discordem, Slackiem, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, Emailem i więcej. Twój tutor spotyka Cię tam, gdzie jesteś.
- **Zespół i Sub-Agenci** — Twórz sub-agentów w tle lub orkiestruj zespoły wieloagentowe w obrębie pojedynczego bota dla złożonych, długo działających zadań.

```bash
deeptutor bot create math-tutor --persona "Socratic math teacher who uses probing questions"
deeptutor bot create writing-coach --persona "Patient, detail-oriented writing mentor"
deeptutor bot list                  # Zobacz wszystkich aktywnych tutorów
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — Interfejs natywny dla agentów

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor jest w pełni natywny dla CLI. Każda capability, baza wiedzy, sesja, memory i TutorBot są dostępne jednym poleceniem — bez konieczności przeglądarki. CLI służy zarówno ludziom (z bogatym renderingiem terminalowym), jak i agentom AI (z ustrukturyzowanym wyjściem JSON).

Przekaż [`SKILL.md`](../../SKILL.md) z katalogu głównego projektu dowolnemu agentowi używającemu narzędzi ([nanobot](https://github.com/HKUDS/nanobot) lub dowolny LLM z dostępem do narzędzi), a będzie mógł konfigurować i obsługiwać DeepTutor autonomicznie.

**Wykonanie jednorazowe** — Uruchom dowolną capability bezpośrednio z terminala:

```bash
deeptutor run chat "Explain the Fourier transform" -t rag --kb textbook
deeptutor run deep_solve "Prove that √2 is irrational" -t reason
deeptutor run deep_question "Linear algebra" --config num_questions=5
deeptutor run deep_research "Attention mechanisms in transformers"
deeptutor run visualize "Draw the architecture of a transformer"
```

**Interaktywny REPL** — Trwała sesja czatu z przełączaniem trybów na żywo:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Wewnątrz REPL: /cap, /tool, /kb, /history, /notebook, /config aby przełączać w locie
```

**Cykl życia bazy wiedzy** — Buduj, odpytuj i zarządzaj kolekcjami gotowymi dla RAG w całości z terminala:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # Utwórz z dokumentu
deeptutor kb add my-kb --docs-dir ./papers/         # Dodaj folder artykułów
deeptutor kb search my-kb "gradient descent"        # Szukaj bezpośrednio
deeptutor kb set-default my-kb                      # Ustaw jako domyślną dla wszystkich poleceń
```

**Tryb podwójnego wyjścia** — Bogaty rendering dla ludzi, ustrukturyzowany JSON dla potoków:

```bash
deeptutor run chat "Summarize chapter 3" -f rich    # Kolorowe, sformatowane wyjście
deeptutor run chat "Summarize chapter 3" -f json    # Zdarzenia JSON oddzielone liniami
```

**Ciągłość sesji** — Wznów dowolną rozmowę dokładnie tam, gdzie ją zostawiłeś:

```bash
deeptutor session list                              # Lista wszystkich sesji
deeptutor session open <id>                         # Wznów w REPL
```

<details>
<summary><b>Pełna referencja poleceń CLI</b></summary>

**Najwyższy poziom**

| Polecenie | Opis |
|:---|:---|
| `deeptutor run <capability> <message>` | Uruchom dowolną capability w jednej turze (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | Interaktywny REPL z opcjonalnym `--capability`, `--tool`, `--kb`, `--language` |
| `deeptutor serve` | Uruchom serwer API DeepTutor |

**`deeptutor bot`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor bot list` | Lista wszystkich instancji TutorBot |
| `deeptutor bot create <id>` | Utwórz i uruchom nowego bota (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Uruchom bota |
| `deeptutor bot stop <id>` | Zatrzymaj bota |

**`deeptutor kb`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor kb list` | Lista wszystkich baz wiedzy |
| `deeptutor kb info <name>` | Pokaż szczegóły bazy wiedzy |
| `deeptutor kb create <name>` | Utwórz z dokumentów (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Dodawaj dokumenty przyrostowo |
| `deeptutor kb search <name> <query>` | Przeszukaj bazę wiedzy |
| `deeptutor kb set-default <name>` | Ustaw jako domyślną KB |
| `deeptutor kb delete <name>` | Usuń bazę wiedzy (`--force`) |

**`deeptutor memory`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor memory show [file]` | Wyświetl pamięć (`summary`, `profile` lub `all`) |
| `deeptutor memory clear [file]` | Wyczyść pamięć (`--force`) |

**`deeptutor session`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor session list` | Lista sesji (`--limit`) |
| `deeptutor session show <id>` | Wyświetl wiadomości sesji |
| `deeptutor session open <id>` | Wznów sesję w REPL |
| `deeptutor session rename <id>` | Zmień nazwę sesji (`--title`) |
| `deeptutor session delete <id>` | Usuń sesję |

**`deeptutor notebook`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor notebook list` | Lista notatników |
| `deeptutor notebook create <name>` | Utwórz notatnik (`--description`) |
| `deeptutor notebook show <id>` | Wyświetl rekordy notatnika |
| `deeptutor notebook add-md <id> <path>` | Importuj markdown jako rekord |
| `deeptutor notebook replace-md <id> <rec> <path>` | Zastąp rekord markdown |
| `deeptutor notebook remove-record <id> <rec>` | Usuń rekord |

**`deeptutor book`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor book list` | Lista wszystkich książek w workspace |
| `deeptutor book health <book_id>` | Sprawdź dryf KB i zdrowie książki |
| `deeptutor book refresh-fingerprints <book_id>` | Odśwież odciski palców KB i wyczyść przestarzałe strony |

**`deeptutor config` / `plugin` / `provider`**

| Polecenie | Opis |
|:---|:---|
| `deeptutor config show` | Wypisz podsumowanie bieżącej konfiguracji |
| `deeptutor plugin list` | Lista zarejestrowanych narzędzi i capabilities |
| `deeptutor plugin info <name>` | Pokaż szczegóły narzędzia lub capability |
| `deeptutor provider login <provider>` | Auth dostawcy (`openai-codex` logowanie OAuth; `github-copilot` waliduje istniejącą sesję auth Copilot) |

</details>

---

<a id="multi-user"></a>
### 👥 Multi-User — Współdzielone wdrożenia z przestrzeniami roboczymi per użytkownik

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Włącz uwierzytelnianie, a DeepTutor zamienia się we wdrożenie multi-tenant z **izolowanymi przestrzeniami roboczymi per użytkownik** oraz **zasobami kurowanymi przez administratora**. Pierwsza osoba, która się rejestruje, staje się administratorem i konfiguruje modele, klucze API i bazy wiedzy w imieniu wszystkich pozostałych. Kolejne konta są tworzone przez administratora (tylko z zaproszenia), każde dostaje własne ograniczone czaty / pamięć / notatniki / bazy wiedzy i widzi tylko LLM-y, KB i Skills, które administrator im przypisał.

**Szybki start (5 kroków):**

```bash
# 1. Włącz auth w data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Zrestartuj stack webowy.
deeptutor start

# 3. Otwórz http://localhost:3782/register i utwórz pierwsze konto.
#    Pierwsza rejestracja jest jedyną publiczną; ten użytkownik staje się
#    administratorem, a endpoint /register jest automatycznie zamykany.

# 4. Jako administrator przejdź do /admin/users → "Add user", aby
#    udostępnić konta zespołowi.

# 5. Dla każdego użytkownika kliknij ikonę suwaka → przypisz profile LLM,
#    bazy wiedzy i Skills. Zapisz. Użytkownik może już się zalogować i pracować.
```

**Co widzi administrator:**

- **Pełna strona Settings** pod `/settings` — zarządzaj dostawcami LLM / embeddingów / wyszukiwania, kluczami API, katalogami modeli oraz runtime „Apply”.
- **Zarządzanie użytkownikami** pod `/admin/users` — twórz, awansuj, degraduj i usuwaj konta. Publiczny endpoint `/register` jest automatycznie zamykany, gdy istnieje pierwszy administrator; dalsze konta przechodzą przez `POST /api/v1/auth/users` (tylko admin).
- **Edytor grantów** — dla każdego nieadminowego użytkownika wybierz profile modeli, bazy wiedzy i Skills, których może używać. Granty niosą **tylko logiczne ID**; klucze API nigdy nie przekraczają granicy grantu.
- **Ścieżka audytu** — każda zmiana grantu i dostęp do przypisanego zasobu są dopisywane do `multi-user/_system/audit/usage.jsonl`.

**Co dostają zwykli użytkownicy:**

- **Izolowana przestrzeń robocza** pod `multi-user/<uid>/` — własna historia czatu (`chat_history.db`), pamięć (`SUMMARY.md` / `PROFILE.md`), notatniki i osobiste bazy wiedzy. Domyślnie nic nie jest współdzielone.
- **Dostęp tylko do odczytu** do baz wiedzy i Skills przypisanych przez admina, eksponowane inline obok ich własnych zasobów z odznaką „Assigned by admin”.
- **Zredagowana strona Settings** — tylko motyw, język i podsumowanie przyznanych modeli. Klucze API, base URL-e i endpointy dostawców nigdy nie są zwracane dla żądań nieadministratora.
- **Ograniczone LLM** — tury czatu są kierowane przez model przypisany przez admina. Jeśli żaden LLM nie jest przyznany, tura jest odrzucana z góry (żadnego cichego fallbacku do kluczy admina).

**Układ przestrzeni roboczej:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Zhashowane dane uwierzytelniające, role
│   ├── auth/auth_secret         # Sekret podpisujący JWT (auto-generowany)
│   ├── grants/<uid>.json        # Granty zasobów per użytkownik (zarządzane przez admina)
│   └── audit/usage.jsonl        # Ścieżka audytu
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Referencja konfiguracji:**

| Ustawienie | Wymagane | Opis |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Tak | Ustaw na `true`, aby włączyć auth multi-user. Domyślnie `false` (tryb single-user — wszędzie ścieżki admina). |
| `multi-user/_system/auth/auth_secret` | Zalecane | Sekret podpisujący JWT. Auto-generowany przy pierwszym uwierzytelnionym starcie, jeśli brak. |
| `data/user/settings/auth.json: token_expire_hours` | Nie | Czas życia JWT; domyślnie `24`. |
| `data/user/settings/auth.json: username/password_hash` | Nie | Opcjonalne dane startowe headless single-user. Pozostaw puste, gdy używasz rejestracji przez przeglądarkę. |
| `data/user/settings/system.json` | Nie | `deeptutor start` wyprowadza flagi auth frontendu oraz API base z ustawień runtime. |

> ⚠️ **Tryb PocketBase (ustawiony `integrations.pocketbase_url`) jest tylko single-user.** Domyślny schemat PocketBase nie ma pola `role` w `users` (każde logowanie rozstrzyga się jako `role=user`, nie można utworzyć admina), a zapytania `sessions` / `messages` / `turns` nie są filtrowane po `user_id`. Wdrożenia multi-user muszą zachować puste `integrations.pocketbase_url` i używać domyślnego backendu JSON/SQLite.

> ⚠️ **Zalecenie pojedynczego procesu.** Promocja pierwszy-użytkownik-zostaje-adminem jest chroniona w-procesowym `threading.Lock`. Wdrożenia wielo-workerowe powinny aprowizować pierwszego admina offline (start z `auth.json.enabled=false`, zarejestruj admina przez przepływ startowy, następnie ustaw `auth.json.enabled=true`) lub oprzeć magazyn użytkowników na systemie zewnętrznym.

<a id="community"></a>
## 🌐 Społeczność i ekosystem

DeepTutor stoi na ramionach wybitnych projektów open-source:

| Projekt | Rola w DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Ultralekki silnik agenta zasilający TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Kręgosłup potoku RAG i indeksowania dokumentów |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | Generowanie animacji matematycznych sterowane AI dla Math Animator |

**Z ekosystemu HKUDS:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| Prosty i szybki RAG | Framework agenta bez kodu | Zautomatyzowane badania | Ultralekki agent AI |


## 🤝 Współtworzenie

<div align="center">

Mamy nadzieję, że DeepTutor stanie się prezentem dla społeczności. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

Zobacz [CONTRIBUTING.md](../../CONTRIBUTING.md), aby zapoznać się z wytycznymi dotyczącymi konfiguracji środowiska deweloperskiego, standardów kodu i przepływu pull request.

## ⭐ Historia gwiazdek

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

[⭐ Oznacz nas gwiazdką](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Zgłoś błąd](https://github.com/HKUDS/DeepTutor/issues) · [💬 Dyskusje](https://github.com/HKUDS/DeepTutor/discussions)

---

Na licencji [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
