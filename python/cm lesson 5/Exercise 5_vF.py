import asyncio
import json
from agent_framework_foundry_local import FoundryLocalClient

# ==========================================
# 1. RESPONSE FORMAT CONFIGURATION
# ==========================================
# Options: "TEXT", "JSON", "XML", "YAML"
RESPONSE_FORMAT = "TEXT" 

# Example Schema for JSON (useful for Casualty/Reinsurance use cases)
# This guides the LLM on EXACTLY how to structure the data.
JSON_STRUCTURE_GUIDE = {
    "analysis_metadata": {
        "sentiment": "positive|negative|neutral",
        "confidence_score": "float (0.0-1.0)",
        "source_reliability": "string"
    },
    "extracted_entities": ["list of key terms/entities"],
    "summary": "brief reason", # originally "string", but for sentiment analysis we want a breif reason
    "recommended_action": "string",
    "reasoning_steps": ["list of logical steps taken"]
}

# ==========================================
# 2. AGENT IDENTITY CONFIGURATION
# ==========================================
AGENT_CONFIG = {
    "name": "Sentiment_Analysis_Agent",
    "base_instructions": "You are a sentiment analysis agent. Analyze the input and provide technical insights.",
}

# ==========================================
# 3. RUNTIME & MODEL CONFIGURATION
# ==========================================
USE_QWEN = True 
STREAMING_ENABLED = False # JSON/XML is often safer with non-streaming (False) to ensure valid closing tags
MODEL_ALIAS = "qwen2.5-7b" if USE_QWEN else "phi-3.5-mini"

# ==========================================
# 4. FORMATTING UTILITY
# ==========================================
def get_format_instructions():
    """Injects formatting constraints into the system prompt."""
    if RESPONSE_FORMAT == "JSON":
        return f"\n\nCRITICAL: Return ONLY valid JSON. Follow this schema exactly: {json.dumps(JSON_STRUCTURE_GUIDE)}"
    elif RESPONSE_FORMAT == "XML":
        return "\n\nCRITICAL: Return ONLY valid XML. Use <analysis>, <summary>, and <action> tags."
    elif RESPONSE_FORMAT == "YAML":
        return "\n\nCRITICAL: Return ONLY valid YAML format. Do not use Markdown code blocks."
    return "" # Default to plain text

# ==========================================
# 5. INTERACTION FUNCTIONS
# ==========================================

async def handle_non_streaming(agent, user_input):
    result = await agent.run(user_input)
    print(f"[{RESPONSE_FORMAT} Output]:\n{result}\n")

async def handle_streaming(agent, user_input):
    print(f"[{RESPONSE_FORMAT} Stream]: ", end="", flush=True)
    async for chunk in agent.run(user_input, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")

# ==========================================
# 6. MAIN EXECUTION CONTROLLER
# ==========================================

async def main():
    client = FoundryLocalClient(model=MODEL_ALIAS)

    # Combine base instructions with formatting constraints
    full_instructions = AGENT_CONFIG["base_instructions"] + get_format_instructions()

    agent = client.as_agent(
        name=AGENT_CONFIG["name"],
        instructions=full_instructions,
        default_options={"temperature": 0.7, "max_tokens": 2000}
    )

    print(f"=== Agent: {AGENT_CONFIG['name']} | Model: {MODEL_ALIAS} ===")
    print(f"=== Format: {RESPONSE_FORMAT} | Streaming: {STREAMING_ENABLED} ===\n")

    try:
        while True:
            user_input = input("User Request: ")
            if user_input.strip().lower() in ("quit", "exit"):
                break
            
            if STREAMING_ENABLED:
                await handle_streaming(agent, user_input)
            else:
                await handle_non_streaming(agent, user_input)

    finally:
        client.manager.unload_model(MODEL_ALIAS)
        print(f"\nResources released.")

if __name__ == "__main__":
    asyncio.run(main())