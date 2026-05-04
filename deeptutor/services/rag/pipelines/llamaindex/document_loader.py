"""Document loading for the LlamaIndex RAG pipeline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from llama_index.core import Document

from deeptutor.services.rag.file_routing import FileTypeRouter
from deeptutor.utils.document_extractor import DocumentExtractionError, extract_text_from_path
from deeptutor.utils.document_validator import DocumentValidator


class LlamaIndexDocumentLoader:
    """Convert source files into LlamaIndex ``Document`` objects."""

    def __init__(self, logger=None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    async def load(self, file_paths: Iterable[str]) -> list[Document]:
        documents: list[Document] = []
        classification = FileTypeRouter.classify_files(list(file_paths))

        for file_path_str in classification.parser_files:
            file_path = Path(file_path_str)
            self.logger.info(f"Parsing document: {file_path.name}")
            text = self._extract_parser_text(file_path)
            self._append_if_nonempty(documents, file_path, text)

        for file_path_str in classification.text_files:
            file_path = Path(file_path_str)
            self.logger.info(f"Parsing text: {file_path.name}")
            text = await FileTypeRouter.read_text_file(str(file_path))
            self._append_if_nonempty(documents, file_path, text)

        for file_path_str in classification.unsupported:
            self.logger.warning(f"Skipped unsupported file: {Path(file_path_str).name}")

        return documents

    def _extract_parser_text(self, file_path: Path) -> str:
        max_bytes = (
            DocumentValidator.MAX_PDF_SIZE
            if file_path.suffix.lower() == ".pdf"
            else DocumentValidator.MAX_FILE_SIZE
        )
        try:
            return extract_text_from_path(file_path, max_bytes=max_bytes, max_chars=None)
        except (DocumentExtractionError, OSError) as exc:
            self.logger.error(f"Failed to extract {file_path.name}: {exc}")
            return ""

    def _append_if_nonempty(self, documents: list[Document], file_path: Path, text: str) -> None:
        if text.strip():
            documents.append(
                Document(
                    text=text,
                    metadata={
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                    },
                )
            )
            self.logger.info(f"Loaded: {file_path.name} ({len(text)} chars)")
        else:
            self.logger.warning(f"Skipped empty document: {file_path.name}")
