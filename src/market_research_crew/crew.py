from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
import os
from crewai_tools import ScrapeWebsiteTool, SeleniumScrapingTool
from crewai.tools import tool

load_dotenv()

# ── LLM Configuration ──────────────────────────────────────────────────────────
llm = LLM(
    model=os.environ.get("MODEL"),           # groq/llama-3.3-70b-versatile
    api_key=os.environ.get("GROQ_API_KEY"),  # gsk_...
    temperature=0.7,
    max_tokens=1024
)

# ── Tools ──────────────────────────────────────────────────────────────────────
@tool("DuckDuckGo Search")
def duck_search_tool(query: str) -> str:
    """Search the web using DuckDuckGo. Input should be a search query string."""
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        return "\n".join([f"{r['title']}: {r['body']}" for r in results])



toolkit = [duck_search_tool]


# ── Crew ───────────────────────────────────────────────────────────────────────
@CrewBase
class MarketResearchCrew():
    """MarketResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    # ── Agents ─────────────────────────────────────────────────────────────────

    @agent
    def market_research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["market_research_specialist"],
            tools=toolkit,
            llm=llm
        )

    @agent
    def competitive_intelligence_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["competitive_intelligence_analyst"],
            tools=toolkit,
            llm=llm
        )

    @agent
    def customer_insights_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_insights_researcher"],
            tools=toolkit,
            llm=llm
        )

    @agent
    def product_strategy_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["product_strategy_advisor"],
            tools=toolkit,
            llm=llm
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],
            tools=toolkit,
            llm=llm
        )

    # ── Tasks ──────────────────────────────────────────────────────────────────

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_research_task"]
        )

    @task
    def competitive_intelligence_task(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_intelligence_task"],
            context=[self.market_research_task()]
        )

    @task
    def customer_insights_task(self) -> Task:
        return Task(
            config=self.tasks_config["customer_insights_task"],
            context=[
                self.market_research_task(),
                self.competitive_intelligence_task()
            ]
        )

    @task
    def product_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_strategy_task"],
            context=[
                self.market_research_task(),
                self.competitive_intelligence_task(),
                self.customer_insights_task()
            ]
        )

    @task
    def business_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config["business_analyst_task"],
            context=[
                self.market_research_task(),
                self.competitive_intelligence_task(),
                self.customer_insights_task(),
                self.product_strategy_task()
            ]
        )

    # ── Crew ───────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )