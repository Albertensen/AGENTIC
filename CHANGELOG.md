# Changelog — CrewAI Ebook

Semua perubahan pada program dicatat di sini sebelum di-push ke git.
Format: `[tanggal] [jenis] pesan ringkas — file yang diubah`

Jenis: `feat` (fitur baru), `fix` (perbaikan), `refactor` (ubah struktur tanpa ubah perilaku), `docs` (dokumentasi), `chore` (tugas teknis).

---

## [2026-08-02] docs — tambah RELEASE_NOTES.md + aturan release notes wajib
- File: `RELEASE_NOTES.md` (baru), `CONTRIBUTING.md`, `AGENTS.md`
- Setiap rilis wajib update `RELEASE_NOTES.md` (format `## v<MAJOR>.<MINOR>.<PATCH> — YYYY-MM-DD`) sebelum push.
- `CONTRIBUTING.md`: section 2 baru (Release Notes), penomoran ulang.
- `AGENTS.md`: rule utama nomor 2 (release notes), struktur proyek + alur kerja diperbarui.

## [2026-08-02] docs — changelog rule, contributing guide, agent instructions
- File: `AGENTS.md` (baru), `CONTRIBUTING.md` (baru), `CHANGELOG.md` (baru)
- Rule wajib: changelog sebelum push, uji sebelum commit, destinasi hasil di `ebook_saver.DEFAULT_OUTPUT_DIR`, engine PDF Typst, model tanpa slash.

## [2026-08-02] refactor — logika simpan/konversi dipindah ke modul `ebook_saver.py`
- File: `ebook_saver.py` (baru), `main.py`
- `main.py` hanya memanggil `save_ebook(markdown, topic, output_dir=None)`.
- Ganti destinasi hasil: ubah `DEFAULT_OUTPUT_DIR` di `ebook_saver.py` — tanpa menyentuh `main.py`.
- `slugify()` pindah ke `ebook_saver.py`.

## [2026-08-02] fix — konverter PDF beralih ke engine Typst
- File: `pdf_epub_converter.py`
- `--pdf-engine=xelatex` gagal (exit 47, pdflatex/xelatex tidak terpasang) → ganti ke `--pdf-engine=typst`.
- WeasyPrint dicoba tapi butuh `libgobject` (GObject) yang tidak ada di Windows → diabaikan.

## [2026-08-02] feat — modul konverter PDF/EPUB + test script
- File: `pdf_epub_converter.py` (baru), `test_converter.py` (baru)
- `markdown_to_pdf(input, output_dir)` dan `markdown_to_epub(input, output_dir)` via Pandoc.

## [2026-08-02] feat — integrasi OpenRouter LLM via GPT-3.5 Turbo
- File: `main.py`, `custom_tools.py`, `.env`
- `.env` memakai `OPENAI_API_KEY` + `OPENAI_API_BASE` (OpenRouter).

## [2026-08-01] feat — ganti ke local Ollama LLM (deepseek-v4-flash)
- File: `main.py`

## [2026-08-01] feat — setup CrewAI agents, tasks, dan main workflow
- File: `main.py`

## [2026-08-01] feat — skeleton tool GeminiChromeBridgeTool
- File: `custom_tools.py`

## [2026-08-01] init — setup awal proyek
- File: struktur proyek CrewAI Ebook.
