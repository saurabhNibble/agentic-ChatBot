
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import BaseMessage, add_messages

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os
import sqlite3

# NEW: SQLite persistent checkpointer
from langgraph.checkpoint.sqlite import SqliteSaver


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# 2. INITIALIZE LLM
# ==========================================

llm = ChatOpenAI(
    model="gpt-oss:20b",
    base_url="https://ollama.com/v1",
    api_key=os.getenv("OLLAMA_API_KEY"),
    temperature=0,
    streaming=True
)


# ==========================================
# 3. DEFINE CHAT STATE
# ==========================================

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]


# ==========================================
# 4. CHATBOT NODE
# ==========================================

def chat_node(state: ChatState) -> ChatState:

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# ==========================================
# 5. SQLITE DATABASE CONNECTION
# ==========================================

# NEW: Create persistent SQLite connection

conn = sqlite3.connect(
    "chat_memory.db",
    check_same_thread=False
)


# ==========================================
# 6. INITIALIZE CHECKPOINTER
# ==========================================

# OLD:
# from langgraph.checkpoint.memory import InMemorySaver
# checkpoint = InMemorySaver()

# NEW:
checkpoint = SqliteSaver(conn)

# Create required checkpoint tables
checkpoint.setup()


# ==========================================
# 7. BUILD LANGGRAPH WORKFLOW
# ==========================================

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")

graph.add_edge("chat_node", END)


# ==========================================
# 8. COMPILE CHATBOT
# ==========================================

chatbot = graph.compile(
    checkpointer=checkpoint
)
# ==========================================
# 9. DELETE LANGGRAPH CHECKPOINTS
# ==========================================

def delete_chat_history(thread_id):

    checkpoint.delete_thread(thread_id)
if __name__ == "__main__":

    test_thread_id = "test_123"

    config = {
        "configurable": {
            "thread_id": test_thread_id
        }
    }

    chatbot.invoke(
        {"messages": [{"role": "user", "content": "Hello"}]},
        config=config
    )

    print("Before deletion:")
    print(chatbot.get_state(config).values)

    delete_chat_history(test_thread_id)

    print("After deletion:")
    print(chatbot.get_state(config).values)