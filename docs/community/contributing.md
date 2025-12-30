# Contributing

Thank you for your interest in contributing to DeepTutor! 🎉

We welcome contributions from the community! To ensure code quality and consistency, please follow the guidelines below.

## Ways to Contribute

- 🐛 **Report bugs** — Open an issue with reproduction steps
- 💡 **Suggest features** — Share your ideas in discussions
- 📖 **Improve docs** — Fix typos, add examples
- 🔧 **Submit PRs** — Code contributions welcome!

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/DeepTutor.git
cd DeepTutor
```

### 2. Set Up Environment

```bash
# Using conda (recommended)
conda create -n aitutor python=3.10
conda activate aitutor

# Or using venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Automated installation (recommended)
bash scripts/install_all.sh

# Or manual installation
pip install -r requirements.txt
npm install
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install Git hooks
pre-commit install

# (Optional) Run checks on all files
pre-commit run --all-files
```

## Code Quality Tools

We use automated tools to maintain code quality:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Python linting & formatting | `pyproject.toml` |
| **Prettier** | Frontend code formatting | `web/.prettierrc.json` |
| **detect-secrets** | Security check | `.secrets.baseline` |

> **Note**: The project uses **Ruff format** instead of Black to avoid formatting conflicts.

Every time you run `git commit`, pre-commit hooks will automatically:
- Format Python code with Ruff
- Format frontend code with Prettier
- Check for syntax errors
- Validate YAML/JSON files
- Detect potential security issues

## Pull Request Process

1. **Create Branch**: `git checkout -b feature/amazing-feature`
2. **Make Changes**: Write your code following the project's style
3. **Test**: Ensure your changes work correctly
4. **Commit**: Pre-commit hooks will automatically format your code
5. **Push and PR**: Push to your fork and create a Pull Request

### Common Commands

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

## Contribution Guidelines

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Create Branch**: Create a feature branch from `main`
3. **Install Pre-commit**: Follow the setup steps above
4. **Make Changes**: Write your code following the project's style
5. **Test**: Ensure your changes work correctly
6. **Commit**: Pre-commit hooks will automatically format your code
7. **Push and PR**: Push to your fork and create a Pull Request

## Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Provide detailed information about the issue
- Include steps to reproduce if it's a bug

## Code of Conduct

Please be respectful and inclusive. We're building a welcoming community for learners and contributors alike.

## Questions?

- Open a [GitHub Discussion](https://github.com/HKUDS/DeepTutor/discussions)
- Check existing issues for similar questions

---

❤️ Thank you for helping make DeepTutor better!
