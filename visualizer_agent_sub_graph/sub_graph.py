from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode
from langchain.tools import tool
from visualizer_agent_sub_graph.visualizer_state import visualize_state
from visualizer_agent_sub_graph.visualize_agent import visualize_agent
from tools.visualisation_tool import create_visualiser_tool as tool
# data_visualizer = tool(df)
from visualizer_agent_sub_graph.visualize_agent import data_visualizer
from state import analyst_state
from langgraph.checkpoint.memory import MemorySaver
from langchain.messages import HumanMessage,AIMessage
from uuid import uuid4
memory = MemorySaver()

# @tool
# def data_visualizer(code:str,name:str) -> str:
#     """
#             this is a python code executor used to execute data visuslizing.
            
#             ARGS : 
#                     code : str (description: python code for visualizing data)
#                     name : str(description: name of the graph image, name should be like a description of the graph-code. example: age_distribution_histogram)
#             """
            
    # return "graph created successfully"
def sub_graph_router(state : visualize_state):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        if last_msg.tool_calls[0]["name"] == "transfer_back_to_supervisor":
            return END
        else:
            return "tools"
    return END

builder = StateGraph(visualize_state)

builder.add_node("visualize_agent",visualize_agent)
builder.add_node("tools",ToolNode([data_visualizer]))

builder.add_edge(START,"visualize_agent")
builder.add_conditional_edges("visualize_agent",sub_graph_router,[END,"tools"])
builder.add_edge("tools","visualize_agent")
# builder.add_adge("visualize_agent",END)

graph = builder.compile(checkpointer = memory)


def bridge_visualize_graph(state: analyst_state):
    requests = state["request"]
    
    config = {"configurable" : {"thread_id" : str(uuid4())}}
    
    sub_graph_results = graph.invoke({"messages" : HumanMessage(requests)},config)
    response = sub_graph_results["messages"][-1]
    if response.tool_calls and response.tool_calls[0]["name"] == "transfer_back_to_supervisor":
        print("hi")
        final_response = response.tool_calls[0]["args"]["final_response"]
        return {"messages" : AIMessage(final_response),"active_agent" : None}
    return {"messages" : response}