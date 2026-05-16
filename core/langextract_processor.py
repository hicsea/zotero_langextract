import langextract as lx
import textwrap
from config import GEMINI_API_KEY

def extract_from_papers(papers, query):
    prompt = textwrap.dedent("""\
        Extract research methodology, fitness functions, constraints, parameters, and algorithms.
        Use exact text for extractions. Focus on technical details and specifications.
        """)
    
    examples = [
        lx.data.ExampleData(
            text="We used a genetic algorithm with tournament selection to optimize the multi-objective fitness function f(x) = w1*accuracy + w2*complexity. The input parameter space consisted of 50 decision variables bounded between [0,1]. Population size was set to 100 with crossover probability 0.8.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="algorithm",
                    extraction_text="genetic algorithm with tournament selection",
                    attributes={"type": "optimization", "selection_method": "tournament"}
                ),
                lx.data.Extraction(
                    extraction_class="fitness_function", 
                    extraction_text="f(x) = w1*accuracy + w2*complexity",
                    attributes={"type": "multi-objective", "components": "accuracy, complexity"}
                ),
                lx.data.Extraction(
                    extraction_class="parameters",
                    extraction_text="50 decision variables bounded between [0,1]",
                    attributes={"dimension": "50", "bounds": "[0,1]"}
                ),
                lx.data.Extraction(
                    extraction_class="constraints",
                    extraction_text="Population size was set to 100 with crossover probability 0.8",
                    attributes={"population": "100", "crossover": "0.8"}
                )
            ]
        )
    ]
    
    results = []
    for paper in papers:
        result = lx.extract(
            text_or_documents=paper['text'],
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
            api_key=GEMINI_API_KEY,
            extraction_passes=2,
            max_workers=5,
            max_char_buffer=2000
        )
        results.append({
            'title': paper['title'],
            'extraction': result
        })
    return results