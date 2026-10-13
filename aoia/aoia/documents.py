from __future__ import annotations

from typing import Tuple
from bs4 import BeautifulSoup
from .page_gate import classify_page

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

def parse_html_document(html_content: str, url: str) -> Tuple[str, str, str]:
    """Parse HTML content, returning (title, plain_text, kind)."""
    soup = BeautifulSoup(html_content, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    kind = classify_page(url=url, title=title, status=200, text=text)
    return title, text, kind

def parse_pdf_document(pdf_bytes: bytes, url: str) -> Tuple[str, str, str]:
    """Parse text-layer PDF with PyMuPDF. No OCR; image-only PDFs yield empty text."""
    if not fitz:
        return "", "", "OTHER"
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)
        full_text = "\n".join(text_parts).strip()
        doc_title = (doc.metadata.get("title") or "").strip() if doc.metadata else ""
        if not doc_title and full_text:
            lines = [line.strip() for line in full_text.splitlines() if line.strip()]
            if lines:
                doc_title = lines[0][:100]
        kind = classify_page(url=url, title=doc_title, status=200, text=full_text)
        return doc_title, full_text, kind
    except Exception:
        return "", "", "OTHER"
