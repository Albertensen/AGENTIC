import os
import subprocess
import tempfile

def markdown_to_pdf(input_path, output_dir):
    """
    Konversi file Markdown ke format PDF menggunakan Pandoc dengan Typst engine.
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    try:
        subprocess.run(
            [
                "pandoc",
                input_path,
                "-o", output_path,
                "--pdf-engine=typst"
            ],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke PDF gagal: {e}")
    return output_path


def markdown_to_epub(input_path, output_dir):
    """
    Konversi file Markdown ke format EPUB menggunakan Pandoc.
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".epub")
    try:
        subprocess.run(
            ["pandoc", input_path, "-o", output_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke EPUB gagal: {e}")
    return output_path