import os
import re
from pypdf import PdfReader

# Folders ke paths define karo
RAW_FOLDER = "data/raw"
PROCESSED_FOLDER = "data/processed"

def clean_text(text):
    """PDF se nikalne wale text ko saaf karo (extra spaces aur random characters hatao)"""
    # Extra spaces ko single space mein badlo
    text = re.sub(r'\s+', ' ', text)
    # Agar koi weird Unicode characters hain toh unko hatao ya replace karo
    text = text.replace('\x00', '').replace('\ufffd', '')
    return text.strip()

def convert_pdfs_to_markdown():
    # Agar processed folder nahi hai toh bana do
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)
    
    # Raw folder mein jo bhi PDF files hain, unko loop karo
    for filename in os.listdir(RAW_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(RAW_FOLDER, filename)
            print(f"⏳ Processing: {filename} ...")
            
            # PDF reader object banao
            reader = PdfReader(pdf_path)
            full_text = ""
            
            # Har page ka text nikal kar jama karo
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n"
            
            # Clean karo
            clean_full_text = clean_text(full_text)
            
            # Output filename: .pdf ko .md mein badlo
            md_filename = filename.replace(".pdf", ".md")
            md_path = os.path.join(PROCESSED_FOLDER, md_filename)
            
            # Markdown file mein save karo
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(clean_full_text)
            
            print(f"✅ Saved: {md_path} (Total characters: {len(clean_full_text)})")

# Agar aap is file ko directly run karein toh yeh function chalega
if __name__ == "__main__":
    print("🚀 Starting PDF to Markdown Conversion...")
    convert_pdfs_to_markdown()
    print("🎉 All PDFs converted successfully!")