# Release Notes — CrewAI Ebook

Ringkasan rilis per versi. Detail teknis lengkap di `CHANGELOG.md`.

---

## v1.2.0 — 2026-08-02

**Fitur**
- Auto-save hasil crew: Markdown final + PDF + EPUB otomatis masuk ke `C:/Users/Administrator/Desktop/ebook-crew` setelah `crew.kickoff()`.
- Modul `ebook_saver.py`: pengaturan destinasi hasil terpusat (`DEFAULT_OUTPUT_DIR`) — ganti folder tujuan cukup edit satu file.
- Modul `pdf_epub_converter.py`: konversi Markdown → PDF & EPUB via Pandoc.
- Aturan pengembangan: `AGENTS.md` (instruksi agent AI), `CONTRIBUTING.md` (aturan kontribusi), `CHANGELOG.md` (catatan perubahan wajib sebelum push).

**Perbaikan**
- Engine PDF beralih ke Typst (`--pdf-engine=typst`) — xelatex/pdflatex tidak tersedia di sistem, sebelumnya gagal exit 47.

**Catatan**
- Kredensial API di `.env` (tidak di-commit). Model pakai OpenRouter via `OPENAI_API_KEY`/`OPENAI_API_BASE`.

---

## v1.1.0 — 2026-08-02

**Fitur**
- Integrasi OpenRouter LLM (GPT-3.5 Turbo) sebagai model crew.

---

## v1.0.0 — 2026-08-01

**Fitur**
- Setup CrewAI: 3 agent (researcher, writer, qc_editor) + 3 task sequential.
- Tool riset `GeminiChromeBridgeTool` (skeleton).
- Alur: riset niche → tulis draf Markdown → QC ejaan/layout.
