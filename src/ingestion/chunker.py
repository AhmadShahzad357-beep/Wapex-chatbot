import os
import re
import json

PROCESSED_FOLDER = "data/processed"
CHUNKS_JSONL = "data/chunks/chunks.jsonl"

def parse_qa_pairs(text, section_title="General"):
    chunks = []
    pattern_qa = r"Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|\Z)"
    matches = re.findall(pattern_qa, text, re.DOTALL | re.IGNORECASE)

    if matches:
        for q, a in matches:
            q = q.strip()
            a = a.strip()
            if q and a:
                chunks.append({
                    "text": f"Section: {section_title}\nQ: {q}\nA: {a}",
                    "metadata": {"section": section_title, "type": "qa_pair", "question": q[:100]}
                })
        return chunks

    parts = re.split(r'Q:\s*', text)
    for part in parts[1:]:
        if part.strip():
            chunks.append({
                "text": f"Section: {section_title}\nQ: {part.strip()}",
                "metadata": {"section": section_title, "type": "qa_pair", "question": part.strip()[:100]}
            })
    return chunks

def parse_course_table(text):
    chunks = []
    lines = text.split("\n")
    header_re = re.compile(r"^(.+?)\s*\((\d+\s*months?|-)\)\s*$", re.IGNORECASE)
    stop_markers = ("contact number:", "section 2", "section 3")

    headers = []
    for i, line in enumerate(lines):
        m = header_re.match(line.strip())
        if m:
            headers.append((i, m.group(1).strip(), m.group(2).strip()))

    for idx, (line_no, name, duration_raw) in enumerate(headers):
        end_line = len(lines)
        for j in range(line_no + 1, len(lines)):
            if any(marker in lines[j].strip().lower() for marker in stop_markers):
                end_line = j
                break
        if idx + 1 < len(headers):
            end_line = min(end_line, headers[idx + 1][0])

        body_lines = [l.strip() for l in lines[line_no + 1:end_line] if l.strip()]
        if not body_lines:
            continue

        fee_line = body_lines[0]
        curriculum_lines = body_lines[1:]
        cleaned_curriculum = []
        for cl in curriculum_lines:
            cl = re.sub(r"^[l\u2022]\s*", "", cl).strip()
            if cl:
                cleaned_curriculum.append(cl)

        duration_text = "flexible / no fixed duration" if duration_raw == "-" else duration_raw
        chunk_text = f"Course: {name}\nDuration: {duration_text}\n{fee_line}"
        if cleaned_curriculum:
            chunk_text += "\nCurriculum:\n- " + "\n- ".join(cleaned_curriculum)

        chunks.append({
            "text": chunk_text,
            "metadata": {"section": "Courses", "type": "course_fee", "course_name": name}
        })

    return chunks

def run_chunker():
    all_chunks = []

    kb_path = os.path.join(PROCESSED_FOLDER, "WAPEXP_Chatbot_Knowledge_Base.md")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            text = f.read()
        sections = re.split(r"##\s+", text)
        if len(sections) == 1:
            sections = [text]
        for section in sections:
            if not section.strip():
                continue
            lines = section.split("\n")
            sec_title = lines[0].strip() if lines else "General"
            if len(sec_title) > 50:
                sec_title = sec_title[:50]
            chunks = parse_qa_pairs(section, sec_title)
            all_chunks.extend(chunks)
        print(f"Knowledge Base: {len(all_chunks)} chunks extracted.")

    courses_path = os.path.join(PROCESSED_FOLDER, "WAPEXP_Courses_and_FAQs.md")
    if os.path.exists(courses_path):
        with open(courses_path, "r", encoding="utf-8") as f:
            course_text = f.read()
        course_chunks = parse_course_table(course_text)
        all_chunks.extend(course_chunks)
        print(f"Courses: {len(course_chunks)} course fee chunks extracted.")
        faq_chunks = parse_qa_pairs(course_text, "FAQs from Courses")
        all_chunks.extend(faq_chunks)
        print(f"FAQs: {len(faq_chunks)} FAQ chunks extracted.")

    os.makedirs(os.path.dirname(CHUNKS_JSONL), exist_ok=True)
    with open(CHUNKS_JSONL, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"TOTAL chunks created: {len(all_chunks)}")
    print(f"Saved to: {CHUNKS_JSONL}")

if __name__ == "__main__":
    print("Starting Chunking Process (Hybrid Parser)...")
    run_chunker()
    print("Chunking complete!")
