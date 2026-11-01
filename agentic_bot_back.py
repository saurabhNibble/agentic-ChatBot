import os
import sqlite3
from typing import TypedDict, Annotated

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from rag_pipeline import search_documents, initialize_pdf

# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

# Build the PDF index only if it doesn't exist yet
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
    Search the user's uploaded PDF documents and return the most
    relevant passages with their page numbers. Use this first for
    any question that could be answered by the documents.
    """
    docs = search_documents(query)

    if not docs:
        return "No relevant information found in the uploaded documents."

    results = []
    for doc in docs:
        source = os.path.basename(doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page", "Unknown")
        results.append(
            f"Source: {source}\nPage: {page}\nContent:\n{doc.page_content}"
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
# 5. CHATBOT NODE
# ==========================================

SYSTEM_PROMPT = SystemMessage(
    content="""
You are an AI chatbot developed by Saurabh Yadav.

If anyone asks who built you, who created you, or who developed you,
respond: "I was built by Saurabh Yadav."
Do not claim that someone else built you.

You have two tools:
- rag_tool: searches the user's uploaded PDF documents. Use it first
  for any question that could relate to the documents.
- tavily_search: searches the web. Use it only for current events or
  topics clearly not covered by the documents.

When you answer from a PDF, mention the source file and page number.
If rag_tool finds nothing relevant, say so before using web search.
For greetings and general chat, answer normally without tools.
"""
)


def chat_node(state: ChatState) -> ChatState:
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ==========================================
# 6. SQLITE CHECKPOINTER
# ==========================================

conn = sqlite3.connect("chat_memory.db", check_same_thread=False)

checkpoint = SqliteSaver(conn)
checkpoint.setup()


# ==========================================
# 7. BUILD LANGGRAPH WORKFLOW
# ==========================================

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")


# ==========================================
# 8. COMPILE CHATBOT
# ==========================================

chatbot = graph.compile(checkpointer=checkpoint)


# ==========================================
# 9. DELETE CHAT HISTORY
# ==========================================

def delete_chat_history(thread_id):
    checkpoint.delete_thread(thread_id)


# ==========================================
# 10. QUICK TEST
# ==========================================

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test_pdf"}}

    result = chatbot.invoke(
        {"messages": [{"role": "user", "content": "your PDF-specific question here"}]},
        config=config,
    )

    for m in result["messages"]:
        calls = getattr(m, "tool_calls", None)
        print(type(m).__name__, "|", calls if calls else "", "|", str(m.content)[:150])

    delete_chat_history("test_pdf")