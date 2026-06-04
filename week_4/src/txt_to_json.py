import ollama
import json
from pathlib import Path

def convert_single_txt_to_json(input_file_path, output_file_path):
    # 1. Read the text file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Define the Prompt
    prompt = f"""
    You are an expert examiner assistant. Convert the following marking scheme into JSON.
    Structure: {{"exam_paper": "...", "questions": [{{"number": "...", "description": "...", "marking_criteria": [{{"point": "...", "marks": int}}]}}]}}
    
    Rules:
    - Return ONLY valid JSON. 
    - Do not include markdown code blocks or explanatory text.
    - If a point has a mark (e.g., '1m'), extract the integer 1.
    - If no mark is present, set marks to 0.
    
    Content to convert:
    {content}
    """

    print(f"🤖 Sending {input_file_path.name} to gemma2:2b...")
    
    # 3. Call the model
    response = ollama.chat(model='gemma2:2b', messages=[{'role': 'user', 'content': prompt}])
    json_output = response['message']['content']

    # 4. Save the result
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(json_output)
    
    print(f"✅ Success! Saved to {output_file_path}")

# --- CONFIGURATION ---
file_to_convert = Path('results/SKEMA JOHOR 2025.txt') # Change to your file
output_file = Path('results2/SKEMA JOHOR 2025.json')

# Ensure output directory exists
output_file.parent.mkdir(parents=True, exist_ok=True)

# Run
convert_single_txt_to_json(file_to_convert, output_file)