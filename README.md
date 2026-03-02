# 🧠 Market Research Crew

A multi-agent AI system built with **CrewAI** and powered by **Groq's LLaMA 3.3 70B** model. Five specialized AI agents collaborate sequentially to produce a comprehensive market research report for any product idea.

---

## 🚀 Demo

Input a product idea like `"AI-powered smart home assistant"` and the crew generates:

- 📊 Market Research Report
- 🕵️ Competitive Intelligence Report
- 👥 Customer Insights Report
- 🗺️ Product Strategy Roadmap
- 📈 Business Analysis Report

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

## 🛠️ Tech Stack

- **Framework:** [CrewAI](https://crewai.com)
- **LLM:** Groq — `llama-3.3-70b-versatile` (free tier)
- **Language:** Python 3.13
- **Package Manager:** uv

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/syed-kaif07/market-research-crew.git
cd market-research-crew
```

### 2. Install dependencies
```bash
pip install crewai uv
uv sync
```

### 3. Set up environment variables
Create a `.env` file in the root directory:
```env
MODEL=groq/llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: [console.groq.com](https://console.groq.com)

### 4. Run the crew
```bash
crewai run
```

---


---

## 🔧 Configuration

Modify the product idea in `src/market_research_crew/main.py`:

```python
inputs = {
    "product_idea": "Your product idea here"
}
```

---

## 📌 Notes

- Uses **Groq's free tier** — no credit card required
- Agents run **sequentially**, each building on previous results
- Rate limit: 12,000 tokens/minute on free tier

---

## 📬 Connect

Built by [Syed Kaifuddin](https://github.com/syed-kaif07)
