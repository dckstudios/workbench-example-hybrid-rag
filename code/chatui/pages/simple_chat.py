# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Simple Chat Interface for End Users - Dell & NVIDIA RAG Demo"""

import gradio as gr
import subprocess
import time
from typing import List, Tuple, Generator

from chatui import chat_client

PATH = "/demo"
TITLE = "Dell & NVIDIA AI Assistant"

# Default configuration for RAG
DEFAULT_CONFIG = {
    "inference_mode": "cloud",
    "nvcf_model_id": "meta/llama3-70b-instruct",
    "local_model_id": "",
    "nim_model_ip": "",
    "nim_model_port": "",
    "nim_model_id": "",
    "temperature": 0.7,
    "top_p": 0.95,
    "freq_pen": 0,
    "pres_pen": 0,
    "num_tokens": 500,
    "use_knowledge_base": True,
}

# Custom CSS for clean, professional look
CUSTOM_CSS = """
/* Main container */
.gradio-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%) !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}

/* Header with logos */
#header-row {
    background: linear-gradient(90deg, #1a1a2e 0%, #0d1b2a 100%);
    padding: 20px 40px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

#logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 40px;
}

#title-text {
    text-align: center;
    color: #ffffff;
    font-size: 1.8rem;
    font-weight: 600;
    margin-top: 15px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

#subtitle-text {
    text-align: center;
    color: #a0a0a0;
    font-size: 1rem;
    margin-top: 5px;
}

/* Chat container */
#chat-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(118, 185, 0, 0.2);
}

/* Chatbot styling */
.chatbot {
    background: #fafafa !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 450px !important;
}

/* User messages - Dell Blue */
.chatbot .user {
    background: linear-gradient(135deg, #0076CE 0%, #0063B1 100%) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 14px 18px !important;
    margin: 8px 0 !important;
    box-shadow: 0 3px 10px rgba(0, 118, 206, 0.3) !important;
    color: #ffffff !important;
    font-weight: 500 !important;
}

/* Bot messages - NVIDIA Green */
.chatbot .bot {
    background: linear-gradient(135deg, #e8f5e0 0%, #d4edcc 100%) !important;
    border: 1px solid rgba(118, 185, 0, 0.2) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 14px 18px !important;
    margin: 8px 0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    color: #2d3748 !important;
}

/* Input textbox */
#msg-input textarea {
    background: #ffffff !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}

#msg-input textarea:focus {
    border-color: #76b900 !important;
    box-shadow: 0 0 0 3px rgba(118, 185, 0, 0.15) !important;
}

/* Send button */
#send-btn {
    background: linear-gradient(135deg, #76b900 0%, #8bc926 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(118, 185, 0, 0.35) !important;
    transition: all 0.3s ease !important;
}

#send-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(118, 185, 0, 0.45) !important;
}

/* Clear button */
#clear-btn {
    background: #ffffff !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 12px !important;
    color: #666666 !important;
    transition: all 0.3s ease !important;
}

#clear-btn:hover {
    border-color: #0076CE !important;
    color: #0076CE !important;
}

/* Footer */
#footer-text {
    text-align: center;
    color: #888888;
    font-size: 12px;
    margin-top: 20px;
}

/* Hide Gradio footer */
footer {
    display: none !important;
}

/* Status indicator */
#status-indicator {
    text-align: center;
    padding: 8px;
    border-radius: 8px;
    font-size: 13px;
    margin-bottom: 15px;
}

.status-ready {
    background: rgba(118, 185, 0, 0.1);
    color: #4d6721;
    border: 1px solid rgba(118, 185, 0, 0.3);
}

.status-loading {
    background: rgba(0, 118, 206, 0.1);
    color: #0063B1;
    border: 1px solid rgba(0, 118, 206, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
    #header-row {
        padding: 15px 20px;
    }
    #title-text {
        font-size: 1.4rem;
    }
}
"""

# SVG Logos
DELL_LOGO = """
<svg width="120" height="40" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="10" y="28" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#0076CE">DELL</text>
</svg>
"""

NVIDIA_LOGO = """
<svg width="140" height="40" viewBox="0 0 140 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <text x="10" y="28" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#76b900">NVIDIA</text>
</svg>
"""


def initialize_backend() -> bool:
    """Initialize the RAG backend if not already running."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        # Try to start the backend
        try:
            subprocess.Popen(
                ["/bin/bash", "/project/code/scripts/rag-consolidated.sh"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)
            return True
        except:
            return False


def build_page(client: chat_client.ChatClient) -> gr.Blocks:
    """Build the simple chat page for end users."""

    with gr.Blocks(title=TITLE, css=CUSTOM_CSS, theme=gr.themes.Soft()) as page:

        # Header with logos
        with gr.Row(elem_id="header-row"):
            gr.HTML(f"""
                <div id="logo-container">
                    {DELL_LOGO}
                    <span style="color: #666; font-size: 24px;">×</span>
                    {NVIDIA_LOGO}
                </div>
                <div id="title-text">AI Assistant</div>
                <div id="subtitle-text">Powered by RAG Technology</div>
            """)

        # Chat container
        with gr.Column(elem_id="chat-container"):

            # Status indicator
            status = gr.HTML(
                value='<div id="status-indicator" class="status-ready">✓ Ready to chat</div>',
                elem_id="status-box"
            )

            # Chatbot
            chatbot = gr.Chatbot(
                label="",
                show_label=False,
                elem_id="chatbot",
                height=450,
                avatar_images=(None, None),
            )

            # Input row
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your question here...",
                    show_label=False,
                    container=False,
                    elem_id="msg-input",
                    scale=4,
                    lines=1,
                )
                send_btn = gr.Button("Send", elem_id="send-btn", scale=1)
                clear_btn = gr.Button("Clear", elem_id="clear-btn", scale=1)

        # Footer
        gr.HTML('<div id="footer-text">Dell Technologies & NVIDIA - Enterprise AI Solutions</div>')

        # State
        backend_ready = gr.State(False)

        def check_backend():
            """Check if backend is ready."""
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=3)
                if response.status_code == 200:
                    return True, '<div id="status-indicator" class="status-ready">✓ Ready to chat</div>'
            except:
                pass
            return False, '<div id="status-indicator" class="status-loading">⏳ Connecting to AI backend...</div>'

        def respond(
            message: str,
            chat_history: List[Tuple[str, str]],
        ) -> Generator:
            """Generate a response to the user message."""

            if not message.strip():
                yield chat_history, ""
                return

            # Check backend
            try:
                import requests
                requests.get("http://localhost:8000/health", timeout=2)
            except:
                chat_history.append((message, "⚠️ The AI backend is not available. Please try again in a moment."))
                yield chat_history, ""
                return

            # Add user message
            chat_history.append((message, ""))
            yield chat_history, ""

            # Generate response with streaming
            try:
                response_text = ""
                chunk_count = 0

                for chunk in client.predict(
                    query=message,
                    mode=DEFAULT_CONFIG["inference_mode"],
                    local_model_id=DEFAULT_CONFIG["local_model_id"],
                    nvcf_model_id=DEFAULT_CONFIG["nvcf_model_id"],
                    nim_model_ip=DEFAULT_CONFIG["nim_model_ip"],
                    nim_model_port=DEFAULT_CONFIG["nim_model_port"],
                    nim_model_id=DEFAULT_CONFIG["nim_model_id"],
                    temp_slider=DEFAULT_CONFIG["temperature"],
                    top_p_slider=DEFAULT_CONFIG["top_p"],
                    freq_pen_slider=DEFAULT_CONFIG["freq_pen"],
                    pres_pen_slider=DEFAULT_CONFIG["pres_pen"],
                    use_knowledge_base=DEFAULT_CONFIG["use_knowledge_base"],
                    num_tokens=DEFAULT_CONFIG["num_tokens"],
                ):
                    # Skip the first chunk (TTFT metric)
                    if chunk_count == 0:
                        chunk_count += 1
                        continue

                    response_text += chunk
                    chat_history[-1] = (message, response_text)
                    yield chat_history, ""
                    chunk_count += 1

            except Exception as e:
                error_msg = f"⚠️ An error occurred: {str(e)}"
                chat_history[-1] = (message, error_msg)
                yield chat_history, ""

        def clear_chat():
            """Clear the chat history."""
            return [], ""

        # Event handlers
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        send_btn.click(respond, [msg, chatbot], [chatbot, msg])
        clear_btn.click(clear_chat, None, [chatbot, msg])

        # Check backend on load
        page.load(check_backend, None, [backend_ready, status])

    page.queue()
    return page
