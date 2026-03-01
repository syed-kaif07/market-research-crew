from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

# ── LLM Configuration ──────────────────────────────────────────────────────────
llm = LLM(
    model=os.environ.get("MODEL"),
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.7,
    max_tokens=500,
    max_retries=3,
)

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
            llm=llm
        )

    @agent
    def competitive_intelligence_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["competitive_intelligence_analyst"],
            llm=llm
        )

    @agent
    def customer_insights_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_insights_researcher"],
            llm=llm
        )

    @agent
    def product_strategy_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["product_strategy_advisor"],
            llm=llm
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],
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
    def crew(self) -> Crew:          # Must be named 'crew' for @crew decorator
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            max_rpm=5
        )