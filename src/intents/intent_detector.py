import re

def detect_intent(query: str) -> str:
    if not query:
        return "none"
    text = query.lower()
    # Location: specific phrases
    if re.search(r'\b(?:address|location|map|office (?:address|location)|where is|kahan (?:ho|hain)|pata kya)\b', text):
        return "location"
    # Contact: specific phrases, avoid single word "number"
    if re.search(r'\b(?:phone number|contact (?:number|info)|whatsapp (?:number|)|email address|call (?:us|me)|raabta karo|rabta karen)\b', text):
        return "contact"
    return "none"
