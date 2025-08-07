import mimetypes
from app.models.document import store_document

async def ingest_from_file(data, file):
    content = await file.read()
    mime_type, _ = mimetypes.guess_type(file.filename)
    text = None

    if mime_type and mime_type.startswith("text"):
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin1', errors='replace')  # fallback for unusual encodings
    else:
        # For binary files, you should use a parser (e.g., PDF, DOCX) here.
        # For now, just store a placeholder or handle as needed.
        text = "[Binary file uploaded: {}]".format(file.filename)
    print(f"File type: {mime_type}, Content Length: {len(content)}")
    return await store_document(data, text)