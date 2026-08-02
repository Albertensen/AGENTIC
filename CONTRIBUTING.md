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

## 2. Release Notes Per Rilis

- Setiap rilis (setelah kumpulan perubahan bermakna) WAJIB update `RELEASE_NOTES.md` di bagian atas.
- Format: `## v<MAJOR>.<MINOR>.<PATCH> — YYYY-MM-DD`, lalu section `Fitur`, `Perbaikan`, `Catatan`.
- Detail teknis tetap di `CHANGELOG.md`; release notes untuk ringkasan pengguna.

## 3. Uji Sebelum Commit

- Jangan commit kode yang belum diuji sukses.
- Konversi PDF/EPUB wajib diverifikasi file outputnya benar-benar ada.

## 4. Destinasi Hasil Ebook

- Folder hasil default: `C:/Users/Administrator/Desktop/ebook-crew`.
- Ubah destinasi di `ebook_saver.py` (`DEFAULT_OUTPUT_DIR`) — **JANGAN** ubah di `main.py`.

## 5. Engine PDF

- PDF memakai Pandoc dengan engine Typst (`--pdf-engine=typst`).
- Jangan ganti ke xelatex/pdflatex tanpa memasang TeX Live (engine tidak tersedia di sistem ini).

## 6. Model LLM

- Model id TANPA slash (misal `gemini-3.5-flash-lite`, `COMBO-UTAMA`) agar lewat 9Router base_url.
- `kr/*` dan id berslash gagal lewat CrewAI (LiteLLM unknown provider).
- `gemini-3.6-flash` kena rate limit 429 setelah 2-3 run — pakai `gemini-3.5-flash-lite`.

## 7. Jangan Commit

- `output/`, `test.md`, `.env` (kredensial), `venv/`, `__pycache__/`.

## 8. Struktur Modul

- `main.py` — orkestrasi crew (agents/tasks/kickoff), panggil `save_ebook()`.
- `ebook_saver.py` — penyimpanan + konversi, `DEFAULT_OUTPUT_DIR` di sini.
- `pdf_epub_converter.py` — `markdown_to_pdf()` / `markdown_to_epub()` via Pandoc.
- `RELEASE_NOTES.md` — ringkasan rilis per versi.
- `CHANGELOG.md` — catatan semua perubahan (WAJIB diupdate tiap perubahan).
