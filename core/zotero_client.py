from pyzotero import zotero
import fitz
from config import ZOTERO_LIBRARY_ID, ZOTERO_API_KEY

def get_papers_text():
    z = zotero.Zotero(ZOTERO_LIBRARY_ID, 'user', ZOTERO_API_KEY)
    items = z.top(limit=3)
    
    papers = []
    for item in items:
        if item['data'].get('itemType') == 'journalArticle':
            title = item['data'].get('title', '')
            abstract = item['data'].get('abstractNote', '')
            
            text = f"Title: {title}\n\nAbstract: {abstract}" if abstract else f"Title: {title}"
            papers.append({'title': title, 'text': text})
    
    return papers