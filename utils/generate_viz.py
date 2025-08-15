#!/usr/bin/env python3
import langextract as lx
import os

# Generate a working visualization from existing results
print("🔧 GENERATING VISUALIZATION FROM EXISTING DATA")
print("="*50)

# Check what JSONL files we have
import glob
jsonl_files = glob.glob("*.jsonl") + glob.glob("**/*.jsonl", recursive=True)

print(f"Found JSONL files: {jsonl_files}")

if jsonl_files:
    for jsonl_file in jsonl_files:
        print(f"\n📄 Processing: {jsonl_file}")
        
        # Get just the filename without path/extension for HTML name
        base_name = os.path.basename(jsonl_file).replace('.jsonl', '')
        html_name = f"{base_name}_visualization.html"
        
        try:
            # Generate visualization
            html_content = lx.visualize(jsonl_file)
            
            # Save to current directory
            with open(html_name, "w") as f:
                f.write(html_content)
            
            full_path = os.path.abspath(html_name)
            print(f"✅ Generated: {html_name}")
            print(f"📁 Full path: {full_path}")
            print(f"🌐 Open with: firefox '{full_path}'")
            
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")

else:
    print("❌ No JSONL files found. Run a main_*.py script first!")

print(f"\n💡 TO VIEW VISUALIZATIONS:")
print(f"   1. Open file manager: nautilus {os.getcwd()}")
print(f"   2. Double-click the .html file")  
print(f"   3. Or run: firefox *.html")