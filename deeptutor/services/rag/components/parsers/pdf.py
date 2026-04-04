"""
PDF Parser
==========

Parser for PDF documents.
"""

import json
from pathlib import Path
from typing import Optional, Union

from ...types import Document
from ..base import BaseComponent


class PDFParser(BaseComponent):
    """
    PDF parser for extraction.
    """

    name = "pdf_parser"

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize PDF parser.

        Args:
            output_dir: Directory to store parsed output
        """
        super().__init__()
        self.output_dir = output_dir

    async def process(self, file_path: Union[str, Path], **kwargs) -> Document:
        """
        Parse a PDF file into a Document.

        Args:
            file_path: Path to the PDF file
            **kwargs: Additional arguments

        Returns:
            Parsed Document with content and content_items
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        self.logger.info(f"Parsing PDF: {file_path.name}")

        # Check for existing parsed content
        output_dir = Path(kwargs.get("output_dir", self.output_dir or file_path.parent))
        content_list_file = output_dir / f"{file_path.stem}.json"

        content_items = []
        content = ""

        if content_list_file.exists():
            # Load existing parsed content
            self.logger.info(f"Loading existing parsed content from {content_list_file}")
            with open(content_list_file, "r", encoding="utf-8") as f:
                content_items = json.load(f)

            # Extract text content
            content = self._extract_text_from_content_items(content_items)
        else:
            # Parse PDF with local fallback extraction
            self.logger.warning(
                "No pre-parsed content found. Falling back to local PDF text extraction."
            )
            # Basic text extraction fallback
            content = await self._basic_pdf_extract(file_path)

        return Document(
            content=content,
            file_path=str(file_path),
            content_items=content_items,
            metadata={
                "filename": file_path.name,
                "parser": self.name,
            },
        )

    def _extract_text_from_content_items(self, content_items: list) -> str:
        """Extract plain text from content-item payloads."""
        texts = []
        for item in content_items:
            if isinstance(item, dict):
                if "text" in item:
                    texts.append(item["text"])
                elif "content" in item:
                    texts.append(item["content"])
        return "\n\n".join(texts)

    async def _basic_pdf_extract(self, file_path: Path) -> str:
        """Basic PDF text extraction fallback."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            texts = []
            for page in doc:
                texts.append(page.get_text())
            doc.close()
            return "\n\n".join(texts)
        except ImportError:
            self.logger.warning("PyMuPDF not installed. Cannot extract PDF text.")
            return ""
        except Exception as e:
            self.logger.error(f"Failed to extract PDF text: {e}")
            return ""
