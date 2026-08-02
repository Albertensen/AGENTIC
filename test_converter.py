import os
import sys
import tempfile
import shutil
import pdf_epub_converter

def test_converter():
    # Create temp markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('# Test Ebook\n\nSimple test content.')
        md_path = f.name

    # Create temp output dir
    output_dir = tempfile.mkdtemp()

    try:
        # PDF
        pdf_path = pdf_epub_converter.markdown_to_pdf(md_path, output_dir)
        assert os.path.exists(pdf_path), f"PDF not created: {pdf_path}"

        # EPUB
        epub_path = pdf_epub_converter.markdown_to_epub(md_path, output_dir)
        assert os.path.exists(epub_path), f"EPUB not created: {epub_path}"

        print("✅ PDF conversion OK")
        print("✅ EPUB conversion OK")
        return True
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return False
    finally:
        try: os.unlink(md_path)
        except: pass
        try: shutil.rmtree(output_dir)
        except: pass

if __name__ == "__main__":
    sys.exit(0 if test_converter() else 1)