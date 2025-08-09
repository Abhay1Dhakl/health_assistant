import mimetypes
from app.models.document import store_document
from PyPDF2 import PdfReader
from docx import Document
import io

def split_text_into_chunks(text, chunk_size=500):
    """Split text into chunks of a specified size."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > chunk_size:  # +1 for space
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

async def ingest_from_file(data, file):
    content = await file.read()
    mime_type, _ = mimetypes.guess_type(file.filename)
    text = None
    metadata = []

    if mime_type and mime_type.startswith("text"):
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin1', errors='replace')  # Fallback for unusual encodings
    elif mime_type == "application/pdf":
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            metadata = [{"page": i, "text": page.extract_text()} for i, page in enumerate(reader.pages) if page.extract_text()]
                # Split text into chunks
            chunks = split_text_into_chunks(text)

            # Store each chunk with metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_index": i,
                    "file_name": file.filename,
                    "mime_type": mime_type,
                    "source_metadata": metadata
                }
                await store_document(chunk_metadata, chunk)

            return {"status": "success", "chunks_stored": len(chunks)}
        except Exception as e:
            print(f"Error reading PDF: {e}")
            text = "[PDF content could not be extracted]"
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)
            metadata = [{"paragraph_index": i, "text": paragraph.text} for i, paragraph in enumerate(doc.paragraphs) if paragraph.text]
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            text = "[DOCX content could not be extracted]"
    else:
        text = f"[Unsupported file type: {file.filename}]"

    print(f"File type: {mime_type}, Content Length: {len(content)}")
    return {"status": "success", "chunks_stored": len(chunks)}