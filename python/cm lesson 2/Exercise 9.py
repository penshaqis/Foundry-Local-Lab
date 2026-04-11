from foundry_local import FoundryLocalManager

manager = FoundryLocalManager()
manager.start_service()

alias = "qwen2.5-7b"
print(f"Full model name is {manager.get_model_info(alias).id}")

# Refresh the catalog to get the latest model list
manager.refresh_catalog()

# Check if a cached model has a newer version available
if manager.is_model_upgradeable(alias):
    print(f"{alias} has a newer version available!")
    manager.upgrade_model(alias)
    print("Upgrade complete")
else:
    print(f"{alias} is up to date")