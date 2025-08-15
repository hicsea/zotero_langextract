import yaml
import langextract as lx
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ExtractionExample:
    text: str
    extractions: List[Dict[str, Any]]

@dataclass
class ExtractionConfig:
    name: str
    description: str
    prompt: str
    examples: List[ExtractionExample]
    extraction_passes: int = 2
    max_workers: int = 5
    max_char_buffer: int = 2000

def load_config(config_path: str) -> ExtractionConfig:
    """Load extraction configuration from YAML file"""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Parse examples
    examples = []
    for ex_data in data.get('examples', []):
        examples.append(ExtractionExample(
            text=ex_data['text'],
            extractions=ex_data['extractions']
        ))
    
    # Parse extraction settings
    settings = data.get('extraction_settings', {})
    
    return ExtractionConfig(
        name=data['name'],
        description=data['description'],
        prompt=data['prompt'],
        examples=examples,
        extraction_passes=settings.get('extraction_passes', 2),
        max_workers=settings.get('max_workers', 5),
        max_char_buffer=settings.get('max_char_buffer', 2000)
    )

def config_to_langextract_examples(examples: List[ExtractionExample]) -> List[lx.data.ExampleData]:
    """Convert config examples to LangExtract format"""
    langextract_examples = []
    
    for example in examples:
        extractions = []
        for ext in example.extractions:
            extraction = lx.data.Extraction(
                extraction_class=ext['class'],
                extraction_text=ext['text'],
                attributes=ext.get('attributes', {})
            )
            extractions.append(extraction)
        
        langextract_examples.append(lx.data.ExampleData(
            text=example.text,
            extractions=extractions
        ))
    
    return langextract_examples

def list_available_configs(config_dir: str = "configs") -> List[str]:
    """List all available configuration files"""
    config_path = Path(config_dir)
    if not config_path.exists():
        return []
    
    configs = []
    for yaml_file in config_path.glob("*.yaml"):
        configs.append(yaml_file.name)
    
    return sorted(configs)