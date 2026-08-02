"""
ebook_saver.py — Modul penyimpanan & konversi ebook.

Semua pengaturan destinasi hasil ada DI SINI. Ubah DEFAULT_OUTPUT_DIR
untuk memindahkan folder tujuan tanpa menyentuh main.py.
"""

import os
import re
from datetime import datetime
from pathlib import Path

import pdf_epub_converter

# ============================================================
# DESTINASI HASIL EBOOK — ubah path ini untuk pindah folder
# ============================================================
DEFAULT_OUTPUT_DIR = Path("C:/Users/Administrator/Desktop/ebook-crew")


def slugify(text, max_len=60):
    """Ubah teks topik menjadi nama file yang aman."""
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "_", slug).strip("-_")
    return slug[:max_len] or "ebook"


def save_ebook(markdown_text, topic, output_dir=None):
    """
    Simpan naskah Markdown ke folder tujuan lalu konversi ke PDF + EPUB.

    Args:
        markdown_text: Isi ebook final (string Markdown).
        topic: Topik/judul ebook — dipakai untuk nama file.
        output_dir: Folder tujuan (optional). Default: DEFAULT_OUTPUT_DIR.

    Returns:
        tuple (md_path, pdf_path, epub_path)
    """
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{slugify(topic)}_{timestamp}"

    md_path = out_dir / f"{base_name}.md"
    md_path.write_text(markdown_text, encoding="utf-8")
    print(f"[SAVE] Markdown -> {md_path}")

    pdf_path = pdf_epub_converter.markdown_to_pdf(str(md_path), str(out_dir))
    epub_path = pdf_epub_converter.markdown_to_epub(str(md_path), str(out_dir))
    print(f"[SAVE] PDF -> {pdf_path}")
    print(f"[SAVE] EPUB -> {epub_path}")
    return md_path, pdf_path, epub_path
