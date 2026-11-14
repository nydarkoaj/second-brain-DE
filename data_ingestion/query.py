import os
import sys
import pinecone
from dotenv import load_dotenv

load_dotenv()
def pc_object():
    return pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

pc = pc_object()
index = pc.Index("cv-index")

query_text = " ".join(sys.argv[1:]) or "where did I get networking experience"


def search_pinecone(query_text):
    results = index.search(
        namespace="cv-namespace",
        query={"inputs": {"text": query_text}, "top_k": 10},
        fields=["file_name", "section", "page", "text"],
    )
    return results

def format_results(results):
    formatted_results = []
    for hit in results["result"]["hits"]:
        f = hit.fields
        formatted_results.append({
            "score": hit.score,
            "id": hit.id,
            "file_name": f.get("file_name"),
            "section": f.get("section"),
            "page": int(f.get("page", 0)),
            "text": f.get("text", "").replace("\n", " ")
        })
    return formatted_results
# results = search_pinecone(query_text)
# print(format_results(results))
