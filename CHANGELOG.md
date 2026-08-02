# Changelog — CrewAI Ebook

Semua perubahan pada program dicatat di sini sebelum di-push ke git.
Format: `[tanggal] [jenis] pesan ringkas — file yang diubah`

Jenis: `feat` (fitur baru), `fix` (perbaikan), `refactor` (ubah struktur tanpa ubah perilaku), `docs` (dokumentasi), `chore` (tugas teknis).

---

## [2026-08-02] fix — QC jangan pangkas draf, max_tokens hemat credit, pendahuluan lolos filter
- File: `main.py`
- **QC hanya dipanggil jika draf belum lolos** (cek kualitas sebelum panggil QC) — sebelumnya QC selalu dipanggil dan memangkas draf 2883→1736 kata. Sekarang draf bagus langsung lolos.
- **Anti-pangkas**: jika output QC lebih pendek dari draf, pertahankan draf asli (hanya ambil feedback).
- **max_tokens 3000** (OpenRouter 402: credit tak cukup untuk default 16384 / 8000) — hemat saldo, output bab ~700 kata tetap cukup.
- **"Pendahuluan" dihapus dari stopwords** `extract_chapters` — Bab 1 Pendahuluan berisi konten penting, jangan difilter.
- Hasil uji (Jenis-Jenis Pals): 11 bab, 6.670 kata, 11 gambar lokal (5 unik), PDF 44 halaman 255 KB (22 objek ImageC/B ter-embed), EPUB, 0 placeholder → lolos QC tanpa dipangkas.

## [2026-08-02] feat — gambar lokal terunduh (PDF render), retry backoff, CLI topik
- File: `ebook_saver.py`, `pdf_epub_converter.py`, `main.py`
- **PDF/EPUB sekarang render gambar**: `download_images()` unduh semua URL Wikimedia ke folder `_assets/`, refer path lokal (sebelumnya URL remote tak di-render typst → PDF tanpa gambar). Konverter pakai `--resource-path` + `cwd=output_dir`.
- **Fallback `Special:FilePath`**: URL thumbnail writer yang 404 di-rescue ke file asli; jika semua kandidat gagal → komentar HTML (bukan URL mati di ebook).
- **`extract_chapters`** tangkap format `#### Bab N` + daftar isi numerik (`1. **Judul**`); stopwords + "penutup"/"kata pengantar".
- **`is_real_image_url`** terima file lokal (`img_N.jpg`) — ebook memakai hasil download.
- **Topik via CLI**: `python main.py "Topik Baru"` (sebelumnya hardcoded).
- Hasil uji (Resep Masakan Nusantara): 10 bab, 8.737 kata, 15 gambar lokal, PDF 62 halaman, 0 placeholder → lolos QC.

## [2026-08-02] feat — feedback loop QC→Writer, penulisan per bab, tool gambar Wikimedia
- File: `main.py`, `image_tools.py` (baru), `AGENTS.md`
- **Komunikasi 2 arah**: `Process.hierarchical` + manager_agent dicoba → gagal (gpt-3.5/4o-mini manager tidak meneruskan hasil antar agent, output kosong/loop delegasi). Ganti ke **sequential + feedback loop eksplisit**: QC editor menilai draf, jika < MIN_TOTAL_WORDS atau ada placeholder → kirim catatan revisi ke Writer, ulang maks MAX_REVISION_ROUNDS.
- **Target panjang**: penulisan dipecah PER BAB (`chapter_write_task`), tiap bab target 700+ kata → total 4.000+ kata. `extract_chapters()` ekstrak judul bab dari outline (level ## / ### Bab N, filter kesimpulan/daftar isi/daftar pustaka/sub-bab numerik).
- **Gambar nyata**: `WikimediaImageSearchTool` baru (Commons API gratis, tanpa key) — multi-query fallback, filter relevansi kata kunci di judul, delay anti-rate-limit. Whitelist URL `upload.wikimedia.org` di `has_placeholder()` (anti-halusinasi URL unsplash/pixabay).
- **Model**: `openai/gpt-4o-mini` via OpenRouter (id `google/*`/`deepseek/*` terdeteksi native provider CrewAI dan bypass OpenRouter; gpt-3.5-turbo output terlalu pendek).
- Hasil uji Palworld: 7 bab, 4.101 kata, 7 gambar nyata, 0 placeholder, PDF+EPUB tersimpan.

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
