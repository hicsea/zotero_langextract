#!/usr/bin/env python3
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.folder_scanner import get_available_collections

def find_collections(search_term=None):
    """Find collections matching search term"""
    collections = get_available_collections()
    
    if search_term:
        matching = [c for c in collections if search_term.lower() in c.lower()]
        print(f"🔍 Collections containing '{search_term}':")
        for collection in matching:
            print(f"   '{collection}'")
        
        if not matching:
            print(f"❌ No collections found containing '{search_term}'")
    else:
        print("📋 All available collections:")
        for collection in collections:
            print(f"   '{collection}'")

if __name__ == "__main__":
    search_term = sys.argv[1] if len(sys.argv) > 1 else None
    find_collections(search_term)