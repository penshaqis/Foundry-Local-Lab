![Foundry Local](https://www.foundrylocal.ai/logos/foundry-local-logo-color.svg)

# Part 2: Foundry Local SDK Deep Dive

> **Goal:** Master the Foundry Local SDK to manage models, services, and caching programmatically - and understand why the SDK is the recommended approach over the CLI for building applications.

## Overview

In Part 1 you used the **Foundry Local CLI** to download and run models interactively. The CLI is great for exploration, but when you build real applications you need **programmatic control**. The Foundry Local SDK gives you that - it manages the **control plane** (starting the service, discovering models, downloading, loading) so your application code can focus on the **data plane** (sending prompts, receiving completions).

This lab teaches you the full SDK API surface across Python, JavaScript, and C#. By the end you will understand every method available and when to use each one.

## Learning Objectives

By the end of this lab you will be able to:

- Explain why the SDK is preferred over the CLI for application development
- Install the Foundry Local SDK for Python, JavaScript, or C#
- Use `FoundryLocalManager` to start the service, manage models, and query the catalog
- List, download, load, and unload models programmatically
- Inspect model metadata using `FoundryModelInfo`
- Understand the difference between catalog, cache, and loaded models
- Use the constructor bootstrap (Python) and `create()` + catalog pattern (JavaScript)
- Understand the C# SDK redesign and its object-oriented API

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Foundry Local CLI** | Installed and on your `PATH` ([Part 1](part1-getting-started.md)) |
| **Language runtime** | **Python 3.9+** and/or **Node.js 18+** and/or **.NET 9.0+** |

---

## Concept: SDK vs CLI - Why Use the SDK?

| Aspect | CLI (`foundry` command) | SDK (`foundry-local-sdk`) |
|--------|------------------------|--------------------------|
| **Use case** | Exploration, manual testing | Application integration |
| **Service management** | Manual: `foundry service start` | Automatic: `manager.start_service()` (Python) / `manager.startWebService()` (JS/C#) |
| **Port discovery** | Read from CLI output | `manager.endpoint` (Python) / `manager.urls[0]` (JS/C#) |
| **Model download** | `foundry model download alias` | `manager.download_model(alias)` (Python) / `model.download()` (JS/C#) |
| **Error handling** | Exit codes, stderr | Exceptions, typed errors |
| **Automation** | Shell scripts | Native language integration |
| **Deployment** | Requires CLI on end-user machine | C# SDK can be self-contained (no CLI needed) |

> **Key insight:** The SDK handles the entire lifecycle: starting the service, checking the cache, downloading missing models, loading them, and discovering the endpoint, in a few lines of code. Your application does not need to parse CLI output or manage subprocesses.

---

## Lab Exercises

### Exercise 1: Install the SDK

<details>
<summary><h3>🐍 Python</h3></summary>

```bash
pip install foundry-local-sdk
```

Verify the installation:

```python
from foundry_local import FoundryLocalManager
print("SDK installed successfully")
```

</details>


---

### Exercise 2: Start the Service and List the Catalog

The first thing any application does is start the Foundry Local service and discover what models are available.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
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
```

#### Python SDK - Service Management Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `is_service_running()` | `() -> bool` | Check if the service is running |
| `start_service()` | `() -> None` | Start the Foundry Local service |
| `service_uri` | `@property -> str` | The base service URI |
| `endpoint` | `@property -> str` | The API endpoint (service URI + `/v1`) |
| `api_key` | `@property -> str` | API key (from env or default placeholder) |

#### Python SDK - Catalog Management Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_catalog_models()` | `() -> list[FoundryModelInfo]` | List all models in the catalog |
| `refresh_catalog()` | `() -> None` | Refresh the catalog from the service |
| `get_model_info()` | `(alias_or_model_id: str, raise_on_not_found=False) -> FoundryModelInfo \| None` | Get info for a specific model |

</details>

---

### Exercise 3: Download and Load a Model

The SDK separates downloading (to disk) from loading (into memory). This lets you pre-download models during setup and load them on demand.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
from foundry_local import FoundryLocalManager

alias = "phi-3.5-mini"

# Option A: Manual step-by-step
manager = FoundryLocalManager()
manager.start_service()

# Check cache first
cached = manager.list_cached_models()
model_info = manager.get_model_info(alias)
is_cached = any(m.id == model_info.id for m in cached) if model_info else False

if not is_cached:
    print(f"Downloading {alias}...")
    manager.download_model(alias)

print(f"Loading {alias}...")
loaded = manager.load_model(alias)
print(f"Loaded: {loaded.id}")
print(f"Endpoint: {manager.endpoint}")

# Option B: One-liner bootstrap (recommended)
# Pass alias to constructor - it starts the service, downloads, and loads automatically
manager = FoundryLocalManager(alias)
print(f"Ready! Endpoint: {manager.endpoint}")
```

#### Python - Model Management Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `download_model()` | `(alias_or_model_id, token=None, force=False) -> FoundryModelInfo` | Download a model to local cache |
| `load_model()` | `(alias_or_model_id, ttl=600) -> FoundryModelInfo` | Load a model into the inference server |
| `unload_model()` | `(alias_or_model_id, force=False) -> None` | Unload a model from the server |
| `list_loaded_models()` | `() -> list[FoundryModelInfo]` | List all currently loaded models |

#### Python - Cache Management Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_cache_location()` | `() -> str` | Get the cache directory path |
| `list_cached_models()` | `() -> list[FoundryModelInfo]` | List all downloaded models |

</details>


---

### Exercise 4: Inspect Model Metadata

The `FoundryModelInfo` object contains rich metadata about each model. Understanding these fields helps you choose the right model for your application.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
from foundry_local import FoundryLocalManager

manager = FoundryLocalManager()
manager.start_service()

# Get detailed info about a specific model
info = manager.get_model_info("phi-3.5-mini")
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
```

</details>



#### FoundryModelInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `alias` | string | Short name (e.g. `phi-3.5-mini`) |
| `id` | string | Unique model identifier |
| `version` | string | Model version |
| `task` | string | `chat-completions` or `automatic-speech-recognition` |
| `device_type` | DeviceType | CPU, GPU, or NPU |
| `execution_provider` | string | Runtime backend (CUDA, CPU, QNN, WebGPU, etc.) |
| `file_size_mb` | int | Size on disk in MB |
| `supports_tool_calling` | bool | Whether the model supports function/tool calling |
| `publisher` | string | Who published the model |
| `license` | string | License name |
| `uri` | string | Model URI |
| `prompt_template` | dict/null | Prompt template, if any |

---

### Exercise 5: Manage Model Lifecycle

Practice the full lifecycle: list → download → load → use → unload.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
from foundry_local import FoundryLocalManager

alias = "qwen2.5-0.5b"  # Small model for quick testing

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
```

</details>


---

### Exercise 6: The Quick-Start Patterns

Each language provides a shortcut to start the service and load a model in one call. These are the **recommended patterns** for most applications.

<details>
<summary><h3>🐍 Python - Constructor Bootstrap</h3></summary>

```python
from foundry_local import FoundryLocalManager

# Pass an alias to the constructor - it handles everything:
# 1. Starts the service if not running
# 2. Downloads the model if not cached
# 3. Loads the model into the inference server
manager = FoundryLocalManager("phi-3.5-mini")

# Ready to use immediately
print(f"Endpoint: {manager.endpoint}")
print(f"Model ID: {manager.get_model_info('phi-3.5-mini').id}")
```

The `bootstrap` parameter (default `True`) controls this behaviour. Set `bootstrap=False` if you want manual control:

```python
# Manual mode - nothing happens automatically
manager = FoundryLocalManager(bootstrap=False)
```

</details>

---

### Exercise 8: Model Variants and Hardware Selection

Models can have multiple **variants** optimised for different hardware. The SDK selects the best variant automatically, but you can also inspect and choose manually.


<details>
<summary><h3>🐍 Python</h3></summary>

In Python, the SDK automatically selects the best variant based on hardware. Use `get_model_info()` to see what was selected:

```python
from foundry_local import FoundryLocalManager

manager = FoundryLocalManager()
manager.start_service()

info = manager.get_model_info("phi-3.5-mini")
print(f"Selected model: {info.id}")
print(f"Device: {info.device_type}")
print(f"Provider: {info.execution_provider}")
```

</details>

#### Models with NPU Variants

Some models have NPU-optimised variants for devices with Neural Processing Units (Qualcomm Snapdragon, Intel Core Ultra):

| Model | NPU Variant Available |
|-------|:---:|
| phi-3.5-mini | ✅ |
| phi-3-mini-128k | ✅ |
| phi-3-mini-4k | ✅ |
| deepseek-r1-14b | ✅ |
| deepseek-r1-7b | ✅ |
| qwen2.5-1.5b | ✅ |
| qwen2.5-7b | ✅ |

> **Tip:** On NPU-capable hardware, the SDK automatically selects the NPU variant when available. You do not need to change your code. For C# projects on Windows, add the `Microsoft.AI.Foundry.Local.WinML` NuGet package to enable the QNN execution provider — QNN is delivered as a plugin EP through WinML.

---

### Exercise 9: Model Upgrades and Catalog Refresh

The model catalogue is updated periodically. Use these methods to check for and apply updates.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
from foundry_local import FoundryLocalManager

manager = FoundryLocalManager()
manager.start_service()

alias = "phi-3.5-mini"

# Refresh the catalog to get the latest model list
manager.refresh_catalog()

# Check if a cached model has a newer version available
if manager.is_model_upgradeable(alias):
    print(f"{alias} has a newer version available!")
    manager.upgrade_model(alias)
    print("Upgrade complete")
else:
    print(f"{alias} is up to date")
```

</details>

---

### Exercise 10: Working with Reasoning Models

The **phi-4-mini-reasoning** model includes chain-of-thought reasoning. It wraps its internal thinking in `<think>...</think>` tags before producing its final answer. This is useful for tasks that require multi-step logic, maths, or problem-solving.

<details>
<summary><h3>🐍 Python</h3></summary>

```python
import openai
from foundry_local import FoundryLocalManager

# phi-4-mini-reasoning is ~4.6 GB
manager = FoundryLocalManager("phi-4-mini-reasoning")

client = openai.OpenAI(base_url=manager.endpoint, api_key=manager.api_key)
model_id = manager.get_model_info("phi-4-mini-reasoning").id

response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": "What is 17 × 23?"}],
)

content = response.choices[0].message.content

# The model wraps its thinking in <think>...</think> tags
if "<think>" in content and "</think>" in content:
    think_start = content.index("<think>") + len("<think>")
    think_end = content.index("</think>")
    thinking = content[think_start:think_end].strip()
    answer = content[think_end + len("</think>"):].strip()
    print(f"Thinking: {thinking}")
    print(f"Answer: {answer}")
else:
    print(content)
```

</details>


> **When to use reasoning models:**
> - Maths and logic problems
> - Multi-step planning tasks
> - Complex code generation
> - Tasks where showing working improves accuracy
>
> **Trade-off:** Reasoning models produce more tokens (the `<think>` section) and are slower. For simple Q&A, a standard model like phi-3.5-mini is faster.

---

### Exercise 11: Understanding Aliases and Hardware Selection

When you pass an **alias** (like `phi-3.5-mini`) instead of a full model ID, the SDK automatically selects the best variant for your hardware:

| Hardware | Selected Execution Provider |
|----------|---------------------------|
| NVIDIA GPU (CUDA) | `CUDAExecutionProvider` |
| Qualcomm NPU | `QNNExecutionProvider` (via WinML plugin) |
| Intel NPU | `OpenVINOExecutionProvider` |
| AMD GPU | `VitisAIExecutionProvider` |
| NVIDIA RTX | `NvTensorRTRTXExecutionProvider` |
| Any device (fallback) | `CPUExecutionProvider` or `WebGpuExecutionProvider` |

```python
from foundry_local import FoundryLocalManager

manager = FoundryLocalManager()
manager.start_service()

# The alias resolves to the best variant for YOUR hardware
info = manager.get_model_info("phi-3.5-mini")
print(f"Selected variant: {info.id}")
print(f"Execution provider: {info.execution_provider}")
print(f"Device type: {info.device_type}")
```

> **Tip:** Always use aliases in your application code. When you deploy to a user's machine, the SDK picks the optimal variant at runtime - CUDA on NVIDIA, QNN on Qualcomm, CPU elsewhere.


---

## Complete API Reference

### Python

| Category | Method | Description |
|----------|--------|-------------|
| **Init** | `FoundryLocalManager(alias?, bootstrap=True)` | Create manager; optionally bootstrap with a model |
| **Service** | `is_service_running()` | Check if service is running |
| **Service** | `start_service()` | Start the service |
| **Service** | `endpoint` | API endpoint URL |
| **Service** | `api_key` | API key |
| **Catalog** | `list_catalog_models()` | List all available models |
| **Catalog** | `refresh_catalog()` | Refresh the catalog |
| **Catalog** | `get_model_info(alias_or_model_id)` | Get model metadata |
| **Cache** | `get_cache_location()` | Cache directory path |
| **Cache** | `list_cached_models()` | List downloaded models |
| **Model** | `download_model(alias_or_model_id)` | Download a model |
| **Model** | `load_model(alias_or_model_id, ttl=600)` | Load a model |
| **Model** | `unload_model(alias_or_model_id)` | Unload a model |
| **Model** | `list_loaded_models()` | List loaded models |
| **Model** | `is_model_upgradeable(alias_or_model_id)` | Check if a newer version is available |
| **Model** | `upgrade_model(alias_or_model_id)` | Upgrade a model to the latest version |
| **Service** | `httpx_client` | Pre-configured HTTPX client for direct API calls |


---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| **SDK vs CLI** | The SDK provides programmatic control - essential for applications |
| **Control plane** | The SDK manages services, models, and caching |
| **Dynamic ports** | Always use `manager.endpoint` (Python) or `manager.urls[0]` (JS/C#) - never hardcode a port |
| **Aliases** | Use aliases for automatic hardware-optimal model selection |
| **Quick-start** | Python: `FoundryLocalManager(alias)`, JS: `FoundryLocalManager.create()` + `await catalog.getModel(alias)` |
| **C# redesign** | v0.8.0+ is self-contained - no CLI needed on end-user machines |
| **Model lifecycle** | Catalog → Download → Load → Use → Unload |
| **FoundryModelInfo** | Rich metadata: task, device, size, license, tool calling support |
| **ChatClient** | `createChatClient()` (JS) / `GetChatClientAsync()` (C#) for OpenAI-free usage |
| **Variants** | Models have hardware-specific variants (CPU, GPU, NPU); selected automatically |
| **Upgrades** | Python: `is_model_upgradeable()` + `upgrade_model()` to keep models current |
| **Catalog refresh** | `refresh_catalog()` (Python) / `updateModels()` (JS) to discover new models |

---

## Resources

| Resource | Link |
|----------|------|
| SDK Reference (all languages) | [Microsoft Learn - Foundry Local SDK Reference](https://learn.microsoft.com/en-us/azure/foundry-local/reference/reference-sdk) |
| Integrate with inference SDKs | [Microsoft Learn - Inference SDK Integration](https://learn.microsoft.com/en-us/azure/foundry-local/how-to/how-to-integrate-with-inference-sdks) |
| C# SDK API Reference | [Foundry Local C# API Reference](https://aka.ms/fl-csharp-api-ref) |
| C# SDK Samples | [GitHub - Foundry Local SDK Samples](https://aka.ms/foundrylocalSDK) |
| Foundry Local website | [foundrylocal.ai](https://foundrylocal.ai) |

---

## Next Steps

Continue to [Part 3: Using the SDK with OpenAI](part3-sdk-and-apis.md) to connect the SDK to the OpenAI client library and build your first chat completion application.
