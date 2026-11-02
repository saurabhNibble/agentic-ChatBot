
import os
import sqlite3
from typing import TypedDict, Annotated

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from rag_pipeline import search_documents, initialize_pdf


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

# Build PDF index if it doesn't exist
initialize_pdf()


# ==========================================
# 2. INITIALIZE LLM
# ==========================================

llm = ChatOpenAI(
    model="gpt-oss:20b",
    base_url="https://ollama.com/v1",
    api_key=os.getenv("OLLAMA_API_KEY"),
    temperature=0,
    streaming=True,
)


# ==========================================
# 3. INITIALIZE TOOLS
# ==========================================

@tool
def rag_tool(query: str) -> str:
    """
    Search uploaded PDF documents and return
    relevant passages with their page numbers.
    Use this for questions related to uploaded documents.
    """

    docs = search_documents(query)

    if not docs:
        return "No relevant information found in uploaded documents."

    results = []

    for doc in docs:

        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )

        page = doc.metadata.get("page", "Unknown")

        results.append(
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(results)


search_tool = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
)

tools = [rag_tool, search_tool]

llm_with_tools = llm.bind_tools(tools)


# ==========================================
# 4. DEFINE CHAT STATE
# ==========================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ==========================================
# 5. SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = SystemMessage(
    content="""
You are an AI chatbot developed by Saurabh Yadav.

If anyone asks who built you, who created you,
or who developed you, respond:
"I was built by Saurabh Yadav."

You have two tools:

1. rag_tool:
   Searches the user's uploaded PDF documents.
   Use it for questions related to uploaded documents.

2. TavilySearch:
   Searches the web.
   Use it for current events or topics not covered
   by the uploaded documents.

When answering from a PDF, mention the source file
and page number.

For greetings and general conversation,
respond normally without tools.
"""
)


# ==========================================
# 6. CHATBOT NODE
# ==========================================

def chat_node(state: ChatState) -> ChatState:

    messages = [SYSTEM_PROMPT] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# ==========================================
# 7. HUMAN-IN-THE-LOOP NODE
# ==========================================

tool_node = ToolNode(tools)


def tools_with_approval(state: ChatState):

    last_message = state["messages"][-1]

    tool_calls = last_message.tool_calls

    # Request human approval before tool execution
    decision = interrupt({
        "message": "The chatbot wants to execute the following tools.",
        "tool_calls": [
            {
                "name": call["name"],
                "args": call["args"],
            }
            for call in tool_calls
        ],
        "options": ["approve", "reject"],
    })

    # Reject tool execution
    if decision != "approve":

        return {
            "messages": [
                ToolMessage(
                    content="The user rejected this tool execution.",
                    tool_call_id=call["id"],
                )
                for call in tool_calls
            ]
        }

    # Execute tools after approval
    return tool_node.invoke(state)


# ==========================================
# 8. SQLITE CHECKPOINTER
# ==========================================

APP_DATA_DIR = os.getenv(
    "APP_DATA_DIR",
    os.path.dirname(os.path.abspath(__file__))
)
os.makedirs(APP_DATA_DIR, exist_ok=True)

conn = sqlite3.connect(
    os.path.join(APP_DATA_DIR, "chat_memory.db"),
    check_same_thread=False
)

checkpoint = SqliteSaver(conn)

checkpoint.setup()


# ==========================================
# 9. BUILD LANGGRAPH WORKFLOW
# ==========================================

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

# HITL approval wrapper
graph.add_node("tools", tools_with_approval)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

graph.add_edge("tools", "chat_node")


# ==========================================
# 10. COMPILE CHATBOT
# ==========================================

chatbot = graph.compile(
    checkpointer=checkpoint
)


# ==========================================
# 11. DELETE CHAT HISTORY
# ==========================================

def delete_chat_history(thread_id: str):

    checkpoint.delete_thread(thread_id)


# ==========================================
# 12. QUICK TEST
# ==========================================

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "test_pdf"
        }
    }

    result = chatbot.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What does my PDF say about machine learning?"
                }
            ]
        },
        config=config,
    )

    # Check whether graph is interrupted
    if result.get("__interrupt__"):

        print("\nHUMAN APPROVAL REQUIRED")

        for intr in result["__interrupt__"]:
            print(intr.value)

        decision = input(
            "\nEnter approve or reject: "
        ).strip().lower()

        # Resume the interrupted graph
        result = chatbot.invoke(
            Command(resume=decision),
            config=config,
        )

    # Print conversation
    for message in result["messages"]:

        print(
            type(message).__name__,
            "|",
            str(message.content)[:500]
        )

    # Uncomment to delete test conversation
    # delete_chat_history("test_pdf")
