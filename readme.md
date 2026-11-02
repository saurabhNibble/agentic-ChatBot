# Agentic ChatBot

A production-style AI chatbot application built with Python, Streamlit, LangGraph, and LangChain. The system supports multi-threaded conversations, PDF-based knowledge retrieval, and tool-augmented responses using both local document context and external web search.

## Overview

Agentic ChatBot is a lightweight conversational AI project designed for experimentation and practical use in document-grounded Q&A workflows. It combines:

- a Streamlit-based user interface,
- persistent conversation memory with SQLite,
- a LangGraph agent workflow,
- a FAISS vector store for uploaded PDF retrieval,
- Tavily-powered web search for current or external information,
- an Ollama-compatible local LLM backend.

This project is intended to demonstrate how modern AI agents can orchestrate memory, RAG, and tool calling in a simple and deployable application.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Security and Operational Notes](#security-and-operational-notes)
- [License](#license)
- [Contact](#contact)

## Features

- Multi-threaded chat experience with independent conversation histories
- Persistent thread metadata and checkpoints stored in SQLite
- PDF upload and indexing for local RAG workflows
- FAISS-powered semantic retrieval over uploaded documents
- Web search integration through Tavily for external knowledge
- Tool-augmented responses using a LangGraph workflow
- Streamlit admin-like chat controls for renaming, switching, and deleting threads
- Compatible with local or OpenAI-compatible LLM providers via Ollama

## Architecture

The application follows a simple Agent + Tool + Memory architecture:

1. User input is submitted through the Streamlit UI.
2. The active chat thread is resolved from SQLite metadata.
3. The LangGraph agent prepares the system prompt and conversation history.
4. The LLM decides whether to answer directly or call a tool.
5. The `rag_tool` searches uploaded PDFs via FAISS when document-grounded answers are needed.
6. The Tavily tool is used for current or external information.
7. The final answer is streamed back to the interface and saved as part of the conversation state.

```text
User → Streamlit UI → LangGraph Agent → LLM
                                ├── rag_tool (PDF retrieval)
                                └── Tavily search (external information)
                                      ↓
                               SQLite memory
```

## Technology Stack

- Python 3.10+
- Streamlit
- LangChain
- LangGraph
- FAISS
- FastEmbed
- PyPDF
- SQLite
- Ollama / OpenAI-compatible API
- Tavily Search
- python-dotenv

## Repository Structure

```text
agentic-chatbot/
├── app.py                     # Streamlit frontend and chat experience
├── agentic_bot_back.py        # Agent workflow, tool definitions, and LLM integration
├── rag_pipeline.py            # PDF ingestion, chunking, and document retrieval
├── thread_db.py               # SQLite operations for thread management
├── requirements.txt           # Python dependencies
├── readme.md                  # Project documentation
├── .env                       # Local environment variables (not committed)
├── chat_memory.db             # SQLite chat/checkpoint database
├── indexed_files.json         # Hash-based registry for uploaded PDFs
├── faiss_index/               # Local FAISS vector store files
├── uploads/                   # Uploaded PDF documents
├── set.pdf                    # Default local PDF used for initialization
├── chat_bot_workflow.ipynb    # Exploratory notebook for workflow testing
└── .gitignore                 # Excludes local runtime artifacts and sensitive files
```

## Prerequisites

Before running the application, ensure that you have:

- Python 3.10 or newer
- A working Ollama installation or OpenAI-compatible API endpoint
- A valid Tavily API key
- Internet access for external web search
- A local environment capable of running vector embedding and document processing

## Installation

1. Clone the repository:

```bash
git clone https://github.com/saurabhNibble/agentic-ChatBot.git
cd agentic-ChatBot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install project dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following values:

```env
OLLAMA_API_KEY=your_ollama_api_key
TAVILY_API_KEY=your_tavily_api_key
```

If you use a custom OpenAI-compatible model endpoint, update the `base_url` and model values in `agentic_bot_back.py` as required.

## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

After startup, open the local URL displayed in the terminal, typically:

```text
http://localhost:8501
```

## Usage

1. Open the application in your browser.
2. Use the sidebar to create a new chat thread or switch between existing ones.
3. Upload one or more PDFs from the document section.
4. Click `Add to knowledge base` to index the uploaded documents.
5. Ask questions in natural language about the uploaded material.
6. For questions outside the uploaded knowledge base, the assistant may use Tavily web search.
7. Rename or delete chats as needed from the sidebar controls.

## Security and Operational Notes

- Store secrets such as API keys only in `.env` files or secure secret managers.
- Do not commit sensitive environment files to version control.
- Validate third-party APIs and model endpoints before production use.
- Monitor storage usage for FAISS index files and uploaded PDFs.
- Treat uploaded PDFs as untrusted content; validate file types and sanitize inputs where applicable.
- If you deploy this project externally, place it behind proper authentication and access controls.

## License

This project does not currently include a license file. Before public or commercial use, add an appropriate open-source license such as MIT or Apache 2.0.

## Contact

Saurabh Yadav

Project repository: https://github.com/saurabhNibble/agentic-ChatBot

## Notes

- The project automatically initializes a vector index from `set.pdf` if one does not already exist.
- Duplicate PDFs are skipped using a SHA-256 registry stored in `indexed_files.json`.
- Conversation checkpoints are stored in `chat_memory.db` to preserve thread state between app sessions.
