# from agents.visualizer_agent import visualize_agent
# from agents.executer_agent import sql_agent
from agents.supervisor_agent import supervisor_agent
from state import analyst_state
# from tools.sql_tools.query_executer import query_executer_tool
# from typing import TypedDict
from langchain.messages import HumanMessage
from langgraph.graph import StateGraph,START,END
# from langgraph.prebuilt import ToolNode,tools_condition
# from langgraph.graph import MessagesState
# from IPython.display import display,Image
from visualizer_agent_sub_graph.sub_graph import bridge_visualize_graph
from sql_agent_sub_graph.sql_graph import bridge_graph

# from sql_agent_sub_graph.sql_agent import sql_agent

def route_desicion(state : analyst_state):
    next = state['next']
    if next.lower() == "finish":
        return END
    return next

def bridge_route(state : analyst_state):
    active_agent = state["active_agent"]
    if active_agent in ("sql_agent","visualize_agent"):
        return END
    return "supervisor_agent"

def human_message_router(state: analyst_state):
    active_agent = state.get("active_agent","supervisor_agent")
    if active_agent == "sql_agent":
        return "sql_agent"
    elif active_agent == "visualize_agent":
        return "visualize_agent"
    return "supervisor_agent"
builder = StateGraph(analyst_state)

builder.add_node("supervisor_agent" , supervisor_agent)
builder.add_node("sql_agent" , bridge_graph)
builder.add_node("visualize_agent",bridge_visualize_graph)
# builder.add_node("tools",ToolNode(query_executer_tool))

builder.add_conditional_edges(START,human_message_router,["supervisor_agent","sql_agent","visualize_agent"])
builder.add_conditional_edges("supervisor_agent",route_desicion,["sql_agent","visualize_agent",END])
# builder.add_conditional_edges("sql_agent",tools_condition,{"tools" : "tools","__end__" : "supervisor_agent"})
# builder.add_edge("tools","sql_agent")
builder.add_conditional_edges("sql_agent",bridge_route,[END,"supervisor_agent"])
builder.add_conditional_edges("visualize_agent",bridge_route,[END,"supervisor_agent"])
# builder.add_edge("sql_agent","supervisor_agent")
# builder.add_edge("visualize_agent","supervisor_agent")
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
graph = builder.compile(checkpointer = memory)

config = {"configurable" : {"thread_id" : "dfg8"}}

def main():
    while True:
        try:
            humn_msg = input("user : ")
            if humn_msg.lower() == "exit":
                break
            for event in graph.stream({"messages" : [HumanMessage(humn_msg)],"request" : humn_msg},config,stream_mode="values"):
                event["messages"][-1].pretty_print()
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()