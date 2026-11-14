import requests
import json
import sys
from data_ingestion.query import index,format_results,search_pinecone

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:1.5b"


def ask_ollama(question,results):
    formatted_prompt = f"""
You are a helpful assistant that can answer questions about my CV.
this data {results} is a JSON array of records from my CV, each record has the following fields: id, file_name, section, page, text.
Please keep the answer concise and to the point.
You will take user inputs from {question} and answer them based on the CV records. You should not make up answers that are not in the records. You should only answer based on the information in the records. If the answer is not in the records, you should say "I don't know".\
Add the chunk ids from the question in the generated answer. If the answer is not in the records, you should say "I don't know".\
"""

    payload = {
        "model": MODEL,
        "prompt": formatted_prompt,
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
        user_input = " ".join(sys.argv[1:])
        if user_input.lower() == "exit":
            break
        query_results = search_pinecone(user_input)
        results = format_results(query_results)
        print("Bot:", ask_ollama(question = user_input, results = results).strip())
        sys.exit(0)

if __name__ == "__main__":
    main()