<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor : Tutorat personnalisé natif aux agents

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-CDCFD4"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-CDCFD4"></a>&nbsp;
  <a href="README_FR.md"><img alt="Français" height="40" src="https://img.shields.io/badge/Français-BCDCF7"></a>&nbsp;
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

[Fonctionnalités](#key-features) · [Démarrage](#get-started) · [Découvrir](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [Multi-utilisateur](#multi-user) · [Communauté](#community)

</div>

---

> 🤝 **Toute contribution est la bienvenue !** Stratégie de branches, normes de code et prise en main : [Guide de contribution](../../CONTRIBUTING.md).
>
> 🗺️ **La feuille de route** est publique sur [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — commentez pour voter ou proposer de nouveaux éléments.

### 📦 Versions

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — Atelier Memory trois couches (L1/L2/L3), toutes les capacités de chat reconstruites sur un unique moteur agentique, RAG exclusivement sur LlamaIndex et une surface unifiée Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Correction du CORS Docker distant, `DISABLE_SSL_VERIFY` pour les fournisseurs SDK, citations de blocs de code plus sûres et E2EE Matrix en extension optionnelle.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — TutorBot avec support Zulip et NVIDIA NIM, routage des modèles de raisonnement plus sûr, `deeptutor start`, infobulles de la barre latérale et parité du stockage de sessions.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Déploiements multi-utilisateurs optionnels avec espaces de travail isolés, droits admin, routes d'authentification et accès runtime à portée limitée.

<details>
<summary><b>Versions précédentes (plus de 2 semaines)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Correctifs modèles de raisonnement/fournisseurs, historique d'index Knowledge visible, vidage Co-Writer et édition de modèles plus sûrs.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Sélection de modèles par catalogue (chat et TutorBot), réindexation RAG plus sûre, plafonds de tokens OpenAI Responses, validation de l'éditeur Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Paramètres de lancement locaux plus fluides, requêtes RAG plus sûres, auth embeddings locale clarifiée, mode sombre des réglages peaufiné.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Persistance du chat sur les pages livre et flux de reconstruction, références chat→livre, langage/raisonnement renforcés, extraction RAG durcie.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — Embeddings NVIDIA NIM et Gemini, contexte Space unifié (historique chat/skills/mémoire), instantanés de session, résilience de réindexation RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — URLs d'embedding visibles, réindexation si vecteurs invalides, nettoyage mémoire pour sortie thinking, correctif Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Stabilité : routage RAG et validation embeddings, persistance Docker, saisie IME, robustesse Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Index KB versionnés et flux de réindexation, espace connaissances refait, auto-détection d'embeddings et nouveaux adaptateurs, hub Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Pièces jointes persistantes et tiroir d'aperçu, pipelines sensibles aux PJ, export Markdown TutorBot.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — PJ texte/code/SVG, Setup Tour en une commande, export Markdown du chat, UI KB compacte.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — PJ documents, blocs de raisonnement, éditeur de modèles Soul, Co-Writer vers carnet.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — Skills utilisateur, perf. saisie chat, démarrage auto TutorBot, UI bibliothèque, plein écran visualisation.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Plafonds tokens par étape, régénérer partout, compatibilité RAG & Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Compilateur Book Engine « livre vivant », Co-Writer multi-documents, HTML interactif, @ dans la banque de questions.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Onglet Channels piloté par schéma, pipeline RAG unique, prompts externalisés.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — « Répondre maintenant » universel, sync défilement Co-Writer, panneau réglages unifié, bouton Stop streaming.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Blocs LaTeX, sonde diagnostic LLM, guide Docker & LLM local.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Sessions URL, thème Snow, heartbeat WebSocket et reconnexion auto, registre d'embeddings refondu.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Carnet de questions avec marque-pages, Mermaid dans Visualize, détection mismatch embeddings, Qwen/vLLM, LM Studio & llama.cpp, thème Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Recherche unifiée + SearXNG, correctif changement fournisseur, fuites ressources frontend.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Visualize (Chart.js/SVG), anti-doublons quiz, o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Suivi progression embeddings avec retry limite de débit, correctifs dépendances multiplateforme, validation MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — SDK natif OpenAI/Anthropic (suppression litellm), animateur math Windows, parsing JSON robuste, i18n chinois complet.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Rechargement à chaud des réglages, sortie imbriquée MinerU, correctif WebSocket, Python 3.11+ minimum.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Réécriture architecture native agentique (~200k lignes) : modèle de plugins Tools + Capabilities, CLI & SDK, TutorBot, Co-Writer, Apprentissage guidé et mémoire persistante.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Persistance de session, upload incrémental, import pipeline RAG flexible, localisation chinoise complète.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Support Docling pour RAG-Anything, optimisation logging, corrections de bugs.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Configuration unifiée des services, sélection pipeline RAG par KB, refonte génération de questions, personnalisation barre latérale.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Support multi-fournisseur LLM & embeddings, nouvelle page d'accueil, découplage module RAG, refactorisation variables d'environnement.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Architecture PromptManager unifiée, CI/CD GitHub Actions, images Docker préconstruites sur GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Docker, Next.js 16 & React 19, sécurisation WebSocket, corrections de vulnérabilités critiques.

</details>

### 📰 Actualités

> **[2026.4.19]** 🎉 Nous avons atteint 20k étoiles en 111 jours ! Merci pour ce soutien incroyable — nous sommes déterminés à itérer continuellement vers un tutorat véritablement personnalisé et intelligent pour tous.

> **[2026.4.10]** 📄 Notre article est maintenant sur arXiv ! Lisez le [preprint](https://arxiv.org/abs/2604.26962) pour en savoir plus sur la conception et les idées derrière DeepTutor.

> **[2026.4.4]** Longtemps sans nouvelles ! ✨ DeepTutor v1.0.0 est enfin là — une évolution native aux agents avec une réécriture complète de l'architecture, TutorBot et un changement de mode flexible sous licence Apache-2.0. Un nouveau chapitre commence !

> **[2026.2.6]** 🚀 Nous avons atteint 10k étoiles en seulement 39 jours ! Un immense merci à notre incroyable communauté !

> **[2026.1.1]** Bonne année ! Rejoignez notre [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) ou [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — construisons ensemble l'avenir de DeepTutor !

> **[2025.12.29]** DeepTutor est officiellement lancé !


<a id="key-features"></a>
## ✨ Fonctionnalités clés

**Surfaces de travail**

- Chat — Chat, Solve, Quiz, Research et Visualize partagent une même session, base de connaissances et historique de citations, vous permettant d'escalader en pleine conversation sans perdre le contexte.
- Co-Writer — espace de travail Markdown en vue divisée où toute sélection peut être réécrite, développée ou raccourcie, optionnellement ancrée dans votre KB ou le web. Les brouillons sont sauvegardés directement dans les carnets.
- Book Engine — un pipeline multi-agents compile vos matériaux en « livres vivants » interactifs avec 13 types de blocs : quiz, cartes flash, chronologies, graphes de concepts, un visualiseur GeoGebra intégré, animations, et plus. Les pages sont empreintes numériques du KB, rendant toute dérive détectable.

**Votre bibliothèque**

- Knowledge Bases — collections versionnées prêtes pour RAG, de bout en bout sur LlamaIndex. Chaque (ré)indexation est tracée, comparable et réversible.
- Space — une bibliothèque personnelle de révision regroupant l'historique des chats, les carnets, la banque de questions et les skills créés par l'utilisateur (`SKILL.md`) qui changent la personnalité de DeepTutor.
- Mémoire à trois couches — traces L1 en ajout seul, faits L2 organisés par surface avec citations et synthèse L3 entre surfaces. Un atelier inspectable et un graphe de mémoire vous permettent d'auditer *pourquoi* DeepTutor sait ce qu'il sait.

**Extensibilité et contrôle**

- Outils composables — RAG, recherche web, exécution de code, raisonnement, brainstorming, recherche d'articles, analyse GeoGebra et assistants de chat (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). Les serveurs MCP se connectent aux côtés des outils intégrés.
- TutorBots personnels — tuteurs persistants et autonomes, chacun avec son propre espace de travail, soul, skills et canaux (Telegram, Discord, Slack, Matrix, Zulip, …). Construits sur [nanobot](https://github.com/HKUDS/nanobot).
- Settings unifiés — un atelier brouillon / Apply pour l'apparence, les modèles, les embeddings, la recherche, les capacités, la mémoire, les serveurs MCP et les outils, avec suivi partagé du coût par appel.
- CLI native aux agents — chaque capacité, KB, session et TutorBot est accessible en une commande ; sortie enrichie pour les humains, JSON structuré pour les agents. Donnez le [`SKILL.md`](../../SKILL.md) à n'importe quel LLM avec accès aux outils et il peut piloter DeepTutor de manière autonome.
- Authentification optionnelle — désactivée par défaut ; activez-la pour les déploiements multi-utilisateurs avec bcrypt + JWT, un tableau de bord admin et un sidecar optionnel PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 Démarrage

DeepTutor propose désormais quatre chemins d'installation parallèles. Tous utilisent le même schéma de configuration d'exécution :

- Les réglages résident dans `data/user/settings/` sous votre espace de travail actuel, ou sous `DEEPTUTOR_HOME` / `deeptutor start --home` quand vous en choisissez un explicitement.
- `model_catalog.json` stocke les profils de fournisseurs de modèles, les URLs de base, les clés API, les modèles actifs, les réglages d'embeddings et de recherche.
- `system.json` stocke les ports de lancement, la base API publique, le CORS, le TLS et les options de pièces jointes.
- `auth.json` stocke le commutateur d'authentification optionnel et le hash des identifiants de démarrage.
- `integrations.json` stocke les sidecars optionnels tels que PocketBase.
- Le `.env` à la racine du projet n'est plus utilisé comme fichier de configuration de l'application.

Pour l'application locale complète, l'ordre recommandé est **choisir un espace de travail → installer → `deeptutor init` → `deeptutor start`**.

### Option 1 — Installer DeepTutor

À utiliser quand vous voulez l'application web locale complète et la CLI sans cloner le dépôt.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **Vous essayez la bêta v1.4.0 ?** PyPI normalise `1.4.0-beta` en `1.4.0b0`, donc `pip install -U deeptutor` restera sur la dernière version stable. Optez pour la pré-version avec :
>
> ```bash
> pip install --pre -U deeptutor      # dernière pré-version
> pip install -U deeptutor==1.4.0b0   # épingler exactement à v1.4.0-beta
> ```

`deeptutor init` écrit la configuration dans `data/user/settings/` dans le répertoire où vous l'exécutez. Il vous demande :

- Port du backend, par défaut `8001`
- Port du frontend, par défaut `3782`
- Fournisseur LLM, URL de base, clé API et nom du modèle
- Fournisseur d'embeddings optionnel pour Knowledge Base / RAG

Après `deeptutor start`, ouvrez l'URL du frontend affichée dans le terminal. Avec les ports par défaut, cette URL est [http://127.0.0.1:3782](http://127.0.0.1:3782).

Gardez le terminal `deeptutor start` ouvert. Appuyez sur `Ctrl+C` dans ce terminal pour arrêter le backend et le frontend.

Notes :

- `deeptutor start` lance le backend FastAPI et le frontend Next.js packagé ensemble.
- L'application web packagée ne nécessite ni `git clone` ni `npm install`, mais a besoin d'un runtime Node.js 20+ local.
- Si vous sautez délibérément `deeptutor init` pour un essai rapide, l'application démarre avec des ports sécurisés par défaut et des réglages de modèles vides ; configurez les modèles ensuite dans **Settings → Models**.

### Option 2 — Installation depuis les sources

À utiliser quand vous développez DeepTutor ou souhaitez l'exécuter directement depuis un checkout.
Utilisez Python 3.11+ et Node.js 22 LTS pour la meilleure correspondance avec CI et Docker.

**1. Cloner le dépôt**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Créer un environnement Python**

macOS / Linux avec `venv` :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell avec `venv` :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Conda / Miniconda :

```bash
conda create -n deeptutor python=3.11
conda activate deeptutor
python -m pip install --upgrade pip
```

**3. Installer le paquet local et les dépendances frontend**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

**4. Configurer et démarrer**

```bash
deeptutor init
deeptutor start
```

Si `deeptutor start` signale un frontend existant qui ne répond pas, supprimez les fichiers de verrou obsolètes et redémarrez :

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

Extras utiles pour les développeurs :

```bash
pip install -e ".[dev]"             # outils tests/lint
pip install -e ".[tutorbot]"        # moteur TutorBot + SDKs canaux
pip install -e ".[matrix]"          # canal Matrix sans E2EE/libolm
pip install -e ".[matrix-e2e]"      # E2EE Matrix ; nécessite libolm
pip install -e ".[math-animator]"   # addon Manim ; nécessite LaTeX/ffmpeg/libs système
```

### Option 3 — Docker

À utiliser quand vous voulez l'application web complète dans un conteneur. Les images sont publiées sur GitHub Container Registry :

- `ghcr.io/hkuds/deeptutor:latest` — version stable
- `ghcr.io/hkuds/deeptutor:pre` — pré-version, quand disponible

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Ouvrez ensuite [http://127.0.0.1:3782](http://127.0.0.1:3782). La configuration, les clés API, les logs, les fichiers de l'espace de travail, la mémoire et les bases de connaissances sont stockés dans le volume `deeptutor-data` sous `/app/data`.

#### Connexion à Ollama ou d'autres services de l'hôte

À l'intérieur d'un conteneur Docker, `localhost` fait référence au conteneur lui-même. Si vous exécutez Ollama, LM Studio, llama.cpp, vLLM ou un autre service de modèles sur l'hôte, utilisez l'une de ces approches.

Option A — passerelle hôte, recommandée pour les exécutions Docker normales :

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Puis dans **DeepTutor Settings → Models**, définissez l'URL de base du fournisseur sur `host.docker.internal` :

- Endpoint LLM Ollama : `http://host.docker.internal:11434/v1`
- Endpoint embeddings Ollama : `http://host.docker.internal:11434/api/embed`
- LM Studio : `http://host.docker.internal:1234/v1`
- llama.cpp : `http://host.docker.internal:8080/v1`

Option B — réseau hôte, Linux uniquement :

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Pour exécuter en arrière-plan :

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

### Option 4 — CLI uniquement

À utiliser quand vous n'avez pas besoin de l'interface web.

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

Windows PowerShell :

```powershell
py -3.11 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ./packaging/deeptutor-cli
deeptutor init --cli
deeptutor chat
```

`deeptutor init --cli` utilise le même schéma `data/user/settings/` que l'application complète, mais modifie le comportement de l'assistant :

- Ignore les invites de ports backend/frontend car l'utilisation CLI seule ne démarre pas l'application web.
- Écrit quand même les fichiers `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml` et `agents.yaml` par défaut.
- Invite toujours à choisir le fournisseur et le modèle LLM actif.
- Demande si configurer les embeddings, mais la réponse par défaut est `Non` ; choisissez `Oui` si vous prévoyez d'utiliser `deeptutor kb ...` ou les outils RAG.

Commandes CLI courantes :

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "Expliquer la transformée de Fourier"
deeptutor run deep_solve "Résoudre x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
deeptutor config show
```

### Référence de configuration

| Fichier | Rôle |
|:---|:---|
| `data/user/settings/model_catalog.json` | Profils de fournisseurs LLM, embeddings et recherche ; clés API ; modèles actifs |
| `data/user/settings/system.json` | Ports backend/frontend, base API publique, CORS, vérification SSL, répertoire pièces jointes |
| `data/user/settings/auth.json` | Commutateur d'auth optionnel, nom d'utilisateur, hash du mot de passe, réglages tokens/cookies |
| `data/user/settings/integrations.json` | Réglages d'intégration PocketBase et sidecars optionnels |
| `data/user/settings/interface.json` | Préférences de langue/thème/barre latérale de l'interface |
| `data/user/settings/main.yaml` | Paramètres de comportement d'exécution et injection de chemins |
| `data/user/settings/agents.yaml` | Température et limites de tokens des capacités/outils |

<a id="explore-deeptutor"></a>
## 📖 Découvrir DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

La refactorisation v1.4.0-beta réorganise DeepTutor autour de **cinq surfaces principales** — Chat, Co-Writer, Book, Knowledge, Space — plus une **Mémoire à trois couches** sous-jacente à toutes et un atelier de **Settings** unifié. Les capacités (Solve / Quiz / Research / Visualize) et les outils (RAG, web, code, raisonnement, brainstorming, recherche d'articles, `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) se composent librement par-dessus.

### 💬 Chat — Espace de travail intelligent unifié

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Un fil, cinq modes, n'importe quel outil. Le sélecteur de capacités se trouve dans le compositeur ; la même session, base de connaissances, pièces jointes et références vous accompagnent entre les modes — passez d'une question décontractée à une résolution multi-agents, à un quiz, à un rapport de recherche complet, sans perdre le contexte.

| Mode | Ce qu'il fait | Construit sur |
|:---|:---|:---|
| **Chat** | Conversation flexible avec n'importe quel outil ; choisissez parmi RAG, recherche web, exécution de code, raisonnement profond, brainstorming, recherche d'articles, analyse GeoGebra. | RAG LlamaIndex + registre d'outils |
| **Solve** | Plan → investiguer → résoudre → vérifier en plusieurs étapes, avec citations précises de sources. | Moteur agentique (`deep_solve`) |
| **Quiz** | Génération de questions auto-validées ancrées dans votre KB ; génère un compositeur de chat de suivi par question. | Moteur agentique (`deep_question`) |
| **Research** | Décompose un sujet en sous-thèmes, envoie des agents parallèles à travers RAG / web / arXiv, et produit un rapport cité avec des révisions itératives en mode ajout. | `pipeline.py` reconstruit (~45% plus petit, citations + rapports itératifs préservés) |
| **Visualize** | Génère des diagrammes SVG, graphiques Chart.js, graphes Mermaid, pages HTML interactives **ou** vidéos/storyboards Manim — l'analyseur choisit le bon `render_type`. | Pipeline Visualize (Animator intégré) |

**Nouveaux outils de chat** livrés avec la refactorisation : `ask_user` (pose une question de clarification structurée en milieu de tour), `web_fetch` (intègre une URL spécifique dans le contexte), `write_note` / `list_notebook` (sauvegarde et liste les enregistrements du carnet depuis la surface de chat) et `github_query` (consultations d'issues / PR / dépôts). Les outils restent **découplés des flux de travail** — chaque mode vous permet d'activer ou désactiver les outils par tour.

Une session porte également un **inventaire cumulé de sources** entre les tours, de sorte que les citations des hits RAG / web antérieurs restent réutilisables plus tard dans la même conversation.

### ✍️ Co-Writer — Espace de travail d'écriture IA multi-documents

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer est un plan de travail Markdown en vue divisée (éditeur brut à gauche, aperçu en direct à droite) pour les notes, rapports, tutoriels et brouillons assistés par IA. Chaque document vit dans son propre espace de travail avec sauvegarde automatique, Markdown téléchargeable et **Sauvegarder dans le carnet** en un clic.

Sélectionnez n'importe quel texte et choisissez **Réécrire**, **Développer** ou **Raccourcir** — chaque action s'exécute comme une modification d'agent tracée qui peut optionnellement puiser dans une base de connaissances ou le web.

### 📖 Book Engine — « Livres vivants » interactifs

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

Donnez un sujet à DeepTutor, pointez-le vers votre base de connaissances, et il produit un livre structuré et interactif — pas une exportation statique, mais un document vivant que vous pouvez lire, sur lequel vous interroger et discuter en contexte.

En coulisses, un pipeline multi-agents gère le travail intensif : proposer un plan, récupérer des sources pertinentes de votre KB, synthétiser un arbre de chapitres, planifier chaque page et compiler chaque bloc. Vous restez maître — révisez la proposition, réorganisez les chapitres et chattez aux côtés de n'importe quelle page.

Les pages sont assemblées à partir de 13 types de blocs — texte, encadré, quiz, cartes flash, code, figure, plongée approfondie, animation, démo interactive (incluant maintenant un **visualiseur GeoGebra**), chronologie, graphe de concepts, section et note utilisateur.

### 📚 Knowledge Bases — Bibliothèques de documents prêtes pour RAG

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

Un espace de travail dédié pour les collections de documents qui alimentent RAG. Chaque base de connaissances a quatre onglets :

- **Files** — Parcourez les sources téléchargées, prévisualisez les PDFs en ligne et consultez la taille/statut par fichier.
- **Add documents** — Ajoutez des PDFs, fichiers Office (DOCX / XLSX / PPTX), Markdown, texte brut et une large gamme de types de fichiers code/données. Les documents sont acheminés automatiquement vers l'extracteur approprié.
- **Index versions** — Chaque (ré)indexation est une version tracée. Revenez à un index antérieur, comparez les modèles d'embeddings ou inspectez les statistiques de chunking sans perdre la compilation précédente.
- **Settings** — Choisissez le fournisseur/modèle d'embeddings, les paramètres de chunking et le reranker pour la KB.

L'indexation est construite sur **LlamaIndex** de bout en bout, avec réindexation sûre aux pannes, détection de discordance d'embeddings et gestion résiliente des vecteurs persistés corrompus.

### 🌐 Space — Votre bibliothèque personnelle d'apprentissage

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space est la contrepartie de **lecture / révision** des surfaces actives. Là où Chat / Co-Writer / Book sont des surfaces où vous *produisez*, Space est l'endroit où vit tout ce que vous produisez, avec recherche et rejeu.

- **Chat History** — Chaque conversation sur chaque mode, avec renommage de titre, suppression et reprise.
- **Notebooks** — Sauvegardez les sorties de Chat, Research et Co-Writer dans des carnets catégorisés et codés par couleur.
- **Question Bank** — Chaque question de quiz générée automatiquement, marque-pageable et @-mentionnable dans le chat.
- **Skills** — Fichiers `SKILL.md` créés par l'utilisateur définissant des personas d'enseignement. Quand actif, un skill est injecté dans le prompt système du chat.

### 🧠 Mémoire — Architecture à trois couches

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

La mémoire de DeepTutor est désormais un **pipeline à trois couches** avec un atelier inspectable à `/memory`.

| Couche | Rôle | Stockage |
|:---|:---|:---|
| **L1 · Miroir de l'espace de travail** (EN DIRECT) | Trace en ajout seul de chaque interaction, par surface, par jour. L'enregistrement sans perte de ce qui s'est réellement passé. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Résumés par surface** (CURÉ) | Faits spécifiques à la surface extraits par le consolidateur. Chaque fait porte des citations de notes de bas de page vers les traces L1. | `L2/<surface>.md` |
| **L3 · Connaissance inter-surfaces** (SYNTHÈSE) | Synthèse inter-surfaces : votre `profile`, chronologie `recent`, `scope` des connaissances et `preferences`. Affirmations nuancées, chacune étayée par des preuves L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

Sept surfaces alimentent le pipeline : **chat, notebook, quiz, kb, book, tutorbot, cowriter**.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

Le **Memory Graph** (`/memory/graph`) rend les trois couches à la fois : synthèse L3 au centre, faits L2 dans l'anneau intermédiaire, traces L1 à l'extérieur, groupées par surface.

### ⚙️ Settings — Centre de contrôle unifié

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

La surface des réglages a été unifiée dans v1.4 et divisée par domaine, avec un modèle brouillon / **Apply** pour que les changements soient atomiques :

- **Appearance** — Langue de l'interface et thème (Cream, Snow, Dark, Glass).
- **Status** — Sonde de santé en direct pour LLM, embeddings, recherche et backends de stockage.
- **LLM**, **Embedding**, **Search** — Catalogue de fournisseurs, URLs de base, clés API et sélection des modèles actifs.
- **Capabilities** — Ajustables par capacité pour Chat, Solve, Quiz, Research, Visualize et Co-Writer. Soutenus par une enveloppe unifiée `emit_capability_result` et un `UsageTracker` partagé affichant le coût par appel.
- **Memory** — Activez/désactivez les exécutions du consolidateur, configurez la cadence et le budget, et accédez à l'atelier de mémoire.
- **MCP servers** — Enregistrez des serveurs externes Model Context Protocol ; leurs outils sont exposés aux côtés des outils intégrés.
- **Tools** — Inspectez chaque outil intégré, ses paramètres, son statut (activé / à venir) et son état i18n.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — Tuteurs IA persistants et autonomes

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot n'est pas un chatbot — c'est un **agent persistant multi-instances** construit sur [nanobot](https://github.com/HKUDS/nanobot). Chaque TutorBot exécute sa propre boucle d'agent avec espace de travail, mémoire et personnalité indépendants.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Modèles Soul** — Définissez la personnalité, le ton et la philosophie d'enseignement de votre tuteur via des fichiers Soul éditables.
- **Espace de travail indépendant** — Chaque bot a son propre répertoire avec mémoire, sessions, skills et configuration séparés.
- **Battement de cœur proactif** — Les bots ne font pas que répondre — ils prennent l'initiative. Le système Heartbeat intégré permet des révisions d'étude récurrentes, des rappels de révision et des tâches planifiées.
- **Accès complet aux outils** — Chaque bot accède à la boîte à outils complète de DeepTutor : récupération RAG, exécution de code, recherche web, recherche d'articles académiques, raisonnement profond et brainstorming.
- **Apprentissage de Skills** — Enseignez à votre bot de nouvelles compétences en ajoutant des fichiers de skills à son espace de travail.
- **Présence multi-canal** — Connectez les bots à Telegram, Discord, Slack, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, Email, et plus.
- **Équipes et sous-agents** — Générez des sous-agents en arrière-plan ou orchestrez des équipes multi-agents au sein d'un seul bot.

```bash
deeptutor bot create math-tutor --persona "Professeur de maths socratique qui pose des questions stimulantes"
deeptutor bot create writing-coach --persona "Mentor d'écriture patient et orienté détails"
deeptutor bot list                  # Voir tous vos tuteurs actifs
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — Interface native aux agents

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor est entièrement natif pour la CLI. Chaque capacité, base de connaissances, session, mémoire et TutorBot est accessible en une commande — sans navigateur nécessaire.

**Exécution en une seule commande** :

```bash
deeptutor run chat "Expliquer la transformée de Fourier" -t rag --kb textbook
deeptutor run deep_solve "Prouver que √2 est irrationnel" -t reason
deeptutor run deep_question "Algèbre linéaire" --config num_questions=5
deeptutor run deep_research "Mécanismes d'attention dans les transformers"
deeptutor run visualize "Dessiner l'architecture d'un transformer"
```

**REPL interactif** :

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Dans le REPL : /cap, /tool, /kb, /history, /notebook, /config pour changer à la volée
```

**Cycle de vie de la base de connaissances** :

```bash
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb add my-kb --docs-dir ./papers/
deeptutor kb search my-kb "descente de gradient"
deeptutor kb set-default my-kb
```

**Mode de sortie dual** :

```bash
deeptutor run chat "Résumer le chapitre 3" -f rich    # Sortie colorée et formatée
deeptutor run chat "Résumer le chapitre 3" -f json    # Événements JSON délimités par ligne
```

**Continuité de session** :

```bash
deeptutor session list
deeptutor session open <id>
```

<details>
<summary><b>Référence complète des commandes CLI</b></summary>

**Niveau supérieur**

| Commande | Description |
|:---|:---|
| `deeptutor run <capability> <message>` | Exécuter n'importe quelle capacité en un seul tour (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | REPL interactif avec `--capability`, `--tool`, `--kb`, `--language` optionnels |
| `deeptutor serve` | Démarrer le serveur API DeepTutor |

**`deeptutor bot`**

| Commande | Description |
|:---|:---|
| `deeptutor bot list` | Lister toutes les instances TutorBot |
| `deeptutor bot create <id>` | Créer et démarrer un nouveau bot (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Démarrer un bot |
| `deeptutor bot stop <id>` | Arrêter un bot |

**`deeptutor kb`**

| Commande | Description |
|:---|:---|
| `deeptutor kb list` | Lister toutes les bases de connaissances |
| `deeptutor kb info <name>` | Afficher les détails de la base de connaissances |
| `deeptutor kb create <name>` | Créer depuis des documents (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Ajouter des documents de manière incrémentale |
| `deeptutor kb search <name> <query>` | Rechercher dans une base de connaissances |
| `deeptutor kb set-default <name>` | Définir comme KB par défaut |
| `deeptutor kb delete <name>` | Supprimer une base de connaissances (`--force`) |

**`deeptutor memory`**

| Commande | Description |
|:---|:---|
| `deeptutor memory show [file]` | Voir la mémoire (`summary`, `profile` ou `all`) |
| `deeptutor memory clear [file]` | Effacer la mémoire (`--force`) |

**`deeptutor session`**

| Commande | Description |
|:---|:---|
| `deeptutor session list` | Lister les sessions (`--limit`) |
| `deeptutor session show <id>` | Voir les messages de la session |
| `deeptutor session open <id>` | Reprendre la session dans le REPL |
| `deeptutor session rename <id>` | Renommer une session (`--title`) |
| `deeptutor session delete <id>` | Supprimer une session |

**`deeptutor notebook`**

| Commande | Description |
|:---|:---|
| `deeptutor notebook list` | Lister les carnets |
| `deeptutor notebook create <name>` | Créer un carnet (`--description`) |
| `deeptutor notebook show <id>` | Voir les enregistrements du carnet |
| `deeptutor notebook add-md <id> <path>` | Importer markdown comme enregistrement |
| `deeptutor notebook replace-md <id> <rec> <path>` | Remplacer un enregistrement markdown |
| `deeptutor notebook remove-record <id> <rec>` | Supprimer un enregistrement |

**`deeptutor book`**

| Commande | Description |
|:---|:---|
| `deeptutor book list` | Lister tous les livres dans l'espace de travail |
| `deeptutor book health <book_id>` | Vérifier la dérive KB et la santé du livre |
| `deeptutor book refresh-fingerprints <book_id>` | Actualiser les empreintes KB et effacer les pages obsolètes |

**`deeptutor config` / `plugin` / `provider`**

| Commande | Description |
|:---|:---|
| `deeptutor config show` | Afficher le résumé de la configuration actuelle |
| `deeptutor plugin list` | Lister les outils et capacités enregistrés |
| `deeptutor plugin info <name>` | Afficher les détails d'un outil ou d'une capacité |
| `deeptutor provider login <provider>` | Authentification du fournisseur |

</details>

---

<a id="multi-user"></a>
### 👥 Multi-utilisateur — Déploiements partagés avec espaces de travail par utilisateur

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Activez l'authentification et DeepTutor devient un déploiement multi-tenant avec **espaces de travail isolés par utilisateur** et **ressources gérées par l'administrateur**.

**Démarrage rapide (5 étapes) :**

```bash
# 1. Activez l'auth dans data/user/settings/auth.json :
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Redémarrez le stack web.
deeptutor start

# 3. Ouvrez http://localhost:3782/register et créez le premier compte.
#    La première inscription est la seule publique ; cet utilisateur devient admin
#    et l'endpoint /register se ferme automatiquement ensuite.

# 4. En tant qu'admin, naviguez vers /admin/users → "Add user" pour créer des comptes.

# 5. Pour chaque utilisateur, cliquez sur l'icône curseur → assignez les profils LLM,
#    bases de connaissances et skills. Sauvegardez.
```

**Ce que voit l'administrateur :**

- **Page Settings complète** sur `/settings` — gérez les fournisseurs LLM / embeddings / recherche, clés API, catalogues de modèles et "Apply" en temps réel.
- **Gestion des utilisateurs** sur `/admin/users` — créer, promouvoir, rétrograder et supprimer des comptes.
- **Éditeur de droits** — pour chaque utilisateur non-admin, choisissez les profils de modèles, bases de connaissances et skills autorisés.
- **Journal d'audit** — chaque changement de droits est ajouté à `multi-user/_system/audit/usage.jsonl`.

**Ce qu'obtiennent les utilisateurs ordinaires :**

- **Espace de travail isolé** sous `multi-user/<uid>/` — leur propre historique de chat (`chat_history.db`), mémoire, carnets et bases de connaissances personnelles.
- **Accès en lecture seule** aux bases de connaissances et skills assignés par l'admin.
- **Page Settings expurgée** — seulement thème, langue et résumé des modèles accordés.
- **LLM à portée limitée** — les tours de chat sont acheminés via le modèle assigné par l'admin.

**Schéma de l'espace de travail :**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Identifiants hachés, rôles
│   ├── auth/auth_secret         # Secret de signature JWT (auto-généré)
│   ├── grants/<uid>.json        # Droits de ressources par utilisateur (gérés par admin)
│   └── audit/usage.jsonl        # Journal d'audit
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Référence de configuration :**

| Réglage | Requis | Description |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Oui | Mettre à `true` pour activer l'auth multi-utilisateur. Par défaut `false` (mode mono-utilisateur). |
| `multi-user/_system/auth/auth_secret` | Recommandé | Secret de signature JWT. Auto-généré au premier démarrage authentifié si manquant. |
| `data/user/settings/auth.json: token_expire_hours` | Non | Durée de vie du JWT ; par défaut `24`. |
| `data/user/settings/auth.json: username/password_hash` | Non | Identifiant de démarrage optionnel pour un seul utilisateur sans tête. |
| `data/user/settings/system.json` | Non | `deeptutor start` dérive les indicateurs d'auth du frontend depuis les réglages d'exécution. |

> ⚠️ **Le mode PocketBase (`integrations.pocketbase_url` défini) est mono-utilisateur uniquement.** Les déploiements multi-utilisateurs doivent laisser `integrations.pocketbase_url` vide et utiliser le backend JSON/SQLite par défaut.

> ⚠️ **Recommandation de processus unique.** La promotion du premier utilisateur en admin est protégée par un `threading.Lock` en processus. Les déploiements multi-workers doivent provisionner le premier admin hors ligne ou soutenir le magasin d'utilisateurs avec un système externe.

<a id="community"></a>
## 🌐 Communauté et écosystème

DeepTutor est construit sur les épaules de projets open source remarquables :

| Projet | Rôle dans DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Moteur d'agent ultra-léger alimentant TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Pipeline RAG et colonne vertébrale d'indexation des documents |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | Génération d'animations mathématiques pilotée par IA pour Math Animator |

**De l'écosystème HKUDS :**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| RAG Simple et Rapide | Framework d'Agents Sans Code | Recherche Automatisée | Agent IA Ultra-Léger |


## 🤝 Contributions

<div align="center">

Nous espérons que DeepTutor sera un cadeau pour la communauté. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

Consultez [CONTRIBUTING.md](../../CONTRIBUTING.md) pour les directives sur la configuration de votre environnement de développement, les normes de code et le flux de travail des pull requests.

## ⭐ Historique des étoiles

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

[⭐ Nous donner une étoile](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Signaler un bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussions](https://github.com/HKUDS/DeepTutor/discussions)

---

Sous licence [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
