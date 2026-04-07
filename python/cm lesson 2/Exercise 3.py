from foundry_local import FoundryLocalManager 
alias = "phi-3.5-mini" 

# Option A: Manual step-by-step 
# manager = FoundryLocalManager() 
# manager.start_service() 

# # Check cache first 
# cached = manager.list_cached_models() 
# model_info = manager.get_model_info(alias) 
# is_cached = any(m.id == model_info.id for m in cached) if model_info else False 
 
# if not is_cached: 
#     print(f"Downloading {alias}...") 
#     manager.download_model(alias) 
 
# print(f"Loading {alias}...") 
# loaded = manager.load_model(alias) 
# print(f"Loaded: {loaded.id}") 
# print(f"Endpoint: {manager.endpoint}") 
 
# Option B: One-liner bootstrap (recommended) 
# Pass alias to constructor - it starts the service, downloads, and loads automatically 
manager = FoundryLocalManager(alias) 
print(f"Ready! Endpoint: {manager.endpoint}") 