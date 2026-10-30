# AI Chatbot using LangGraph and Streamlit

An interactive AI-powered chatbot built with **LangGraph**, **LangChain**, **Ollama Cloud**, and **Streamlit**. The application provides a conversational interface with context-aware responses, conversation persistence, and real-time streaming.

## Features

- **LangGraph Workflow:** Uses a graph-based architecture to manage chatbot execution.
- **Ollama Cloud Integration:** Connects to hosted LLMs using an OpenAI-compatible API.
- **Conversation Memory:** Maintains conversation history using LangGraph's `InMemorySaver` checkpointer.
- **Thread Management:** Uses unique thread IDs to maintain separate conversations.
- **Real-Time Streaming:** Displays AI-generated responses progressively.
- **Interactive UI:** Provides a user-friendly chat interface using Streamlit.

## Tech Stack

- Python
- LangGraph
- LangChain
- Ollama Cloud
- Streamlit
- OpenAI-compatible API

## Architecture

The project separates the frontend and backend:

- `app.py` – Handles the Streamlit user interface, user input, and streaming output.
- `agentic_bot_back.py` – Defines the LLM, chatbot state, LangGraph workflow, and memory checkpointer.

## Purpose

This project explores building stateful AI applications using LangGraph, integrating cloud-hosted language models, managing conversational context, and delivering real-time AI interactions through a web interface.