import requests
import json
from data_ingestion.query import index,format_results

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:1.5b"

def ask_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False 
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        result = response.json()
        if "response" in result:
            return result["response"]
        else:
            return "No response received from the model"

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure it's running (ollama serve)"
    except requests.exceptions.HTTPError as he:
        if "404" in str(he):
            return f"Error: Model '{MODEL}' not found. Try running: ollama pull {MODEL}"
        return f"HTTP Error: {he}"
    except json.JSONDecodeError:
        return "Error: Invalid response from Ollama"
    except Exception as e:
        return f"Error: {e}"

def main():
    print(f"Chatbot using {MODEL} via Ollama. Type 'exit' to quit.")
    while True:
        user_input = input("you are deepseek, a personal assistant that can answer questions about my CV. Ask me anything: ")
        if user_input.lower() == "exit":
            break
        print("Bot:", ask_ollama(user_input).strip())

if __name__ == "__main__":
    main()