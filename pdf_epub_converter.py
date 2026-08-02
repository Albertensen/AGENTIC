import os
import subprocess
import tempfile

def markdown_to_pdf(input_path, output_dir, resource_path=None):
    """
    Konversi file Markdown ke format PDF menggunakan Pandoc dengan Typst engine.
    resource_path: folder tempat gambar lokal berada (assets dir). Wajib di-set
    agar pandoc resolve img_XX.jpg -> PDF (tanpa ini gambar tak muncul di PDF).
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    rp = resource_path or output_dir
    try:
        subprocess.run(
            [
                "pandoc",
                input_path,
                "-o", output_path,
                "--pdf-engine=typst",
                "--resource-path=" + rp,
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=output_dir,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke PDF gagal: {e}")
    return output_path


def markdown_to_epub(input_path, output_dir, resource_path=None):
    """
    Konversi file Markdown ke format EPUB menggunakan Pandoc.
    resource_path: folder tempat gambar lokal berada (assets dir) agar
    gambar ter-embed ke EPUB.
    """
    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".epub")
    rp = resource_path or output_dir
    try:
        subprocess.run(
            ["pandoc", input_path, "-o", output_path, "--resource-path=" + rp],
            check=True,
            capture_output=True,
            text=True,
            cwd=output_dir,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Konversi ke EPUB gagal: {e}")
    return output_path