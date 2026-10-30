
import streamlit as st
import uuid

from agentic_bot_back import chatbot
from langchain_core.messages import HumanMessage


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 My AI Chatbot")


# ==========================================
# 2. INITIALIZE SESSION STATE
# ==========================================

if "chats" not in st.session_state:

    chat_id = str(uuid.uuid4())

    st.session_state.chats = {
        chat_id: {
            "title": "New Chat",
            "messages": []
        }
    }

    st.session_state.active_chat_id = chat_id


# ==========================================
# 3. CREATE NEW CHAT
# ==========================================

def create_new_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.active_chat_id = chat_id


# ==========================================
# 4. SWITCH BETWEEN CHATS
# ==========================================

def switch_chat(chat_id):

    st.session_state.active_chat_id = chat_id


# ==========================================
# 5. SIDEBAR - CHATGPT STYLE HISTORY
# ==========================================

with st.sidebar:

    st.title("💬 My Conversations")

    # New Chat button
    st.button(
        "＋ New Chat",
        key="new_chat_button",
        on_click=create_new_chat,
        use_container_width=True
    )

    st.divider()

    st.caption("RECENTS")

    # Display conversations (latest first)
    chat_items = list(st.session_state.chats.items())

    for chat_id, chat in reversed(chat_items):

        is_active = (
            chat_id == st.session_state.active_chat_id
        )

        st.button(
            chat["title"],
            key=f"chat_{chat_id}",
            on_click=switch_chat,
            args=(chat_id,),
            use_container_width=True,
            type="primary" if is_active else "secondary"
        )


# ==========================================
# 6. GET ACTIVE CONVERSATION
# ==========================================

active_chat_id = st.session_state.active_chat_id

current_chat = st.session_state.chats[active_chat_id]


# LangGraph configuration
config = {
    "configurable": {
        "thread_id": active_chat_id
    }
}


# ==========================================
# 7. DISPLAY PREVIOUS CHAT MESSAGES
# ==========================================

for message in current_chat["messages"]:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# ==========================================
# 8. STREAM LANGGRAPH RESPONSE
# ==========================================

def generate_response(user_input):

    for message_chunk, metadata in chatbot.stream(

        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },

        config=config,

        stream_mode="messages"
    ):

        if isinstance(message_chunk.content, str):

            if message_chunk.content:

                yield message_chunk.content


# ==========================================
# 9. GET USER INPUT
# ==========================================

user_input = st.chat_input("Ask something...")


# ==========================================
# 10. PROCESS USER MESSAGE
# ==========================================

if user_input:

    # Save user message
    current_chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    # Generate title from first question
    if current_chat["title"] == "New Chat":

        current_chat["title"] = user_input[:30]

    # Display user message
    with st.chat_message("user"):

        st.write(user_input)


    # Generate and stream AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = st.write_stream(
                generate_response(user_input)
            )


    # Save assistant response
    current_chat["messages"].append({
        "role": "assistant",
        "content": answer
    })
