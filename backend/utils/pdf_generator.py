from fpdf import FPDF
import io

def create_pdf(text: str) -> bytes:
    """
    Generates a PDF from the given text string.
    
    Args:
        text (str): The content to put in the PDF.
        
    Returns:
        bytes: The binary content of the generated PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Use Unicode-compatible font
    # DejaVuSans is standard on many Linux systems and supports a wide range of characters
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        pdf.add_font("DejaVu", fname=font_path)
        pdf.set_font("DejaVu", size=12)
    except Exception as e:
        print(f"Warning: Could not load DejaVuSans font: {e}. Falling back to Helvetica (Unicode issues may occur).")
        pdf.set_font("Helvetica", size=12)
    
    # Efficiently write text with automatic line wrapping
    pdf.multi_cell(0, 10, text)
    
    # Return as bytes
    return bytes(pdf.output())
