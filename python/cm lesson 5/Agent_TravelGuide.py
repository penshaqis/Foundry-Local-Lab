import asyncio
from agent_framework_foundry_local import FoundryLocalClient

# ==========================================
# 1. AGENT IDENTITY CONFIGURATION
# ==========================================
AGENT_CONFIG = {
    "name": "Travel Guide",
    "instructions": "You are a friendly travel guide. Give personalized recommendations for destinations, activities, and local cuisine.",
}

# ==========================================
# 2. RUNTIME & MODEL CONFIGURATION
# ==========================================
# TOGGLE: Set to True for "qwen2.5-7b", False for "phi-3.5-mini"
USE_QWEN = True 

# TOGGLE: Set to True for streaming, False for standard response
STREAMING_ENABLED = True 

MODEL_ALIAS = "qwen2.5-7b" if USE_QWEN else "phi-3.5-mini"

# ==========================================
# 3. INTERACTION FUNCTIONS
# ==========================================

async def handle_non_streaming(agent, user_input):
    """Executes a standard one-shot completion."""
    result = await agent.run(user_input)
    print(f"Agent: {result}\n")

async def handle_streaming(agent, user_input):
    """Executes a streaming completion with real-time output."""
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run(user_input, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")

# ==========================================
# 4. MAIN EXECUTION CONTROLLER
# ==========================================

async def main():
    print(f"=== Initializing Foundry Local: {MODEL_ALIAS} ===")

    # Initialize client and load model
    client = FoundryLocalClient(model=MODEL_ALIAS)

    # Print model metadata
    for model in client.manager.list_loaded_models():
        if model.alias == MODEL_ALIAS:
            print(f"Alias: {model.alias} -> Model id: {model.id}")
    print(f"Endpoint: {client.manager.endpoint}\n")

    # Create the agent using the identity config
    agent = client.as_agent(
        name=AGENT_CONFIG["name"],
        instructions=AGENT_CONFIG["instructions"],
    )

    print(f"Chatting with '{AGENT_CONFIG['name']}' (Type 'quit' to exit)")
    print(f"Mode: {'Streaming' if STREAMING_ENABLED else 'Non-Streaming'}\n")

    try:
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in ("quit", "exit"):
                break
            
            if STREAMING_ENABLED:
                await handle_streaming(agent, user_input)
            else:
                await handle_non_streaming(agent, user_input)

    finally:
        # Cleanup: release resources
        client.manager.unload_model(MODEL_ALIAS)
        print(f"\n{MODEL_ALIAS} unloaded successfully.")

if __name__ == "__main__":
    asyncio.run(main())