import openai
from foundry_local import FoundryLocalManager 
 
# Pass an alias to the constructor - it handles everything: 
# 1. Starts the service if not running 
# 2. Downloads the model if not cached 
# 3. Loads the model into the inference server 
alias = "phi-3.5-mini"

manager = FoundryLocalManager(alias) 
 
# Ready to use immediately 
print(f"Endpoint: {manager.endpoint}") 
print(f"Model ID: {manager.get_model_info(alias).id}")

# Configure the OpenAI client to use the local Foundry service.
# Foundry Local assigns a dynamic port — always use manager.endpoint.
client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key  # API key is not required for local usage
)

# Generate a streaming chat completion
stream = client.chat.completions.create(
    model=manager.get_model_info(alias).id,
    messages=[{"role": "user", "content": "Who wins in best of 5 series of fights between a 100 men and a gorilla?"}],
    stream=True, #false for non-streaming response
)

# Print the streaming response
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True) #set flush to false for non-streaming response, i.e. if stream=False in client chat.completions.create()
print()