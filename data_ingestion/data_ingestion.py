from importlib.resources import path

import pymupdf
import pinecone
import datetime as dt
import pathlib
import os
from dotenv import load_dotenv
load_dotenv()
import re
import sys

source_parent_dir = pathlib.Path(r'C:\Users\NanaYawDarko\Documents\Internal Projects\second-brain-DE\DataSources')
data_source_type = 'CVs'
cv_file_names = [path.name for path in source_parent_dir.joinpath(data_source_type).iterdir() if path.is_file()]
single_file = cv_file_names[0]  # For testing, you can change this to any file in the list

pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_index_name = 'cv-index'
pinecone_cv_namespace = 'cv-namespace'
pc = pinecone.Pinecone(api_key=pinecone_api_key)
dense_index = pc.Index(pinecone_index_name)
BATCH_SIZE = 90

payload = []

def clean_file_name(file_name):
    if "_" in file_name or "-" in file_name:
        return file_name.replace("_", " ").replace("-", " ")
    return file_name


def clean(t):
    t = re.sub(r'</?(sup|u)>', '', t)
    t = t.replace('**', '')
    t = re.sub(r'^#+\s*', '', t, flags=re.M)
    return t

def inspect_pinecone_records(index, ns):
    # Target the index
    # dense_index = pc.Index(index_name)

    # Fetch records from the namespace
    records = []
    for page in index.list(namespace=ns, limit=100):
        records.extend(page)
    return records

def delete_pinecone_records(index, ns):
    # Delete all records in the namespace
    index.delete(namespace=ns, delete_all=True)

def ingest_to_pinecone(payload,ns,index,batch_size=BATCH_SIZE):
    for i in range(0,len(payload),batch_size):
        batch = payload[i:i+batch_size]
        index.upsert_records(namespace=ns,records=batch)
        print(f"Upserted batch {i//batch_size + 1} of {len(payload)//batch_size + 1} into Pinecone.")

# build a main function to loop through the files in the cv_file_names list, extract text from each file, and build a JSON payload for each file. Then ingest the payload into Pinecone.

def main():
    records = []
    for rec_counter,file in enumerate([cv_file_names], start=1):
        for file in cv_file_names:
            print(f"\nProcessing file: {file}...")
            with pymupdf.open(source_parent_dir.joinpath(data_source_type).joinpath(file)) as doc:
                page_count = doc.page_count
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
                      
        ingest_to_pinecone(records,pinecone_cv_namespace, dense_index,batch_size=BATCH_SIZE)
        print(f"file {file} ingested successfully.")           
    print(f"Records in Pinecone namespace:{len(inspect_pinecone_records(dense_index,pinecone_cv_namespace))}")            
    return records[-5:]  # Return the last 5 records for inspection
       
    
if __name__ == "__main__":
    print(main())