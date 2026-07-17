from sql_agent_sub_graph.sql_agent_state import sql_state
from langchain.messages import SystemMessage
from langchain.chat_models import init_chat_model
from tools.sql_tools.query_executer import query_executer_tool
# from agents.visualizer_agent import schema
from visualizer_agent_sub_graph.visualize_agent import schema
from tools.end_session import transfer_back_to_supervisor

# sys_prompt = """You are an expert in writing sql queries, you job is to change the user given 
#                 natural language query into an list of error less SQL QUERIES or a single QUERY in a list.
#                 here is the schema of the table you are dealing with 
#                 SCHEMA: {schema}
                
#                 INSTRUCTIONS : 
#                 1. you are allowed to use tools to complete user task.
#                 2. once you get response from a tool call write the response in a professional natural language to the user.
#                 """
llm = init_chat_model("groq:openai/gpt-oss-20b")
llm_with_tools = llm.bind_tools([query_executer_tool,transfer_back_to_supervisor])

def sql_agent(state : sql_state):
    sys_prompt = """You are an expert in writing sql queries, your job is to change the user given 
                natural language query into an error less SQL QUERY.
                here is the schema of the table you are dealing with 
                SCHEMA: {schema}
                
                INSTRUCTIONS : 
                1. You are allowed to use tools to complete the user task.
                3. and when you need more information, then ask user to give more info to complete the task.
                2. Once you get a response from the `query_executer` tool, YOU MUST CALL transfer_back_to_supervisor tool and write the final answer in natural language and pass it as an argument to call "transfer_back_to_supervisor".
                3. CRITICAL: you must call the "transfer_back_to_supervisor" tool if you answered users question correctly or user asks a question completely unrelated to databases/SQL (like drawing a graph or general chat)
                """
    sys_prompt = sys_prompt.replace("{schema}",schema)
    response = llm_with_tools.invoke([SystemMessage(sys_prompt)]+state["messages"])
    return{"messages" : response}