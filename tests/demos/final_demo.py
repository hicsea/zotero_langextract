#!/usr/bin/env python3
import langextract as lx
from local_pdf_client import get_local_papers
from config import GEMINI_API_KEY

# Final working demo
papers = get_local_papers()
paper = papers[0]

# Take middle section (likely has methodology)
text = paper['text']
start = len(text) // 3  # Skip intro, get middle content
section = text[start:start+2000]

print("🚀 FINAL DEMO: Genetic Algorithm Research Extraction")
print("="*60)
print(f"📄 Paper: {paper['pdf_path'].split('/')[-1][:50]}...")
print(f"📝 Analyzing {len(section)} characters from middle section")
print(f"📖 Content preview:")
print(f"   {section[:300].replace(chr(10), ' ')}...")

example = lx.data.ExampleData(
    text="The genetic algorithm parameters were: population size 100, mutation rate 0.05, crossover probability 0.8. The fitness function evaluated time-to-collision (TTC) values.",
    extractions=[
        lx.data.Extraction(
            extraction_class="parameters",
            extraction_text="population size 100, mutation rate 0.05, crossover probability 0.8",
            attributes={"population_size": "100", "mutation_rate": "0.05", "crossover_prob": "0.8"}
        ),
        lx.data.Extraction(
            extraction_class="fitness_function", 
            extraction_text="time-to-collision (TTC) values",
            attributes={"metric": "time-to-collision", "abbreviation": "TTC"}
        )
    ]
)

print("\n🔄 Processing with LangExtract...")
result = lx.extract(
    text_or_documents=section,
    prompt_description="Extract genetic algorithm parameters, fitness functions, experimental setup, and performance metrics",
    examples=[example],
    model_id="gemini-2.5-flash", 
    api_key=GEMINI_API_KEY
)

print("\n🎯 GENETIC ALGORITHM RESEARCH FINDINGS:")
print("="*60)

if result.extractions:
    for i, extraction in enumerate(result.extractions, 1):
        print(f"{i}. 🔍 {extraction.extraction_class.upper()}")
        print(f"   📝 Text: '{extraction.extraction_text}'")
        print(f"   📍 Location: chars {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}")
        if extraction.attributes:
            print(f"   🏷️  Attributes: {extraction.attributes}")
        print()
    
    print(f"✅ Successfully extracted {len(result.extractions)} research elements!")
    print("✅ Your Zotero + LangExtract system is fully operational! 🎉")
else:
    print("No extractions found in this section - try a different part of the paper")

print(f"\n📊 Processing stats:")
print(f"   • Characters processed: {len(section):,}")
print(f"   • Papers available: {len(papers)}")
print(f"   • Ready for full research analysis!")