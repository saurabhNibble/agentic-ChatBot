
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import BaseMessage, add_messages
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os
import sqlite3

# NEW: SQLite persistent checkpointer
from langgraph.checkpoint.sqlite import SqliteSaver

from langgraph.prebuilt import ToolNode,tools_condition
from langchain_tavily import TavilySearch


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
# 3. INITIALIZE TOOLS
# ==========================================

search_tool = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic"
)

tools = [search_tool]

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)



# ==========================================
# 3. DEFINE CHAT STATE
# ==========================================

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]


# ==========================================
# 4. CHATBOT NODE
# ==========================================

def chat_node(state: ChatState) -> ChatState:

    system_prompt = SystemMessage(
        content="""
        You are an AI chatbot developed by Saurabh Yadav.

        If anyone asks who built you, who created you,
        or who developed you, respond:

        "I was built by Saurabh Yadav."

        Do not claim that someone else built you.

        Answer other questions normally and helpfully.
        """
    )

    messages = [system_prompt] + state["messages"]

    response = llm_with_tools.invoke(messages)

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

# NEW: Tool execution node
graph.add_node("tools", ToolNode(tools))

# Workflow edges
graph.add_edge(START, "chat_node")

# Decide whether to execute tools or finish
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

graph.add_edge("tools", "chat_node")


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