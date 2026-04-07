from foundry_local import FoundryLocalManager 
 
# Create a manager and start the service 
manager = FoundryLocalManager() 
manager.start_service() 
 
# List all models available in the catalog 
catalog = manager.list_catalog_models() 
print(f"Models available in catalog: {len(catalog)}") 
 
for model in catalog: 
    print(f"  - {model.alias} ({model.id})") 
    print(f"    Task: {model.task}, Size: {model.file_size_mb} MB") 
    print(f"    Device: {model.device_type}, Provider: {model.publisher}")