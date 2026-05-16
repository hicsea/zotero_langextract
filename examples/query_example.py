#!/usr/bin/env python3
import sys
sys.path.append('..')
from main import query_papers

queries = [
    "Extract the main methodology used",
    "What are the key findings?",
    "List the limitations mentioned"
]

for q in queries:
    print(f"\n{'='*50}")
    print(f"QUERY: {q}")
    print('='*50)
    query_papers(q)