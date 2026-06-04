import os
import json
from pypdf import PdfReader
from pydantic import BaseModel, Field
import ollama

# 1. Define the exact structure we want gemma2:2b to return
class QuestionAnswerPair(BaseModel):
    question_number: str = Field(description="The number of the question, e.g., Question 3b")
    question_text: str = Field(description="The complete question text. Convert any data tables directly into Markdown tables.")
    answer_key: str = Field(description="The matching answer guidelines or working steps found for this question.")

class TopicFilterPayload(BaseModel):
    topic_name: str
    questions_found: list[QuestionAnswerPair] = []


def extract_topic_to_markdown(pdf_filename: str, target_topic: str):
    input_path = os.path.join("data_papers", pdf_filename)
    output_dir = "output_folder"
    
    # Check if the source file exists
    if not os.path.exists(input_path):
        print(f"❌ Error: Cannot find your exam paper at '{input_path}'")
        print("Please create the 'data_papers' folder and drop your PDF inside it.")
        return

    # Data Component: Extract plain text out of the PDF pages
    print(f"📖 Reading text data layers from {pdf_filename}...")
    reader = PdfReader(input_path)
    raw_exam_text = ""
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_exam_text += f"\n--- PAGE {idx + 1} ---\n{text}"

    print(f"🧠 Querying local gemma2:2b for topic: '{target_topic}'...")
    
    system_instruction = (
        "You are an academic parser. Scan the text document and extract ONLY questions and "
        "their matching answers that belong to the requested topic. Ignore exam rules and headers. "
        "Convert data grids/tables into clean Markdown pipe formatting."
    )
    
    prompt = f"Target Topic: {target_topic}\n\nExam Text Content:\n{raw_exam_text}"

    try:
        # AI Component: Constrained JSON schema extraction via Ollama
        response = ollama.chat(
            model='gemma2:2b',
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': prompt}
            ],
            format=TopicFilterPayload.model_json_schema()
        )
        
        # Parse and validate the response against our Pydantic structural rules
        extracted_data = TopicFilterPayload.model_validate_json(response.message.content)
        
    except Exception as e:
        print(f"❌ Local model parsing failed: {e}")
        return

    # Check if any questions were actually returned
    if not extracted_data.questions_found:
        print(f"⚠️ No questions matching '{target_topic}' were detected in this paper.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the unified output markdown file name
    clean_topic_name = target_topic.replace(" ", "_").lower()
    output_filename = f"{os.path.splitext(pdf_filename)[0]}_{clean_topic_name}.md"
    output_path = os.path.join(output_dir, output_filename)

    # File Compiler: Write out the structured single Markdown document
    print(f"💾 Saving unified question bank sheet to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as md_file:
        md_file.write(f"# 📚 Topic Question Bank: {target_topic}\n")
        md_file.write(f"- **Source Material:** `{pdf_filename}`\n\n")
        md_file.write("---\n\n")

        for item in extracted_data.questions_found:
            md_file.write(f"## 📝 {item.question_number}\n\n")
            md_file.write("### ❓ Question Text:\n")
            md_file.write(f"{item.question_text}\n\n")
            md_file.write("### 🔑 Answer Key / Working Guidelines:\n")
            md_file.write(f"{item.answer_key}\n\n")
            md_file.write("---\n\n")

    print(f"✅ Part 1 complete! Successfully isolated {len(extracted_data.questions_found)} topics questions.")


if __name__ == "__main__":
    # --- CONFIGURE YOUR TEST RUN HERE ---
    # 1. Drop a real PDF into your data_papers/ folder
    # 2. Match the name and topic variables below:
    FILE_IN_DATA_PAPERS = "past_year_2025.pdf" 
    TOPIC_TO_SEARCH = "Matrices"

    extract_topic_to_markdown(FILE_IN_DATA_PAPERS, TOPIC_TO_SEARCH)