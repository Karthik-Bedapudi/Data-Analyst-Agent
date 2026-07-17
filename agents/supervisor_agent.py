from typing import Literal
from state import analyst_state
from langchain.chat_models import init_chat_model
from pydantic import BaseModel,Field
from langchain_core.messages import HumanMessage,SystemMessage

sys_prompt = """
# identity : 
                your are an supervisor agent.
# instructions                
                    you have two workers:
                    
                    1. sql_agent description : (capable of writing and executing sql_queries.)
                    2. visualize_agent description : (capable of writing by itself and executing data visualization codes by it self in seaborn.) 
                
            ## Routing rules (CRITICAL) :
             - Evaluate User request and current conversation history.
             - if the user asks for multiple requests then you must send one request at a time to worker.
             - send the next request only if you get a successfull message of the last request from worker.
             - if the user asks for a graph/chart, and it has not been created yet,just route to 'visualize_agent' and the request need to be like just a request with no suggestions on how to create.
             - if the user asks for data/metrics, and it has not been created yet, route to 'sql_agent`.
            
            ## STOPPING CONDITION (READ CAREFULLY) :
             - always look at very last MESSAGE in convorsation.
             - if the last message is from worker or AI and it say's the workers job is successfully finished.
             - and users request also finished then YOU MUST route to FINISH. Do not route to a worker if their task is already finished!
                    
                

"""
future = """and describe the users's request more precisely and effectively to get the maximum results.
                    NOTE: if there is a need to call visualize_agent, then make sure to describe the user's intent or your intent of how the graph need to look like to get a wonderful graph.    
"""

class desicion_schema(BaseModel):
    """decide wich agent to call next or Finish the conversation"""
    next : Literal["sql_agent","visualize_agent","Finish"]
    request : str
llm = init_chat_model(model="groq:openai/gpt-oss-120b")
supervisor_llm = llm.with_structured_output(desicion_schema)

def supervisor_agent(state : analyst_state):
    convo = state.get('messages','')
    response = supervisor_llm.invoke([SystemMessage(sys_prompt)] + convo)
    return {"next" : f"{response.next}", "request" : f"{response.request}","messages" : f"{[response]}","active_agent" : f"{response.next}"}