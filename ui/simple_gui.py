#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import threading
import yaml
import webbrowser
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.folder_scanner import get_available_collections, scan_zotero_folders

from extract_processor import extract_from_papers, extract_and_get_html

class ZoteroExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zotero Language Extractor")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        self.load_collections()
        self.load_example_prompts()
        self.last_html_content = None
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        ttk.Label(main_frame, text="Zotero Collection:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.collection_var = tk.StringVar()
        self.collection_combo = ttk.Combobox(main_frame, textvariable=self.collection_var, state="readonly")
        self.collection_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="Extraction Prompt:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        self.prompt_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.prompt_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Load GA Example", command=lambda: self.load_prompt("genetic_algorithms")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load ML Example", command=lambda: self.load_prompt("machine_learning")).pack(side=tk.LEFT, padx=5)
        self.run_button = ttk.Button(button_frame, text="Run Extraction", command=self.run_extraction)
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.viz_button = ttk.Button(button_frame, text="Show Visualization", command=self.show_visualization, state="disabled")
        self.viz_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="Results:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.results_text.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
    def load_collections(self):
        try:
            collections = get_available_collections()
            self.collection_combo['values'] = collections
            if collections:
                self.collection_combo.set(collections[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Zotero collections: {e}")
            
    def load_example_prompts(self):
        self.prompts = {}
        configs_dir = Path(__file__).parent.parent / "configs"
        
        for config_file in configs_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    self.prompts[config_file.stem] = config.get('prompt', '')
            except Exception as e:
                print(f"Error loading {config_file}: {e}")
        
        if not self.prompts and 'genetic_algorithms' not in self.prompts:
            self.prompts['default'] = "Extract key information from the research papers."
            
    def load_prompt(self, prompt_type):
        if prompt_type in self.prompts:
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, self.prompts[prompt_type])
        else:
            messagebox.showwarning("Warning", f"No prompt found for {prompt_type}")
            
    def run_extraction(self):
        collection = self.collection_var.get()
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        
        if not collection:
            messagebox.showerror("Error", "Please select a collection")
            return
            
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt")
            return
            
        self.run_button.config(state='disabled')
        self.status_var.set("Running extraction...")
        self.results_text.delete(1.0, tk.END)
        
        threading.Thread(target=self._extract_thread, args=(collection, prompt), daemon=True).start()
        
    def _extract_thread(self, collection, prompt):
        try:
            papers = scan_zotero_folders([collection])
            
            if not papers:
                self.root.after(0, lambda: self.update_results("No papers found in selected collection"))
                return
                
            self.root.after(0, lambda: self.update_status(f"Processing {len(papers)} papers..."))
            
            paper_dicts = [{'title': p.title, 'text': p.text} for p in papers]
            results, html_content = extract_and_get_html(paper_dicts, prompt)
            self.last_html_content = html_content
            
            output = f"Extraction Results ({len(results)} papers):\n"
            output += "="*50 + "\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"{i}. {result['title']}\n"
                output += "-" * 40 + "\n"
                
                if hasattr(result['extraction'], 'extractions'):
                    # Handle AnnotatedDocument objects
                    annotated_doc = result['extraction']
                    if annotated_doc.extractions:
                        output += f"  Found {len(annotated_doc.extractions)} extractions:\n\n"
                        for j, extraction in enumerate(annotated_doc.extractions, 1):
                            output += f"  [{j}] Class: {extraction.extraction_class}\n"
                            output += f"      Text: \"{extraction.extraction_text}\"\n"
                            if extraction.attributes:
                                output += f"      Attributes: {extraction.attributes}\n"
                            if extraction.char_interval:
                                output += f"      Position: chars {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}\n"
                            output += "\n"
                    else:
                        output += "  No extractions found\n\n"
                elif isinstance(result['extraction'], list):
                    if result['extraction']:
                        for j, extraction in enumerate(result['extraction'], 1):
                            output += f"  Extraction {j}:\n"
                            output += f"    Class: {extraction.extraction_class}\n"
                            output += f"    Text: {extraction.extraction_text}\n"
                            if extraction.attributes:
                                output += f"    Attributes: {extraction.attributes}\n"
                            output += "\n"
                    else:
                        output += "  No extractions found\n\n"
                else:
                    output += f"{result['extraction']}\n\n"
                
            self.root.after(0, lambda: self.update_results(output))
            self.root.after(0, lambda: print(f"Updated GUI with {len(results)} results, HTML available: {html_content is not None}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_results(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self._enable_buttons)
            
    def _enable_buttons(self):
        self.run_button.config(state='normal')
        if self.last_html_content:
            self.viz_button.config(state='normal')
            print(f"Visualization button enabled - HTML length: {len(self.last_html_content)}")
        else:
            self.viz_button.config(state='disabled')
            print("No HTML content available for visualization")
        self.status_var.set("Ready")
            
    def update_results(self, text):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        
    def update_status(self, status):
        self.status_var.set(status)
        
    def show_visualization(self):
        if not self.last_html_content:
            messagebox.showwarning("Warning", "No visualization available. Run an extraction first.")
            return
            
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(self.last_html_content)
                html_file = f.name
            
            webbrowser.open(f'file://{html_file}')
            self.status_var.set("Opened visualization in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open visualization: {e}")

def main():
    root = tk.Tk()
    app = ZoteroExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()