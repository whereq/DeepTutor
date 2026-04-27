from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from deeptutor.services.rag.index_versioning import EmbeddingSignature


def _signature() -> EmbeddingSignature:
    return EmbeddingSignature(
        binding="openai",
        model="embed-a",
        dimension=1024,
        base_url="https://example.test/v1",
        api_version="",
    )


@pytest.mark.asyncio
async def test_incremental_add_migrates_matching_legacy_index_to_flat_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from deeptutor.services.rag.pipelines import llamaindex as llamaindex_module

    sig = _signature()
    kb_dir = tmp_path / "kb"
    raw_file = kb_dir / "raw" / "new.txt"
    raw_file.parent.mkdir(parents=True)
    raw_file.write_text("new content", encoding="utf-8")

    legacy_version_dir = kb_dir / "index_versions" / sig.hash()
    legacy_storage_dir = legacy_version_dir / "llamaindex_storage"
    legacy_storage_dir.mkdir(parents=True)
    (legacy_storage_dir / "docstore.json").write_text("{}", encoding="utf-8")
    (legacy_version_dir / "meta.json").write_text(
        json.dumps({"signature": sig.hash(), "version": sig.hash()}),
        encoding="utf-8",
    )

    captured: dict[str, str] = {}

    class _FakeStorageContext:
        @classmethod
        def from_defaults(cls, persist_dir: str):
            captured["load_dir"] = persist_dir
            return cls()

        def persist(self, persist_dir: str) -> None:
            captured["persist_dir"] = persist_dir
            target = Path(persist_dir)
            target.mkdir(parents=True, exist_ok=True)
            (target / "docstore.json").write_text("{}", encoding="utf-8")

    class _FakeIndex:
        def __init__(self) -> None:
            self.storage_context = _FakeStorageContext()
            self.inserted = []

        def insert(self, document) -> None:
            self.inserted.append(document)

    async def _read_text_file(path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    async def _verify_embedding_connectivity(self) -> None:
        return None

    monkeypatch.setattr(
        llamaindex_module.LlamaIndexPipeline,
        "_configure_settings",
        lambda self: None,
    )
    monkeypatch.setattr(
        llamaindex_module.Settings,
        "_embed_model",
        object(),
        raising=False,
    )
    monkeypatch.setattr(
        llamaindex_module.LlamaIndexPipeline,
        "_verify_embedding_connectivity",
        _verify_embedding_connectivity,
    )
    monkeypatch.setattr(llamaindex_module, "signature_from_embedding_config", lambda: sig)
    monkeypatch.setattr(
        llamaindex_module.FileTypeRouter,
        "classify_files",
        lambda paths: SimpleNamespace(
            parser_files=[],
            text_files=list(paths),
            unsupported=[],
        ),
    )
    monkeypatch.setattr(
        llamaindex_module.FileTypeRouter,
        "read_text_file",
        _read_text_file,
    )
    monkeypatch.setattr(llamaindex_module, "StorageContext", _FakeStorageContext)
    monkeypatch.setattr(
        llamaindex_module,
        "load_index_from_storage",
        lambda _storage_context: _FakeIndex(),
    )

    pipeline = llamaindex_module.LlamaIndexPipeline(kb_base_dir=str(tmp_path))

    assert await pipeline.add_documents("kb", [str(raw_file)]) is True

    flat_storage_dir = kb_dir / "version-1"
    assert captured["load_dir"] == str(legacy_storage_dir)
    assert captured["persist_dir"] == str(flat_storage_dir)
    assert (flat_storage_dir / "docstore.json").exists()
    assert json.loads((flat_storage_dir / "meta.json").read_text())["signature"] == sig.hash()
