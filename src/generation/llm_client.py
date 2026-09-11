import os
from openai import OpenAI
from config.settings import Config

def generate_answer(user_query: str, context: str, memory_context: str = "") -> str:
    """
    Sirf context ke andar se jawab banayega. 
    Agar context mein nahi hai toh "I don't know" bolega.
    """

    # 🔥 Groq OpenAI-compatible endpoint
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),   # .env mein GROQ_API_KEY daalo
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = """
You are WAPEXP's official assistant. Answer ONLY using the provided context below.
- If the answer is not in the context, say: "Iska specific jawab mere paas available nahi hai, please contact our team at 0321-7658485."
- NEVER use your own general knowledge to fill gaps.
- NEVER guess numbers, fees, or dates not present in context.
- Quote exact figures from context (fees, phone numbers, timings) exactly as given.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Previous conversation: {memory_context}\n\nRetrieved Context:\n{context}\n\nQuestion: {user_query}"}
    ]

    try:
        # 🔥 New OpenAI client syntax (v1.0+)
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,  # .env mein "openai/gpt-oss-120b" (Groq model) set karna
            messages=messages,
            temperature=0.0,
            max_tokens=900
        )
        return response.choices[0].message.content

    except Exception as e:
        # 🔥 DEBUG: asli error ab terminal mein bhi print hoga, taake pata chale
        # ke API key, model name, ya network mein se kya masla hai
        print(f"❌ LLM CALL FAILED: {type(e).__name__}: {e}")
        return f"⚠️ Error generating response: {str(e)}"