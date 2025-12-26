from pypdf import PdfReader
import docx
import io
from fastapi import UploadFile

def parse_file(file_obj, filename: str) -> str:
    """
    Parses the content of a file based on its extension.

    Args:
        file_obj: The file-like object to read.
        filename (str): The name of the file including extension.

    Returns:
        str: The extracted text content from the file.
    """
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    ext = f".{ext}"
    
    # Ensure we are at the beginning of the file
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)
        
    try:
        if ext == ".pdf":
            reader = PdfReader(file_obj)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        
        if ext == ".docx":
            # python-docx expects a binary file-like object
            doc = docx.Document(file_obj)
            return "\n".join([para.text for para in doc.paragraphs])
            
        if ext in [".txt", ".md"]:
            # Read content, assuming it might be bytes or string
            content = file_obj.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="ignore")
            return content
            
        raise ValueError(f"Unsupported file extension: {ext}")
        
    except Exception as e:
        # Log or re-raise with context if needed
        raise ValueError(f"Error parsing file {filename}: {str(e)}")
