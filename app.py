
# # ============================================================
# # PREVIOUS IMPLEMENTATION
# # ============================================================
# #
# # This implementation used st.session_state to store:
# # 1. Chat IDs
# # 2. Chat titles
# # 3. Conversation messages
# #
# # Problem:
# # Conversation data was stored in Streamlit session memory.
# # It was not guaranteed to survive session loss or app restart.
# #
# # import streamlit as st
# # import uuid
# #
# # from agentic_bot_back import chatbot
# # from langchain_core.messages import HumanMessage
# #
# # st.set_page_config(
# #     page_title="AI Chatbot",
# #     page_icon="🤖",
# #     layout="wide"
# # )
# #
# # st.title("🤖 My AI Chatbot")
# #
# # if "chats" not in st.session_state:
# #
# #     chat_id = str(uuid.uuid4())
# #
# #     st.session_state.chats = {
# #         chat_id: {
# #             "title": "New Chat",
# #             "messages": []
# #         }
# #     }
# #
# #     st.session_state.active_chat_id = chat_id
# #
# # def create_new_chat():
# #
# #     chat_id = str(uuid.uuid4())
# #
# #     st.session_state.chats[chat_id] = {
# #         "title": "New Chat",
# #         "messages": []
# #     }
# #
# #     st.session_state.active_chat_id = chat_id
# #
# # def switch_chat(chat_id):
# #
# #     st.session_state.active_chat_id = chat_id
# #
# # with st.sidebar:
# #
# #     st.title("💬 My Conversations")
# #
# #     st.button(
# #         "＋ New Chat",
# #         key="new_chat_button",
# #         on_click=create_new_chat,
# #         use_container_width=True
# #     )
# #
# #     st.divider()
# #     st.caption("RECENTS")
# #
# #     chat_items = list(st.session_state.chats.items())
# #
# #     for chat_id, chat in reversed(chat_items):
# #
# #         is_active = (
# #             chat_id == st.session_state.active_chat_id
# #         )
# #
# #         st.button(
# #             chat["title"],
# #             key=f"chat_{chat_id}",
# #             on_click=switch_chat,
# #             args=(chat_id,),
# #             use_container_width=True,
# #             type="primary" if is_active else "secondary"
# #         )
# #
# # active_chat_id = st.session_state.active_chat_id
# #
# # current_chat = st.session_state.chats[active_chat_id]
# #
# # config = {
# #     "configurable": {
# #         "thread_id": active_chat_id
# #     }
# # }
# #
# # for message in current_chat["messages"]:
# #
# #     with st.chat_message(message["role"]):
# #         st.write(message["content"])
# #
# # def generate_response(user_input):
# #
# #     for message_chunk, metadata in chatbot.stream(
# #
# #         {
# #             "messages": [
# #                 HumanMessage(content=user_input)
# #             ]
# #         },
# #
# #         config=config,
# #         stream_mode="messages"
# #
# #     ):
# #
# #         if isinstance(message_chunk.content, str):
# #
# #             if message_chunk.content:
# #                 yield message_chunk.content
# #
# # user_input = st.chat_input("Ask something...")
# #
# # if user_input:
# #
# #     current_chat["messages"].append({
# #         "role": "user",
# #         "content": user_input
# #     })
# #
# #     if current_chat["title"] == "New Chat":
# #         current_chat["title"] = user_input[:30]
# #
# #     with st.chat_message("user"):
# #         st.write(user_input)
# #
# #     with st.chat_message("assistant"):
# #
# #         with st.spinner("Thinking..."):
# #
# #             answer = st.write_stream(
# #                 generate_response(user_input)
# #             )
# #
# #     current_chat["messages"].append({
# #         "role": "assistant",
# #         "content": answer
# #     })


# # ============================================================
# # NEW IMPLEMENTATION - PERMANENT THREAD MEMORY
# # ============================================================

# import streamlit as st

# from agentic_bot_back import chatbot, delete_chat_history
# from thread_db import db
# from langchain_core.messages import HumanMessage


# # ============================================================
# # 1. PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="AI Chatbot",
#     page_icon="🤖",
#     layout="wide"
# )

# st.title("🤖 My AI Chatbot")


# # ============================================================
# # 2. INITIALIZE THREAD DATABASE
# # ============================================================

# # Get all previously saved conversations from SQLite

# threads = db.get_all_threads()


# # If database has no conversations, create the first one

# if not threads:

#     db.create_thread("New Chat")

#     threads = db.get_all_threads()

# if "rename_chat_id" not in st.session_state:
#     st.session_state.rename_chat_id = None

# if "delete_chat_id" not in st.session_state:
#     st.session_state.delete_chat_id = None
# # ============================================================
# # 3. INITIALIZE ACTIVE CHAT
# # ============================================================

# # Session state now stores only the currently selected thread ID.
# # Actual conversation messages are retrieved from LangGraph.

# if "active_chat_id" not in st.session_state:

#     st.session_state.active_chat_id = threads[0][0]


# # Check whether selected thread still exists

# thread_ids = [thread[0] for thread in threads]

# if st.session_state.active_chat_id not in thread_ids:

#     st.session_state.active_chat_id = threads[0][0]


# # ============================================================
# # 4. CREATE NEW CHAT
# # ============================================================

# def create_new_chat():

#     # Create a permanent thread record in SQLite

#     chat_id = db.create_thread("New Chat")

#     # Set newly created thread as active

#     st.session_state.active_chat_id = chat_id


# # ============================================================
# # 5. SWITCH BETWEEN CHATS
# # ============================================================

# def switch_chat(chat_id):

#     st.session_state.active_chat_id = chat_id

# # ==========================================
# # UPDATE CHAT TITLE
# # ==========================================

# def rename_chat(chat_id, new_title):

#     if new_title.strip():

#         db.update_thread_title(
#             chat_id,
#             new_title.strip()
#         )

#     st.session_state.rename_chat_id = None


# # ==========================================
# # DELETE CHAT
# # ==========================================

# def delete_chat(chat_id):

#     # Delete actual LangGraph conversation history
#     delete_chat_history(chat_id)

#     # Delete thread metadata
#     db.delete_thread(chat_id)

#     # If deleted chat was active, select another chat
#     if st.session_state.active_chat_id == chat_id:

#         remaining_threads = db.get_all_threads()

#         if remaining_threads:

#             st.session_state.active_chat_id = remaining_threads[0][0]

#         else:

#             new_chat_id = db.create_thread()

#             st.session_state.active_chat_id = new_chat_id

#     st.session_state.delete_chat_id = None


# # ==========================================
# # SIDEBAR - CHAT HISTORY
# # ==========================================

# with st.sidebar:

#     st.title("💬 My Conversations")

#     # Create new chat
#     st.button(
#         "＋ New Chat",
#         key="new_chat_button",
#         on_click=create_new_chat,
#         use_container_width=True
#     )

#     st.divider()

#     st.caption("RECENTS")

#     threads = db.get_all_threads()

#     for chat_id, chat_name, created_at in threads:

#         is_active = (
#             chat_id == st.session_state.active_chat_id
#         )

#         # Display chat title and action buttons
#         col1, col2, col3 = st.columns([5, 1, 1])

#         with col1:

#             st.button(
#                 chat_name,
#                 key=f"chat_{chat_id}",
#                 on_click=switch_chat,
#                 args=(chat_id,),
#                 use_container_width=True,
#                 type="primary" if is_active else "secondary"
#             )

#         with col2:

#             if st.button("✏️", key=f"rename_{chat_id}", help="Rename chat"):
#                 st.session_state.rename_chat_id = chat_id

#         with col3:

#             if st.button(
#                 "🗑️",
#                 key=f"delete_{chat_id}",
#                 help="Delete chat"
#             ):

#                 st.session_state.delete_chat_id = chat_id

#         # Rename interface
#         if st.session_state.get("rename_chat_id") == chat_id:

#             with st.form(key=f"rename_form_{chat_id}"):

#                 new_title = st.text_input(
#                     "New chat name",
#                     value=chat_name
#                 )

#                 save, cancel = st.columns(2)

#                 with save:

#                     submitted = st.form_submit_button("Save")

#                 with cancel:

#                     cancelled = st.form_submit_button("Cancel")

#                 if submitted:

#                     rename_chat(chat_id, new_title)

#                     st.rerun()

#                 if cancelled:

#                     st.session_state.rename_chat_id = None

#                     st.rerun()

#         # Delete confirmation
#         if st.session_state.get("delete_chat_id") == chat_id:

#             st.warning(f"Delete '{chat_name}'?")

#             confirm, cancel = st.columns(2)

#             with confirm:

#                 if st.button(
#                     "Confirm",
#                     key=f"confirm_delete_{chat_id}"
#                 ):

#                     delete_chat(chat_id)

#                     st.rerun()

#             with cancel:

#                 if st.button(
#                     "Cancel",
#                     key=f"cancel_delete_{chat_id}"
#                 ):

#                     st.session_state.delete_chat_id = None

#                     st.rerun()


# # ============================================================
# # 7. GET ACTIVE THREAD
# # ============================================================

# active_chat_id = st.session_state.active_chat_id

# # Every thread gets its own LangGraph checkpoint history

# config = {
#     "configurable": {
#         "thread_id": active_chat_id
#     }
# }


# # ============================================================
# # 8. RETRIEVE PREVIOUS MESSAGES FROM LANGGRAPH
# # ============================================================

# # Get the saved graph state for this particular thread

# state = chatbot.get_state(config)

# messages = state.values.get("messages", [])


# # Display previous conversation messages

# for message in messages:

#     if message.type == "human":

#         role = "user"

#     elif message.type == "ai":

#         role = "assistant"

#     else:

#         continue

#     # Display only normal text messages

#     if isinstance(message.content, str):

#         with st.chat_message(role):

#             st.write(message.content)


# # ============================================================
# # 9. STREAM LANGGRAPH RESPONSE
# # ============================================================

# def generate_response(user_input):

#     for message_chunk, metadata in chatbot.stream(

#         {
#             "messages": [
#                 HumanMessage(content=user_input)
#             ]
#         },

#         config=config,

#         stream_mode="messages"

#     ):

#         if isinstance(message_chunk.content, str):

#             if message_chunk.content:

#                 yield message_chunk.content


# # ============================================================
# # 10. GET USER INPUT
# # ============================================================

# user_input = st.chat_input("Ask something...")


# # ============================================================
# # 11. PROCESS USER MESSAGE
# # ============================================================

# if user_input:

#     # Update title using the first user question

#     current_threads = db.get_all_threads()

#     current_thread = next(
#         (
#             thread for thread in current_threads
#             if thread[0] == active_chat_id
#         ),
#         None
#     )

#     if current_thread and current_thread[1] == "New Chat":

#         db.update_thread_title(
#             active_chat_id,
#             user_input[:30]
#         )

#     # Display user message

#     with st.chat_message("user"):

#         st.write(user_input)

#     # Generate and stream AI response

#     with st.chat_message("assistant"):

#         with st.spinner("Thinking..."):

#             answer = st.write_stream(
#                 generate_response(user_input)
#             )

#     # IMPORTANT:
#     # No need to append messages manually.
#     # LangGraph's checkpointer saves the updated messages.

#     st.rerun()



import streamlit as st

from agentic_bot_back import chatbot, delete_chat_history
from thread_db import db
from langchain_core.messages import HumanMessage


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

/* Hide edit and delete buttons by default */
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:nth-child(2) button,
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]
div[data-testid="column"]:nth-child(3) button {
    opacity: 0;
    transition: opacity 0.2s ease;
}

/* Show buttons when hovering over a chat row */
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="column"]:nth-child(2) button,
div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover
div[data-testid="column"]:nth-child(3) button {
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
        chat_id = db.create_thread()
        st.session_state.active_chat_id = chat_id


if "rename_chat_id" not in st.session_state:
    st.session_state.rename_chat_id = None

if "delete_chat_id" not in st.session_state:
    st.session_state.delete_chat_id = None


# ==========================================
# 4. CREATE NEW CHAT
# ==========================================

def create_new_chat():

    chat_id = db.create_thread("New Chat")

    st.session_state.active_chat_id = chat_id

    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None


# ==========================================
# 5. SWITCH CHAT
# ==========================================

def switch_chat(chat_id):

    st.session_state.active_chat_id = chat_id

    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None


# ==========================================
# 6. RENAME CHAT
# ==========================================

def rename_chat(chat_id, new_title):

    if new_title.strip():

        db.update_thread_title(
            chat_id,
            new_title.strip()
        )

    st.session_state.rename_chat_id = None


# ==========================================
# 7. DELETE CHAT
# ==========================================

def delete_chat(chat_id):

    # Delete LangGraph conversation checkpoints
    delete_chat_history(chat_id)

    # Delete thread metadata
    db.delete_thread(chat_id)

    # Reset rename and delete states
    st.session_state.rename_chat_id = None
    st.session_state.delete_chat_id = None

    # Get remaining chats
    remaining_threads = db.get_all_threads()

    if remaining_threads:

        # Switch to the most recent remaining chat
        if st.session_state.active_chat_id == chat_id:

            st.session_state.active_chat_id = remaining_threads[0][0]

    else:

        # Create a new chat if no chats remain
        new_chat_id = db.create_thread("New Chat")

        st.session_state.active_chat_id = new_chat_id


# ==========================================
# 8. SIDEBAR - CHAT MANAGEMENT
# ==========================================

with st.sidebar:

    st.title("💬 My Conversations")

    # Create new chat
    st.button(
        "＋ New Chat",
        key="new_chat_button",
        on_click=create_new_chat,
        use_container_width=True
    )

    st.divider()

    st.caption("RECENTS")

    threads = db.get_all_threads()

    for chat_id, chat_name, created_at in threads:

        is_active = (
            chat_id == st.session_state.active_chat_id
        )

        # Chat title and action buttons
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

        # ----------------------------------
        # RENAME INTERFACE
        # ----------------------------------

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

        # ----------------------------------
        # DELETE CONFIRMATION
        # ----------------------------------

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
# 9. GET ACTIVE CHAT
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
# 10. LOAD CONVERSATION HISTORY
# ==========================================

state = chatbot.get_state(config)

messages = (
    state.values.get("messages", [])
    if state and state.values
    else []
)


# ==========================================
# 11. DISPLAY PREVIOUS MESSAGES
# ==========================================

for message in messages:

    if message.type == "human":

        role = "user"

    elif message.type == "ai":

        role = "assistant"

    else:

        continue

    with st.chat_message(role):

        st.write(message.content)


# ==========================================
# 12. GENERATE STREAMING RESPONSE
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
# 13. USER INPUT AND CHAT RESPONSE
# ==========================================

user_input = st.chat_input("Ask something...")

if user_input:

    # Display user message
    with st.chat_message("user"):

        st.write(user_input)

    # Automatically generate title for new chats
    current_threads = db.get_all_threads()

    current_chat = next(
        (thread for thread in current_threads
         if thread[0] == active_chat_id),
        None
    )

    if current_chat and current_chat[1] == "New Chat":

        db.update_thread_title(
            active_chat_id,
            user_input[:30]
        )

    # Generate assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = st.write_stream(
                generate_response(user_input)
            )

    # Refresh UI and load messages from SQLite checkpoint
    st.rerun()
