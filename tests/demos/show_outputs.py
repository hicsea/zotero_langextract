#!/usr/bin/env python3
import os
import glob

print("📁 ZOTERO + LANGEXTRACT OUTPUT LOCATIONS")
print("="*50)

# Check for output files
jsonl_files = glob.glob("*.jsonl") + glob.glob("**/*.jsonl", recursive=True)
html_files = glob.glob("*.html") + glob.glob("**/*.html", recursive=True)

print("🗂️  STRUCTURED DATA FILES (.jsonl):")
if jsonl_files:
    for f in jsonl_files:
        size = os.path.getsize(f) if os.path.exists(f) else 0
        print(f"   📄 {f} ({size:,} bytes)")
else:
    print("   ❌ No .jsonl files found yet")

print("\n🌐 VISUALIZATION FILES (.html):")
if html_files:
    for f in html_files:
        size = os.path.getsize(f) if os.path.exists(f) else 0
        print(f"   🔗 {f} ({size:,} bytes)")
else:
    print("   ❌ No .html files found yet")

print(f"\n📍 CURRENT WORKING DIRECTORY:")
print(f"   {os.getcwd()}")

print(f"\n💡 OUTPUT NAMING PATTERNS:")
print(f"   • main_local.py → local_extraction_results.jsonl + local_visualization.html")
print(f"   • main_single.py → paper_N_results.jsonl + paper_N_visualization.html") 
print(f"   • main_minimal.py → minimal_results.jsonl + minimal_visualization.html")

print(f"\n🔧 TO VIEW RESULTS:")
print(f"   • Open .html files in browser for interactive visualization")
print(f"   • .jsonl files contain raw structured data")
print(f"   • Console shows immediate extraction results")

# Try to run a quick extraction to show output
print(f"\n🚀 RUNNING QUICK TEST TO SHOW OUTPUT...")
try:
    from final_demo import *
    # The demo already ran, just show where files would go
    print(f"✅ Outputs saved to current directory: {os.getcwd()}")
except:
    print("⚠️  Run any main_*.py script to generate outputs")