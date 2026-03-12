# Web Frontend

DeepTutor's frontend is a Next.js 16 application with a warm, Claude-inspired
interface built around four pages:

- `/` — unified chat
- `/knowledge` — knowledge bases and notebooks
- `/memory` — learner memory
- `/playground` — tools and capabilities
- `/settings` — API keys and interface preferences

## Structure

```text
web/
├── app/
│   ├── page.tsx
│   ├── knowledge/page.tsx
│   ├── memory/page.tsx
│   ├── playground/page.tsx
│   ├── settings/page.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── Sidebar.tsx
│   ├── ThemeScript.tsx
│   └── common/
│       └── MarkdownRenderer.tsx
├── context/
│   └── UnifiedChatContext.tsx
├── i18n/
│   ├── I18nClientBridge.tsx
│   └── I18nProvider.tsx
└── lib/
    ├── api.ts
    ├── latex.ts
    └── unified-ws.ts
```

## Main Ideas

### Unified chat

The home page is the primary interaction surface. It combines:

- tool toggles on the left side of the composer
- capability selection on the right side
- streaming progress blocks for long-running tasks
- markdown rendering with KaTeX support

### Knowledge workspace

The knowledge page keeps all core knowledge-base operations:

- create knowledge base
- upload documents
- track processing progress
- set default knowledge base
- delete knowledge bases
- create and list notebooks

### Memory and playground

- Memory reads from user-data and displays summary / weakness / reflection
- Playground splits registered **tools** and **capabilities**

## Development

```bash
cd web
npm install
npm run dev
```

## Production build

```bash
cd web
npm run build
```
