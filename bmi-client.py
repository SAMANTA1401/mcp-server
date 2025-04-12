
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from dotenv import load_dotenv
load_dotenv()
import json
from groq import Groq 
import asyncio

server_params = StdioServerParameters(command="python", args=["bmi-server.py"])

def llm_client(message:str):
    """" send a message to the llm and return the response"""
    client = Groq( api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You area an intelligent assistance. You will execute tasks as prompted",
                "role": "user",
                "content": message
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
        max_tokens=250,
        temperature=0.2
    )
    return chat_completion.choices[0].message.content.strip()

def get_prompt_to_identity_tool_and_arguments(query,tools):
    tools_description = "\n".join([f"-{tool.name}: {tool.description}, {tool.inputSchema}" for tool in tools])
    return ("You are a helpful assistant with access to the following tools:\n"
            f"{tools_description}\n\n"
            f"Given the user's query: {query}\n\n"
            "Please identify the tool that best matches the query and provide the arguments for the tool. "
            "Return the response in the following JSON format:\n"
            "{\n"
            '  "tool": "tool-name",\n'
            '    "arguments": {\n'
            '        "argument-name": "value"\n'
            "    }\n"
            "}\n"
            "Ensure that the JSON is valid and that the tool name and arguments match the tool's description. ")

# In Python, await is a keyword used within async functions to pause execution until an awaitable object 
# (like a coroutine, Task, or Future) completes. This allows other tasks to run concurrently while the
#  current task is waiting, making asynchronous programming more efficient. 



async def run (query:str):
    async with stdio_client(server_params) as (read, write): # run bmi-server.py
        async with ClientSession(read, write) as session:
            # Send a request to the server
            await session.initialize()
            tools = await session.list_tools() # collect and list tools from bmi-server.py
            print(f"Available tools:{tools}")
            prompt = get_prompt_to_identity_tool_and_arguments(query, tools.tools) # create prompt to choose right tools and arguments
            print(prompt)

            llm_response = llm_client(prompt) # get  tools and argument in json format
            print(f"llm_response: {llm_response}")

            tool_call = json.loads(llm_response) # load json for tools and argument
            result = await session.call_tool(tool_call["tool"], tool_call["arguments"]) # call tool function 
            print(f"Result: {result}")

            print(f"BMI for weight {tool_call["arguments"]["weight"]}kg and height {tool_call["arguments"]["height"]}m is {result.content[0].text}")

if __name__ == "__main__":
    query = "calculate bmi for a person with weight 70kg and height 1.75m"
    asyncio.run(run(query))

