import langextract as lx
import textwrap
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def extract_from_papers(papers, prompt):
    return _extract_and_visualize(papers, prompt)[0]

def extract_and_get_html(papers, prompt):
    return _extract_and_visualize(papers, prompt)

def _extract_and_visualize(papers, prompt):
    if not GEMINI_API_KEY:
        results = []
        for paper in papers:
            result_text = f"⚠️ No GEMINI_API_KEY found in .env file\n\nPrompt: {prompt}\n\nPaper: {paper['title']}\nText length: {len(paper['text'])} characters\n\nFirst 500 chars:\n{paper['text'][:500]}..."
            results.append({
                'title': paper['title'],
                'extraction': result_text
            })
        return results, None
    
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
    all_extractions = []
    
    for paper in papers:
        try:
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
            if hasattr(result, 'extractions'):
                all_extractions.extend(result.extractions)
            else:
                all_extractions.extend(result)
        except Exception as e:
            results.append({
                'title': paper['title'],
                'extraction': f"Error processing paper: {str(e)}"
            })
    
    html_content = None
    print(f"Total extractions collected: {len(all_extractions)}")
    
    if all_extractions:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
                lx.io.save_annotated_documents(all_extractions, f.name)
                print(f"Saved annotations to {f.name}")
                html_content = lx.visualize(f.name)
                print(f"Generated HTML visualization, length: {len(html_content) if html_content else 0}")
                os.unlink(f.name)
        except Exception as e:
            print(f"Error generating visualization: {e}")
    else:
        print("No extractions to visualize")
    
    return results, html_content