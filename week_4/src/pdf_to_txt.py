import pdfplumber
import os
from pathlib import Path

# --- CONFIGURATION ---
INPUT_DIR = Path('data')
OUTPUT_DIR = Path('result/pdf_to_txt')

# This single line handles everything: 
# It creates 'result', then creates 'pdf_to_json' inside it.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def process_pdfs():
    # Find all files starting with 'skema' (case insensitive)
    files = list(INPUT_DIR.glob('*skema*')) + list(INPUT_DIR.glob('*SKEMA*'))
    
    if not files:
        print("No files starting with 'skema' found.")
        return

    for pdf_path in files:
        if pdf_path.suffix.lower() == '.pdf':
            print(f"📄 Processing: {pdf_path.name}...")
            
            # Define output path (change .pdf to .txt)
            txt_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                f.write(text + "\n\n")
                                
                            # Extract tables and format them nicely
                            tables = page.extract_tables()
                            for table in tables:
                                for row in table:
                                    # Join row cells with a tab for clean spacing
                                    f.write(" | ".join([str(cell) if cell else "" for cell in row]) + "\n")
                                f.write("\n")
                
                print(f"✅ Finished: {txt_path.name}")
                
            except Exception as e:
                print(f"❌ Error processing {pdf_path.name}: {e}")

if __name__ == "__main__":
    process_pdfs()