# deeptutor-cli

CLI-only DeepTutor distribution. It installs the `deeptutor` command and the
Python modules required for terminal workflows, RAG, document parsing, and model
provider integrations, but it does not ship the packaged Next.js Web assets or
FastAPI/Uvicorn server dependencies used by `deeptutor start`.

Build from this repository root with a release workflow that uses this directory
as the package project.
