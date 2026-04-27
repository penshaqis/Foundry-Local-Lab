![Foundry Local](https://www.foundrylocal.ai/logos/foundry-local-logo-color.svg)

# Part 6: Multi-Agent Workflows

> **Goal:** Combine multiple specialised agents into coordinated pipelines that divide complex tasks among collaborating agents - all running locally with Foundry Local.

## Why Multi-Agent?

A single agent can handle many tasks, but complex workflows benefit from **Specialisation**. Instead of one agent trying to research, write, and edit simultaneously, you break the work into focused roles:

![Multi-Agent Workflow](../images/part6-multi-agent-flow.png)

| Pattern | Description |
|---------|-------------|
| **Sequential** | Output of Agent A feeds into Agent B → Agent C |
| **Feedback loop** | An evaluator agent can send work back for revision |
| **Shared context** | All agents use the same model/endpoint, but different instructions |
| **Typed output** | Agents produce structured results (JSON) for reliable hand-offs |

---

## Exercises

### Exercise 1 - Run the Multi-Agent Pipeline

The workshop includes a complete Researcher → Writer → Editor workflow.

<details>
<summary><strong>🐍 Python</strong></summary>

**Setup 1: Activate an Existing venv**
```bash
# search "Foundry_VENV_Windows_VSCode_Playbook.docx" for detailed info
# Step 1 - Open VS Code at Foundry-Local-Lab root
# Step 2 - Open Terminal → New Terminal (PowerShell).

# Step 3 - change to python subfolder
cd python

# Step 4 - Run venv\Scripts\Activate.ps1 or .venv\Scripts\Activate.ps1
venv\Scripts\Activate.ps1 # Windows (PowerShell)

# Step 5 - Confirm '(venv) PS' appears in the terminal  
# Step 6 - Verify with: where python (must point into venv\Scripts) 
```

**Setup 2: Create a new venv (clean reset)**
```bash
# search "Foundry_VENV_Windows_VSCode_Playbook.docx" for detailed info
# Step 1 - change to python subfolder
cd python

# Step 2 - Delete old venv folder (not the .venv module in main Python instance)
# Step 3 - Run python -m venv venv to create a NEW venv at within the Python subfolder
python -m venv venv

# Step 4 - Activate with venv\Scripts\Activate.ps1
venv\Scripts\Activate.ps1 # Windows (PowerShell)

# Step 5 - Install deps: pip install -r requirements.txt
pip install -r requirements.txt

# Step 6 - Verify with: where python (must point into venv\Scripts)
```




**Run:**
```bash
python foundry-local-multi-agent.py
```

**What happens:**
1. **Researcher** receives a topic and returns bullet-point facts
2. **Writer** takes the research and drafts a blog post (3-4 paragraphs)
3. **Editor** reviews the article for quality and returns ACCEPT or REVISE

</details>


---

### Exercise 2 - Anatomy of the Pipeline

Study how agents are defined and connected:

**1. Shared model client**

All agents share the same Foundry Local model:

```python
# Python - FoundryLocalClient handles everything
from agent_framework_foundry_local import FoundryLocalClient

client = FoundryLocalClient(model_id="phi-3.5-mini")
```


**2. specialised instructions**

Each agent has a distinct persona:

| Agent | Instructions (summary) |
|-------|----------------------|
| Researcher | "Provide key facts, statistics, and background. Organise as bullet points." |
| Writer | "Write an engaging blog post (3-4 paragraphs) from the research notes. Do not invent facts." |
| Editor | "Review for clarity, grammar, and factual consistency. Verdict: ACCEPT or REVISE." |

**3. Data flows between agents**

```python
# Step 1 - output from researcher becomes input to writer
research_result = await researcher.run(f"Research: {topic}")

# Step 2 - output from writer becomes input to editor
writer_result = await writer.run(f"Write using:\n{research_result}")

# Step 3 - editor reviews both research and article
editor_result = await editor.run(
    f"Research:\n{research_result}\n\nArticle:\n{writer_result}"
)
```


> **Key insight:** Each agent receives the cumulative context from previous agents. The editor sees both the original research and the draft - this lets it check factual consistency.

---

### Exercise 3 - Add a Fourth Agent

Extend the pipeline by adding a new agent. Choose one:

| Agent | Purpose | Instructions |
|-------|---------|-------------|
| **Fact-Checker** | Verify claims in the article | `"You verify factual claims. For each claim, state whether it is supported by the research notes. Return JSON with verified/unverified items."` |
| **Headline Writer** | Create catchy titles | `"Generate 5 headline options for the article. Vary style: informative, clickbait, question, listicle, emotional."` |
| **Social Media** | Create promotional posts | `"Create 3 social media posts promoting this article: one for Twitter (280 chars), one for LinkedIn (professional tone), one for Instagram (casual with emoji suggestions)."` |

<details>
<summary><strong>🐍 Python - adding a Headline Writer</strong></summary>

```python
headline_agent = client.as_agent(
    name="HeadlineWriter",
    instructions=(
        "You are a headline specialist. Given an article, generate exactly "
        "5 headline options. Vary the style: informative, question-based, "
        "listicle, emotional, and provocative. Return them as a numbered list."
    ),
)

# After the editor accepts, generate headlines
headline_result = await headline_agent.run(
    f"Generate headlines for this article:\n\n{writer_result}"
)
print(f"\n--- Headlines ---\n{headline_result}")
```

</details>

---

### Exercise 4 - Design Your Own Workflow

Design a multi-agent pipeline for a different domain. Here are some ideas:

| Domain | Agents | Flow |
|--------|--------|------|
| **Code Review** | Analyser → Reviewer → Summariser | Analyse code structure → review for issues → produce summary report |
| **Customer Support** | Classifier → Responder → QA | Classify ticket → draft response → check quality |
| **Education** | Quiz Maker → Student Simulator → Grader | Generate quiz → simulate answers → grade and explain |
| **Data Analysis** | Interpreter → Analyst → Reporter | Interpret data request → analyse patterns → write report |

**Steps:**
1. Define 3+ agents with distinct `instructions`
2. Decide the data flow - what does each agent receive and produce?
3. Implement the pipeline using the patterns from Exercises 1-3
4. Add a feedback loop if one agent should evaluate another's work

---

## Orchestration Patterns

Here are orchestration patterns that apply to any multi-agent system (explored in depth in [Part 7](part7-zava-creative-writer.md)):

### Sequential Pipeline

![Sequential Pipeline](../images/part6-sequential-pipeline.png)

Each agent processes the output of the previous one. Simple and predictable.

### Feedback Loop

![Feedback Loop](../images/part6-feedback-loop.png)

An evaluator agent can trigger re-execution of earlier stages. The Zava Writer uses this: the editor can send feedback back to the researcher and writer.

### Shared Context

![Shared Context](../images/part6-shared-context.png)

All agents share a single `foundry_config` so they use the same model and endpoint.

---

## Key Takeaways

| Concept | What You Learned |
|---------|-----------------|
| Agent Specialisation | Each agent does one thing well with focused instructions |
| Data hand-offs | Output from one agent becomes input to the next |
| Feedback loops | An evaluator can trigger retries for higher quality |
| Structured output | JSON-formatted responses enable reliable agent-to-agent communication |
| Orchestration | A coordinator manages the pipeline sequence and error handling |
| Production patterns | Applied in [Part 7: Zava Creative Writer](part7-zava-creative-writer.md) |

---

## Next Steps

Continue to [Part 7: Zava Creative Writer - Capstone Application](part7-zava-creative-writer.md) to explore a production-style multi-agent app with 4 specialised agents, streaming output, product search, and feedback loops - available in Python, JavaScript, and C#.
