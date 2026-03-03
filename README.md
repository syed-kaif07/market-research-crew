# 🧠 Market Research Crew

A multi-agent AI system built with **CrewAI** and powered by **Groq's LLaMA 3.3 70B** model. Five specialized AI agents collaborate sequentially to produce a comprehensive market research report for any product idea — with a **Streamlit UI** and **live terminal agent monitoring**.

---

## 🚀 Demo

Input a product idea like `"AI-powered smart home assistant"` and the crew generates:

- 📊 Market Research Report
- 🕵️ Competitive Intelligence Report
- 👥 Customer Insights Report
- 🗺️ Product Strategy Roadmap
- 📈 Business Analysis Report

> While the Streamlit UI tracks agent progress in real time, the **IDE terminal streams live CrewAI verbose output** — showing every agent's thoughts, tool calls, and completions as they happen.

---

## 🤖 Agents

| Agent | Role |
|-------|------|
| `market_research_specialist` | Analyzes industry size, trends, and opportunities |
| `competitive_intelligence_analyst` | Evaluates competitors, pricing, and market share |
| `customer_insights_researcher` | Uncovers customer personas, pain points, and needs |
| `product_strategy_advisor` | Develops positioning strategy and feature roadmap |
| `business_analyst` | Synthesizes findings into actionable recommendations |

---

## 🏗️ Architecture

```
User (Streamlit UI)
       │
       ▼
streamlit_app.py  ──────────────────────────────────────────────►  Browser UI
       │                                                           (agent cards,
       │  subprocess.Popen(stdout=None)                            reports, tabs)
       │
       ▼
main.py  ──►  CrewAI Crew  ──►  Agent 1  ──►  Agent 2  ──►  ...  ──►  Agent 5
       │             │
       │             └──  task_callback  ──►  Live colored banners in IDE terminal
       │
       ▼
  output/*.md  (one file per agent, picked up by Streamlit)
```

**Both the UI and the terminal update simultaneously** — the UI polls output files every 4 seconds while the terminal streams verbose agent output in real time.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | [CrewAI](https://crewai.com) |
| **LLM** | Groq — `llama-3.3-70b-versatile` (free tier) |
| **Frontend** | Streamlit |
| **Language** | Python 3.13 |
| **Package Manager** | uv |

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/syed-kaif07/market-research-crew.git
cd market-research-crew
```

### 2. Install dependencies
```bash
pip install uv
uv sync --prerelease=allow
```

### 3. Set up environment variables

Create a `.env` file in the root directory:
```env
MODEL=groq/llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: [console.groq.com](https://console.groq.com)

### 4. Run via Streamlit UI
```bash
python -m streamlit run src/market_research_crew/streamlit_app.py
```

### 5. Or run directly from terminal
```bash
python src/market_research_crew/main.py --product-idea "your idea here"
```

---

## 🖥️ Live Terminal Output

When running from either the UI or CLI, the IDE terminal shows live colored agent banners:

```
=================================================================
        MARKET RESEARCH CREW - AGENT PIPELINE
        Powered by CrewAI x Groq x LLaMA 3.3 70B
=================================================================

  Research Topic: future of Gen AI in health sector

  AGENT PIPELINE QUEUE:

  1. 📊  Market Research Specialist        [ QUEUED ]
  2. 🕵️  Competitive Intelligence Analyst  [ QUEUED ]
  3. 👥  Customer Insights Researcher      [ QUEUED ]
  4. 🗺️  Product Strategy Advisor          [ QUEUED ]
  5. 📈  Business Analyst                  [ QUEUED ]

-----------------------------------------------------------------
  >> AGENT 1/5 STARTING  📊  Market Research Specialist
-----------------------------------------------------------------

  ✓ AGENT 1/5 COMPLETE  📊  Market Research Specialist
  Time taken: 43.2s
  Progress: [█░░░░] 1/5
```

---

## 🔧 Configuration

Agents and tasks are configured via YAML files:

```
src/market_research_crew/config/
├── agents.yaml   ← agent roles, goals, and backstories
└── tasks.yaml    ← task descriptions and output file names
```

To change the LLM or tweak parameters, edit `crew.py`:
```python
llm = LLM(
    model=os.environ.get("MODEL"),
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.7,
    max_tokens=2048,
    max_retries=5,
    timeout=120,
)
```

---

## 📌 Notes

- Uses **Groq's free tier** — no credit card required
- Agents run **sequentially**, each building on previous results
- Rate limit: 12,000 tokens/minute on free tier
- Use `--prerelease=allow` with `uv sync` — crewai[litellm] requires it

---

## 📝 Article
Read the full build story on Dev.to → [(https://dev.to/syed_kaif777/title-building-a-multi-agent-ai-market-research-tool-with-crewai-groq-22na)]

## 📬 Connect

Built by [Syed Kaifuddin](https://github.com/syed-kaif07)