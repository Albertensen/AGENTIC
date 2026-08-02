import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from custom_tools import GeminiChromeBridgeTool
from ebook_saver import save_ebook

# Load environment variables from .env file in the project directory
project_dir = Path("C:/Users/Administrator/Desktop/CrewAI_Ebook")
env_path = project_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

# Model identifier for OpenRouter (string, not instantiated object)
llm_model = os.getenv("MODEL_NAME")  # Should be "openai/gpt-3.5-turbo"

# Agent Definitions (using string model identifier)
researcher = Agent(
    role="Senior Multimodal Niche Researcher",
    goal="Menghasilkan outline ebook komprehensif, data tren pasar terbaru, dan aset gambar/prompt visual via LLM",
    backstory="Kamu adalah analis tren dan prompt engineer veteran. Kamu mencari topik viral dan merangkai data mentah menjadi outline terstruktur dengan aset visual.",
    tools=[GeminiChromeBridgeTool()],
    llm=llm_model,
    verbose=True
)

writer = Agent(
    role="Lead Ebook Copywriter & Layout Architect",
    goal="Mengubah outline dan aset gambar menjadi naskah ebook format Markdown yang persuasif (target 15 halaman) dan siap jual.",
    backstory="Kamu penulis kelas atas bergaya kasual, interaktif, dan kekinian. Kamu ahli meletakkan gambar (format Markdown) di tempat yang tepat agar pembaca tidak bosan.",
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

# Task Definitions
def research_task():
    return Task(
        description="Lakukan riset mendalam tentang topik: {topic}. Gunakan tool untuk mendapatkan tren, outline lengkap per bab, dan deskripsi/link gambar.",
        expected_output="Dokumen kerangka ebook & list gambar",
        agent=researcher
    )

def write_task():
    return Task(
        description="Tulis ebook berformat Markdown secara lengkap berdasarkan hasil riset dari researcher. Gunakan heading, list, dan placeholder gambar secara proporsional.",
        expected_output="Draf Ebook Markdown",
        agent=writer
    )

def qc_task():
    return Task(
        description="Periksa draf Markdown dari writer. Koreksi ejaan, perbaiki transisi kalimat, dan verifikasi UX penempatan teks & gambar.",
        expected_output="Final Ebook Markdown siap kemas",
        agent=qc_editor
    )


# Main Execution
if __name__ == "__main__":
    topic = "Rencana Strategis 3 Tahun dan Proyeksi Margin untuk Bisnis Pembiakan Anjing Ras Pembroke Welsh Corgi"

    research_task_instance = research_task()
    write_task_instance = write_task()
    qc_task_instance = qc_task()

    crew = Crew(
        agents=[researcher, writer, qc_editor],
        tasks=[research_task_instance, write_task_instance, qc_task_instance],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff(inputs={'topic': topic})

    print("\n=== Final Ebook Output ===")
    print(result)

    # Auto-save final markdown + convert to PDF/EPUB in ebook-crew
    final_md = str(result)
    if final_md.strip():
        save_ebook(final_md, topic)
    else:
        print("[SAVE] Gagal: hasil crew kosong, tidak ada file disimpan.")