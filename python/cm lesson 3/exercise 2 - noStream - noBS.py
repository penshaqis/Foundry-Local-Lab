
import openai
from foundry_local import FoundryLocalManager

# By using an alias, the most suitable model variant will be
# downloaded for your end-user's device hardware.
alias = "qwen2.5-7b"

# Step 1: Create a FoundryLocalManager and start the service
print("Starting Foundry Local service...")
manager = FoundryLocalManager()
manager.start_service()

# # Step 2: Check if the model is already downloaded
# cached = manager.list_cached_models()
# catalog_info = manager.get_model_info(alias)
# is_cached = any(m.id == catalog_info.id for m in cached) if catalog_info else False

# if is_cached:
#     print(f"Model already downloaded: {alias}")
# else:
#     print(f"Downloading model: {alias} (this may take several minutes)...")
#     manager.download_model(alias)
#     print(f"Download complete: {alias}")

# # Step 3: Load the model into memory
# print(f"Loading model: {alias}...")
# manager.load_model(alias)
# print(f"Cached models: {[m.id for m in cached]}")

# Configure the OpenAI client to use the local Foundry service.
# Foundry Local assigns a dynamic port — always use manager.endpoint.
client = openai.OpenAI(
    base_url=manager.endpoint,
    # api_key=manager.api_key  # API key is not required for local usage
)

# Or turn off streaming:
response = client.chat.completions.create(
    model=manager.get_model_info(alias).id,
    messages=[{"role": "user", "content": "Why is fire hot?"}],
    stream=False,
)
print(response.choices[0].message.content)

# # Cleanup: unload the model to release resources
# manager.unload_model(alias)  # newline at end