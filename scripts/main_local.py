#!/usr/bin/env python3
import langextract as lx
from local_pdf_client import get_local_papers
from langextract_processor import extract_from_papers

def query_local_papers(query):
    papers = get_local_papers()
    print(f"Found {len(papers)} local PDF papers")
    
    if not papers:
        print("No local PDFs found. Check Zotero data directory.")
        return
    
    results = extract_from_papers(papers, query)
    
    for result in results:
        print(f"\n{'='*60}")
        print(f"📄 {result['title']}")
        print('='*60)
        print(result['extraction'])
    
    # Save results
    all_results = [result['extraction'] for result in results]
    lx.io.save_annotated_documents(all_results, output_name="./local_extraction_results.jsonl")
    
    html_content = lx.visualize("./local_extraction_results.jsonl")
    with open("./local_visualization.html", "w") as f:
        f.write(html_content)
    
    print(f"\n✅ Processed {len(results)} local PDFs")
    print("✅ Saved to local_extraction_results.jsonl")
    print("✅ Generated local_visualization.html")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 main_local.py 'your query here'")
        print("\nExample queries:")
        print("  'Extract genetic algorithm parameters'")
        print("  'Find fitness functions and constraints'")
        print("  'Extract methodology and experimental setup'")
        sys.exit(1)
    
    query = sys.argv[1]
    query_local_papers(query)