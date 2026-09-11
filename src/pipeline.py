from src.intents.intent_detector import detect_intent
from src.intents.handlers.location_handler import get_location_reply
from src.intents.handlers.contact_handler import get_contact_reply
from src.memory.session_memory import get_context, add_to_memory
from src.retrieval.hybrid_search import hybrid_search
from src.generation.llm_client import generate_answer
from src.security.input_sanitizer import sanitize_input
from src.security.output_validator import validate_output
from src.security.rate_limiter import is_rate_limited
from config.settings import Config

def run_pipeline(user_id: str, user_query: str):
    # 1. Rate Limit
    if is_rate_limited(user_id):
        return "⚠️ Too many requests. Please wait a minute."
    
    # 2. Input Sanitization
    clean_query = sanitize_input(user_query)
    if not clean_query:
        return "⚠️ Invalid input."
    
    # 3. Intent Detection (LLM Bypass Zone)
    intent = detect_intent(clean_query)
    if intent == "location":
        return get_location_reply()
    if intent == "contact":
        return get_contact_reply()
    
    # 4. Memory
    memory_context = get_context(user_id)
    
    # 5. Retrieval (Hybrid)
    retrieved_chunks = hybrid_search(clean_query)
    if not retrieved_chunks:
        return "Is sawal ka jawab meri knowledge base mein nahi hai. Visit wapex.com"
    
    context_text = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])
    
    # 6. LLM Generation
    bot_reply = generate_answer(clean_query, context_text, memory_context)
    
    # 7. Output Validation (Grounding Check)
    if not validate_output(bot_reply, context_text):
        return "⚠️ I couldn't generate a reliable answer. Please contact support."
    
    # 8. Save to Memory
    add_to_memory(user_id, clean_query, bot_reply)
    
    return bot_reply