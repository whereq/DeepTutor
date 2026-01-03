# Contributing to DeepTutor

Thank you for your interest in contributing to DeepTutor! 🎉

You can join our discord community for further discussion: https://discord.gg/aka9p9EW

## 🔄 Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow existing code style and conventions
3. **Test locally**: Ensure your changes work correctly
4. **Commit**: Pre-commit hooks will auto-format your code
5. **Push & PR**: Open a pull request with a clear description

## 🛠️ Code Quality

We use automated tools to maintain code quality:

- **Ruff** — Python linting & formatting (`pyproject.toml`)
- **Prettier** — Frontend formatting (`web/.prettierrc.json`)
- **detect-secrets** — Security scanning

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
pre-commit run --all-files
```

## ⚙️ Configuration Guidelines

- **LLM parameters** (`temperature`, `max_tokens`): Edit `config/agents.yaml`
- **System settings** (paths, logging, tools): Edit `config/main.yaml`
- **API keys**: Use `.env` file (never commit secrets)

See [config/README.md](config/README.md) for details.

## 📋 Commit Message Format

```
<type>: <short description>

[optional body]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
- `feat: add PDF export for research reports`
- `fix: resolve WebSocket connection timeout`
- `docs: update installation instructions`

---

Let's build a tutoring system for the whole community TOGETHER! 🚀

