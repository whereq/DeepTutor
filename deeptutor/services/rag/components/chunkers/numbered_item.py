"""
Numbered Item Extractor
=======================

Extracts numbered items (definitions, theorems, equations) from documents.
"""

from typing import List

from ...types import Chunk, Document
from ..base import BaseComponent


class NumberedItemExtractor(BaseComponent):
    """
    Extract numbered items (definitions, theorems, equations) from documents.

    Uses LLM to identify and extract structured academic content like
    definitions, theorems, lemmas, propositions, equations, etc.
    """

    name = "numbered_item_extractor"

    def __init__(self, batch_size: int = 20, max_concurrent: int = 5):
        """
        Initialize numbered item extractor.

        Args:
            batch_size: Number of content items to process per batch
            max_concurrent: Maximum concurrent LLM calls
        """
        super().__init__()
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent

    async def process(self, doc: Document, **kwargs) -> List[Chunk]:
        """
        Extract numbered items from a document.

        Args:
            doc: Document to extract from (must have content_items)
            **kwargs: Additional arguments

        Returns:
            List of Chunks representing numbered items
        """
        if not doc.content_items:
            self.logger.warning("No content_items in document, skipping extraction")
            return []

        _ = kwargs
        self.logger.info(
            "Numbered item extraction is deprecated and disabled in llamaindex-only mode; skipping"
        )
        return []
