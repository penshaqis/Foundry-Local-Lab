"""
Foundry Local — Single Agent with Microsoft Agent Framework

Demonstrates creating a single AI agent using FoundryLocalClient
from the Microsoft Agent Framework. The agent runs entirely on-device
via Foundry Local — no cloud required.
"""

import asyncio


from agent_framework_foundry_local import FoundryLocalClient


async def main():
    #alias = "phi-3.5-mini" 
    alias = "qwen2.5-7b" 

    print("=== Basic Foundry Local Client Agent Example ===")

    # FoundryLocalClient handles service start, model download, and loading
    client = FoundryLocalClient(model=alias)

    for model in client.manager.list_loaded_models():
        if model.alias == alias:
                print(f"Alias: {model.alias} -> Model id: {model.id}")
                
    print(f"Endpoint: {client.manager.endpoint}\n")

    
    # Create an agent with system instructions
    agent = client.as_agent(
        name="Socratic Tutor",
        instructions="You are a Socratic tutor. Never give direct answers - instead, guide the student with thoughtful questions.",
    )
#------------------------------------------------------------------------------
    # Non-streaming: get the complete response at once
    print("Chat with the agent (type 'quit' to exit):\n")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("quit","exit"):
             break
        result = await agent.run(user_input)
        print(f"Agent: {result}\n")

#------------------------------------------------------------------------------
    # Streaming: get results as they are generated

    print("Chat with the agent (type 'quit' to exit):\n", end="", flush=True)
    while True:
         user_input = input("You: ")
         if user_input.strip().lower() in ("quit","exit"):
             break  
         print("Agent:")
         async for chunk in agent.run(user_input, stream=True):
             if chunk.text:
                 print(chunk.text, end="", flush=True)
         print()

#------------------------------------------------------------------------------

    # Cleanup: unload the model to release resources
    client.manager.unload_model(alias)
    print(f"{model.alias} unloaded")


asyncio.run(main())