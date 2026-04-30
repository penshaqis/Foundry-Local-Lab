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
USE_QWEN = True 

# TOGGLE: Set to True for streaming, False for standard response
STREAMING_ENABLED = True 

MODEL_ALIAS = "qwen2.5-7b" if USE_QWEN else "phi-3.5-mini"

TOPIC = "Explain the history of the bismuth rotary device. What applications can be produced when combined with spinning and quantum mechanics?"

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
            "You are a Reinsurance research assistant. When given a topic, provide a concise "
            "CRITICAL DEFINITION: In (re)insurance, a 'Soft Market' is characterized by "
            "excess underwriting capacity (high supply) and lower demand, leading to "
            "intense competition and falling rates. A 'Hard Market' is the opposite. "
            "Ensure all findings adhere to these industry-standard definitions."
        ),
        default_options={"temperature": 0.2, "max_tokens": 1024}
    )

    writer = client.as_agent(
        name="Writer",
        instructions=(
            "You are a skilled blog writer. Using the research notes provided, "
            "write a short, engaging blog post (3-4 paragraphs). "
            "CRITICAL DEFINITION: In (re)insurance, a 'Soft Market' is characterized by "
            "excess underwriting capacity (high supply) and lower demand, leading to "
            "intense competition and falling rates. A 'Hard Market' is the opposite. "
            "Ensure all findings adhere to these industry-standard definitions."
            "Include a catchy title. Do not make up facts beyond what is given."
        ),
        default_options={"temperature": 0.7, "max_tokens": 1024}
    )

    editor = client.as_agent(
        name="Editor",
        instructions=(
            "You are a senior editor. Review the blog post below for clarity, "
            "grammar, and factual consistency with the research notes. "
            "Provide a brief editorial verdict: ACCEPT if the post is "
            "publication-ready, or REVISE with specific suggestions."
        ),
        default_options={"temperature": 0.2, "max_tokens": 1024}
    )

    factcheck_agent = client.as_agent(
        name="FactChecker",
        instructions=(
            "You are a pedantic Insurance Industry Auditor. Your sole job is to catch definition errors.\n\n"
            "CRITICAL KNOWLEDGE:\n"
            "- Soft Market = High Supply/Capacity + Low/Stable Demand = Low Prices.\n"
            "- Hard Market = Low Supply/Capacity + High Demand = High Prices.\n\n"
            "TASK:\n"
            "1. Scan the text for any definition of 'Soft Market'.\n"
            "2. If the text says demand exceeds supply, it is FACTUALLY WRONG.\n"
            "3. Output ONLY a JSON object. No conversational text.\n\n"
            "JSON STRUCTURE:\n"
            "{\n"
            "  'status': 'ERROR' or 'VERIFIED',\n"
            "  'errors': [{'claim': '...', 'correction': '...'}],\n"
            "  'explanation': 'Briefly explain why based on supply/demand logic'\n"
            "}"
        ),
        default_options={"temperature": 0.0, "max_tokens": 1024}
    )



    # ── Agent workflow: Researcher → Writer → Editor ─────────────────────
    print("=" * 60)
    print(f"📋 Topic: {TOPIC}")
    print("=" * 60)

    # Step 1 — Research
    print("\n🔍 Researcher is gathering information...")
    research_result = await researcher.run(
        f"Research the following topic and provide key facts:\n{TOPIC}"
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

    # Step 4 — Verify factual claims are supported
    print("📝 Fact Checker is verifying accuracy of factual statements...")
    factcheck_result = await factcheck_agent.run(
        f"Confirm article's factual claims are supported by empirical evidence.\n\n"
        f"Review the claims within the article approved by the editor:\n{writer_result.text}\n\n"
    )
    print(f"\n--- Fact-checker Report ---\n{factcheck_result.text}\n")


    print("=" * 60)
    print("✅ Multi-agent workflow complete!")

    # Cleanup: unload the model to release resources
    client.manager.unload_model(MODEL_ALIAS)
    print(f"\n{MODEL_ALIAS} unloaded successfully.")

# ... all your agent definitions and the async def main() go above ...

if __name__ == "__main__":
    # This only runs if you double-click THIS file or run it via CMD
    asyncio.run(main())
