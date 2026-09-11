import os
import re
import json

PROCESSED_FOLDER = "data/processed"
CHUNKS_JSONL = "data/chunks/chunks.jsonl"

def parse_qa_pairs(text, section_title="General"):
    """Hybrid parser: handles Q: + A: pairs OR just Q: with answer in same block."""
    chunks = []
    
    # 1. TRY: Explicit Q: ... A: ... pairs (for courses_faqs)
    pattern_qa = r"Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|\Z)"
    matches = re.findall(pattern_qa, text, re.DOTALL | re.IGNORECASE)
    
    if matches:
        for q, a in matches:
            q = q.strip()
            a = a.strip()
            if q and a:
                chunks.append({
                    "text": f"Section: {section_title}\nQ: {q}\nA: {a}",
                    "metadata": {
                        "section": section_title,
                        "type": "qa_pair",
                        "question": q[:100]
                    }
                })
        return chunks

    # 2. FALLBACK: Sirf Q: hai, A: nahi (knowledge_base wali format)
    # Split by Q: and treat the entire block as content
    parts = re.split(r'Q:\s*', text)
    # parts[0] is header text before first Q, ignore it
    for part in parts[1:]:
        if part.strip():
            chunks.append({
                "text": f"Section: {section_title}\nQ: {part.strip()}",
                "metadata": {
                    "section": section_title,
                    "type": "qa_pair",
                    "question": part.strip()[:100]
                }
            })
    return chunks

def parse_course_table(text):
    """Extract course fee/duration tables WITHOUT requiring bold/heading."""
    chunks = []
    # Pattern: "Course Name (X months) ... Fee: Rs YYY"
    pattern = r"(.*?)\s*\((\d+)\s*months\).*?Fee:\s*Rs\s*([\d,]+)"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for course_name, duration, fee in matches:
        clean_fee = fee.replace(",", "")
        chunk_text = f"Course: {course_name.strip()}\nDuration: {duration} months\nFee: Rs {clean_fee}"
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "section": "Courses",
                "type": "course_fee",
                "course_name": course_name.strip()
            }
        })
    return chunks

def run_chunker():
    all_chunks = []
    
    # 1. Process Knowledge Base
    kb_path = os.path.join(PROCESSED_FOLDER, "WAPEXP_Chatbot_Knowledge_Base.md")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Split by sections (## headings) but handle if no ##
        sections = re.split(r"##\s+", text)
        if len(sections) == 1:
            # Agar koi heading nahi mili, toh poora text ek section hai
            sections = [text]
            title = "General Knowledge"
        else:
            title = "Default"
        
        for section in sections:
            if not section.strip():
                continue
            # Section title extract karo
            lines = section.split("\n")
            sec_title = lines[0].strip() if lines else "General"
            if len(sec_title) > 50:
                sec_title = sec_title[:50]
            
            chunks = parse_qa_pairs(section, sec_title)
            all_chunks.extend(chunks)
        
        print(f"✅ Knowledge Base: {len(all_chunks)} chunks extracted.")
    
    # 2. Process Courses & FAQs
    courses_path = os.path.join(PROCESSED_FOLDER, "WAPEXP_Courses_and_FAQs.md")
    if os.path.exists(courses_path):
        with open(courses_path, "r", encoding="utf-8") as f:
            course_text = f.read()
        
        # Pehle course fees table extract karo
        course_chunks = parse_course_table(course_text)
        all_chunks.extend(course_chunks)
        print(f"✅ Courses: {len(course_chunks)} course fee chunks extracted.")
        
        # Phir isi file mein FAQ section bhi hai (Q/A) — usko bhi parse karo
        faq_chunks = parse_qa_pairs(course_text, "FAQs from Courses")
        all_chunks.extend(faq_chunks)
        print(f"✅ FAQs: {len(faq_chunks)} FAQ chunks extracted.")
    
    # 3. Ensure chunks folder exists
    os.makedirs(os.path.dirname(CHUNKS_JSONL), exist_ok=True)
    
    # 4. Save to JSONL
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    
    print(f"🎉 TOTAL chunks created: {len(all_chunks)}")
    print(f"📁 Saved to: {CHUNKS_JSONL}")

if __name__ == "__main__":
    print("🚀 Starting Chunking Process (Hybrid Parser)...")
    run_chunker()
    print("✅ Chunking complete!")