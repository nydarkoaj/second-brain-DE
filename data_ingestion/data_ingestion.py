import pymupdf
import pinecone
import datetime as dt
import pathlib
import os
from dotenv import load_dotenv
load_dotenv()

source_parent_dir = pathlib.Path(r'C:\Users\NanaYawDarko\Documents\Internal Projects\second-brain-DE\DataSources')
data_source_type = 'CVs'
cv_file_names = [path.name for path in source_parent_dir.joinpath(data_source_type).iterdir() if path.is_file()]


pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_index_name = 'cv-index'
pinecone_cv_namespace = 'cv-namespace'



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
    if "_" in file_name:
        return file_name.replace("_", " ")
    return file_name


def ingest_to_pinecone(payload,index_name,pinecone_api_key, ns):
    pc = pinecone.Pinecone(api_key=pinecone_api_key)
    # Target the index
    dense_index = pc.Index(index_name)

    # Upsert the records into a namespace
    dense_index.upsert_records(namespace=ns, records=payload)



def main():
    for rec_counter,file in enumerate(cv_file_names, start=1):
        print(f"Processing file: {file}...")
        doc = pymupdf.open(source_parent_dir.joinpath(data_source_type).joinpath(file))
        page = doc.load_page(0)
        page_text = page.get_text()
        print(f"Extracted text from {file}: {page_text[:100]}...")  # Print the first 100 characters of the extracted text
        payload.append(build_json_payload(page_text, file, data_source_type, rec_counter))
    
    print("Ingesting data into Pinecone...")
    response = ingest_to_pinecone(payload,pinecone_index_name,pinecone_api_key,pinecone_cv_namespace)
    print(f"Response from Pinecone: {response}")
    
if __name__ == "__main__":
    main ()