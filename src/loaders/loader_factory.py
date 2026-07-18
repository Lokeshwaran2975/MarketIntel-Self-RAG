from pathlib import Path

from src.loaders.pdf_loader import load_pdf
from src.loaders.docx_loader import load_docx
from src.loaders.txt_loader import load_txt
from src.loaders.html_loader import load_html


def load_document(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".docx":
        return load_docx(file_path)

    elif extension == ".txt":
        return load_txt(file_path)

    elif extension in [".html", ".htm"]:
        return load_html(file_path)

    else:
        raise ValueError(f"Unsupported file type : {extension}")