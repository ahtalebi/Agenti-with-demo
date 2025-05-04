"""
Utility script to list all files in the data directory and generate
a JavaScript array for use in the demo.html file.
"""
import os
import json
import mimetypes
from pathlib import Path

def get_file_size(file_path):
    """Get human-readable file size."""
    size_bytes = os.path.getsize(file_path)
    # Convert to KB
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.0f} KB"
    # Convert to MB
    size_mb = size_kb / 1024
    return f"{size_mb:.1f} MB"

def get_file_type(file_path):
    """Get simplified file type."""
    mime_type = mimetypes.guess_type(file_path)[0]
    if mime_type:
        if "pdf" in mime_type:
            return "pdf"
        elif "excel" in mime_type or "spreadsheet" in mime_type:
            return "excel"
        elif "word" in mime_type or "document" in mime_type:
            return "word"
        elif "text" in mime_type:
            return "text"
    # Default to file extension if MIME type doesn't match
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return "pdf"
    elif ext in [".xls", ".xlsx", ".csv"]:
        return "excel"
    elif ext in [".doc", ".docx"]:
        return "word"
    elif ext in [".txt", ".md"]:
        return "text"
    return "unknown"

def generate_description(file_name):
    """Generate a simple description based on the file name."""
    name = os.path.splitext(file_name)[0]
    # Convert underscore to space and capitalize each word
    name = name.replace("_", " ").title()
    return f"{name} document for reference."

def get_document_list(data_dir="data"):
    """Get a list of all documents in the data directory."""
    documents = []
    
    if not os.path.exists(data_dir):
        print(f"Warning: Data directory '{data_dir}' does not exist.")
        return documents
    
    for file_name in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file_name)
        
        # Skip directories and hidden files
        if os.path.isdir(file_path) or file_name.startswith('.'):
            continue
        
        # Skip very large files (over 10MB)
        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            print(f"Skipping large file: {file_name}")
            continue
        
        # Create ID from filename (remove extension, replace spaces with hyphens)
        file_id = os.path.splitext(file_name)[0].lower().replace(" ", "-").replace("_", "-")
        
        # Create a title from filename (replace underscores with spaces, capitalize)
        title = os.path.splitext(file_name)[0].replace("_", " ").title()
        
        document = {
            "id": file_id,
            "title": title,
            "filename": file_name,
            "description": generate_description(file_name),
            "size": get_file_size(file_path),
            "type": get_file_type(file_path)
        }
        
        documents.append(document)
    
    return documents

def main():
    documents = get_document_list()
    
    if not documents:
        print("No documents found in the data directory.")
        return
    
    # Print some basic info
    print(f"Found {len(documents)} documents:")
    for doc in documents:
        print(f"- {doc['title']} ({doc['filename']}, {doc['size']})")
    
    # Generate JavaScript array code
    js_array = json.dumps(documents, indent=4)
    js_code = f"const knowledgeDocuments = {js_array};"
    
    # Save to a file
    with open("document_list.js", "w") as f:
        f.write(js_code)
    
    print(f"\nJavaScript array saved to document_list.js")
    print("You can copy this into your demo.html file.")

if __name__ == "__main__":
    main()