import os
import asyncio
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Check for API Key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    print("Please set it in .env or export it.")
    sys.exit(1)

client = Anthropic(api_key=api_key)

async def run_agent():
    # Define server connection parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None # Inherit env
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            tool_definitions = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools.tools
            ]
            
            print(f"Connected to MCP Server. Found {len(tools.tools)} tools.")
            
            # Simple interaction loop
            while True:
                try:
                    user_input = input("\nYou: ")
                    if user_input.lower() in ["quit", "exit"]:
                        break
                    
                    messages = [{"role": "user", "content": user_input}]
                    
                    # Call Claude
                    response = client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=1000,
                        messages=messages,
                        tools=tool_definitions
                    )
                    
                    # Process response
                    final_content = []
                    
                    # Handle tool use
                    if response.stop_reason == "tool_use":
                        for content in response.content:
                            if content.type == "tool_use":
                                print(f"[Agent] Calling tool: {content.name}")
                                tool_result = await session.call_tool(
                                    content.name,
                                    arguments=content.input
                                )
                                messages.append({"role": "assistant", "content": response.content})
                                messages.append({
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "tool_result",
                                            "tool_use_id": content.id,
                                            "content": str(tool_result.content)
                                        }
                                    ]
                                })
                        
                         # Get follow-up response from Claude
                        response_followup = client.messages.create(
                             model="claude-3-opus-20240229",
                             max_tokens=1000,
                             messages=messages,
                             tools=tool_definitions
                        )
                        print(f"Agent: {response_followup.content[0].text}")

                    else:
                        print(f"Agent: {response.content[0].text}")
                        
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_agent())
