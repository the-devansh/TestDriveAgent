import json
import os
from datetime import datetime
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
from langgraph.checkpoint.memory import MemorySaver

# Tools
@tool
def search_cars(query: str):
    """Searches the car database for specific models or types (suv, sedan, electric)."""
    data = get_cars_data()
    query = query.lower()
    results = []
    
    # Check for categories
    categories = ["suv", "sedan", "electric"]
    matched_cats = [cat for cat in categories if cat in query]
    
    if matched_cats:
        for cat in matched_cats:
            results.extend(data.get(cat + "s" if cat != "electric" else "electric", []))
    
    # Check for specific models
    for cat_cars in data.values():
        for car in cat_cars:
            if car["model"].lower() in query:
                results.append(car)
    
    if not results:
        return "I couldn't find any specific matches. We have SUVs, Sedans, and Electric cars available."
    
    model_list = list(set([c["model"] for c in results]))
    # Return raw data for the LLM to process into a conversational response
    return {"models": model_list, "category": matched_cats[0] if matched_cats else "cars"}

@tool
def book_test_drive(model: str, date: str, time: str):
    """Books a test drive. Use this ONLY after the user has confirmed a specific model name."""
    booking_file = "data/bookings.json"
    new_booking = {
        "model": model,
        "date": date,
        "time": time,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if os.path.exists(booking_file):
            with open(booking_file, "r") as f:
                bookings = json.load(f)
        else:
            bookings = []
            
        bookings.append(new_booking)
        
        with open(booking_file, "w") as f:
            json.dump(bookings, f, indent=2)
            
        return f"Your test drive for the {model} is scheduled for {date} at {time}. We look forward to seeing you!"
    except Exception as e:
        print(f"Booking Error: {e}")
        return "I'm sorry, I encountered an error while saving your booking. But don't worry, I've noted it down!"

tools = [search_cars, book_test_drive]
tool_node = ToolNode(tools)

# LLM setup
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    "You are a professional auto dealership voice assistant. You MUST follow this logic flow exactly:\n"
    "1. If the user asks for a category (like SUV) or to book a drive without a specific model name:\n"
    "   - IMMEDIATELY call `search_cars` with the category.\n"
    "   - When you get the results, list the available models and then PROPOSE one specifically to confirm. "
    "   - Example: 'I found these SUVs: TrailBlazer X and MountainPeak 360. Do you want to test drive the TrailBlazer X?'\n"
    "2. If the user confirms a model but forgot date/time, ask for them.\n"
    "3. ONLY call `book_test_drive` after you have a specific model, date, and time confirmed.\n"
    "4. If you have all details (model, date, time), call the tool and then repeat the confirmation clearly.\n"
    "Keep responses concise and energetic for voice interaction."
)

# Nodes
def agent_node(state: AgentState):
    """A single agent node that uses tools to answer the user."""
    # Build history with system prompt
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
memory = MemorySaver()
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

app = workflow.compile(checkpointer=memory)

def run_agent(input_text: str, thread_id: str = "default_user"):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(
        {"messages": [HumanMessage(content=input_text)]},
        config=config
    )
    return result["messages"][-1].content
