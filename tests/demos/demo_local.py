#!/usr/bin/env python3
from local_pdf_client import get_local_papers

# Demo: Show what local PDFs contain
papers = get_local_papers()

print("🔍 LOCAL ZOTERO PDF ANALYSIS")
print("="*50)
print(f"Found {len(papers)} local research papers:")

for i, paper in enumerate(papers, 1):
    print(f"\n📄 Paper {i}: {paper['title']}")
    print(f"📁 Path: {paper['pdf_path'].split('/')[-2:]}")
    print(f"📝 Text length: {len(paper['text']):,} characters")
    
    # Show first 500 chars as preview
    preview = paper['text'][:500].replace('\n', ' ')
    print(f"📖 Preview: {preview}...")

print(f"\n✅ Ready to process with LangExtract!")
print("   When API quota resets, run:")
print("   python3 main_local.py 'Extract genetic algorithm parameters'")

# Show example of what we have access to
if papers:
    print(f"\n🔬 Sample data from first paper:")
    sample_text = papers[0]['text'][1000:2000]  # Skip headers
    print(f"'{sample_text[:300]}...'")
    print(f"\nThis rich content can be analyzed for:")
    print("• Genetic algorithm parameters")
    print("• Fitness functions and constraints") 
    print("• Experimental methodology")
    print("• Performance metrics")
    print("• Implementation details")