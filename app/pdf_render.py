from __future__ import annotations

import io
from typing import Dict, Iterable, List, Optional

import fitz  # PyMuPDF


def render_pdf_pages_to_images(
    pdf_path: str,
    dpi: int = 200,
    page_numbers: Optional[Iterable[int]] = None,
) -> Dict[int, bytes]:
    """
    Render selected PDF pages to PNG images in-memory.

    Args:
        pdf_path: Path to the input PDF file.
        dpi: Dots per inch for rendering; controls output resolution.
        page_numbers: 1-indexed page numbers to render. If None, render all pages.

    Returns:
        Mapping from 1-indexed page number to PNG byte content.
    """
    images_by_page: Dict[int, bytes] = {}
    with fitz.open(pdf_path) as doc:
        total_pages: int = doc.page_count
        if page_numbers is None:
            target_pages: List[int] = list(range(1, total_pages + 1))
        else:
            target_pages = sorted({p for p in page_numbers if 1 <= p <= total_pages})
            if not target_pages:
                return images_by_page

        zoom: float = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        for page_number in target_pages:
            page = doc.load_page(page_number - 1)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            png_bytes: bytes = pix.tobytes("png")
            images_by_page[page_number] = png_bytes

    return images_by_page