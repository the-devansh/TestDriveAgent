import json
import os
from typing import Annotated, TypedDict, List, Union
from typing_extensions import TypedDict

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Define State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    next_agent: str
    booking_details: dict
    car_info: str

# Load Knowledge Base
def get_cars_data():
    with open("data/cars.json", "r") as f:
        return json.load(f)

from langgraph.prebuilt import ToolNode

# Tools
@tool
def search_cars(query: str):
    """Searches the car database for specific models or types (suv, sedan, electric)."""
    data = get_cars_data()
    query = query.lower()
    results = []
    for category, cars in data.items():
        if category in query:
            results.extend(cars)
        for car in cars:
            if car["model"].lower() in query:
                results.append(car)
    
    if not results:
        return "I couldn't find any specific matches for that. We have various SUVs, Sedans, and Electric cars available."
    return "Here are some models I found: " + ", ".join([c["model"] for c in results[:3]])

@tool
def book_test_drive(model: str, date: str, time: str):
    """Books a test drive for a specific model at a given date and time."""
    return f"I have successfully booked your test drive for the {model} on {date} at {time}. We look forward to seeing you!"

tools = [search_cars, book_test_drive]
tool_node = ToolNode(tools)

# LLM setup
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    "You are a helpful and professional auto dealership assistant. "
    "If the user's message is empty or unclear, kindly ask them to repeat. "
    "If the user wants to book a test drive, use the book_test_drive tool. "
    "If the user wants to know about cars, use the search_cars tool. "
    "Always respond in natural, spoken English."
)

# Nodes
def agent_node(state: AgentState):
    """A single agent node that uses tools to answer the user."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Determines if we should call a tool or end the conversation."""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

def run_agent(input_text: str):
    initial_state = {
        "messages": [HumanMessage(content=input_text)],
        "next_agent": "",
        "booking_details": {},
        "car_info": ""
    }
    result = app.invoke(initial_state)
    return result["messages"][-1].content
