import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from image_tools import WikimediaImageSearchTool
from ebook_saver import save_ebook

# Load environment variables from .env file in the project directory
project_dir = Path("C:/Users/Administrator/Desktop/CrewAI_Ebook")
env_path = project_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

# Model identifier for OpenRouter (string, not instantiated object)
llm_model = os.getenv("MODEL_NAME")

# ============================================================
# Konstanta kualitas
# ============================================================
MIN_WORDS_PER_CHAPTER = 700    # target kata per bab
TARGET_WORDS = "4.000-6.000"
MIN_TOTAL_WORDS = 2500          # ambang lolos total (realistis utk model output ~700/bab x 5 bab)
MAX_REVISION_ROUNDS = 1         # 1 putaran QC (QC hanya koreksi, jangan potong)

PLACEHOLDER_MARKERS = [
    "url_gambar", "](url", "gambar akan", "gambar disini",
    "image will", "insert image", "placeholder gambar", "gambar belum",
]

# Pattern gambar markdown: ![alt](url)
IMG_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]*)\)")

# Domain terpercaya hasil tool pencarian — HANYA URL dari sini yang dianggap nyata.
# upload.wikimedia.org = CDN file gambar langsung (hasil thumburl tool).
# Ini sengaja ketat: writer dilarang menyemat URL dari domain lain (anti-halusinasi).
TRUSTED_IMG_DOMAINS = ("upload.wikimedia.org",)


def is_real_image_url(url: str) -> bool:
    """URL gambar nyata = berasal dari domain tool (Wikimedia) ATAU file lokal (img_*.jpg).
    URL lain (unsplash.com/photos/..., example.com/...) dianggap placeholder/halusinasi."""
    low = url.strip().lower()
    if not low.startswith("http"):
        # path lokal hasil download_images (img_01.jpg)
        return bool(re.match(r"^img_\d+\.(?:jpg|jpeg|png|gif|webp)$", low))
    return any(d in low for d in TRUSTED_IMG_DOMAINS)


def has_placeholder(text: str) -> bool:
    low = text.lower()
    # 1) marker teks eksplisit
    if any(marker in low for marker in PLACEHOLDER_MARKERS):
        return True
    # 2) setiap gambar markdown harus URL nyata
    for url in IMG_PATTERN.findall(text):
        if not is_real_image_url(url):
            return True
    return False


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def quality_report(text: str) -> tuple:
    words = count_words(text)
    ph = has_placeholder(text)
    return words, ph


def extract_chapters(outline: str) -> list:
    """Ekstrak judul bab utama dari outline riset.
    Tangkap heading level 2-3 dengan pola 'Bab N' / 'Chapter N', ATAU level 2 biasa.
    Sub-bab numerik (1.1, 2.3) dan bab penutup (kesimpulan/daftar isi) diabaikan."""
    STOPWORDS = ("kesimpulan", "daftar isi", "daftar pustaka", "pendahuluan", "referensi", "draft", "outline", "dokumen kerangka", "penutup", "kata pengantar")
    chapters = []
    for line in outline.splitlines():
        line = line.strip()
        # heading markdown: ## / ### / ####
        m = re.match(r"^#{2,4}\s+(.+)", line)
        if m:
            title = m.group(1).strip()
            title = re.sub(r"[*_`]", "", title).strip()
            low = title.lower()
            # bab utama: mengandung 'bab n'/'chapter n' ATAU level 2 (##) non-numerik
            is_bab = bool(re.match(r"^(bab|chapter)\s+\d+", low))
            is_sub = bool(re.match(r"^\d+\.\d+", title))  # 1.1, 2.3 = sub-bab
            if is_bab or (line.startswith("## ") and not is_sub and not re.match(r"^\d", title)):
                if not any(w in low for w in STOPWORDS):
                    chapters.append(title)
            continue
        # daftar isi: "1. **Pengantar**" / "2. **Dasar-Dasar**" (tanpa heading)
        m_toc = re.match(r"^(\d+)\.\s+\*{0,2}(.+?)\*{0,2}\s*$", line)
        if m_toc:
            title = m_toc.group(2).strip()
            if not any(w in title.lower() for w in STOPWORDS):
                chapters.append(title)
            continue
        # pola teks: Bab 1: ... / BAB 1: ... (tanpa markdown)
        if re.match(r"^(?:Bab|BAB|Chapter)\s+\d+[.:]?\s+\S", line, re.I):
            title = re.sub(r"^(?:Bab|BAB|Chapter)\s+(\d+)[.:]?\s*", r"Bab \1: ", line, flags=re.I).strip()
            if title and not any(w in title.lower() for w in STOPWORDS):
                chapters.append(title)
    return chapters


# Agent Definitions (using string model identifier)
researcher = Agent(
    role="Senior Multimodal Niche Researcher",
    goal="Menghasilkan outline ebook komprehensif, data tren pasar terbaru, dan aset gambar/prompt visual via LLM",
    backstory="Kamu adalah analis tren dan prompt engineer veteran. Kamu mencari topik viral dan merangkai data mentah menjadi outline terstruktur dengan aset visual.",
    tools=[WikimediaImageSearchTool()],
    llm=llm_model,
    verbose=True
)

writer = Agent(
    role="Lead Ebook Copywriter & Layout Architect",
    goal=f"Mengubah outline menjadi naskah ebook format Markdown yang persuasif, mendalam ({TARGET_WORDS} kata / 15-25 halaman) dan siap jual.",
    backstory="Kamu penulis kelas atas bergaya kasual, interaktif, dan kekinian. Kamu ahli meletakkan gambar (format Markdown) di tempat yang tepat agar pembaca tidak bosan.",
    tools=[WikimediaImageSearchTool()],
    allow_delegation=False,
    llm=llm_model,
    verbose=True
)

qc_editor = Agent(
    role="Quality Assurance & UX Editor",
    goal="Memastikan draf Markdown sempurna secara ejaan, grammar, dan estetika penempatan visual/teks.",
    backstory="Kamu editor perfeksionis yang memastikan tidak ada typo, kalimat kaku, atau tata letak berantakan. Standarmu adalah produk premium.",
    llm=llm_model,
    verbose=True
)


def research_task():
    return Task(
        description=(
            "Lakukan riset mendalam tentang topik: {topic}. "
            "Gunakan tool pencarian gambar untuk mendapatkan aset visual relevan. "
            "Hasil akhir harus berupa kerangka ebook terstruktur (bab + sub-bab) "
            "dan daftar kata kunci gambar per bab yang relevan."
        ),
        expected_output="Dokumen kerangka ebook lengkap (bab + sub-bab) & daftar kata kunci gambar",
        agent=researcher
    )


def chapter_write_task(chapter_title: str, outline: str, feedback: str = ""):
    """Task menulis SATU bab secara mendalam."""
    desc = (
        f"Tulis SATU BAB ebook dalam format Markdown tentang: '{chapter_title}'.\n"
        f"Konteks outline keseluruhan:\n{outline[:2000]}\n\n"
        f"Persyaratan bab ini:\n"
        f"- Panjang: MINIMAL {MIN_WORDS_PER_CHAPTER} kata (tulis mendalam, jangan ringkas).\n"
        f"- Bagi menjadi 2-3 sub-bab (###).\n"
        f"- Gunakan list, tabel, kutipan, contoh nyata secara proporsional.\n"
        f"- Bahasa Indonesia baku (KBBI), gaya kasual-interaktif.\n"
        f"GAMBAR:\n"
        f"- Panggil tool 'wikimedia_image_search_tool' dengan kata kunci relevan bab ini "
        f"(mis. '{chapter_title.lower()}', 'indonesian food', 'traditional recipe').\n"
        f"- Ambil URL gambar dari HASIL tool — SALIN PERSIS URL lengkap yang dikembalikan tool "
        f"(contoh format: https://upload.wikimedia.org/wikipedia/commons/thumb/.../960px-....jpg).\n"
        f"- JANGAN PERNAH membuat/menebak URL sendiri — URL yang kamu tulis harus KOPI dari output tool.\n"
        f"- Sematkan MINIMAL 1 gambar NYATA dengan format ![Keterangan](URL).\n"
        f"- JANGAN PERNAH menulis placeholder seperti url_gambar, [Gambar:, atau URL non-Wikimedia."
    )
    if feedback:
        desc += f"\n\nCATATAN REVISI QC — TERAPKAN SEMUA:\n{feedback}"
    return Task(
        description=desc,
        expected_output=f"Draf Markdown bab '{chapter_title}' lengkap minimal {MIN_WORDS_PER_CHAPTER} kata dengan gambar nyata",
        agent=writer
    )


def qc_task():
    return Task(
        description=(
            "Berikut adalah DRAF EBOOK yang harus kamu periksa dan revisi:\n\n"
            "=== DRAF MULAI ===\n{draft}\n=== DRAF SELESAI ===\n\n"
            "Periksa draf di atas secara menyeluruh: "
            "1) Koreksi ejaan (KBBI) dan grammar; "
            "2) Perbaiki transisi kalimat agar mengalir; "
            "3) Verifikasi UX penempatan teks & gambar; "
            "4) Pastikan panjang naskah memenuhi target; "
            "5) Pastikan gambar NYATA (URL upload.wikimedia.org), BUKAN placeholder. "
            "PENTING: JANGAN HAPUS bab atau konten apa pun — hanya perbaiki ejaan/grammar/format "
            "dan pertahankan SEMUA bab dan SEMUA kata. JANGAN menulis ulang atau meringkas draf. "
            "Keluarkan DRAF MARKDOWN LENGKAP yang sudah direvisi."
        ),
        expected_output="Draf Markdown FINAL lengkap (ejaan benar, panjang sesuai target, gambar nyata)",
        agent=qc_editor
    )


# Main Execution
if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "Game Palworld: Panduan Lengkap Tips dan Trik untuk Pemula"

    # ---- Fase 1: Riset ----
    crew_research = Crew(
        agents=[researcher],
        tasks=[research_task()],
        process=Process.sequential,
        verbose=True
    )
    outline = crew_research.kickoff(inputs={'topic': topic})
    print("\n=== OUTLINE RISET ===")
    print(outline)

    chapters = extract_chapters(str(outline))
    if not chapters:
        print("[WARN] Tidak ada bab terdeteksi di outline — pakai topik sebagai satu bab.")
        chapters = [topic]

    # ---- Fase 2: Tulis per bab ----
    print(f"\n=== MENULIS {len(chapters)} BAB ===")
    all_chapters_md = []
    for i, ch in enumerate(chapters, 1):
        print(f"\n--- Bab {i}/{len(chapters)}: {ch} ---")
        crew_ch = Crew(
            agents=[writer],
            tasks=[chapter_write_task(ch, str(outline))],
            process=Process.sequential,
            verbose=True
        )
        ch_result = crew_ch.kickoff(inputs={'topic': topic, 'outline': str(outline)})
        all_chapters_md.append(f"## {ch}\n\n{str(ch_result).strip()}")
        w, ph = quality_report(str(ch_result))
        print(f"  [BAB] kata={w} placeholder={ph}")

    full_draft = "\n\n---\n\n".join(all_chapters_md)
    words, ph = quality_report(full_draft)
    print(f"\n=== DRAF GABUNGAN: kata={words} placeholder={ph} ===")

    # ---- Fase 3: QC + feedback loop ----
    feedback = ""
    for attempt in range(1, MAX_REVISION_ROUNDS + 1):
        print(f"\n{'='*60}\nQC PUTARAN {attempt}/{MAX_REVISION_ROUNDS}\n{'='*60}")
        crew_qc = Crew(
            agents=[qc_editor],
            tasks=[qc_task()],
            process=Process.sequential,
            verbose=True
        )
        result = crew_qc.kickoff(inputs={'topic': topic, 'draft': full_draft})
        full_draft = str(result)
        words, ph = quality_report(full_draft)
        print(f"[QC-CHECK] putaran={attempt} kata={words} placeholder={ph}")

        if words >= MIN_TOTAL_WORDS and not ph:
            print("[QC-CHECK] LOLOS.")
            break

        issues = []
        if words < MIN_TOTAL_WORDS:
            issues.append(
                f"Panjang naskah baru {words} kata, target minimal {MIN_TOTAL_WORDS} kata. "
                "Perluas setiap bab dan sub-bab dengan penjelasan mendalam, contoh, tabel, dan tips praktis."
            )
        if ph:
            issues.append(
                "Masih ada placeholder gambar. WAJIB ganti semua dengan URL nyata "
                "dari tool wikimedia_image_search_tool (upload.wikimedia.org)."
            )
        feedback = "\n".join(f"- {i}" for i in issues)
        print(f"[QC-CHECK] Belum lolos. Feedback:\n{feedback}")

    # ---- Fase 4: Simpan + konversi ----
    words, ph = quality_report(full_draft)
    print(f"\n=== FINAL: kata={words} placeholder={ph} ===")
    print(full_draft[:800])

    if full_draft.strip():
        save_ebook(full_draft, topic)
    else:
        print("[SAVE] Gagal: hasil kosong.")
