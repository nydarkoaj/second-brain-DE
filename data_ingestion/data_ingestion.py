from importlib.resources import path

import pymupdf
import pinecone
import datetime as dt
import pathlib
import os
from dotenv import load_dotenv
load_dotenv()
import re

source_parent_dir = pathlib.Path(r'C:\Users\NanaYawDarko\Documents\Internal Projects\second-brain-DE\DataSources')
data_source_type = 'CVs'
cv_file_names = [path.name for path in source_parent_dir.joinpath(data_source_type).iterdir() if path.is_file()]
single_file = cv_file_names[0]  # For testing, you can change this to any file in the list

pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_index_name = 'cv-index'
pinecone_cv_namespace = 'cv-namespace'
pc = pinecone.Pinecone(api_key=pinecone_api_key)


payload = []


def build_json_payload(text, file, data_source_type, rec_counter):
    return {
        "_id": f"rec_{rec_counter}",
        "text": text,
        "data_source_type": data_source_type,
        "file_name": clean_file_name(file),
        "ingestion_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def clean_file_name(file_name):
    if "_" in file_name or "-" in file_name:
        return file_name.replace("_", " ").replace("-", " ")
    return file_name

# new function to loop through pages in a doc and get text with headers
def extract_text_with_headers(doc):
    text_with_headers = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        text_with_headers.append(f"Page {page_num + 1}:\n{page_text}")
    return "\n".join(text_with_headers)

def clean(t):
    t = re.sub(r'</?(sup|u)>', '', t)
    t = t.replace('**', '')
    t = re.sub(r'^#+\s*', '', t, flags=re.M)
    return t

def ingest_to_pinecone(payload,index_name, ns):
    # Target the index
    dense_index = pc.Index(index_name)

    # Upsert the records into a namespace
    dense_index.upsert_records(namespace=ns, records=payload)

def inspect_pinecone_records(index_name, ns):
    # Target the index
    dense_index = pc.Index(index_name)

    # Fetch records from the namespace
    records = []
    for page in dense_index.list(namespace=ns, limit=100):
        records.extend(page)
    return records

def delete_pinecone_records(index_name, ns):
    # Target the index
    dense_index = pc.Index(index_name)

    # Delete all records in the namespace
    dense_index.delete(namespace=ns, delete_all=True)

# build a main function to loop through the files in the cv_file_names list, extract text from each file, and build a JSON payload for each file. Then ingest the payload into Pinecone.

def main():
    records = []
    for rec_counter,file in enumerate([single_file], start=1):
        with pymupdf.open(source_parent_dir.joinpath(data_source_type).joinpath(file)) as doc:
            page_count = doc.page_count
            print(f"\nProcessing file: {file}...")
            print(f"Total pages in {file}: {page_count}")
            chunks = doc.to_chunks()          # one call per file
            for c in chunks.to_dicts():       # list of dicts, one per chunk
               # print(c["id"], c["metadata"]["section_path"], c["metadata"]["page_start"])
                m=c["metadata"]
                text = c["text"]
                section = " > ".join(m["section_path"]) or "Introduction"
                records.append({
                    "_id": f"{file}_{c['id']}".replace(" ", "_"),
                    "section": section,
                    "text": f"{clean_file_name(file)} | {section}\n\n{clean(text)}",
                    "page": m["page_start"],
                    "data_source_type": data_source_type,
                    "file_name": clean_file_name(file),
                    "ingestion_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                print(f"Ingesting chunk {c['id']} into Pinecone...")
                ingest_to_pinecone([records[-1]],pinecone_index_name,pinecone_cv_namespace)
                print(f"Chunk {c['id']} ingested successfully.")
                print(f"Records in Pinecone namespace:{len(inspect_pinecone_records(pinecone_index_name,pinecone_cv_namespace))}")
                
    return records[0]
        # print(f"Extracted text from {file}: {page_text[:200]}...")  # Print the first 200 characters of the extracted text
        # payload.append(build_json_payload(page_text, file, data_source_type, rec_counter))
    
    # print("Ingesting data into Pinecone...")
    # response = ingest_to_pinecone(payload,pinecone_index_name,pinecone_api_key,pinecone_cv_namespace)
    # print(f"Response from Pinecone: {response}")
    
if __name__ == "__main__":
    print(main())