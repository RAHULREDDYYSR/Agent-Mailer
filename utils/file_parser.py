from pypdf import PdfReader
import os

def parse_file(path: str) -> str:
    """
    Parses the content of a file based on its extension.

    Args:
        path (str): The file path.

    Returns:
        str: The extracted text content from the file.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    raise ValueError(f"Unsupported file extension: {ext}")