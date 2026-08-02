"""
ebook_saver.py — Modul penyimpanan & konversi ebook.

Semua pengaturan destinasi hasil ada DI SINI. Ubah DEFAULT_OUTPUT_DIR
untuk memindahkan folder tujuan tanpa menyentuh main.py.
"""

import os
import re
import time
import urllib.request
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


import time

IMG_MD_PATTERN = re.compile(r"!\[([^\]]*)\]\((https?://[^)]+)\)")
# pattern utk path gambar lokal yg sudah ada di markdown (mis. img_01.jpg hasil run sblmnya)
IMG_LOCAL_PATTERN = re.compile(r"!\[([^\]]*)\]\((img_\d+\.(?:jpg|jpeg|png|gif|webp|svg))\)")


def download_images(markdown_text, assets_dir):
    """Unduh semua gambar remote ke folder assets, return markdown dgn path lokal.
    Juga salin path gambar lokal yang sudah ada (img_XX.ext) ke assets_dir agar
    output self-contained (resource-path konverter = assets_dir)."""
    os.makedirs(assets_dir, exist_ok=True)
    counter = [0]

    def _copy_local(m):
        alt, fname = m.group(1), m.group(2)
        src = Path(fname)
        if not src.exists():
            # reuse markdown: gambar ada di folder *_assets (cwd atau sibling output)
            search_dirs = [Path.cwd(), assets_dir.parent]
            for d in search_dirs:
                for cand in d.glob(f"*_assets/{fname}"):
                    src = cand
                    break
                if src.exists():
                    break
        if src.exists():
            dest = assets_dir / fname
            if not dest.exists():
                dest.write_bytes(src.read_bytes())
            counter[0] += 1
            return f"![{alt}]({fname})"
        return m.group(0)  # biarkan — nanti di-resolve via resource-path

    def _replace(m):
        alt, url = m.group(1), m.group(2)
        if "upload.wikimedia.org" not in url:
            return m.group(0)  # skip non-wikimedia
        counter[0] += 1
        ext = ".jpg"
        for e in (".png", ".gif", ".webp", ".svg", ".jpeg"):
            if e in url.split("?")[0].lower():
                ext = e
                break
        fname = f"img_{counter[0]:02d}{ext}"
        dest = assets_dir / fname
        # jika URL thumbnail 404, coba Special:FilePath (redirect ke file asli)
        candidates = [url]
        m_fname = re.search(r"/(?:thumb/)?[^/]+/([^/?#]+\.(?:jpg|jpeg|png|gif|webp|svg))(?:\\?|$)", url, re.I)
        if m_fname:
            # buang prefix thumbnail "330px-" / "960px-" -> nama file asli
            raw = m_fname.group(1)
            real = re.sub(r"^\d+px-", "", raw)
            candidates.append(
                "https://commons.wikimedia.org/wiki/Special:FilePath/" + real
            )
        for cand in candidates:
            try:
                req = urllib.request.Request(
                    cand, headers={"User-Agent": "CrewAI-Ebook/1.0 (image download)"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    dest.write_bytes(resp.read())
                time.sleep(3)  # hindari rate limit Wikimedia
                print(f"[IMG] {fname} ({dest.stat().st_size} bytes)")
                return f"![{alt}]({fname})"
            except Exception as e:
                print(f"[IMG] coba {cand[:60]}... -> {e}")
        print(f"[IMG] GAGAL {url[:60]}")
        # URL mati — ganti jadi komentar HTML, bukan biarkan URL rusak di ebook
        return f"<!-- gambar gagal diunduh: {url[:80]} -->"

    # 1) salin path lokal yang sudah ada, 2) unduh URL remote
    out = IMG_LOCAL_PATTERN.sub(_copy_local, markdown_text)
    return IMG_MD_PATTERN.sub(_replace, out)


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
    assets_dir = out_dir / f"{base_name}_assets"

    # Unduh gambar remote ke lokal agar PDF/EPUB render gambar
    markdown_local = download_images(markdown_text, assets_dir)

    md_path = out_dir / f"{base_name}.md"
    md_path.write_text(markdown_local, encoding="utf-8")
    print(f"[SAVE] Markdown -> {md_path}")

    # resource-path = folder assets agar pandoc resolve img_XX.jpg (fix gambar tak muncul di PDF)
    pdf_path = pdf_epub_converter.markdown_to_pdf(str(md_path), str(out_dir), str(assets_dir))
    epub_path = pdf_epub_converter.markdown_to_epub(str(md_path), str(out_dir), str(assets_dir))
    print(f"[SAVE] PDF -> {pdf_path}")
    print(f"[SAVE] EPUB -> {epub_path}")
    return md_path, pdf_path, epub_path
