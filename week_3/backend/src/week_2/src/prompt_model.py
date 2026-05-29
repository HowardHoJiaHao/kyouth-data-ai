import requests

# Use host.docker.internal to reach Windows host from Docker container
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"


def prompt_model(model_identifier: str, prompt: str, context: str = "") -> str:
    # Combine context with prompt if resume is uploaded
    if context and len(context) > 0:
        full_prompt = f"""Based on the following resume content:

{context}

Please answer this question: {prompt}

Provide a helpful, detailed response based on the resume above."""
    else:
        full_prompt = prompt

    # Use deepseek-r1:1.5b as default
    model = "deepseek-r1:1.5b"

    payload = {"model": model, "prompt": full_prompt, "stream": False}

    try:
        print(f"Calling Ollama with model: {model}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json().get("response", "No response from Ollama")
            print(f"Ollama response received: {len(result)} characters")
            return result
        else:
            return f"Ollama Error: Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Ollama Error: Cannot connect. Make sure Ollama is running"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        result = prompt_model(sys.argv[1], sys.argv[2])
        print(result)
