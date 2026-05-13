"""Tests for LlamaIndex document loading."""

from __future__ import annotations

import asyncio
import io
from pathlib import Path

import pytest


def _make_docx(paragraphs: list[str]) -> bytes:
    DocxDocument = pytest.importorskip("docx").Document
    doc = DocxDocument()
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _make_xlsx(rows: list[list[object]]) -> bytes:
    Workbook = pytest.importorskip("openpyxl").Workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Data"
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _make_pptx(texts: list[str]) -> bytes:
    Presentation = pytest.importorskip("pptx").Presentation
    Inches = pytest.importorskip("pptx.util").Inches
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[5])
    for index, text in enumerate(texts):
        text_box = slide.shapes.add_textbox(
            Inches(1),
            Inches(1 + index * 0.5),
            Inches(6),
            Inches(0.5),
        )
        text_box.text_frame.text = text
    buffer = io.BytesIO()
    presentation.save(buffer)
    return buffer.getvalue()


def test_loader_extracts_chat_supported_office_files(tmp_path: Path) -> None:
    pytest.importorskip("llama_index.core")
    from deeptutor.services.rag.pipelines.llamaindex.document_loader import (
        LlamaIndexDocumentLoader,
    )

    docx_path = tmp_path / "notes.docx"
    docx_path.write_bytes(_make_docx(["Docx paragraph"]))
    xlsx_path = tmp_path / "book.xlsx"
    xlsx_path.write_bytes(_make_xlsx([["cell-a", 42]]))
    pptx_path = tmp_path / "slides.pptx"
    pptx_path.write_bytes(_make_pptx(["Slide title", "Slide body"]))

    documents = asyncio.run(
        LlamaIndexDocumentLoader().load([str(docx_path), str(xlsx_path), str(pptx_path)])
    )

    assert {doc.metadata["file_name"] for doc in documents} == {
        "notes.docx",
        "book.xlsx",
        "slides.pptx",
    }
    all_text = "\n".join(doc.text for doc in documents)
    assert "Docx paragraph" in all_text
    assert "cell-a" in all_text
    assert "42" in all_text
    assert "Slide title" in all_text
    assert "Slide body" in all_text


def test_loader_skips_images_when_embedding_provider_is_text_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("llama_index.core")
    from deeptutor.services.rag.pipelines.llamaindex import document_loader as loader_module

    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n")

    class _TextOnlyClient:
        config = type("Config", (), {"binding": "openai", "model": "text-embedding-3-small"})()

        def supports_multimodal_contents(self) -> bool:
            return False

    monkeypatch.setattr(loader_module, "get_embedding_client", lambda: _TextOnlyClient())

    documents = asyncio.run(loader_module.LlamaIndexDocumentLoader().load([str(image_path)]))

    assert documents == []


def test_loader_embeds_images_when_embedding_provider_is_multimodal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("llama_index.core")
    from llama_index.core.schema import ImageNode

    from deeptutor.services.rag.pipelines.llamaindex import document_loader as loader_module

    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n")
    captured: dict[str, object] = {}

    class _MultimodalClient:
        config = type("Config", (), {"binding": "siliconflow", "model": "qwen3-vl"})()

        def supports_multimodal_contents(self) -> bool:
            return True

        async def embed_contents(self, contents):
            captured["contents"] = contents
            return [[0.1, 0.2, 0.3]]

    class _VisionClient:
        config = type("Config", (), {"binding": "openai", "model": "gpt-4o"})()

        def supports_multimodal_images(self) -> bool:
            return True

        async def complete(self, prompt, **kwargs):
            captured["llm_prompt"] = prompt
            captured["llm_kwargs"] = kwargs
            return "A logo image with visible HKU text."

    monkeypatch.setattr(loader_module, "get_embedding_client", lambda: _MultimodalClient())
    monkeypatch.setattr(loader_module, "get_llm_client", lambda: _VisionClient())

    documents = asyncio.run(loader_module.LlamaIndexDocumentLoader().load([str(image_path)]))

    assert len(documents) == 1
    assert isinstance(documents[0], ImageNode)
    assert documents[0].embedding == [0.1, 0.2, 0.3]
    assert documents[0].metadata["content_type"] == "image"
    assert documents[0].metadata["image_description"] == "A logo image with visible HKU text."
    assert "A logo image with visible HKU text." in documents[0].text
    assert captured["contents"][0]["image"].startswith("data:image/png;base64,")
    assert captured["llm_kwargs"]["image_mime_type"] == "image/png"


def test_loader_skips_images_when_llm_is_text_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("llama_index.core")
    from deeptutor.services.rag.pipelines.llamaindex import document_loader as loader_module

    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n")

    class _MultimodalEmbeddingClient:
        config = type("Config", (), {"binding": "siliconflow", "model": "qwen3-vl"})()

        def supports_multimodal_contents(self) -> bool:
            return True

    class _TextOnlyLLMClient:
        config = type("Config", (), {"binding": "openai", "model": "gpt-3.5-turbo"})()

        def supports_multimodal_images(self) -> bool:
            return False

    monkeypatch.setattr(
        loader_module, "get_embedding_client", lambda: _MultimodalEmbeddingClient()
    )
    monkeypatch.setattr(loader_module, "get_llm_client", lambda: _TextOnlyLLMClient())

    documents = asyncio.run(loader_module.LlamaIndexDocumentLoader().load([str(image_path)]))

    assert documents == []


def test_loader_logs_all_missing_multimodal_image_requirements(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    pytest.importorskip("llama_index.core")
    from deeptutor.services.rag.pipelines.llamaindex import document_loader as loader_module

    image_path = tmp_path / "photo.png"
    image_path.write_bytes(b"\x89PNG\r\n")

    class _TextOnlyEmbeddingClient:
        config = type("Config", (), {"binding": "openai", "model": "text-embedding-3-small"})()

        def supports_multimodal_contents(self) -> bool:
            return False

    class _TextOnlyLLMClient:
        config = type("Config", (), {"binding": "openai", "model": "gpt-3.5-turbo"})()

        def supports_multimodal_images(self) -> bool:
            return False

    monkeypatch.setattr(loader_module, "get_embedding_client", lambda: _TextOnlyEmbeddingClient())
    monkeypatch.setattr(loader_module, "get_llm_client", lambda: _TextOnlyLLMClient())

    with caplog.at_level("WARNING"):
        documents = asyncio.run(loader_module.LlamaIndexDocumentLoader().load([str(image_path)]))

    assert documents == []
    assert "requires both multimodal embedding and multimodal LLM support" in caplog.text
    assert "embedding provider/model does not support multimodal contents" in caplog.text
    assert "LLM provider/model does not support multimodal image input" in caplog.text
    assert "text-embedding-3-small" in caplog.text
    assert "gpt-3.5-turbo" in caplog.text
