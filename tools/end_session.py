from langchain.tools import tool

@tool
def transfer_back_to_supervisor(final_response:str) -> bool:
    """used to end a session,
    use this tool when your task is completed and you need to transfer back to supervisor agnet
    args:
    
    final_response : str , final response to the user
    """
    return 
