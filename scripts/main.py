#!/usr/bin/env python3
import langextract as lx
from zotero_client import get_papers_text
from langextract_processor import extract_from_papers

def query_papers(query):
    papers = get_papers_text()
    results = extract_from_papers(papers, query)
    
    for result in results:
        print(f"\n--- {result['title']} ---")
        print(result['extraction'])
    
    # Save results to JSONL file
    all_results = [result['extraction'] for result in results]
    lx.io.save_annotated_documents(all_results, output_name="./extraction_results.jsonl")
    
    # Generate visualization
    html_content = lx.visualize("./extraction_results.jsonl")
    with open("./visualization.html", "w") as f:
        f.write(html_content)
    
    print(f"\n✅ Saved {len(results)} results to extraction_results.jsonl")
    print("✅ Generated visualization.html")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 main.py 'your query here'")
        sys.exit(1)
    
    query = sys.argv[1]
    query_papers(query)