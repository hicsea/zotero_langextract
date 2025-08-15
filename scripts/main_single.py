#!/usr/bin/env python3
import langextract as lx
from local_pdf_client import get_local_papers
from langextract_processor import extract_from_papers

def query_single_paper(query, paper_index=0):
    papers = get_local_papers()
    
    if not papers:
        print("No local PDFs found.")
        return
    
    if paper_index >= len(papers):
        print(f"Paper index {paper_index} not found. Available: 0-{len(papers)-1}")
        return
    
    # Process just one paper
    single_paper = [papers[paper_index]]
    print(f"Processing paper {paper_index + 1}/{len(papers)}: {single_paper[0]['title']}")
    print(f"Text length: {len(single_paper[0]['text']):,} characters")
    
    results = extract_from_papers(single_paper, query)
    
    for result in results:
        print(f"\n{'='*60}")
        print(f"📄 {result['title']}")
        print('='*60)
        print(result['extraction'])
    
    # Save results
    all_results = [result['extraction'] for result in results]
    filename = f"paper_{paper_index}_results.jsonl"
    lx.io.save_annotated_documents(all_results, output_name=f"./{filename}")
    
    html_content = lx.visualize(f"./{filename}")
    html_file = f"paper_{paper_index}_visualization.html"
    with open(f"./{html_file}", "w") as f:
        f.write(html_content)
    
    print(f"\n✅ Processed 1 paper")
    print(f"✅ Saved to {filename}")
    print(f"✅ Generated {html_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 main_single.py 'query' [paper_index]")
        print("\nAvailable papers:")
        papers = get_local_papers()
        for i, paper in enumerate(papers):
            print(f"  {i}: {paper['title']}")
        sys.exit(1)
    
    query = sys.argv[1]
    paper_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    query_single_paper(query, paper_index)