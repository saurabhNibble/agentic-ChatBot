
# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, Annotated
# from langgraph.graph.message import BaseMessage, add_messages
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# import os

# from langgraph.checkpoint.memory import InMemorySaver
# from langchain_core.messages import HumanMessage

# load_dotenv()

# llm = ChatOpenAI(
#     model="gpt-oss:20b",
#     base_url="https://ollama.com/v1",
#     api_key=os.getenv("OLLAMA_API_KEY"),
#     temperature=0
# )

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]


# def chat_node(state: ChatState) -> ChatState:
#     response = llm.invoke(state["messages"])
#     return {"messages": [response]}


# checkpoint = InMemorySaver()

# graph = StateGraph(ChatState)

# graph.add_node("chat_node", chat_node)

# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpoint)

# # Configure conversation thread
# thread_id = 1

# config = {
#     "configurable": {
#         "thread_id": thread_id
#     }
# }

# # Initial conversation
# initial_state = {
#     "messages": [
#         HumanMessage(content="Hello, how are you?")
#     ]
# }

# response = chatbot.invoke(initial_state, config=config)

# print("Chatbot:", response["messages"][-1].content)

# # Continuous conversation
# while True:

#     user_input = input("You: ")

#     if user_input.lower() in ["exit", "quit"]:
#         print("Exiting the chat. Goodbye!")
#         break

#     current_state = {
#         "messages": [HumanMessage(content=user_input)]
#     }

#     response = chatbot.invoke(current_state, config=config)

#     print("Chatbot:", response["messages"][-1].content)

# # Retrieve conversation state
# state = chatbot.get_state(config=config)

# print("\nComplete conversation history:")

# for message in state.values["messages"]:
#     print(message.type, ":", message.content)

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import BaseMessage, add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI(
    model="gpt-oss:20b",
    base_url="https://ollama.com/v1",
    api_key=os.getenv("OLLAMA_API_KEY"),
    temperature=0,
    streaming=True
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState) -> ChatState:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


checkpoint = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpoint)
