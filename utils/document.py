import fitz  # PyMuPDF for PDFs
import docx

def extract_text(file):
    """
    Extracts text from uploaded PDF, DOCX, or generic text files.
    """
    if file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8", errors="ignore")
