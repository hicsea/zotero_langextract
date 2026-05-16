import os
import sqlite3
import fitz
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PaperInfo:
    title: str
    text: str
    pdf_path: str
    folder_name: str
    file_size: int

def get_zotero_data_dir() -> Optional[str]:
    """Find Zotero data directory"""
    zotero_paths = [
        Path.home() / "Zotero",
        Path.home() / ".zotero" / "zotero", 
        Path.home() / "snap/zotero-snap/common/Zotero"
    ]
    
    for path in zotero_paths:
        if path.exists() and (path / "zotero.sqlite").exists():
            return str(path)
    return None

def scan_zotero_folders(target_folders: List[str] = None, limit: Optional[int] = None) -> List[PaperInfo]:
    """Scan Zotero storage for PDFs, optionally filtering by collection folders"""
    data_dir = get_zotero_data_dir()
    if not data_dir:
        return []
    
    db_path = os.path.join(data_dir, "zotero.sqlite")
    storage_path = os.path.join(data_dir, "storage")
    
    papers = []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get PDFs with collection info if available
    query = """
    SELECT items.key, itemAttachments.path, parent.key as parent_key,
           collections.collectionName
    FROM items 
    JOIN itemAttachments ON items.itemID = itemAttachments.itemID
    LEFT JOIN items parent ON itemAttachments.parentItemID = parent.itemID
    LEFT JOIN collectionItems ON parent.itemID = collectionItems.itemID
    LEFT JOIN collections ON collectionItems.collectionID = collections.collectionID
    WHERE itemAttachments.contentType = 'application/pdf' 
    AND itemAttachments.path IS NOT NULL
    ORDER BY collections.collectionName, items.key
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    for item_key, pdf_path, parent_key, collection_name in results:
        if pdf_path:
            # Remove storage: prefix if present
            clean_path = pdf_path.replace("storage:", "")
            full_path = os.path.join(storage_path, item_key, clean_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                continue
            
            # Filter by target folders if specified
            folder_name = collection_name or "uncategorized"
            if target_folders and folder_name.lower() not in [f.lower() for f in target_folders]:
                continue
            
            try:
                # Extract text from PDF
                doc = fitz.open(full_path)
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                
                # Get file info
                file_size = os.path.getsize(full_path)
                title = clean_path.replace('.pdf', '')
                
                papers.append(PaperInfo(
                    title=title,
                    text=text,
                    pdf_path=full_path,
                    folder_name=folder_name,
                    file_size=file_size
                ))
                
            except Exception as e:
                print(f"Error processing {full_path}: {e}")
                continue
    
    conn.close()
    return papers

def scan_filesystem_folders(folder_paths: List[str], recursive: bool = True, limit: Optional[int] = None) -> List[PaperInfo]:
    """Scan filesystem folders for PDF files"""
    papers = []
    
    for folder_path in folder_paths:
        folder = Path(folder_path)
        if not folder.exists():
            print(f"Warning: Folder {folder_path} does not exist")
            continue
        
        # Find PDF files
        if recursive:
            pdf_files = list(folder.rglob("*.pdf"))
        else:
            pdf_files = list(folder.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            if limit and len(papers) >= limit:
                break
                
            try:
                # Extract text from PDF
                doc = fitz.open(str(pdf_file))
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                
                # Get file info
                file_size = pdf_file.stat().st_size
                title = pdf_file.stem
                folder_name = pdf_file.parent.name
                
                papers.append(PaperInfo(
                    title=title,
                    text=text,
                    pdf_path=str(pdf_file),
                    folder_name=folder_name,
                    file_size=file_size
                ))
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
                continue
    
    return papers

def get_available_collections() -> List[str]:
    """Get list of available Zotero collections"""
    data_dir = get_zotero_data_dir()
    if not data_dir:
        return []
    
    db_path = os.path.join(data_dir, "zotero.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT collectionName FROM collections WHERE collectionName IS NOT NULL ORDER BY collectionName")
    collections = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return collections

def print_paper_summary(papers: List[PaperInfo]):
    """Print summary of found papers"""
    if not papers:
        print("No papers found")
        return
    
    print(f"\n📚 Found {len(papers)} papers:")
    print("="*60)
    
    # Group by folder
    by_folder = {}
    for paper in papers:
        folder = paper.folder_name
        if folder not in by_folder:
            by_folder[folder] = []
        by_folder[folder].append(paper)
    
    for folder, folder_papers in by_folder.items():
        total_size = sum(p.file_size for p in folder_papers)
        print(f"\n📁 {folder} ({len(folder_papers)} papers, {total_size/1024/1024:.1f} MB)")
        
        for paper in folder_papers[:3]:  # Show first 3
            print(f"   📄 {paper.title[:50]}...")
        
        if len(folder_papers) > 3:
            print(f"   ... and {len(folder_papers)-3} more")
    
    total_chars = sum(len(p.text) for p in papers)
    print(f"\n📊 Total: {total_chars:,} characters across {len(papers)} papers")