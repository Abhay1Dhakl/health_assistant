import PyPDF2
import json
# Open the PDF file
pdf_path = "document3/JCLA-36-e24427.pdf"
with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    data = []
    
    # Extract text page by page
    for page_number, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text()
        data.append({
            "page": page_number,
            "content": text.strip()
        })

# Convert to JSON
json_path = "document3.json"
with open(json_path, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print(f"PDF successfully converted to {json_path}")

import json

# Load the JSON file containing the FAR document
json_path = "document3.json"
with open(json_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Process each page into smaller chunks
chunks = []
for page in data:
    page_number = page["page"]
    content = page["content"].strip()
    
    # Skip empty content pages
    if not content:
        continue
    
    # Example: Split content into sections or paragraphs based on new lines or headings (you can adjust the logic based on your document's structure)
    sections = content.split("\n")  # Assuming each line is a new section or heading; adjust as needed
    
    for i, section in enumerate(sections, start=1):
        chunk = {
            "page_number": page_number,
            "section_number": i,
            "content": section.strip(),
            "metadata": {
                "section_title": section.split("\n")[0]  # You can modify this if your sections have specific titles
            }
        }
        chunks.append(chunk)

# Save the processed chunks to a new JSON file
processed_json_path = "processed_document3.json"
with open(processed_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(chunks, json_file, indent=4, ensure_ascii=False)

print(f"FAR document successfully processed and saved to {processed_json_path}")