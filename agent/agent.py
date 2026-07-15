
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from tools.menu_tool import menu_prices
from tools.hours_tool import opening_hours_tool
from tools.reservation_tools import table_reservation, check_reservation, cancel_reservation
from agent.prompts import RESTAURANT_SYSTEM

tools = [menu_prices, opening_hours_tool, table_reservation, check_reservation, cancel_reservation]

@st.cache_resource
def build_agent():
    llm            = ChatOpenAI(temperature=0, model_name="gpt-4.1-nano")
    llm_with_tools = llm.bind_tools(tools)
    tool_node      = ToolNode(tools)

    def agent_reason(state: MessagesState) -> MessagesState:
        response = llm_with_tools.invoke([SystemMessage(content=RESTAURANT_SYSTEM), *state["messages"]])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        return "act" if state["messages"][-1].tool_calls else END

    graph = StateGraph(MessagesState)
    graph.add_node("agent_reason", agent_reason)
    graph.add_node("act", tool_node)
    graph.set_entry_point("agent_reason")
    graph.add_conditional_edges("agent_reason", should_continue, {"act": "act", END: END})
    graph.add_edge("act", "agent_reason")
    return graph.compile(checkpointer=MemorySaver())

def chat(app, question: str, session_id: str) -> str:
    config   = {"configurable": {"thread_id": session_id}}
    response = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    return response["messages"][-1].content
