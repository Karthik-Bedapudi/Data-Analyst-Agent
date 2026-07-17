
from connection import conn

"""query executer tool"""
from langchain.tools import tool
@tool
def query_executer(queries : list[str]) -> str:
    """
    execute the sql queries and returns the output
    
    Args : 
        qurries : list,(description: sql query)
    """
    response = ""
    for query in queries:
        try:
            response = response + f"{conn.execute(query).df()}\n"
        except Exception as e:
            response = response + f"QUERY: {query} \n ERROR: {e}"
    return response

query_executer_tool = query_executer