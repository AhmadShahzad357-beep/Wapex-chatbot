import os
from openai import OpenAI
from config.settings import Config

def generate_answer(user_query: str, context: str, memory_context: str = "") -> str:
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = """
You are WAPEXP's official assistant. Answer ONLY using the provided context below.
- If the answer is not in the context, say: "Iska specific jawab mere paas available nahi hai, please contact our team at 0321-7658485."
- NEVER use your own general knowledge to fill gaps.
- NEVER guess numbers, fees, or dates not present in context.
- Quote exact figures from context (fees, phone numbers, timings) exactly as given.
- Agar user ka sawal kisi bhi retrieved chunk se match karta hai - chahe sawal us chunk ka sirf ek chhota sa hissa (jaise sirf "fee" ya sirf "duration") hi kyun na pooch raha ho - to us poori matching entry ka MUKAMMAL jawab do (fee + duration + discount + poora curriculum/policy jo bhi context mein us entry ke liye maujood hai). Jawab ko chota mat karo ya sirf ek line mat do jab context mein us se zyada detail maujood ho.
- Jawab bilkul context jitna complete hona chahiye - na usse chota, na usse bada.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Previous conversation: {memory_context}\n\nRetrieved Context:\n{context}\n\nQuestion: {user_query}"}
    ]

    try:
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=900
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM CALL FAILED: {type(e).__name__}: {e}")
        return f"Error generating response: {str(e)}"
