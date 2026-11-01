# Agentic ChatBot

A Streamlit-based AI chatbot that uses LangGraph, LangChain, and Ollama to provide stateful, tool-augmented conversations with persistent chat history.

## Overview

This project is a conversational AI application designed to:

- maintain separate chat threads for each user session,
- store conversation state in SQLite,
- use a LangGraph workflow to orchestrate the chatbot logic,
- allow the model to call tools such as web search,
- deliver a responsive chat interface through Streamlit.

The application is useful for experimenting with real-world AI agent patterns, memory persistence, and tool use in a compact, easy-to-run project.

## Features

- LangGraph-powered agent workflow
- Streamlit web interface
- Persistent thread metadata in SQLite
- LangChain message-based chat state
- Real-time streaming responses from the LLM
- Tavily web search integration for tool-augmented answers
- Conversation persistence across app restarts
- Per-thread chat management with rename and delete support

## Tech Stack

- Python
- Streamlit
- LangChain
- LangGraph
- Ollama / OpenAI-compatible API
- SQLite
- Tavily Search
- python-dotenv

## Project Structure

- `app.py` — Streamlit frontend and chat UI
- `agentic_bot_back.py` — LangGraph chatbot graph, tools, and model setup
- `thread_db.py` — SQLite helpers for chat thread metadata
- `chat_memory.db` — persistent SQLite database used by the app
- `requirements.txt` — Python dependencies
- `chat_bot_workflow.ipynb` — exploratory workflow notebook

## Architecture

The app follows a simple agent architecture:

1. User enters a message in the Streamlit UI.
2. The message is sent to the LangGraph workflow.
3. The chatbot node prepares the system prompt and conversation history.
4. The model may decide to call tools, such as Tavily search, to answer queries more effectively.
5. The response is streamed back to the UI.
6. Thread metadata and conversation checkpoints are stored in SQLite for persistence.

## Prerequisites

Before running the app, make sure you have:

- Python 3.10+
- An Ollama-compatible model available (the project currently uses `gpt-oss:20b`)
- A Tavily API key
- Access to the internet for Tavily search

## Environment Setup

Create a `.env` file in the project root with the following values:

```env
OLLAMA_API_KEY=your_ollama_api_key
TAVILY_API_KEY=your_tavily_api_key
```

If you are using a local or custom Ollama/OpenAI-compatible endpoint, you may need to adjust the `base_url` and model name in `agentic_bot_back.py`.

## Installation

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal (typically `http://localhost:8501`).

## Usage

- Start a new chat from the sidebar.
- Rename or delete existing threads.
- Ask questions normally or request real-time web-assisted answers.
- The app keeps thread-level memory and chat metadata in SQLite.

## Notes

- The chatbot uses a persistent SQLite checkpointer for the LangGraph graph.
- Thread names and metadata are managed by `thread_db.py`.
- Conversation checkpoints are stored in `chat_memory.db`.
- This project is ideal for learning how small AI applications can combine LLMs, state management, tool calling, and a web UI.

## License

This project is currently unlicensed unless a license file is added later.

## Author

Saurabh Yadav