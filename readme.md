# Agentic ChatBot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Workflow-4B8BF5)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-00A7A7)
![License](https://img.shields.io/badge/License-Unspecified-lightgray)

</div>

A Streamlit-powered AI assistant for multi-threaded chat, PDF-grounded document retrieval, and tool-augmented responses. The app combines LangGraph, LangChain, FAISS, SQLite, and an Ollama-compatible LLM to create a lightweight agentic workflow for conversational AI.

## Overview

Agentic ChatBot is a practical AI application designed to help users:

- hold multiple independent chat conversations,
- upload and query PDF documents,
- retrieve relevant passages using semantic search,
- use Tavily for external web search when needed,
- review and approve tool calls before execution through a human-in-the-loop flow.

The project is intended as a compact, developer-friendly example of an agentic system that mixes memory, retrieval, and tool usage in a real application.

## Features

- Multi-thread chat UI in Streamlit
- Persistent conversation state and metadata via SQLite
- PDF upload and indexing workflow for local RAG
- FAISS vector search over uploaded documents
- Tool-augmented LLM responses using LangGraph
- Tavily web search for external or up-to-date information
- Human approval step before executing certain tool calls
- Rename, switch, and delete chat thread controls in the sidebar
- Local model compatibility through Ollama and OpenAI-compatible endpoints

## Demo

```text
1. Open the app in the browser.
2. Create a chat thread from the sidebar.
3. Upload a PDF and click "Add to knowledge base".
4. Ask a question related to the uploaded document.
5. The assistant retrieves the most relevant passages and answers using them.
6. If the topic is outside the document context, it can use web search.
7. When prompted, approve or reject tool execution before continuing.
```

## Architecture

The application follows a simple agent architecture with memory and retrieval:

1. The user interacts with the Streamlit UI.
2. The active chat thread is loaded from SQLite metadata.
3. The LangGraph agent composes the system prompt and the message history.
4. The LLM decides whether to answer directly or call a tool.
5. `rag_tool` searches uploaded PDF content through FAISS when document-based answers are needed.
6. Tavily search is used for fresh or external information.
7. The final answer is streamed back to the user.
8. The conversation is checkpointed for persistence across sessions.

```text
User → Streamlit UI → LangGraph Agent → LLM
                               ├── rag_tool (PDF retrieval)
                               ├── Tavily Search (web knowledge)
                               └── SQLite memory / thread metadata
```

## Tech Stack

- Python 3.10+
- Streamlit
- LangChain
- LangGraph
- FAISS
- FastEmbed
- PyPDF
- SQLite
- Ollama / OpenAI-compatible endpoints
- Tavily Search
- python-dotenv

## Project Structure

```text
agentic-chatbot/
├── app.py                     # Streamlit chat frontend and approval flow
├── agentic_bot_back.py        # LangGraph workflow, tool definitions, and model setup
├── rag_pipeline.py            # PDF indexing, chunking, and document search logic
├── thread_db.py               # SQLite helper functions for thread management
├── requirements.txt           # Python dependencies
├── readme.md                  # Project documentation
├── .env                       # Local environment variables
├── chat_memory.db             # SQLite database for thread metadata and checkpoints
├── indexed_files.json         # Registry for already-indexed PDFs
├── faiss_index/               # FAISS vector store output
├── uploads/                   # Uploaded PDF files
├── set.pdf                    # Default PDF used during initialization
├── chat_bot_workflow.ipynb    # Notebook for experimentation and workflow testing
└── .gitignore                 # Local file exclusions
```

## Prerequisites

Before running the app, ensure you have:

- Python 3.10 or newer
- An Ollama instance or another OpenAI-compatible API endpoint
- A Tavily API key
- Internet access for web search
- Enough local storage for the FAISS index and uploaded PDFs

## Environment Setup

Create a `.env` file in the project root:

```env
OLLAMA_API_KEY=your_ollama_api_key
TAVILY_API_KEY=your_tavily_api_key
```

If you use a custom endpoint or model, update the configuration in `agentic_bot_back.py` accordingly.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/saurabhNibble/agentic-ChatBot.git
cd agentic-ChatBot
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Usage

1. Open the app in the browser.
2. Create or switch to a chat thread from the sidebar.
3. Upload one or more PDFs to add them to the document knowledge base.
4. Click `Add to knowledge base` to index the files.
5. Ask natural-language questions about the uploaded PDFs.
6. If the request is not covered by the documents, the agent may use Tavily search.
7. Review tool approvals when prompted before continuing.
8. Rename or delete chats from the sidebar when needed.

## Human-in-the-Loop Approval

The user interface includes a safety/approval flow for tool execution. When the agent requests a tool, the app displays:

- the tool name,
- the arguments passed,
- a “Approve” and “Reject” action set.

This helps provide explicit control before executing tool-based actions.

## Notes

- The application builds a local FAISS index from `set.pdf` if it exists and no index is already present.
- Duplicate PDF uploads are prevented using a hash-based registry in `indexed_files.json`.
- Thread metadata and metadata history are stored in SQLite via `thread_db.py`.
- Chat conversations are checkpointed in `chat_memory.db` so session state persists between app restarts.
- This project is a useful base for learning how LLM agents, document retrieval, and tool calling can be assembled in a compact app.

## Security and Operational Considerations

- Keep API keys in a local `.env` file and never commit secrets to source control.
- Validate uploaded files before processing them in production-grade environments.
- Monitor FAISS index and uploaded document storage growth.
- Use authentication and access control if deploying this app beyond a local environment.
- Treat uploaded PDFs as untrusted content and apply validation where appropriate.

## License

This project does not currently include a license file. Add an appropriate open-source license before public or commercial distribution.

## Screenshot / UI Preview

The application is a lightweight chat interface with a sidebar for thread management and document upload. It supports persistent chat history and a human approval flow before tool execution.

![App Preview](https://via.placeholder.com/1200x700?text=Agentic+ChatBot+Preview)

## Author

Saurabh Yadav
