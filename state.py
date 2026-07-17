from langgraph.graph import MessagesState
from typing import Literal
class analyst_state(MessagesState):
    supervisor_memory : str
    active_agent : str 
    request : str
    next : str