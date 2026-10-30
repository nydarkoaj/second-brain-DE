import os
import sys
import pinecone
from dotenv import load_dotenv

load_dotenv()

pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("cv-index")

query_text = " ".join(sys.argv[1:]) or "where did I get networking experience"

results = index.search(
    namespace="cv-namespace",
    query={"inputs": {"text": query_text}, "top_k": 2},
    fields=["file_name", "section", "page", "text"],
)

for hit in results["result"]["hits"]:
    f = hit.fields
    print(f"{hit.score:.3f}  {hit.id}  |  {f.get('file_name')}  |  {f.get('section')}  (p{int(f.get('page', 0))})")
    print("   ", f.get("text", "")[:400].replace("\n", " "), "\n")
