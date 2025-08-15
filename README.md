# Zotero + LangExtract Research Analysis System

A powerful system for extracting structured information from research papers using Google's LangExtract and your Zotero library.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```bash
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run Analysis
```bash
# List available configurations
python3 scripts/main_config.py --list-configs

# List your Zotero collections
python3 scripts/main_config.py --list-collections

# Process specific collections
python3 scripts/main_config.py --config genetic_algorithms.yaml --zotero-collections "Genetic Algorithms"

# Process filesystem folders
python3 scripts/main_config.py --config machine_learning.yaml --folders /path/to/papers/ --recursive
```

## 📁 Directory Structure

```
zotero_langextract/
├── core/                    # Core functionality
│   ├── config.py           # Environment configuration
│   ├── config_loader.py    # YAML config system
│   ├── local_pdf_client.py # Zotero PDF access
│   └── langextract_processor.py # LangExtract integration
├── scripts/                 # Main execution scripts
│   ├── main_config.py      # New configurable main script
│   ├── main.py            # Original API-based script
│   └── main_local.py      # Original local PDF script
├── configs/                 # Analysis configurations
│   ├── genetic_algorithms.yaml
│   ├── machine_learning.yaml
│   └── templates/
├── outputs/                 # Generated results
│   ├── jsonl/              # Structured data
│   ├── html/               # Interactive visualizations
│   └── reports/            # Summary reports
├── utils/                   # Utilities
│   ├── folder_scanner.py   # PDF discovery
│   └── generate_viz.py     # Visualization generator
└── tests/demos/            # Demo scripts
```

## ⚙️ Configuration System

### Creating Custom Configs

Create YAML files in `configs/` directory:

```yaml
name: "Your Analysis Name"
description: "Description of what this extracts"

prompt: |
  Your extraction prompt here.
  Be specific about what to extract.

examples:
  - text: "Example research text here..."
    extractions:
      - class: "algorithm"
        text: "genetic algorithm"
        attributes:
          type: "optimization"
      - class: "parameters"
        text: "population size 100"
        attributes:
          population_size: "100"

extraction_settings:
  extraction_passes: 2
  max_workers: 5
  max_char_buffer: 2000
```

## 🔍 Usage Examples

### Process Zotero Collections
```bash
# Single collection
python3 scripts/main_config.py -c genetic_algorithms.yaml -z "Evolutionary Algorithms"

# Multiple collections
python3 scripts/main_config.py -c machine_learning.yaml -z "Deep Learning" "Neural Networks"

# Limit number of papers
python3 scripts/main_config.py -c genetic_algorithms.yaml -z "GA Papers" --limit 10
```

### Process File System Folders
```bash
# Single folder
python3 scripts/main_config.py -c machine_learning.yaml -f /path/to/ml_papers/

# Multiple folders, recursive
python3 scripts/main_config.py -c genetic_algorithms.yaml -f /papers/ga/ /papers/optimization/ -r

# Custom output directory
python3 scripts/main_config.py -c config.yaml -f /papers/ -o custom_outputs/
```

## 📊 Output Files

For each analysis run, the system generates:

1. **JSONL Data**: `outputs/jsonl/analysis_name_timestamp.jsonl`
   - Structured extraction data
   - Exact character positions
   - Attributes and metadata

2. **HTML Visualization**: `outputs/html/analysis_name_timestamp.html`
   - Interactive web page
   - Highlighted source text
   - Clickable extractions

3. **Summary Report**: `outputs/reports/analysis_name_timestamp_summary.txt`
   - Processing statistics
   - Paper-by-paper breakdown
   - Extraction counts

## 🎯 Available Configurations

- **genetic_algorithms.yaml**: Extract GA parameters, fitness functions, constraints
- **machine_learning.yaml**: Extract ML methods, datasets, performance metrics

## 💡 Tips

1. **Organize Your Papers**: Sort papers into Zotero collections or filesystem folders by topic
2. **Test Small Batches**: Use `--limit 5` when testing new configurations
3. **Monitor API Usage**: Large collections may consume significant API quota
4. **Custom Configs**: Create domain-specific configurations for better results

## 🔧 Advanced Usage

### Create New Configuration Template
```bash
cp configs/genetic_algorithms.yaml configs/my_analysis.yaml
# Edit the new file with your specific prompts and examples
```

### Process Hundreds of Papers
```bash
# Process by folder, 50 papers at a time
python3 scripts/main_config.py -c config.yaml -f /papers/topic1/ --limit 50
python3 scripts/main_config.py -c config.yaml -f /papers/topic2/ --limit 50
```

### Generate Visualizations from Existing Data
```bash
python3 utils/generate_viz.py
```

## 🎉 Success!

Your research analysis system is ready to process hundreds of papers with configurable extraction rules and organized output management!