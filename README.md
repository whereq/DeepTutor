# branch structure and status overview

this document outlines the current state and purpose of the active branches in the repository. documentation is provided to facilitate rebasing strategies and merge order.

## core branches

### dev
primary development branch. serves as the baseline for all feature and work branches. contains the most recent merged code for the agent architectures, api routers, and web interface.

### shk-dev
synchronization branch for upstream/dev. used as a staging area to pull latest changes from the upstream repository and resolve merge conflicts before propagating updates to specific feature branches.

## architectural and feature branches

### feature/config-governance
implements centralized configuration governance. introduces `config_manager.py` to enforce schema validation and provide a unified interface for system settings. this branch is currently required as a dependency for advanced error handling logic to manage retry counts and timeouts globally.

### work/llm-error-framework
introduces a provider-registry architecture, unified error mapping, and telemetry. replaces direct exception pass-through in the service layer with standardized exceptions.
* **status:** high priority integration.
* **dependency:** requires rebasing onto `dev` to resolve conflicts in `factory.py` and sync with `config_manager.py`.

### ui/provider-autofill-model-dropdown
targets the `web/` directory components. enables dynamic population of model selection inputs based on the currently active llm provider configuration. reduces hardcoded values in the frontend interface.

## optimization and maintenance branches

### work/ingestion-oom-hardening
focuses on the `src/knowledge` module. implements improvements to memory management during document parsing and vector store ingestion. designed to prevent out-of-memory process termination when processing large pdfs or extensive datasets.

### work/focused-error-handling
addresses specific, localized exception scenarios within agent loops. distinct from the systemic changes in the `llm-error-framework`, this branch provides immediate patches for common runtime failures in the solve and research agents.

### build/cloud
contains infrastructure configurations required for cloud deployment environments. includes adjustments to `dockerfile` and container orchestration scripts to support remote execution contexts different from local development.
