# Contributing to DeepTutor

Thank you for your interest in contributing to DeepTutor! That menas a lot for our team!

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

This project uses **pre-commit hooks** to automatically format code and check for issues before commits.

**Step 1: Install pre-commit**
```bash
# Using pip
pip install pre-commit

# Or using conda
conda install -c conda-forge pre-commit
```

**Step 2: Install Git hooks**
```bash
cd DeepTutor
pre-commit install
```

**Step 3: Run checks on all files**
```bash
pre-commit run --all-files
```

**Common Commands**

```bash
# Normal commit (hooks run automatically)
git commit -m "Your commit message"

# Manually check all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate

# Skip hooks (not recommended, only for emergencies)
git commit --no-verify -m "Emergency fix"
```

</details>

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

### Let's build a tutoring system for the whole community TOGETHER! 🚀
