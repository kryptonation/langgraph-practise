from typing import TypedDict
from typing_extensions import Annotated

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from config import settings

model = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o")


class State(TypedDict):
    """State of the agent."""
    messages: Annotated[list, add_messages]


def bot(state: State):
    """Bot agent."""
    print(state.get("messages"))
    return {"messages": [model.invoke(state.get("messages"))]}


# Build the graph
graph_builder = StateGraph(State)

# Add the nodes
graph_builder.add_node("bot", bot)

# Set the entry point
graph_builder.set_entry_point("bot")
graph_builder.set_finish_point("bot")

# Build the graph
graph = graph_builder.compile()

# Run the graph
# response = graph.invoke({"messages": ["Hello, how do you do?"]})
# print(response)

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print(f"Assistant: {value["messages"][-1].content}")

    