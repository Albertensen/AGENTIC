import os
from dotenv import load_dotenv

# Load environment variables (none needed for local Ollama)
load_dotenv()

# CrewAI imports
from crewai import Agent, Task, Crew, Process

# Import the custom Chrome bridge tool
from custom_tools import GeminiChromeBridgeTool

# Import Ollama LLM from LangChain community
from langchain_community.llms import Ollama

# Initialize Ollama LLM (local, no API key needed)
llm = Ollama(model="deepseek-v4-flash")

# ----------------------------------------------------------------------
# Agent Definitions
# ----------------------------------------------------------------------

# Senior Multimodal Niche Researcher
researcher = Agent(
    role="Senior Multimodal Niche Researcher",
    goal="Menghasilkan outline ebook komprehensif, data tren pasar terbaru, dan aset gambar/prompt visual via LLM",
    backstory="Kamu adalah analis tren dan prompt engineer veteran. Kamu mencari topik viral dan merangkai data mentah menjadi outline terstruktur dengan aset visual.",
    tools=[GeminiChromeBridgeTool()],
    llm=llm,
    verbose=True
)

# Lead Ebook Copywriter & Layout Architect
writer = Agent(
    role="Lead Ebook Copywriter & Layout Architect",
    goal="Mengubah outline dan aset gambar menjadi naskah ebook format Markdown yang persuasif (target 15 halaman) dan siap jual.",
    backstory="Kamu penulis kelas atas bergaya kasual, interaktif, dan kekinian. Kamu ahli meletakkan gambar (format Markdown) di tempat yang tepat agar pembaca tidak bosan.",
    llm=llm,
    verbose=True
)

# Quality Assurance & UX Editor
qc_editor = Agent(
    role="Quality Assurance & UX Editor",
    goal="Memastikan draf Markdown sempurna secara ejaan, grammar, dan estetika penempatan visual/teks.",
    backstory="Kamu editor perfeksionis yang memastikan tidak ada typo, kalimat kaku, atau tata letak berantakan. Standarmu adalah produk premium.",
    llm=llm,
    verbose=True
)

# ----------------------------------------------------------------------
# Task Definitions (sequential workflow)
# ----------------------------------------------------------------------
def research_task():
    return Task(
        description="Lakukan riset mendalam tentang topik: {topic}. Gunakan tool untuk mendapatkan tren, outline lengkap per bab, dan deskripsi/link gambar.",
        expected_output="Dokumen kerangka ebook & list gambar",
        agent=researcher,
    )

def write_task():
    return Task(
        description="Tulis ebook berformat Markdown secara lengkap berdasarkan hasil riset dari researcher. Gunakan heading, list, dan masukkan placeholder gambar secara proporsional.",
        expected_output="Draf Ebook Markdown",
        agent=writer,
    )

def qc_task():
    return Task(
        description="Periksa draf Markdown dari writer. Koreksi ejaan, perbaiki transisi kalimat, dan verifikasi UX penempatan teks & gambar.",
        expected_output="Final Ebook Markdown siap kemas",
        agent=qc_editor,
    )

# ----------------------------------------------------------------------
# Main Execution Block
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Define the main topic for the ebook
    topic = "Rencana Strategis 3 Tahun dan Proyeksi Margin untuk Bisnis Pembiakan Anjing Ras Pembroke Welsh Corgi"
    
    # Create the sequential tasks
    research_task_instance = research_task()
    write_task_instance = write_task()
    qc_task_instance = qc_task()
    
    # Initialize the Crew with sequential process
    crew = Crew(
        agents=[researcher, writer, qc_editor],
        tasks=[research_task_instance, write_task_instance, qc_task_instance],
        process=Process.sequential,
        verbose=True
    )
    
    # Kick off the workflow, passing the topic as input
    result = crew.kickoff(inputs={'topic': topic})
    
    # Print the final result (should be the polished ebook Markdown)
    print("\n=== Final Ebook Output ===")
    print(result)