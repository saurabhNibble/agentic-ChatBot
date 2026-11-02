
import streamlit as st

from agentic_bot_back import chatbot, delete_chat_history
from rag_pipeline import add_uploaded_pdf
from thread_db import db

from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.types import Command


# ==========================================
# 1. STREAMLIT CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 My AI Chatbot")


# ==========================================
# 2. HOVER EFFECT FOR EDIT AND DELETE
# ==========================================

st.markdown("""
<style>
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:nth-child(2) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:nth-child(3) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="stColumn"]:nth-child(2) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="stColumn"]:nth-child(3) button {
    opacity: 0;
    transition: opacity 0.2s ease;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="column"]:nth-child(2) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="column"]:nth-child(3) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="stColumn"]:nth-child(2) button,
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="stColumn"]:nth-child(3) button {
    opacity: 1;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. INITIALIZE SESSION STATE
# ==========================================

if "active_chat_id" not in st.session_state:

    threads = db.get_all_threads()

    if threads:
        st.session_state.active_chat_id = threads[0][0]
    else:
        st.session_state.active_chat_id = db.create_thread("New Chat")


if "rename_chat_id" not in st.session_state:
    st.session_state.rename_chat_id = None


if "delete_chat_id" not in st.session_state:
    st.session_state.delete_chat_id = None


# ==========================================
# 4. CHAT ACTIONS
# ==========================================

def create_new_chat():

    chat_id = db.create_thread("New Chat")

    st.session_state.active_chat_id = chat_id
    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None


def switch_chat(chat_id):

    st.session_state.active_chat_id = chat_id
    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None


def rename_chat(chat_id, new_title):

    if new_title.strip():
        db.update_thread_title(chat_id, new_title.strip())

    st.session_state.rename_chat_id = None


def delete_chat(chat_id):

    delete_chat_history(chat_id)
    db.delete_thread(chat_id)

    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None

    remaining_threads = db.get_all_threads()

    if remaining_threads:

        if st.session_state.active_chat_id == chat_id:
            st.session_state.active_chat_id = remaining_threads[0][0]

    else:
        st.session_state.active_chat_id = db.create_thread("New Chat")


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("💬 My Conversations")

    st.button(
        "＋ New Chat",
        key="new_chat_button",
        on_click=create_new_chat,
        use_container_width=True
    )

    # ---------- PDF UPLOAD ----------

    st.divider()
    st.caption("DOCUMENTS")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader"
    )

    if uploaded_files and st.button(
        "Add to knowledge base",
        key="index_pdfs_button",
        use_container_width=True
    ):

        for f in uploaded_files:

            with st.spinner(f"Indexing {f.name}..."):

                msg = add_uploaded_pdf(
                    f.getvalue(),
                    f.name
                )

            if msg.startswith("Successfully"):
                st.success(f"{f.name}: {msg}")
            else:
                st.warning(f"{f.name}: {msg}")

    # ---------- CHAT LIST ----------

    st.divider()
    st.caption("RECENTS")

    threads = db.get_all_threads()

    for chat_id, chat_name, created_at in threads:

        is_active = chat_id == st.session_state.active_chat_id

        col1, col2, col3 = st.columns([5, 1, 1])

        with col1:

            st.button(
                chat_name,
                key=f"chat_{chat_id}",
                on_click=switch_chat,
                args=(chat_id,),
                use_container_width=True,
                type="primary" if is_active else "secondary"
            )

        with col2:

            if st.button(
                "✏️",
                key=f"rename_{chat_id}",
                help="Rename chat"
            ):

                st.session_state.rename_chat_id = chat_id
                st.session_state.delete_chat_id = None

        with col3:

            if st.button(
                "🗑️",
                key=f"delete_{chat_id}",
                help="Delete chat"
            ):

                st.session_state.delete_chat_id = chat_id
                st.session_state.rename_chat_id = None

        # ---------- RENAME FORM ----------

        if st.session_state.rename_chat_id == chat_id:

            with st.form(key=f"rename_form_{chat_id}"):

                new_title = st.text_input(
                    "New chat name",
                    value=chat_name
                )

                save, cancel = st.columns(2)

                with save:
                    submitted = st.form_submit_button("Save")

                with cancel:
                    cancelled = st.form_submit_button("Cancel")

                if submitted:
                    rename_chat(chat_id, new_title)
                    st.rerun()

                if cancelled:
                    st.session_state.rename_chat_id = None
                    st.rerun()

        # ---------- DELETE CONFIRMATION ----------

        if st.session_state.delete_chat_id == chat_id:

            st.warning(f"Delete '{chat_name}'?")

            confirm, cancel = st.columns(2)

            with confirm:

                if st.button(
                    "Confirm",
                    key=f"confirm_delete_{chat_id}"
                ):

                    delete_chat(chat_id)
                    st.rerun()

            with cancel:

                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{chat_id}"
                ):

                    st.session_state.delete_chat_id = None
                    st.rerun()


# ==========================================
# 6. GET ACTIVE CHAT
# ==========================================

active_chat_id = st.session_state.active_chat_id

config = {
    "configurable": {
        "thread_id": active_chat_id
    },
    "metadata": {
        "chat_id": active_chat_id,
        "application": "agentic-chatbot"
    },
    "run_name": "Chatbot Conversation"
}


# ==========================================
# 7. LOAD GRAPH STATE
# ==========================================

state = chatbot.get_state(config)

messages = (
    state.values.get("messages", [])
    if state and state.values
    else []
)


# ==========================================
# 8. DISPLAY CHAT HISTORY
# ==========================================

for message in messages:

    if message.type == "human":
        role = "user"

    elif message.type == "ai":
        role = "assistant"

    else:
        continue

    # Skip tool calls without text
    if not message.content:
        continue

    # Only display textual messages
    if not isinstance(message.content, str):
        continue

    with st.chat_message(role):
        st.write(message.content)


# ==========================================
# 9. STREAMING RESPONSE
# ==========================================

def generate_response(graph_input):

    for chunk, metadata in chatbot.stream(
        graph_input,
        config=config,
        stream_mode="messages"
    ):

        if (
            isinstance(chunk, AIMessageChunk)
            and metadata.get("langgraph_node") == "chat_node"
            and isinstance(chunk.content, str)
            and chunk.content
        ):

            yield chunk.content


# ==========================================
# 10. CHECK FOR PENDING INTERRUPTS
# ==========================================

state = chatbot.get_state(config)

pending_interrupts = []

if state and state.tasks:

    for task in state.tasks:

        for intr in task.interrupts:
            pending_interrupts.append(intr)


# ==========================================
# 11. HUMAN-IN-THE-LOOP APPROVAL UI
# ==========================================

if pending_interrupts:

    st.divider()

    st.subheader("🧑 Human Approval Required")

    interrupt_data = pending_interrupts[0].value

    st.warning(interrupt_data["message"])

    st.write("The chatbot wants to execute:")

    for tool in interrupt_data.get("tool_calls", []):

        st.markdown(f"**Tool:** `{tool['name']}`")

        st.markdown("**Arguments:**")

        st.json(tool["args"])

    st.info(
        "Review the requested tool execution before continuing."
    )

    approve_col, reject_col = st.columns(2)

    # ---------- APPROVE ----------

    with approve_col:

        if st.button(
            "✅ Approve",
            key=f"approve_{active_chat_id}",
            use_container_width=True
        ):

            with st.chat_message("assistant"):

                with st.spinner("Executing approved tool..."):

                    st.write_stream(
                        generate_response(
                            Command(resume="approve")
                        )
                    )

            st.rerun()

    # ---------- REJECT ----------

    with reject_col:

        if st.button(
            "❌ Reject",
            key=f"reject_{active_chat_id}",
            use_container_width=True
        ):

            with st.chat_message("assistant"):

                with st.spinner("Processing rejection..."):

                    st.write_stream(
                        generate_response(
                            Command(resume="reject")
                        )
                    )

            st.rerun()


# ==========================================
# 12. USER INPUT
# ==========================================

user_input = st.chat_input(
    "Ask something...",
    disabled=bool(pending_interrupts)
)


if user_input and not pending_interrupts:

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # ---------- AUTO TITLE ----------

    current_chat = next(
        (
            t for t in db.get_all_threads()
            if t[0] == active_chat_id
        ),
        None
    )

    if current_chat and current_chat[1] == "New Chat":

        db.update_thread_title(
            active_chat_id,
            user_input[:30]
        )

    # ---------- GENERATE RESPONSE ----------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            st.write_stream(
                generate_response(
                    {
                        "messages": [
                            HumanMessage(content=user_input)
                        ]
                    }
                )
            )

    # Reload graph state and display updated conversation
    st.rerun()
