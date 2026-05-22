
# ollama list
# ollama run <model-name>
# /bye - to end
# uv run prompt_model.py ds "what is your name"

import os
import sys
import time
import requests
from google import genai
from google.genai.errors import APIError

# Setup local Ollama configurations
OLLAMA_URL = "http://localhost:11434/api/generate"

# Dictionary mapping short names/nicknames to the exact model strings
SHORT_NAMES = {
    # Local Models
    "p3": "phi3:latest",
    "ds": "deepseek-r1:1.5b",
    "g2": "gemma2:2b",
    
    # Gemini Cloud Models
    "gem": "gemini-2.5-flash",
    "gpro": "gemini-2.5-pro",
    "glite": "gemini-2.5-flash-lite"
}

# Initialize the official Google GenAI Client
try:
    gemini_client = genai.Client()
except Exception:
    gemini_client = None


def prompt_model(model_identifier: str, prompt: str) -> str:
    """
    Resolves short names to full model tags, then routes 
    the prompt to either local Ollama or cloud Gemini.
    """
    # Clean input and resolve nickname if it exists, otherwise use raw input string
    cleaned_input = model_identifier.strip().lower()
    actual_model = SHORT_NAMES.get(cleaned_input, model_identifier)

    # 1. Cloud Route: If model starts with 'gemini-', use Google GenAI SDK
    if actual_model.lower().startswith("gemini-"):
        if not os.environ.get("GEMINI_API_KEY"):
            return "Error: GEMINI_API_KEY environment variable is missing."
        try:
            response = gemini_client.models.generate_content(
                model=actual_model,
                contents=prompt
            )
            return response.text
        except APIError as e:
            return f"Gemini API Error: {e.message}"
        except Exception as e:
            return f"An unexpected cloud error occurred: {str(e)}"
            
    # 2. Local Route: Route directly to local Ollama instance
    else:
        payload = {
            "model": actual_model,
            "prompt": prompt,
            "stream": False 
            # stream false is wait untill all load only send back
            # true is send back when ever there is things
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=240)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Ollama Error: Model '{actual_model}' not found or failed to load. (Status: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return "Ollama Error: Could not connect to local server. Is Ollama running?"
        except Exception as e:
            return f"An unexpected local error occurred: {str(e)}"


if __name__ == "__main__":
    # Expecting: script_name model_nickname "prompt"
    if len(sys.argv) < 3:
        print("❌ Error: Missing arguments.")
        print("💡 Usage: python prompt_model.py <nickname/model> \"<prompt>\"")
        print("\nAvailable Nicknames:")
        print("  Local:  ds  -> deepseek-r1:1.5b")
        print("          p3  -> phi3:latest")
        print("          g2  -> gemma2:2b")
        print("  Cloud:  gem -> gemini-2.5-flash")
        print("          gpro-> gemini-2.5-pro")
        sys.exit(1)
        
    user_model_input = sys.argv[1]
    my_prompt = sys.argv[2]
    
    # Resolve name solely for printing display logs nicely
    resolved_name = SHORT_NAMES.get(user_model_input.lower(), user_model_input)
    
    print("============================================================")
    print(f"📡 Input: [{user_model_input}] ➡️ Resolved To: [{resolved_name}]")
    print(f"📝 Prompt: \"{my_prompt}\"")
    print("============================================================\n")
    
    start = time.perf_counter()
    output = prompt_model(user_model_input, my_prompt)
    duration = time.perf_counter() - start
    
    print(f"✨ Response:\n{output.strip()}")
    print("-" * 60)
    print(f"⏱️  Completed in {duration:.2f}s\n")