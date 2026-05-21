<div align="center">

<img src="../../assets/logo.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Tutoría Personalizada Nativa para Agentes

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

<p align="center">
  <a href="../../README.md"><img alt="English" height="40" src="https://img.shields.io/badge/English-CDCFD4"></a>&nbsp;
  <a href="README_CN.md"><img alt="简体中文" height="40" src="https://img.shields.io/badge/简体中文-CDCFD4"></a>&nbsp;
  <a href="README_JA.md"><img alt="日本語" height="40" src="https://img.shields.io/badge/日本語-CDCFD4"></a>&nbsp;
  <a href="README_ES.md"><img alt="Español" height="40" src="https://img.shields.io/badge/Español-BCDCF7"></a>&nbsp;
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

[Características](#key-features) · [Primeros pasos](#get-started) · [Explorar](#explore-deeptutor) · [TutorBot](#tutorbot) · [CLI](#deeptutor-cli) · [Multiusuario](#multi-user) · [Comunidad](#community)

</div>

---

> 🤝 **¡Damos la bienvenida a todo tipo de contribuciones!** Consulta nuestra [Guía de contribución](../../CONTRIBUTING.md) para conocer la estrategia de ramas, los estándares de código y cómo empezar.
>
> 🗺️ **La hoja de ruta** está disponible públicamente en [`HKUDS/DeepTutor#498`](https://github.com/HKUDS/DeepTutor/issues/498) — comenta para votar elementos o proponer nuevos.

### 📦 Lanzamientos

> **[2026.5.21]** [v1.4.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.0-beta) — Panel de trabajo Memory de tres capas (L1/L2/L3), todas las capacidades de chat reconstruidas sobre un único motor agente, RAG exclusivo con LlamaIndex y una superficie unificada de Settings + Capabilities.

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Corrección de CORS en Docker remoto, `DISABLE_SSL_VERIFY` para proveedores SDK, citas en bloques de código más seguras y complemento Matrix E2EE opcional.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — TutorBot con soporte de Zulip y NVIDIA NIM, enrutamiento de modelos de razonamiento más seguro, `deeptutor start`, tooltips en la barra lateral y paridad del almacén de sesiones.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Despliegues multiusuario opcionales con espacios de trabajo aislados por usuario, concesión de permisos de administrador, rutas de autenticación y acceso en tiempo de ejecución con ámbito.

<details>
<summary><b>Lanzamientos anteriores (más de 2 semanas)</b></summary>

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Correcciones de modelos de razonamiento/proveedores, historial de índice de Knowledge visible y edición más segura de plantillas y vaciado en Co-Writer.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Selección de modelos basada en catálogo para chat y TutorBot, reindexado RAG más seguro, correcciones de límites de tokens en OpenAI Responses y validación del editor de Skills.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Configuración de inicio local más fluida, consultas RAG más seguras, autenticación de embeddings locales más clara y mejoras visuales del modo oscuro en Settings.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Persistencia del chat en páginas de libro y flujos de reconstrucción, referencias de chat a libro, manejo mejorado de idioma/razonamiento y extracción de documentos RAG más robusta.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — Soporte de embeddings NVIDIA NIM + Gemini, contexto unificado de Space para historial de chat/skills/memoria, instantáneas de sesión y resiliencia en reindexado RAG.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — URLs de endpoints de embedding transparentes, resiliencia en reindexado RAG para vectores persistidos inválidos, limpieza de memoria para salida de modelos de razonamiento y corrección del tiempo de ejecución de Deep Solve.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Estabilidad: enrutamiento RAG y validación de embeddings más seguros, persistencia Docker, entrada compatible con IME, robustez en Windows/GBK.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Índices de KB versionados con flujo de reindexado, espacio de trabajo de Knowledge reconstruido, autodescubrimiento de embeddings con nuevos adaptadores y centro Space.

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Adjuntos de chat persistentes con cajón de vista previa, pipelines de capacidades con soporte de adjuntos y exportación Markdown de TutorBot.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — Adjuntos de texto/código/SVG, Setup Tour de un comando, exportación Markdown del chat e interfaz compacta de gestión de KB.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Adjuntos de documentos (PDF/DOCX/XLSX/PPTX), visualización de bloques de razonamiento, editor de plantillas Soul y guardado en notebook desde Co-Writer.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — Sistema de Skills creados por el usuario, rendimiento mejorado en la entrada del chat, inicio automático de TutorBot, interfaz de la Biblioteca de libros y pantalla completa en visualización.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Límites de tokens por etapa, Regenerar respuesta en todos los puntos de entrada y correcciones de compatibilidad con RAG y Gemma.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Compilador de «libros vivos» Book Engine, Co-Writer multidocumento, visualizaciones HTML interactivas y mención @ en el banco de preguntas.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Pestaña Channels basada en esquema, consolidación del pipeline RAG en uno solo y prompts de chat externalizados.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — «Responder ahora» universal, sincronización de desplazamiento en Co-Writer, panel de configuración unificado y botón Stop de streaming.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — Revisión de bloques de matemáticas LaTeX, sonda de diagnóstico LLM y guía para Docker y LLM local.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Sesiones con URL favorita, tema Snow, heartbeat y reconexión automática de WebSocket y revisión del registro de embeddings.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Cuaderno de preguntas con marcadores y categorías, Mermaid en Visualize, detección de incompatibilidad de embeddings, compatibilidad con Qwen/vLLM, soporte para LM Studio y llama.cpp y tema Glass.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Consolidación de búsqueda con fallback de SearXNG, corrección del cambio de proveedor y correcciones de fugas de recursos en el frontend.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Capacidad Visualize (Chart.js/SVG), prevención de duplicados en quiz y soporte para o4-mini.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Seguimiento del progreso de embeddings con reintento por límite de tasa, correcciones de dependencias multiplataforma y corrección de validación MIME.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — SDK nativo de OpenAI/Anthropic (eliminación de litellm), soporte del animador matemático en Windows, análisis robusto de JSON e i18n completo en chino.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Recarga en caliente de configuración, salida anidada de MinerU, corrección de WebSocket y Python 3.11+ como mínimo.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Reescritura de arquitectura nativa para agentes (~200k líneas): modelo de plugins Tools + Capabilities, CLI y SDK, TutorBot, Co-Writer, Aprendizaje Guiado y memoria persistente.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Persistencia de sesiones, carga incremental de documentos, importación flexible de pipeline RAG y localización completa al chino.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Soporte de Docling para RAG-Anything, optimización del sistema de logging y correcciones de errores.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Configuración unificada de servicios, selección de pipeline RAG por base de conocimiento, renovación de generación de preguntas y personalización de la barra lateral.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Soporte multi-proveedor para LLM y embeddings, nueva página de inicio, desacoplamiento del módulo RAG y refactorización de variables de entorno.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Arquitectura unificada PromptManager, CI/CD con GitHub Actions e imágenes Docker preconstruidas en GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Despliegue Docker, actualización a Next.js 16 y React 19, refuerzo de seguridad en WebSocket y correcciones de vulnerabilidades críticas.

</details>

### 📰 Noticias

> **[2026.4.19]** 🎉 ¡Hemos alcanzado 20k estrellas en 111 días! Gracias por el increíble apoyo — estamos comprometidos con la iteración continua hacia una tutoría verdaderamente personalizada e inteligente para todos.

> **[2026.4.10]** 📄 ¡Nuestro artículo ya está en arXiv! Lee el [preprint](https://arxiv.org/abs/2604.26962) para conocer más sobre el diseño e ideas detrás de DeepTutor.

> **[2026.4.4]** ¡Mucho tiempo sin vernos! ✨ DeepTutor v1.0.0 ya está aquí — una evolución nativa para agentes con una reescritura completa de arquitectura, TutorBot y cambio de modo flexible bajo la licencia Apache-2.0. ¡Comienza un nuevo capítulo y nuestra historia continúa!

> **[2026.2.6]** 🚀 ¡Hemos alcanzado 10k estrellas en solo 39 días! ¡Un enorme agradecimiento a nuestra increíble comunidad por el apoyo!

> **[2026.1.1]** ¡Feliz Año Nuevo! Únete a nuestro [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78) o [Discusiones](https://github.com/HKUDS/DeepTutor/discussions) — ¡construyamos juntos el futuro de DeepTutor!

> **[2025.12.29]** ¡DeepTutor se lanza oficialmente!


<a id="key-features"></a>
## ✨ Características clave

**Superficies de trabajo**

- Chat — Chat, Solve, Quiz, Research y Visualize comparten una misma sesión, base de conocimiento e historial de citas, por lo que puedes escalar a mitad de conversación sin perder contexto.
- Co-Writer — espacio de trabajo Markdown con vista dividida donde cualquier selección puede reescribirse, expandirse o acortarse, opcionalmente fundamentada en tu KB o la web. Los borradores se guardan directamente en notebooks.
- Book Engine — un pipeline multiagente compila tus materiales en «libros vivos» interactivos con 13 tipos de bloques: quizzes, tarjetas flash, líneas de tiempo, grafos de conceptos, un visor GeoGebra integrado, animaciones y más. Las páginas llevan huella digital del KB para detectar desviaciones.

**Tu biblioteca**

- Knowledge Bases — colecciones versionadas listas para RAG, de extremo a extremo sobre LlamaIndex. Cada (re)indexación es rastreada, comparable y reversible.
- Space — una biblioteca personal de revisión que agrupa historial de chat, notebooks, banco de preguntas y skills creados por el usuario (`SKILL.md`) que cambian la personalidad de DeepTutor.
- Memoria de tres capas — trazas L1 de solo adición, hechos L2 curados por superficie con citas y síntesis L3 entre superficies. Un panel de trabajo inspeccionable y un grafo de memoria te permiten auditar *por qué* DeepTutor sabe lo que sabe.

**Extensibilidad y control**

- Herramientas componibles — RAG, búsqueda web, ejecución de código, razonamiento, lluvia de ideas, búsqueda de artículos, análisis de GeoGebra y ayudantes de chat (`ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`). Los servidores MCP se conectan junto a las herramientas integradas.
- TutorBots personales — tutores persistentes y autónomos, cada uno con su propio espacio de trabajo, soul, skills y canales (Telegram, Discord, Slack, Matrix, Zulip, …). Construidos sobre [nanobot](https://github.com/HKUDS/nanobot).
- Settings unificados — un panel de borrador / Apply para apariencia, modelos, embeddings, búsqueda, capacidades, memoria, servidores MCP y herramientas, con seguimiento compartido del costo por llamada.
- CLI nativa para agentes — cada capacidad, KB, sesión y TutorBot está a un comando de distancia; salida enriquecida para humanos, JSON estructurado para agentes. Entrega el [`SKILL.md`](../../SKILL.md) a cualquier LLM con acceso a herramientas y podrá operar DeepTutor de forma autónoma.
- Autenticación opcional — desactivada por defecto; actívala para despliegues multiusuario con bcrypt + JWT, un panel de administración y un sidecar opcional de PocketBase / OAuth.

---

<a id="get-started"></a>
## 🚀 Primeros pasos

DeepTutor ahora tiene cuatro rutas de instalación paralelas. Todas utilizan el mismo esquema de configuración en tiempo de ejecución:

- Los ajustes se guardan en `data/user/settings/` bajo tu espacio de trabajo actual, o bajo `DEEPTUTOR_HOME` / `deeptutor start --home` cuando eliges uno explícitamente.
- `model_catalog.json` almacena perfiles de proveedores de modelos, URLs base, claves API, modelos activos, configuración de embeddings y configuración de búsqueda.
- `system.json` almacena puertos de inicio, base pública de la API, CORS, TLS y opciones de adjuntos.
- `auth.json` almacena el interruptor de autenticación opcional y el hash de credenciales de arranque.
- `integrations.json` almacena sidecars opcionales como PocketBase.
- El `.env` en la raíz del proyecto ya no se usa como archivo de configuración de la aplicación.

Para la aplicación local completa, el orden recomendado es **elegir un espacio de trabajo → instalar → `deeptutor init` → `deeptutor start`**. `deeptutor start` puede completar los archivos predeterminados faltantes como red de seguridad, pero la configuración normal del primer inicio debe realizarse mediante `deeptutor init` para que los puertos y la configuración de modelos sean explícitos antes de que arranque la aplicación web.

### Opción 1 — Instalar DeepTutor

Úsala cuando quieras la aplicación web local completa y la CLI sin clonar el repositorio.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

> 🧪 **¿Probando la beta v1.4.0?** PyPI normaliza `1.4.0-beta` a `1.4.0b0`, así que `pip install -U deeptutor` permanecerá en la versión estable más reciente. Activa la versión preliminar con:
>
> ```bash
> pip install --pre -U deeptutor      # última versión preliminar
> pip install -U deeptutor==1.4.0b0   # fijar exactamente a v1.4.0-beta
> ```

`deeptutor init` escribe la configuración en `data/user/settings/` en el directorio donde lo ejecutas. Solicita:

- Puerto del backend, por defecto `8001`
- Puerto del frontend, por defecto `3782`
- Proveedor LLM, URL base, clave API y nombre del modelo
- Proveedor de embeddings opcional para Knowledge Base / RAG

Después de `deeptutor start`, abre la URL del frontend que se imprime en el terminal. Con los puertos predeterminados, esa URL es [http://127.0.0.1:3782](http://127.0.0.1:3782). Si cambiaste `frontend_port` durante `deeptutor init` o editaste `data/user/settings/system.json` posteriormente, usa el puerto configurado.

Mantén abierto el terminal de `deeptutor start`. Presiona `Ctrl+C` en ese terminal para detener el backend y el frontend.

Notas:

- `deeptutor start` inicia el backend FastAPI y el frontend Next.js empaquetado juntos.
- La aplicación web empaquetada no requiere `git clone` ni `npm install`, pero sí necesita un tiempo de ejecución local de Node.js 20+ para ejecutar el servidor standalone de Next.js.
- Si omites deliberadamente `deeptutor init` para una prueba rápida, la aplicación arranca con puertos seguros por defecto y configuración de modelos vacía; configura los modelos después en **Settings → Models**.

### Opción 2 — Instalar desde el código fuente

Úsala cuando estés desarrollando DeepTutor o quieras ejecutarlo directamente desde un checkout.
Usa Python 3.11+ y Node.js 22 LTS para la mejor coincidencia con CI y Docker.

**1. Clonar el repositorio**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Crear un entorno Python**

macOS / Linux con `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell con `venv`:

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

**3. Instalar el paquete local y las dependencias del frontend**

```bash
python -m pip install -e .
cd web
npm ci --legacy-peer-deps
cd ..
```

Si cambias intencionalmente las dependencias del frontend, usa `npm install --legacy-peer-deps` para actualizar `web/package-lock.json` y luego confirma tanto `web/package.json` como `web/package-lock.json`.

**4. Configurar e iniciar**

```bash
deeptutor init
deeptutor start
```

Las instalaciones desde código fuente usan el directorio local `web/` para el frontend y lo inician en modo de desarrollo Next.js. Mantén abierto el terminal de `deeptutor start` mientras usas la aplicación.

Si `deeptutor start` reporta un frontend existente que no responde, detén el PID indicado en el mensaje. Si no hay ningún proceso Next.js en ejecución, elimina los archivos de bloqueo obsoletos y vuelve a iniciar:

```bash
rm -f web/.next/dev/lock web/.next/lock
deeptutor start
```

Extras útiles para desarrolladores:

```bash
pip install -e ".[dev]"             # herramientas de tests/lint
pip install -e ".[tutorbot]"        # motor TutorBot + SDKs de canales
pip install -e ".[matrix]"          # canal Matrix sin E2EE/libolm
pip install -e ".[matrix-e2e]"      # E2EE Matrix; requiere libolm
pip install -e ".[math-animator]"   # complemento Manim; requiere LaTeX/ffmpeg/librerías del sistema
```

### Opción 3 — Docker

Úsala cuando quieras la aplicación web completa en un contenedor. Las imágenes se publican en GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — versión estable
- `ghcr.io/hkuds/deeptutor:pre` — versión preliminar, cuando esté disponible

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Luego abre [http://127.0.0.1:3782](http://127.0.0.1:3782). La configuración, claves API, logs, archivos del espacio de trabajo, memoria y bases de conocimiento se almacenan en el volumen `deeptutor-data` bajo `/app/data`.

El contenedor crea `/app/data/user/settings/*.json` automáticamente en el primer inicio. Puedes configurar los proveedores de modelos directamente en la página de Settings web sin preparar archivos JSON locales manualmente.

Para usar puertos de host diferentes, cambia el lado izquierdo de los mapeos `-p`. Por ejemplo, `-p 127.0.0.1:8088:3782` hace que la interfaz web esté disponible en `http://127.0.0.1:8088` mientras el contenedor sigue escuchando en `3782`.

#### Conexión a Ollama u otros servicios del host

Dentro de un contenedor Docker, `localhost` hace referencia al propio contenedor, no a tu máquina host. Si ejecutas Ollama, LM Studio, llama.cpp, vLLM u otro servicio de modelos en el host, usa uno de estos enfoques.

Opción A — puerta de enlace del host, recomendada para ejecuciones Docker normales:

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Luego en **DeepTutor Settings → Models**, establece la URL base del proveedor en `host.docker.internal`:

- Endpoint LLM de Ollama: `http://host.docker.internal:11434/v1`
- Endpoint de embeddings de Ollama: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

En Docker Desktop para macOS/Windows, `host.docker.internal` suele estar disponible incluso sin `--add-host`. En Linux, el indicador `--add-host=host.docker.internal:host-gateway` es la forma portable de crear ese nombre de host en Docker Engine moderno.

Opción B — red del host, solo Linux:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

No se necesita mapeo `-p` en el modo de red del host. El contenedor comparte directamente la red del host, así que abre [http://127.0.0.1:3782](http://127.0.0.1:3782) por defecto, o el `frontend_port` configurado en `/app/data/user/settings/system.json`.

Para ejecutar en segundo plano, añade `-d` y sigue los logs por nombre:

```bash
docker run -d --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
docker logs -f deeptutor
```

Para detener una ejecución Docker en primer plano, presiona `Ctrl+C`. Si usaste el contenedor desacoplado con nombre, ejecuta `docker stop deeptutor`. Antes de iniciar otro contenedor con el mismo nombre, elimina el detenido con `docker rm deeptutor`; el volumen `deeptutor-data` conserva tu configuración y espacio de trabajo.

### Opción 4 — Solo CLI

Úsala cuando no necesites la interfaz web. El paquete solo-CLI se instala desde un checkout de código fuente local en lugar de PyPI.

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

`deeptutor init --cli` usa el mismo esquema `data/user/settings/` que la aplicación completa, pero cambia el comportamiento del asistente:

- Omite las solicitudes de puertos de backend/frontend porque el uso solo-CLI no inicia la aplicación web.
- Aún escribe los archivos `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml` y `agents.yaml` predeterminados.
- Aún solicita el proveedor y modelo LLM activo.
- Pregunta si configurar embeddings, pero la respuesta predeterminada es `No`; elige `Sí` si planeas usar `deeptutor kb ...` o herramientas RAG.

Comandos CLI comunes:

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "Explica la transformada de Fourier"
deeptutor run deep_solve "Resuelve x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
deeptutor config show
```

La instalación local de `deeptutor-cli` no incluye activos web ni dependencias del servidor. Conserva el checkout del código fuente ya que la instalación editable apunta a él.

### Referencia de configuración

La página de Settings web es el editor recomendado, pero los archivos son JSON/YAML simples y pueden gestionarse directamente:

| Archivo | Propósito |
|:---|:---|
| `data/user/settings/model_catalog.json` | Perfiles de proveedores LLM, embeddings y búsqueda; claves API; modelos activos |
| `data/user/settings/system.json` | Puertos de backend/frontend, base pública de la API, CORS, verificación SSL, directorio de adjuntos |
| `data/user/settings/auth.json` | Interruptor de autenticación opcional, nombre de usuario, hash de contraseña, configuración de tokens/cookies |
| `data/user/settings/integrations.json` | Configuración de integración de PocketBase y sidecars opcionales |
| `data/user/settings/interface.json` | Preferencias de idioma/tema/barra lateral de la interfaz |
| `data/user/settings/main.yaml` | Valores predeterminados de comportamiento en tiempo de ejecución e inyección de rutas |
| `data/user/settings/agents.yaml` | Configuración de temperatura y tokens de capacidades/herramientas |

La configuración mínima de modelos puede realizarse en el navegador: abre **Settings → Models**, añade un perfil LLM, establece la URL base / clave API / nombre del modelo y guarda.

<a id="explore-deeptutor"></a>
## 📖 Explorar DeepTutor

<div align="center">
<img src="../../assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

La refactorización de v1.4.0-beta reorganiza DeepTutor alrededor de **cinco superficies principales** — Chat, Co-Writer, Book, Knowledge, Space — más una **Memory de tres capas** que subyace a todas ellas y un panel de trabajo unificado de **Settings** que expone cada ajuste. Las capacidades (Solve / Quiz / Research / Visualize) y las herramientas (RAG, web, código, razonamiento, lluvia de ideas, búsqueda de artículos, `ask_user`, `web_fetch`, `write_note`, `list_notebook`, `github_query`) se componen libremente sobre ellas.

### 💬 Chat — Espacio de trabajo inteligente unificado

<div align="center">
<img src="../../assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Un hilo, cinco modos, cualquier herramienta. El selector de capacidades está en el compositor; la misma sesión, base de conocimiento, adjuntos y referencias viajan contigo entre modos — cambia de una pregunta casual a resolución multiagente, a un quiz, a un informe de investigación completo, sin perder contexto.

| Modo | Qué hace | Construido sobre |
|:---|:---|:---|
| **Chat** | Conversación flexible con cualquier herramienta; elige entre RAG, búsqueda web, ejecución de código, razonamiento profundo, lluvia de ideas, búsqueda de artículos, análisis de GeoGebra. | RAG respaldado por LlamaIndex + registro de herramientas |
| **Solve** | Plan → investigar → resolver → verificar en múltiples pasos, con citas precisas de fuentes. | Motor agente (`deep_solve`) |
| **Quiz** | Generación de preguntas autovalidadas fundamentadas en tu KB; genera un compositor de chat de seguimiento por pregunta. | Motor agente (`deep_question`) |
| **Research** | Descompone un tema en subtemas, despacha agentes paralelos a través de RAG / web / arXiv y produce un informe citado con revisiones iterativas en modo de adición. | `pipeline.py` reconstruido (~45% más pequeño, citas + informes iterativos preservados) |
| **Visualize** | Genera diagramas SVG, gráficos Chart.js, grafos Mermaid, páginas HTML interactivas **o** videos/storyboards Manim — el analizador elige el `render_type` correcto. | Pipeline Visualize (Animator integrado) |

**Nuevas herramientas de chat** lanzadas con la refactorización: `ask_user` (hace una pregunta de aclaración estructurada a mitad de turno), `web_fetch` (incorpora una URL específica al contexto), `write_note` / `list_notebook` (guarda y lista registros de notebook desde la superficie de chat) y `github_query` (consultas de issues / PR / repositorios). Las herramientas permanecen **desacopladas de los flujos de trabajo** — cada modo te permite activar o desactivar herramientas por turno.

Una sesión también lleva un **inventario acumulado de fuentes** entre turnos, por lo que las citas de RAG / web anteriores permanecen reutilizables más tarde en la misma conversación.

### ✍️ Co-Writer — Espacio de trabajo de escritura AI multidocumento

<div align="center">
<img src="../../assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer es un banco de trabajo Markdown con vista dividida (editor sin formato a la izquierda, vista previa en vivo a la derecha) para notas, informes, tutoriales y borradores asistidos por IA. Cada documento vive en su propio espacio de trabajo con guardado automático, Markdown descargable y **Guardar en Notebook** con un clic.

Selecciona cualquier texto y elige **Reescribir**, **Expandir** o **Acortar** — cada acción se ejecuta como una edición de agente rastreada que opcionalmente puede extraer de una base de conocimiento o la web.

### 📖 Book Engine — «Libros vivos» interactivos

<div align="center">
<img src="../../assets/figs/dt-book.png" alt="Book Engine" width="800">
</div>

Dale a DeepTutor un tema, apúntalo a tu base de conocimiento y produce un libro estructurado e interactivo — no una exportación estática, sino un documento vivo que puedes leer, hacerte preguntas sobre él y discutir en contexto.

Detrás de escena, un pipeline multiagente maneja el trabajo pesado: proponer un esquema, recuperar fuentes relevantes de tu KB, sintetizar un árbol de capítulos, planificar cada página y compilar cada bloque. Tú mantienes el control — revisa la propuesta, reordena capítulos y chatea junto a cualquier página.

Las páginas se ensamblan a partir de 13 tipos de bloques — texto, llamada, quiz, tarjetas flash, código, figura, inmersión profunda, animación, demo interactiva (ahora incluyendo un **visor GeoGebra**), línea de tiempo, grafo de conceptos, sección y nota de usuario.

### 📚 Knowledge Bases — Bibliotecas de documentos listas para RAG

<div align="center">
<img src="../../assets/figs/dt-kb.png" alt="Knowledge Bases" width="800">
</div>

Un espacio de trabajo dedicado para las colecciones de documentos que impulsan RAG. Cada base de conocimiento tiene cuatro pestañas:

- **Files** — Explora las fuentes subidas, previsualiza PDFs en línea y consulta el tamaño/estado por archivo.
- **Add documents** — Añade PDFs, archivos Office (DOCX / XLSX / PPTX), Markdown, texto plano y una amplia variedad de tipos de archivos de código/datos. Los documentos se enrutan automáticamente al extractor apropiado.
- **Index versions** — Cada (re)indexación es una versión rastreada. Vuelve a un índice anterior, compara modelos de embeddings o inspecciona estadísticas de chunking sin perder la compilación anterior.
- **Settings** — Elige el proveedor/modelo de embeddings, los parámetros de chunking y el reranker para la KB.

La indexación está construida sobre **LlamaIndex** de extremo a extremo, con reindexado seguro ante fallos, detección de incompatibilidad de embeddings y manejo resiliente de vectores persistidos corruptos.

### 🌐 Space — Tu biblioteca personal de aprendizaje

<div align="center">
<img src="../../assets/figs/dt-space.png" alt="Space" width="800">
</div>

Space es la contraparte de **lectura / revisión** de las superficies activas. Donde Chat / Co-Writer / Book son donde *produces*, Space es donde vive todo lo que produces, con búsqueda y reproducción.

- **Chat History** — Cada conversación en todos los modos, con renombrado de título, eliminación y reanudación.
- **Notebooks** — Guarda salidas de Chat, Research y Co-Writer en notebooks categorizados y codificados por color.
- **Question Bank** — Cada pregunta de quiz generada automáticamente, marcable con favorito y mencionable con @ en el chat.
- **Skills** — Archivos `SKILL.md` creados por el usuario que definen personas de enseñanza (nombre, descripción, disparadores, cuerpo). Cuando está activo, un skill se inyecta en el prompt del sistema del chat.

### 🧠 Memory — Arquitectura de tres capas

<div align="center">
<img src="../../assets/figs/dt-memory.png" alt="Memory Workbench" width="800">
</div>

La memoria de DeepTutor es ahora un **pipeline de tres capas** con un panel de trabajo inspeccionable en `/memory`. El modelo de dos archivos v1 `SUMMARY.md` / `PROFILE.md` ha desaparecido; todo se migra al nuevo esquema en el primer inicio.

| Capa | Rol | Almacenamiento |
|:---|:---|:---|
| **L1 · Espejo del espacio de trabajo** (EN VIVO) | Traza de solo adición de cada interacción, por superficie, por día. El registro sin pérdidas de lo que realmente sucedió. | `trace/<surface>/<YYYY-MM-DD>.jsonl` |
| **L2 · Resúmenes por superficie** (CURADO) | Hechos específicos de la superficie extraídos por el consolidador. Cada hecho lleva citas de notas a pie de página de regreso a las trazas L1. | `L2/<surface>.md` |
| **L3 · Conocimiento entre superficies** (SÍNTESIS) | Síntesis entre superficies: tu `profile`, línea de tiempo `recent`, `scope` del conocimiento y `preferences`. Afirmaciones matizadas, cada una respaldada por evidencia L2. | `L3/<recent\|profile\|scope\|preferences>.md` |

Siete superficies alimentan el pipeline: **chat, notebook, quiz, kb, book, tutorbot, cowriter**. El consolidador está impulsado por LLM y se ejecuta de forma asíncrona — puedes dispararlo desde el panel de trabajo y ver la propagación L1 → L2 → L3.

<div align="center">
<img src="../../assets/figs/dt-memgraph.png" alt="Memory Graph" width="800">
</div>

El **Memory Graph** (`/memory/graph`) renderiza las tres capas a la vez: síntesis L3 en el centro, hechos L2 en el anillo intermedio, trazas L1 en el exterior, agrupadas por superficie. Pasa el cursor sobre cualquier nodo para una vista previa en línea; haz clic para bloquear el resaltado y rastrear las referencias L3 → L2 → L1 hacia adentro.

### ⚙️ Settings — Centro de control unificado

<div align="center">
<img src="../../assets/figs/dt-settings.png" alt="Settings" width="800">
</div>

La superficie de ajustes se unificó en v1.4 y se dividió por ámbito, con un modelo de borrador / **Apply** para que los cambios sean atómicos y puedan revertirse antes de guardar:

- **Appearance** — Idioma de la interfaz y tema (Cream, Snow, Dark, Glass).
- **Status** — Sonda de salud en vivo para LLM, embeddings, búsqueda y backends de almacenamiento.
- **LLM**, **Embedding**, **Search** — Catálogo de proveedores, URLs base, claves API y selección de modelos activos.
- **Capabilities** — Ajustables por capacidad para Chat, Solve, Quiz, Research, Visualize y Co-Writer. Respaldados por un envoltorio unificado `emit_capability_result` y un `UsageTracker` compartido que muestra el costo por llamada.
- **Memory** — Activa/desactiva ejecuciones del consolidador, configura la cadencia y el presupuesto, y accede al panel de trabajo de memoria.
- **MCP servers** — Registra servidores externos de Model Context Protocol; sus herramientas se muestran junto a las herramientas integradas.
- **Tools** — Inspecciona cada herramienta integrada, sus parámetros, estado (habilitado / próximamente) y estado de i18n.

---

<a id="tutorbot"></a>
### 🦞 TutorBot — Tutores de IA persistentes y autónomos

<div align="center">
<img src="../../assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot no es un chatbot — es un **agente persistente de múltiples instancias** construido sobre [nanobot](https://github.com/HKUDS/nanobot). Cada TutorBot ejecuta su propio bucle de agente con espacio de trabajo, memoria y personalidad independientes.

<div align="center">
<img src="../../assets/figs/dt-tutorbot.png" alt="TutorBot Agents" width="800">
</div>

- **Plantillas Soul** — Define la personalidad, el tono y la filosofía de enseñanza de tu tutor mediante archivos Soul editables.
- **Espacio de trabajo independiente** — Cada bot tiene su propio directorio con memoria, sesiones, skills y configuración separados.
- **Latido proactivo** — Los bots no solo responden — toman la iniciativa. El sistema de Heartbeat integrado permite revisiones de estudio recurrentes, recordatorios de repaso y tareas programadas.
- **Acceso completo a herramientas** — Cada bot accede al conjunto de herramientas completo de DeepTutor: recuperación RAG, ejecución de código, búsqueda web, búsqueda de artículos académicos, razonamiento profundo y lluvia de ideas.
- **Aprendizaje de Skills** — Enseña a tu bot nuevas habilidades añadiendo archivos de skills a su espacio de trabajo.
- **Presencia multicanal** — Conecta bots a Telegram, Discord, Slack, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, Email y más.
- **Equipos y subagentes** — Genera subagentes en segundo plano u orquesta equipos de múltiples agentes dentro de un solo bot.

```bash
deeptutor bot create math-tutor --persona "Profesor de matemáticas socrático que usa preguntas de sondeo"
deeptutor bot create writing-coach --persona "Mentor de escritura paciente y orientado a los detalles"
deeptutor bot list                  # Ver todos tus tutores activos
```

---

<a id="deeptutor-cli"></a>
### ⌨️ DeepTutor CLI — Interfaz nativa para agentes

<div align="center">
<img src="../../assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor es completamente nativo para CLI. Cada capacidad, base de conocimiento, sesión, memoria y TutorBot está a un comando de distancia — sin necesidad de navegador. La CLI sirve tanto a humanos (con renderizado enriquecido en terminal) como a agentes de IA (con salida JSON estructurada).

**Ejecución en un solo paso** — Ejecuta cualquier capacidad directamente desde el terminal:

```bash
deeptutor run chat "Explica la transformada de Fourier" -t rag --kb textbook
deeptutor run deep_solve "Demuestra que √2 es irracional" -t reason
deeptutor run deep_question "Álgebra lineal" --config num_questions=5
deeptutor run deep_research "Mecanismos de atención en transformers"
deeptutor run visualize "Dibuja la arquitectura de un transformer"
```

**REPL interactivo** — Una sesión de chat persistente con cambio de modo en vivo:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Dentro del REPL: /cap, /tool, /kb, /history, /notebook, /config para cambiar al instante
```

**Ciclo de vida de la base de conocimiento**:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # Crear desde documento
deeptutor kb add my-kb --docs-dir ./papers/         # Añadir carpeta de artículos
deeptutor kb search my-kb "descenso de gradiente"   # Buscar directamente
deeptutor kb set-default my-kb                      # Establecer como KB predeterminada
```

**Modo de salida dual**:

```bash
deeptutor run chat "Resume el capítulo 3" -f rich    # Salida formateada y coloreada
deeptutor run chat "Resume el capítulo 3" -f json    # Eventos JSON delimitados por líneas
```

**Continuidad de sesión**:

```bash
deeptutor session list                              # Listar todas las sesiones
deeptutor session open <id>                         # Reanudar en REPL
```

<details>
<summary><b>Referencia completa de comandos CLI</b></summary>

**Nivel superior**

| Comando | Descripción |
|:---|:---|
| `deeptutor run <capability> <message>` | Ejecutar cualquier capacidad en un solo turno (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | REPL interactivo con `--capability`, `--tool`, `--kb`, `--language` opcionales |
| `deeptutor serve` | Iniciar el servidor de API de DeepTutor |

**`deeptutor bot`**

| Comando | Descripción |
|:---|:---|
| `deeptutor bot list` | Listar todas las instancias de TutorBot |
| `deeptutor bot create <id>` | Crear e iniciar un nuevo bot (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Iniciar un bot |
| `deeptutor bot stop <id>` | Detener un bot |

**`deeptutor kb`**

| Comando | Descripción |
|:---|:---|
| `deeptutor kb list` | Listar todas las bases de conocimiento |
| `deeptutor kb info <name>` | Mostrar detalles de la base de conocimiento |
| `deeptutor kb create <name>` | Crear desde documentos (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Añadir documentos incrementalmente |
| `deeptutor kb search <name> <query>` | Buscar en una base de conocimiento |
| `deeptutor kb set-default <name>` | Establecer como KB predeterminada |
| `deeptutor kb delete <name>` | Eliminar una base de conocimiento (`--force`) |

**`deeptutor memory`**

| Comando | Descripción |
|:---|:---|
| `deeptutor memory show [file]` | Ver memoria (`summary`, `profile` o `all`) |
| `deeptutor memory clear [file]` | Borrar memoria (`--force`) |

**`deeptutor session`**

| Comando | Descripción |
|:---|:---|
| `deeptutor session list` | Listar sesiones (`--limit`) |
| `deeptutor session show <id>` | Ver mensajes de la sesión |
| `deeptutor session open <id>` | Reanudar sesión en REPL |
| `deeptutor session rename <id>` | Renombrar una sesión (`--title`) |
| `deeptutor session delete <id>` | Eliminar una sesión |

**`deeptutor notebook`**

| Comando | Descripción |
|:---|:---|
| `deeptutor notebook list` | Listar notebooks |
| `deeptutor notebook create <name>` | Crear un notebook (`--description`) |
| `deeptutor notebook show <id>` | Ver registros del notebook |
| `deeptutor notebook add-md <id> <path>` | Importar markdown como registro |
| `deeptutor notebook replace-md <id> <rec> <path>` | Reemplazar un registro markdown |
| `deeptutor notebook remove-record <id> <rec>` | Eliminar un registro |

**`deeptutor book`**

| Comando | Descripción |
|:---|:---|
| `deeptutor book list` | Listar todos los libros en el espacio de trabajo |
| `deeptutor book health <book_id>` | Verificar la deriva del KB y la salud del libro |
| `deeptutor book refresh-fingerprints <book_id>` | Actualizar huellas digitales del KB y borrar páginas obsoletas |

**`deeptutor config` / `plugin` / `provider`**

| Comando | Descripción |
|:---|:---|
| `deeptutor config show` | Imprimir resumen de la configuración actual |
| `deeptutor plugin list` | Listar herramientas y capacidades registradas |
| `deeptutor plugin info <name>` | Mostrar detalles de herramienta o capacidad |
| `deeptutor provider login <provider>` | Autenticación del proveedor |

</details>

---

<a id="multi-user"></a>
### 👥 Multiusuario — Despliegues compartidos con espacios de trabajo por usuario

<div align="center">
<img src="../../assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Activa la autenticación y DeepTutor se convierte en un despliegue multitenant con **espacios de trabajo aislados por usuario** y **recursos curados por el administrador**. La primera persona en registrarse se convierte en el administrador y configura modelos, claves API y bases de conocimiento en nombre de todos los demás.

**Inicio rápido (5 pasos):**

```bash
# 1. Habilita la autenticación en data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Reinicia el stack web.
deeptutor start

# 3. Abre http://localhost:3782/register y crea la primera cuenta.
#    El primer registro es el único público; ese usuario se convierte en admin
#    y el endpoint /register se cierra automáticamente después.

# 4. Como admin, navega a /admin/users → "Add user" para aprovisionar compañeros.

# 5. Para cada usuario, haz clic en el icono de deslizador → asigna perfiles LLM,
#    bases de conocimiento y skills. Guardar.
```

**Lo que ve el administrador:**

- **Página completa de Settings** en `/settings` — gestiona proveedores LLM / embeddings / búsqueda, claves API, catálogos de modelos y "Apply" en tiempo de ejecución.
- **Gestión de usuarios** en `/admin/users` — crear, promover, degradar y eliminar cuentas.
- **Editor de concesiones** — para cada usuario no administrador, elige los perfiles de modelos, bases de conocimiento y skills que pueden usar. Las concesiones llevan **solo IDs lógicos**; las claves API nunca cruzan el límite de concesión.
- **Registro de auditoría** — cada cambio de concesión se añade a `multi-user/_system/audit/usage.jsonl`.

**Lo que obtienen los usuarios ordinarios:**

- **Espacio de trabajo aislado** bajo `multi-user/<uid>/` — su propio historial de chat (`chat_history.db`), memoria, notebooks y bases de conocimiento personales.
- **Acceso de solo lectura** a las bases de conocimiento y skills asignados por el admin.
- **Página de Settings redactada** — solo tema, idioma y un resumen de los modelos concedidos.
- **LLM con ámbito** — los turnos de chat se enrutan a través del modelo asignado por el admin.

**Esquema del espacio de trabajo:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Credenciales hasheadas, roles
│   ├── auth/auth_secret         # Secreto de firma JWT (autogenerado)
│   ├── grants/<uid>.json        # Concesiones de recursos por usuario (gestionadas por admin)
│   └── audit/usage.jsonl        # Registro de auditoría
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Referencia de configuración:**

| Ajuste | Requerido | Descripción |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Sí | Establece `true` para habilitar la autenticación multiusuario. Predeterminado `false` (modo mono-usuario). |
| `multi-user/_system/auth/auth_secret` | Recomendado | Secreto de firma JWT. Se genera automáticamente en el primer inicio autenticado si falta. |
| `data/user/settings/auth.json: token_expire_hours` | No | Tiempo de vida del JWT; predeterminado `24`. |
| `data/user/settings/auth.json: username/password_hash` | No | Credencial de arranque opcional para un solo usuario sin cabeza. |
| `data/user/settings/system.json` | No | `deeptutor start` deriva las banderas de autenticación del frontend desde la configuración en tiempo de ejecución. |

> ⚠️ **El modo PocketBase (`integrations.pocketbase_url` configurado) es solo para un único usuario.** Los despliegues multiusuario deben mantener `integrations.pocketbase_url` en blanco y usar el backend predeterminado JSON/SQLite.

> ⚠️ **Recomendación de proceso único.** La promoción del primer usuario a administrador está protegida por un `threading.Lock` en proceso. Los despliegues con múltiples trabajadores deben aprovisionar el primer administrador sin conexión o respaldar el almacén de usuarios con un sistema externo.

<a id="community"></a>
## 🌐 Comunidad y ecosistema

DeepTutor está construido sobre los hombros de proyectos de código abierto excepcionales:

| Proyecto | Rol en DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Motor de agente ultraligero que impulsa TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | Pipeline RAG y columna vertebral de indexación de documentos |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | Generación de animaciones matemáticas impulsada por IA para Math Animator |

**Del ecosistema HKUDS:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| RAG Simple y Rápido | Framework de Agentes Sin Código | Investigación Automatizada | Agente de IA Ultraligero |


## 🤝 Contribuciones

<div align="center">

Esperamos que DeepTutor sea un regalo para la comunidad. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

Consulta [CONTRIBUTING.md](../../CONTRIBUTING.md) para obtener pautas sobre cómo configurar tu entorno de desarrollo, estándares de código y flujo de trabajo de pull requests.

## ⭐ Historial de estrellas

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

[⭐ Danos una estrella](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Reportar un error](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discusiones](https://github.com/HKUDS/DeepTutor/discussions)

---

Licenciado bajo [Apache License 2.0](../../LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
