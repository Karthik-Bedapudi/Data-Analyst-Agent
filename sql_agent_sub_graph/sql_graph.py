from langchain.messages import HumanMessage,AIMessage
from langgraph.graph import START,END,StateGraph
from sql_agent_sub_graph.sql_agent_state import sql_state
from tools.sql_tools.query_executer import query_executer_tool
from langgraph.prebuilt import ToolNode,tools_condition
from sql_agent_sub_graph.sql_agent import sql_agent
from state import analyst_state
from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4
memory = MemorySaver()
def sub_graph_router(state : sql_state):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        if last_msg.tool_calls[0]["name"] == "transfer_back_to_supervisor":
            return END
        else:
            return "tools"
    return END
builder = StateGraph(sql_state)


builder.add_node("sql_agent",sql_agent)
builder.add_node("tools",ToolNode([query_executer_tool]))

builder.add_edge(START,"sql_agent")
builder.add_conditional_edges("sql_agent", sub_graph_router)
# builder.add_conditional_edges("sql_agent",tools_condition)
builder.add_edge("tools","sql_agent")
# builder.add_edge("sql_agent",END)

graph = builder.compile(checkpointer = memory)


def bridge_graph(state:analyst_state):
    active_agent = state["active_agent"]
    message = state["request"] 
     
    config = {"configurable" : {"thread_id" : str(uuid4())}}
    
    sql_graph_result = graph.invoke({"messages" : HumanMessage(message)},config)
    response = sql_graph_result["messages"][-1]
    if response.tool_calls and response.tool_calls[0]['name'] == "transfer_back_to_supervisor":
        ai_msg = response.tool_calls[0]['args']['final_response']
        try:
            print("ai_msg: ",ai_msg)
            return {"messages" : [AIMessage(content = ai_msg)],"active_agent" : None}
        except:
            return {"messages" : [AIMessage(content = "sql execution completed")],"active_agent" : None}
    return {"messages" : [response]}