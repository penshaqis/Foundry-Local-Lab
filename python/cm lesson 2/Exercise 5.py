from foundry_local import FoundryLocalManager 

alias = "phi-3.5-mini"  # Small model for quick testing 
manager = FoundryLocalManager() 
manager.start_service() 

# 1. Check what is in the catalog 
catalog = manager.list_catalog_models() 
print(f"Catalog: {len(catalog)} models") 

# 2. Check what is already downloaded 
cached = manager.list_cached_models() 
print(f"Cached: {len(cached)} models") 
for m in cached: 
    print(f"  - {m.alias} ({m.file_size_mb} MB)") 
 
# 3. Download a model 
print(f"\nDownloading {alias}...") 
manager.download_model(alias) 
print("Download complete") 
 
# 4. Verify it is in the cache now 
cached = manager.list_cached_models() 
print(f"Cached after download: {len(cached)} models") 
 
# 5. Load it 
print(f"\nLoading {alias}...") 
loaded_info = manager.load_model(alias) 
print(f"Loaded: {loaded_info.id}") 
 
# 6. Check what is loaded 
loaded = manager.list_loaded_models() 
print(f"\nLoaded models: {len(loaded)}") 
for m in loaded: 
    print(f"  - {m.alias} ({m.id})") 
 
# 7. Unload it 
print(f"\nUnloading {alias}...") 
manager.unload_model(alias) 
loaded = manager.list_loaded_models() 
print(f"Loaded models after unload: {len(loaded)}") 