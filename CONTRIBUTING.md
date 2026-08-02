# CONTRIBUTING.md — Aturan Pengembangan CrewAI Ebook

Aturan wajib bagi siapa pun (termasuk agent AI) yang mengubah program ini.

## 1. Changelog Wajib Sebelum Push

Setiap perubahan pada program **WAJIB** dicatat di `CHANGELOG.md` **sebelum** git push.

Langkah:
1. Ubah kode → uji sampai sukses.
2. Tambahkan entri di bagian atas `CHANGELOG.md` (di bawah header), format:
   `## [YYYY-MM-DD] <jenis> — <pesan ringkas>`
   lalu daftar file yang diubah.
3. Commit: sertakan `CHANGELOG.md` dalam commit yang sama dengan perubahan kode.
4. Push ke `main`.

Jenis perubahan: `feat`, `fix`, `refactor`, `docs`, `chore`, `init`.

## 2. Uji Sebelum Commit

- Jangan commit kode yang belum diuji sukses.
- Konversi PDF/EPUB wajib diverifikasi file outputnya benar-benar ada.

## 3. Destinasi Hasil Ebook

- Folder hasil default: `C:/Users/Administrator/Desktop/ebook-crew`.
- Ubah destinasi di `ebook_saver.py` (`DEFAULT_OUTPUT_DIR`) — **JANGAN** ubah di `main.py`.

## 4. Engine PDF

- PDF memakai Pandoc dengan engine Typst (`--pdf-engine=typst`).
- Jangan ganti ke xelatex/pdflatex tanpa memasang TeX Live (engine tidak tersedia di sistem ini).

## 5. Model LLM

- Model id TANPA slash (misal `gemini-3.5-flash-lite`, `COMBO-UTAMA`) agar lewat 9Router base_url.
- `kr/*` dan id berslash gagal lewat CrewAI (LiteLLM unknown provider).
- `gemini-3.6-flash` kena rate limit 429 setelah 2-3 run — pakai `gemini-3.5-flash-lite`.

## 6. Jangan Commit

- `output/`, `test.md`, `.env` (kredensial), `venv/`, `__pycache__/`.

## 7. Struktur Modul

- `main.py` — orkestrasi crew (agents/tasks/kickoff), panggil `save_ebook()`.
- `ebook_saver.py` — penyimpanan + konversi, `DEFAULT_OUTPUT_DIR` di sini.
- `pdf_epub_converter.py` — `markdown_to_pdf()` / `markdown_to_epub()` via Pandoc.
