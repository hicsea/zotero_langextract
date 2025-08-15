#!/usr/bin/env python3
import sys
import os
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.folder_scanner import get_zotero_data_dir

def debug_collection(collection_name):
    """Debug what's in a specific collection"""
    data_dir = get_zotero_data_dir()
    if not data_dir:
        print("❌ Zotero data directory not found")
        return
    
    db_path = os.path.join(data_dir, "zotero.sqlite")
    storage_path = os.path.join(data_dir, "storage")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 Debugging collection: '{collection_name}'")
    print(f"📁 Zotero data: {data_dir}")
    print(f"💾 Storage path: {storage_path}")
    
    # Find the collection
    cursor.execute("SELECT collectionID, collectionName FROM collections WHERE collectionName LIKE ?", (f"%{collection_name}%",))
    collections = cursor.fetchall()
    
    print(f"\n📋 Found {len(collections)} matching collections:")
    for cid, cname in collections:
        print(f"   ID {cid}: '{cname}'")
    
    if not collections:
        print("❌ No collections found with that name")
        return
    
    # Use the first matching collection
    collection_id = collections[0][0]
    collection_name_actual = collections[0][1]
    
    # Get items in this collection
    cursor.execute("""
        SELECT items.key, items.itemID
        FROM items
        JOIN collectionItems ON items.itemID = collectionItems.itemID  
        WHERE collectionItems.collectionID = ?
    """, (collection_id,))
    
    items = cursor.fetchall()
    print(f"\n📄 Found {len(items)} items in '{collection_name_actual}':")
    
    for item_key, item_id in items[:10]:  # Show first 10
        print(f"   {item_key}")
        
        # Check for PDF attachments
        cursor.execute("""
            SELECT itemAttachments.path, itemAttachments.contentType
            FROM itemAttachments
            WHERE itemAttachments.parentItemID = ?
        """, (item_id,))
        
        attachments = cursor.fetchall()
        for path, content_type in attachments:
            if content_type == 'application/pdf':
                clean_path = path.replace("storage:", "") if path else "NO PATH"
                full_path = os.path.join(storage_path, item_key, clean_path)
                exists = "✅" if os.path.exists(full_path) else "❌"
                print(f"      PDF: {clean_path} {exists}")
    
    if len(items) > 10:
        print(f"   ... and {len(items)-10} more items")
    
    # Also check for direct PDF attachments in this collection
    cursor.execute("""
        SELECT items.key, itemAttachments.path, itemAttachments.contentType
        FROM items
        JOIN collectionItems ON items.itemID = collectionItems.itemID
        JOIN itemAttachments ON items.itemID = itemAttachments.itemID
        WHERE collectionItems.collectionID = ? 
        AND itemAttachments.contentType = 'application/pdf'
    """, (collection_id,))
    
    direct_pdfs = cursor.fetchall()
    if direct_pdfs:
        print(f"\n📎 Direct PDF attachments in collection: {len(direct_pdfs)}")
        for item_key, path, content_type in direct_pdfs:
            clean_path = path.replace("storage:", "") if path else "NO PATH"
            full_path = os.path.join(storage_path, item_key, clean_path)
            exists = "✅" if os.path.exists(full_path) else "❌"
            print(f"   {item_key}: {clean_path} {exists}")
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 debug_collections.py 'Collection Name'")
        print("Example: python3 debug_collections.py 'CORE RESEARCH'")
        sys.exit(1)
    
    collection_name = sys.argv[1]
    debug_collection(collection_name)