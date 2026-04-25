"""
Foundry Local — Single Agent with Microsoft Agent Framework

Demonstrates creating a single AI agent using FoundryLocalClient
from the Microsoft Agent Framework. The agent runs entirely on-device
via Foundry Local — no cloud required.
"""

##RECALL: BEFORE TO CALL LLM USED 'foundry_local' & 'openai' NOT 'agent_framework_foundry_local' library
##-------------------------------------------
# import openai
# from foundry_local import FoundryLocalManager
##-------------------------------------------
##Step 1: Create a FoundryLocalManager and start the service
# print("Starting Foundry Local service...")
# manager = FoundryLocalManager()
# manager.start_service()
##-------------------------------------------
##Step 2: Check if the model is already downloaded
# print(f"Downloading model: {alias} (this may take several minutes)...")
# manager.download_model(alias)
##-------------------------------------------
##Step 3: Load the model into memory
# print(f"Loading model: {alias}...")
# manager.load_model(alias)
##-------------------------------------------
#-Step 4: Configure the OpenAI client to use the local Foundry service.
# Foundry Local assigns a dynamic port — always use manager.endpoint | API_key is not required for local usage
# client = openai.OpenAI(
#    base_url=manager.endpoint,
#    # api_key=manager.api_key  
# )
##-------------------------------------------
#-Step 5: Or turn off streaming:
# response = client.chat.completions.create(
#    model=manager.get_model_info(alias).id,
#    messages=[{"role": "user", "content": "Why is fire hot?"}],
#    stream=False,
# )
# print(response.choices[0].message.content)
##-------------------------------------------

import asyncio
from agent_framework_foundry_local import FoundryLocalClient


async def main():
    alias = "phi-3.5-mini" #try next "qwen2.5-7b"

    print("=== Basic Foundry Local Client Agent Example ===")

    # FoundryLocalClient handles service start, model download, and loading
    client = FoundryLocalClient(model=alias)

    for model in client.manager.list_loaded_models():
        if model.alias == alias:
                print(f"Alias: {model.alias} -> Model id: {model.id}")
    print(f"Endpoint: {client.manager.endpoint}\n")

    # Create an agent with system instructions
    agent = client.as_agent(
        name="Joker",
        instructions="You are good at telling jokes.",
    )

    # Non-streaming: get the complete response at once
    print("--- Non-streaming ---")
    result = await agent.run("Tell me a joke about a pirate.")
    print(f"Agent: {result.text}\n")

    # Streaming: get results as they are generated
    print("--- Streaming ---")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run("Tell me a joke about a programmer.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()

    # Cleanup: unload the model to release resources
    client.manager.unload_model(alias)
    print(f"{model.alias} unloaded")

asyncio.run(main())