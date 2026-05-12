import pymupdf

source_parent_dir = r'C:\Users\NanaYawDarko\Documents\Internal Projects\second-brain-DE\DataSources'


doc = pymupdf.open(f"{source_parent_dir}\CVs\YAW ADJEI DARKO CV.pdf")
page = doc.load_page(0)
page_text = page.get_text().encode("utf8")

print(page_text)
    