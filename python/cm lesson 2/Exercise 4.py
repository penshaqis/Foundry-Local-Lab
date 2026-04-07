from foundry_local import FoundryLocalManager 
 
manager = FoundryLocalManager() 
manager.start_service() 
 
# Get detailed info about a specific model 
info = manager.get_model_info("qwen2.5-7b") 
if info: 
    print(f"Alias:              {info.alias}") 
    print(f"Model ID:           {info.id}") 
    print(f"Version:            {info.version}") 
    print(f"Task:               {info.task}") 
    print(f"Device Type:        {info.device_type}") 
    print(f"Execution Provider: {info.execution_provider}") 
    print(f"File Size (MB):     {info.file_size_mb}") 
    print(f"Publisher:          {info.publisher}") 
    print(f"License:            {info.license}") 
    print(f"Tool Calling:       {info.supports_tool_calling}") 