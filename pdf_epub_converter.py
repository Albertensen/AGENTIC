import os
import subprocess
import tempfile

def markdown_to_pdf(input_path, output_dir):
    """
    Konversi file Markdown ke format PDF menggunakan Pandoc dengan Typst engine.
    cwd=output_dir agar path gambar relatif (assets) ter-resolve.
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    try:
        subprocess.run(
            [
                "pandoc",
                input_path,
                "-o", output_path,
                "--pdf-engine=typst",
                "--resource-path=" + output_dir,
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=output_dir,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke PDF gagal: {e}")
    return output_path


def markdown_to_epub(input_path, output_dir):
    """
    Konversi file Markdown ke format EPUB menggunakan Pandoc.
    cwd=output_dir agar path gambar relatif (assets) ter-resolve.
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".epub")
    try:
        subprocess.run(
            ["pandoc", input_path, "-o", output_path, "--resource-path=" + output_dir],
            check=True,
            capture_output=True,
            text=True,
            cwd=output_dir,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke EPUB gagal: {e}")
    return output_path