
import streamlit as st
from agentic_bot_back import chatbot
from langchain_core.messages import HumanMessage
import uuid

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")

st.title("🤖 My AI Chatbot")

# Initialize conversation ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}

# Display previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Function to stream LangGraph response
def generate_response(user_input):

    for message_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="messages"
    ):

        # Extract text from the message chunk
        if isinstance(message_chunk.content, str):
            if message_chunk.content:
                yield message_chunk.content


# Get user input
user_input = st.chat_input("Ask something...")

if user_input:

    # Display user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # Display streaming assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):
            answer = st.write_stream(
                generate_response(user_input)
            )

    # Save completed response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })
