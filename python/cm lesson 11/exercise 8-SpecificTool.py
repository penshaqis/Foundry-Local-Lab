import json
import openai
from foundry_local import FoundryLocalManager

# Tool calling requires a model that supports it.
# Qwen 2.5 models and Phi-4-mini support tool calling in Foundry Local.
alias = "qwen2.5-7b"

# Step 1: Start Foundry Local and bootstrap the model
print("Starting Foundry Local service...")
manager = FoundryLocalManager(alias)

client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key,
)

model_id = manager.get_model_info(alias).id

# Step 2: Define tools the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. London",
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_population",
            "description": "Get the population of a given city",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. London",
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_keyclient",
            "description": "Get key client for a given city",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. London",
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            },
        },
    },
]


# Step 3: Simulate tool execution (in a real app these would call APIs)
def execute_tool(name, arguments):
    if name == "get_weather":
        city = arguments.get("city", "Unknown")
        return json.dumps({"city": city, "temperature": "18°C", "condition": "Partly cloudy"})
    elif name == "get_keyclient":
        city = arguments.get("city", "Unknown")
        keyclient = {"london": "Willis Towers", "paris": "SCOR Re", "tokyo": "Mitsui Amlin"}
        return json.dumps({"city": city, "key client": keyclient})
    elif name == "get_population":
        city = arguments.get("city", "Unknown")
        populations = {"london": "8.8 million", "paris": "2.1 million", "tokyo": "14 million"}
        pop = populations.get(city.lower(), "Unknown")
        return json.dumps({"city": city, "population": pop})
    return json.dumps({"error": "Unknown tool"})


# Step 4: Send a message that should trigger tool calls
messages = [
    {"role": "system", "content": "You are an assistant with access to tools. If a user's request can be answered using a tool, you MUST call that tool. "
    "Do not provide information from your own knowledge if a tool is available."},
    {"role": "user", "content": "Who is our main client in London?"}, #Adding "/no_think" removes thinking output but suboptimal reasoning (e.g. only 1 of 2 when asking for popl & weather)
]

print(f"\nUser: {messages[1]['content']}\n")

response = client.chat.completions.create(
    model=model_id,
    messages=messages,
    tools=tools,
    tool_choice={"type": "function","function":{"name":"get_keyclient"}},
    max_completion_tokens=2000,
    #reasoning_effort="none"
)

#assistant_message = response.choices[0].message
choice = response.choices[0]
assistant_message = choice.message

print("\n--- Assistant (tool planning phase) ---")
print(json.dumps(assistant_message.model_dump(), indent=2))


# Step 5: Handle tool calls if the model requests them
#if assistant_message.tool_calls:
if choice.finish_reason == "tool_calls":
    print(f"Model requested {len(assistant_message.tool_calls)} tool call(s):")
    messages.append(assistant_message.model_dump())


    for tool_call in assistant_message.tool_calls or []:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)
        print(f"  → {fn_name}({fn_args})")

        result = execute_tool(fn_name, fn_args)
         
        tool_msg = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        }
        messages.append(tool_msg)

        print("\n--- Tool response injected ---")
        print(tool_msg)


    # Step 6: Send the tool results back for the final answer

    print("\n--- Full message stack before final call ---")
    for i, m in enumerate(messages):
        print(f"{i}: {m['role']}")
        print(m.get("content"))


    print("\nFinal response:")
    final = client.chat.completions.create(
        model=model_id,
        messages=messages,
        tools=tools,
        max_completion_tokens=2000
    )
    print(final.choices[0].message.content)
else:
    # Model answered directly without calling tools
    print("Response:", assistant_message.content)

# Cleanup: unload the model to release resources
manager.unload_model(alias)
