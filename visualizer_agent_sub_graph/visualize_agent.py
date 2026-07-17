from tools.sql_tools.initial import initiate
from tools.visualisation_tool import create_visualiser_tool
from visualizer_agent_sub_graph.visualizer_state import visualize_state
from langchain.agents import create_agent
from tools.end_session import transfer_back_to_supervisor
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

llm = init_chat_model(model = "groq:openai/gpt-oss-120b")

schema,df = initiate()

data_visualizer = create_visualiser_tool(df)
llm_with_tools = llm.bind_tools([data_visualizer,transfer_back_to_supervisor])
sys_prompt = f"""
                you are a data visualizer agent, your job is to write a python data visualisation code in seaborn,
                on the basis of user query.
            # CRITICAL :
                            CALL data_visualiser tool and send code, never give code as a chat message. only chat when the graph created successfully
                NOTE : DON'T use plt.show() in the last, just leave the code as is, don't show or save.
                
                NOTE: the code sending to the tool, MUST follow these below rules.
                
                1. you need to just write an error less python code, DONT import any thing.
                2. you are allowed to use modules -- mataploatlib.pyplot imported as plt and
                   seaborn imported as sns.
                3. and dataframe of the data imported as "my_data".
                4. and MAKE SURE TO create the graph as proffesional and understandable as possible.
                5. Passing `palette` without assigning `hue` is removed. Assign the `x` variable to `hue` and set `legend=False` for the same effect.
                  here is the schema of the data frame :
                  
                  {schema}
                  
                once you got a successfull message from visualize tool call then write a final_response and send it to transfer_back_to_supervisor tool as an argument.
"""

def visualize_agent(state : visualize_state):
    # data_agent = create_agent(
    #     model = "groq:llama-3.3-70b-versatile",
    #     tools = [data_visualizer,transfer_back_to_supervisor],
    #     system_prompt = sys_prompt
    # )
    sys_prompt = f"""
                you are a data visualizer agent, your job is to write a python data visualisation code in seaborn,
                on the basis of user query.
            # CRITICAL :
                            CALL data_visualiser tool and send code, never give code as a chat message. only chat when the graph created successfully
                NOTE : DON'T use plt.show() in the last, just leave the code as is, don't show or save.
                
                NOTE: the code sending to the tool, MUST follow these below rules.
                
                1. you need to just write an error less python code, DONT import any thing.
                2. you are allowed to use modules -- mataploatlib.pyplot imported as plt and
                   seaborn imported as sns.
                3. and dataframe of the data imported as "my_data".
                4. and MAKE SURE TO create the graph as proffesional and understandable as possible.
                5. Passing `palette` without assigning `hue` is removed. Assign the `x` variable to `hue` and set `legend=False` for the same effect.
                    here is the schema of the data frame :
                  {schema}
                  
                <critical>
                
                 once you got a successfull message from visualize tool call then write a final_response and send it to transfer_back_to_superviso tool as an argument.
                """
    response = llm_with_tools.invoke([SystemMessage(sys_prompt)]+state["messages"])
    # final_response = response["messages"][-1]
    # if final_response.tool_calls[0]["name"] == "transfer_back_to_supervisor":
    #     ai_msg = final_response.tool_calls[0]['args']['final_response']
    # final
    return {"messages" : [response],}