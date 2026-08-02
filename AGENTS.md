# Agent Instructions — CrewAI Ebook

File ini dibaca oleh agent AI (Hermes atau agent lain) yang mengembangkan proyek ini.
Baca SEBELUM mengubah kode.

## RULE UTAMA

1. **Changelog wajib sebelum push** — setiap perubahan kode dicatat di `CHANGELOG.md` dulu, baru commit + push. Format: `## [YYYY-MM-DD] <jenis> — <pesan>`. Commit harus berisi kode + CHANGELOG.md sekaligus.
2. **Release notes per rilis** — update `RELEASE_NOTES.md` (format `## v<MAJOR>.<MINOR>.<PATCH> — YYYY-MM-DD`) setelah kumpulan perubahan bermakna.
3. **Uji dulu, commit belakangan** — jangan pernah commit kode yang belum diuji berhasil.
4. **Destinasi hasil**: ubah `DEFAULT_OUTPUT_DIR` di `ebook_saver.py`, bukan di `main.py`.
5. **Engine PDF** = Typst (`--pdf-engine=typst`). Jangan pakai xelatex/pdflatex (tidak terpasang).
6. **Model LLM**: id tanpa slash (`gemini-3.5-flash-lite`), hindari `gemini-3.6-flash` (429).

## Struktur Proyek

- `main.py` — orkestrasi CrewAI (agents, tasks, kickoff, panggil save_ebook).
- `ebook_saver.py` — simpan + konversi ebook, `save_ebook(markdown, topic, output_dir=None)`, default ke `Desktop/ebook-crew`.
- `pdf_epub_converter.py` — `markdown_to_pdf()` / `markdown_to_epub()` via Pandoc.
- `custom_tools.py` — tool riset (Gemini Chrome Bridge).
- `CHANGELOG.md` — catatan semua perubahan (WAJIB diupdate tiap perubahan).
- `RELEASE_NOTES.md` — ringkasan rilis per versi (WAJIB diupdate per rilis).
- `CONTRIBUTING.md` — aturan lengkap.

## Alur Kerja Wajib

1. Baca CHANGELOG.md + CONTRIBUTING.md.
2. Ubah kode.
3. Uji (konversi file sampel, verifikasi output ada).
4. Update CHANGELOG.md (+ RELEASE_NOTES.md jika rilis baru).
5. Commit kode + CHANGELOG.md bersama.
6. Push ke main.
