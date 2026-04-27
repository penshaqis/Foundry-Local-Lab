"""
Foundry Local — Multi-Agent Workflow with Microsoft Agent Framework

Demonstrates a multi-agent pipeline running entirely on-device using
FoundryLocalClient:
  1. Researcher agent  — gathers background information
  2. Writer agent      — drafts an article from the research
  3. Editor agent      — reviews and provides feedback

Each agent has its own system instructions and persona. The agents
collaborate sequentially: Researcher → Writer → Editor.
"""

import asyncio

from agent_framework_foundry_local import FoundryLocalClient


# ==========================================
# 2. RUNTIME & MODEL CONFIGURATION
# ==========================================
# TOGGLE: Set to True for "qwen2.5-7b", False for "phi-3.5-mini"
USE_QWEN = False 

# TOGGLE: Set to True for streaming, False for standard response
STREAMING_ENABLED = True 

MODEL_ALIAS = "qwen2.5-7b" if USE_QWEN else "phi-3.5-mini"



async def main():
    # ── Start Foundry Local ──────────────────────────────────────────────
    print("=== Multi-Agent Workflow with Foundry Local ===")

    # FoundryLocalClient handles service start, model download, and loading
    client = FoundryLocalClient(model=MODEL_ALIAS)

    for model in client.manager.list_loaded_models():
        if model.alias == MODEL_ALIAS:
            print(f"Model: {model.id}")
    print(f"Endpoint: {client.manager.endpoint}\n")

    # ── Define agents ────────────────────────────────────────────────────
    researcher = client.as_agent(
        name="Researcher",
        instructions=(
            "You are a research assistant. When given a topic, provide a concise "
            "collection of key facts, statistics, and background information. "
            "Organize your findings as bullet points."
        ),
        default_options={"temperature": 0.7, "max_tokens": 2000}
    )

    writer = client.as_agent(
        name="Writer",
        instructions=(
            "You are a skilled blog writer. Using the research notes provided, "
            "write a short, engaging blog post (3-4 paragraphs). "
            "Include a catchy title. Do not make up facts beyond what is given."
        ),
        default_options={"temperature": 0.7, "max_tokens": 2000}
    )

    editor = client.as_agent(
        name="Editor",
        instructions=(
            "You are a senior editor. Review the blog post below for clarity, "
            "grammar, and factual consistency with the research notes. "
            "Provide a brief editorial verdict: ACCEPT if the post is "
            "publication-ready, or REVISE with specific suggestions."
        ),
        default_options={"temperature": 0.7, "max_tokens": 2000}
    )

    topic = "The history and future of renewable energy"

    # ── Agent workflow: Researcher → Writer → Editor ─────────────────────
    print("=" * 60)
    print(f"📋 Topic: {topic}")
    print("=" * 60)

    # Step 1 — Research
    print("\n🔍 Researcher is gathering information...")
    research_result = await researcher.run(
        f"Research the following topic and provide key facts:\n{topic}"
    )
    print(f"\n--- Research Notes ---\n{research_result.text}\n")

    # Step 2 — Write
    print("✍️  Writer is drafting the article...")
    writer_result = await writer.run(
        f"Write a blog post based on these research notes:\n\n{research_result.text}"
    )
    print(f"\n--- Draft Article ---\n{writer_result.text}\n")

    # Step 3 — Edit
    print("📝 Editor is reviewing the article...")
    editor_result = await editor.run(
        f"Review this article for quality and accuracy.\n\n"
        f"Research notes:\n{research_result.text}\n\n"
        f"Article:\n{writer_result.text}"
    )
    print(f"\n--- Editor Verdict ---\n{editor_result.text}\n")

    print("=" * 60)
    print("✅ Multi-agent workflow complete!")

    # Cleanup: unload the model to release resources
    client.manager.unload_model(MODEL_ALIAS)
    print(f"\n{MODEL_ALIAS} unloaded successfully.")

asyncio.run(main())
