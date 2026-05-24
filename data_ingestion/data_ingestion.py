import pymupdf
import datetime as dt
import pathlib
import time

source_parent_dir = pathlib.Path(r'C:\Users\NanaYawDarko\Documents\Internal Projects\second-brain-DE\DataSources')
data_source_type = 'CVs'
cv_file_names = [path.name for path in source_parent_dir.joinpath(data_source_type).iterdir() if path.is_file()]
clean_file_names = [file_name.replace("_", " ") if "_" in file_name else file_name for file_name in cv_file_names]


metadata = {
    "text": '',
    "data_source_type": '',
    "file_name": '',
    "ingestion_time": ''
}

payload = []


def build_json_payload (text,metadata,file,data_source_type): 
    metadata['text'] = text
    metadata ['data_source_type'] = data_source_type
    metadata['file_name'] = file
    metadata['ingestion_time'] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return    

def main():
    for file in cv_file_names:
        print(f"Processing file: {file}...")
        doc = pymupdf.open(source_parent_dir.joinpath(data_source_type).joinpath(file))
        page = doc.load_page(0)
        page_text = page.get_text()
        print(f"Extracted text from {file}: {page_text[:100]}...")  # Print the first 100 characters of the extracted text
        build_json_payload(page_text,metadata,file,data_source_type)
        payload.append(metadata)
    time.sleep(60)
    print(payload)
    
if __name__ == "__main__":
    main ()