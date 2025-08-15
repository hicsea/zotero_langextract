import os
import sqlite3
import fitz
from pathlib import Path

def get_zotero_data_dir():
    zotero_paths = [
        Path.home() / "Zotero",
        Path.home() / ".zotero" / "zotero",
        Path.home() / "snap/zotero-snap/common/Zotero"
    ]
    
    for path in zotero_paths:
        if path.exists() and (path / "zotero.sqlite").exists():
            return str(path)
    return None

def get_local_papers():
    data_dir = get_zotero_data_dir()
    if not data_dir:
        return []
    
    db_path = os.path.join(data_dir, "zotero.sqlite")
    storage_path = os.path.join(data_dir, "storage")
    
    papers = []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get PDFs with their parent item info
    query = """
    SELECT items.key, itemAttachments.path, parent.key as parent_key
    FROM items 
    JOIN itemAttachments ON items.itemID = itemAttachments.itemID
    LEFT JOIN items parent ON itemAttachments.parentItemID = parent.itemID
    WHERE itemAttachments.contentType = 'application/pdf' 
    AND itemAttachments.path IS NOT NULL
    LIMIT 5
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    for item_key, pdf_path, parent_key in results:
        if pdf_path:
            # Remove storage: prefix if present
            clean_path = pdf_path.replace("storage:", "")
            full_path = os.path.join(storage_path, item_key, clean_path)
            
            if os.path.exists(full_path):
                doc = fitz.open(full_path)
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                
                papers.append({
                    'title': f"PDF Document {parent_key or item_key}",
                    'text': text,
                    'pdf_path': full_path
                })
                print(f"Found PDF: {full_path}")
            else:
                print(f"PDF not found: {full_path}")
    
    conn.close()
    return papers