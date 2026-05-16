import os
from dotenv import load_dotenv

load_dotenv()

ZOTERO_LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
ZOTERO_API_KEY = os.getenv('ZOTERO_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')