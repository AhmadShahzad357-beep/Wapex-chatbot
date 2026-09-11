import gradio as gr
import uuid
from src.pipeline import run_pipeline


def chat_response(message, history, session_id):
    # session_id gr.State se aata hai — pehle har message pe naya uuid ban raha
    # tha, isliye memory kabhi kaam nahi karti thi (har message = naya "user").
    reply = run_pipeline(session_id, message)
    return reply


with gr.Blocks(theme="soft") as demo:
    session_id = gr.State(lambda: str(uuid.uuid4()))  # ek hi id poori session ke liye
    gr.ChatInterface(
        fn=chat_response,
        additional_inputs=[session_id],
        title="🤖 WAPEXP Official Chatbot",
        description="WAPEXP courses, fees, location, aur policies ke baare mein poochiye.",
    )

if __name__ == "__main__":
    demo.launch(share=True)