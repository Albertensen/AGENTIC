# Release Notes — CrewAI Ebook

Ringkasan rilis per versi. Detail teknis lengkap di `CHANGELOG.md`.

---

## v1.3.0 — 2026-08-02

**Fitur**
- **Feedback loop 2 arah**: QC Editor menilai draf, kirim instruksi perbaikan ke Writer jika belum memenuhi standar (panjang + gambar), ulang hingga maks 2 putaran.
- **Penulisan per bab**: naskah ditulis bab demi bab (target 700+ kata/bab) → total ebook 4.000+ kata (15-25 halaman), bab + sub-bab terstruktur.
- **Gambar nyata**: tool `WikimediaImageSearchTool` (Commons API gratis) — Writer menyematkan URL gambar asli (upload.wikimedia.org) di tiap bab, bukan placeholder. Validator anti-halusinasi (hanya URL Wikimedia diterima).
- **Model lebih kuat**: `openai/gpt-4o-mini` via OpenRouter (menggantikan gpt-3.5-turbo yang outputnya terlalu pendek).

**Perbaikan**
- `Process.hierarchical` dihapus (manager gpt-4o-mini tidak meneruskan hasil antar agent) → sequential + feedback loop eksplisit yang terbukti bekerja.
- `GeminiChromeBridgeTool` dilepas dari researcher (profil Chrome bermasalah, error WinError 183/profile not found) — riset kini via LLM + tool gambar.
- Filter relevansi gambar Wikimedia + delay anti-rate-limit (HTTP 429).

**Hasil uji (Palworld)**
- 7 bab, 4.101 kata, 7 gambar nyata, 0 placeholder → PDF 174 KB + EPUB 20 KB tersimpan otomatis di `ebook-crew`.

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
