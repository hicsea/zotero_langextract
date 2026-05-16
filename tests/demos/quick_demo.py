#!/usr/bin/env python3
import langextract as lx
from local_pdf_client import get_local_papers
from config import GEMINI_API_KEY

# Quick demo with focused sections
papers = get_local_papers()
paper = papers[0]  # First paper

# Extract methodology section (around 3000 chars)
text = paper['text']
method_start = text.find("methodology") or text.find("Methodology") or text.find("METHOD") or 2000
method_section = text[method_start:method_start+3000]

print("🔬 QUICK GENETIC ALGORITHM EXTRACTION")
print("="*50)
print(f"Paper: {paper['pdf_path'].split('/')[-1]}")
print(f"Section length: {len(method_section)} chars")
print(f"Preview: {method_section[:200]}...")

example = lx.data.ExampleData(
    text="The genetic algorithm used tournament selection with population size 100 and crossover rate 0.8. The fitness function minimized time-to-collision.",
    extractions=[
        lx.data.Extraction(
            extraction_class="parameters",
            extraction_text="population size 100 and crossover rate 0.8",
            attributes={"population": "100", "crossover": "0.8"}
        ),
        lx.data.Extraction(
            extraction_class="fitness_function",
            extraction_text="minimized time-to-collision",
            attributes={"objective": "minimize", "metric": "time-to-collision"}
        )
    ]
)

result = lx.extract(
    text_or_documents=method_section,
    prompt_description="Extract genetic algorithm parameters, fitness functions, and experimental setup details",
    examples=[example],
    model_id="gemini-2.5-flash",
    api_key=GEMINI_API_KEY,
    extraction_passes=1,
    max_workers=3
)

print("\n🎯 EXTRACTION RESULTS:")
print("="*50)
for extraction in result.extractions:
    print(f"🔍 {extraction.extraction_class.upper()}: {extraction.extraction_text}")
    if extraction.attributes:
        for key, value in extraction.attributes.items():
            print(f"   └─ {key}: {value}")
    print(f"   📍 Position: {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}")
    print()

print(f"✅ Found {len(result.extractions)} key elements!")
print("✅ Ready to process all 5 papers with full methodology!")