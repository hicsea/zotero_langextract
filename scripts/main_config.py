#!/usr/bin/env python3
import sys
import os
import argparse
import langextract as lx
from datetime import datetime
from pathlib import Path
import csv
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_loader import load_config, config_to_langextract_examples, list_available_configs
from core.config import GEMINI_API_KEY
from utils.folder_scanner import scan_zotero_folders, scan_filesystem_folders, get_available_collections, print_paper_summary

def extract_from_papers_with_config(papers, config):
    """Extract information from papers using loaded configuration"""
    langextract_examples = config_to_langextract_examples(config.examples)
    
    results = []
    for i, paper in enumerate(papers, 1):
        print(f"\n🔄 Processing paper {i}/{len(papers)}: {paper.title[:50]}...")
        
        try:
            result = lx.extract(
                text_or_documents=paper.text,
                prompt_description=config.prompt,
                examples=langextract_examples,
                model_id="gemini-2.5-flash",
                api_key=GEMINI_API_KEY,
                extraction_passes=config.extraction_passes,
                max_workers=config.max_workers,
                max_char_buffer=config.max_char_buffer
            )
            
            results.append({
                'paper_info': paper,
                'extraction': result
            })
            
            print(f"✅ Extracted {len(result.extractions)} entities")
            
        except Exception as e:
            print(f"❌ Error processing {paper.title}: {e}")
            continue
    
    return results

def save_results(results, config, output_dir):
    """Save results with structured naming"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{config.name.lower().replace(' ', '_')}_{timestamp}"
    
    # Save JSONL
    jsonl_path = output_dir / "jsonl" / f"{base_name}.jsonl"
    extractions = [result['extraction'] for result in results]
    lx.io.save_annotated_documents(extractions, output_name=str(jsonl_path))
    
    # Generate HTML visualization
    html_path = output_dir / "html" / f"{base_name}.html"
    try:
        html_content = lx.visualize(str(jsonl_path))
        with open(html_path, "w") as f:
            f.write(html_content)
        print(f"✅ Generated visualization: {html_path}")
    except Exception as e:
        print(f"⚠️  Visualization error: {e}")
    
    # Create summary report
    report_path = output_dir / "reports" / f"{base_name}_summary.txt"
    with open(report_path, "w") as f:
        f.write(f"Extraction Summary: {config.name}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Configuration: {config.description}\n")
        f.write(f"Papers processed: {len(results)}\n\n")
        
        for result in results:
            paper = result['paper_info']
            extraction = result['extraction']
            f.write(f"Paper: {paper.title}\n")
            f.write(f"Folder: {paper.folder_name}\n")
            f.write(f"Extractions: {len(extraction.extractions)}\n")
            for ext in extraction.extractions:
                f.write(f"  - {ext.extraction_class}: {ext.extraction_text[:100]}...\n")
            f.write("\n")
    
    # Generate CSV export
    csv_path = output_dir / "csv" / f"{base_name}.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Collect all unique attribute keys
    all_attribute_keys = set()
    for result in results:
        for ext in result['extraction'].extractions:
            if hasattr(ext, 'attributes') and ext.attributes:
                all_attribute_keys.update(ext.attributes.keys())
    
    # Sort attribute keys for consistent column order
    sorted_attribute_keys = sorted(all_attribute_keys)
    
    # Create CSV with dynamic columns
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'paper_title', 'paper_folder', 'extraction_class', 'extraction_text',
            'char_start', 'char_end', 'attributes_json'
        ] + [f'attribute_{key}' for key in sorted_attribute_keys]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            paper = result['paper_info']
            for ext in result['extraction'].extractions:
                row = {
                    'paper_title': paper.title,
                    'paper_folder': paper.folder_name,
                    'extraction_class': ext.extraction_class,
                    'extraction_text': ext.extraction_text,
                    'char_start': ext.char_interval.start_pos if hasattr(ext, 'char_interval') else '',
                    'char_end': ext.char_interval.end_pos if hasattr(ext, 'char_interval') else '',
                    'attributes_json': json.dumps(ext.attributes) if hasattr(ext, 'attributes') and ext.attributes else ''
                }
                
                # Add individual attribute columns
                if hasattr(ext, 'attributes') and ext.attributes:
                    for key in sorted_attribute_keys:
                        row[f'attribute_{key}'] = ext.attributes.get(key, '')
                
                writer.writerow(row)
    
    print(f"✅ Generated CSV export: {csv_path}")
    
    return jsonl_path, html_path, report_path, csv_path

def main():
    parser = argparse.ArgumentParser(description="Extract structured information from research papers using configurable prompts")
    parser.add_argument("--config", "-c", help="Path to YAML configuration file")
    parser.add_argument("--zotero-collections", "-z", nargs="+", help="Zotero collection names to process")
    parser.add_argument("--folders", "-f", nargs="+", help="Filesystem folders to scan for PDFs")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recursively scan folders")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of papers to process")
    parser.add_argument("--list-configs", action="store_true", help="List available configurations")
    parser.add_argument("--list-collections", action="store_true", help="List available Zotero collections")
    parser.add_argument("--output-dir", "-o", default="outputs", help="Output directory")
    
    args = parser.parse_args()
    
    # Set up paths
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / args.output_dir
    configs_dir = script_dir / "configs"
    
    # Handle list commands
    if args.list_configs:
        configs = list_available_configs(str(configs_dir))
        print("📋 Available configurations:")
        for config in configs:
            print(f"   {config}")
        return
    
    if args.list_collections:
        collections = get_available_collections()
        print("📁 Available Zotero collections:")
        for collection in collections:
            print(f"   {collection}")
        return
    
    # Check if config is required
    if not args.config and not args.list_configs and not args.list_collections:
        print("❌ Config file required. Use --config or --list-configs")
        return
    
    # Load configuration if provided
    config = None
    if args.config:
        config_path = args.config
        if not os.path.isabs(config_path):
            config_path = configs_dir / config_path
        
        try:
            config = load_config(str(config_path))
            print(f"📋 Loaded config: {config.name}")
            print(f"📝 {config.description}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return
    
    # Scan for papers
    papers = []
    
    if args.zotero_collections:
        print(f"🔍 Scanning Zotero collections: {args.zotero_collections}")
        papers.extend(scan_zotero_folders(args.zotero_collections, args.limit))
    
    if args.folders:
        print(f"🔍 Scanning filesystem folders: {args.folders}")
        papers.extend(scan_filesystem_folders(args.folders, args.recursive, args.limit))
    
    if not papers:
        if not args.zotero_collections and not args.folders:
            print("❌ No paper sources specified. Use --zotero-collections or --folders")
        else:
            print("❌ No papers found in specified locations")
        return
    
    if not config:
        print("❌ Configuration required for processing papers")
        return
    
    print_paper_summary(papers)
    
    # Process papers
    print(f"\n🚀 Starting extraction with {config.name}...")
    results = extract_from_papers_with_config(papers, config)
    
    if not results:
        print("❌ No results generated")
        return
    
    # Save results
    jsonl_path, html_path, report_path = save_results(results, config, output_dir)
    
    print(f"\n✅ Processing complete!")
    print(f"📄 Data: {jsonl_path}")
    print(f"🌐 Visualization: {html_path}")
    print(f"📊 Report: {report_path}")
    print(f"\n💡 Open visualization: firefox '{html_path}'")

if __name__ == "__main__":
    main()