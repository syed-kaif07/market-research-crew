from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, SeleniumScrapingTool
from dotenv import load_dotenv

load_dotenv()

#create the tools for the agent
web_search_tool = SerperDevTool()
web_scraping_tool = ScrapeWebsiteTool()
Selenium_Scraping_Tool = SeleniumScrapingTool()

toolkit = [web_search_tool, web_scraping_tool, Selenium_Scraping_Tool]


#define the crew class
@CrewBase
class MarketResearchCrew():
    """MarketResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    #provide the path for config files for agents and tasks
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    ############ Agents ############
    @agent
    def market_research_specialist(self) -> Agent:
        return Agent(
            config = self.agents_config["market_research_specialist"],
            tools = toolkit
        )
    @agent
    def competitive_intelligence_analyst(self) -> Agent:
        return Agent(
            config = self.agents_config["competitive_intelligence_analyst"],
            tools = toolkit
        )
    @agent
    def customer_insights_researcher(self) -> Agent:
        return Agent(
            config = self.agents_config["customer_insights_researcher"],
            tools = toolkit
        )
    @agent
    def product_strategy_advisor(self) -> Agent:
        return Agent(
            config = self.agents_config["product_strategy_advisor"],
            tools = toolkit
        )    
    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config = self.agents_config["business_analyst"],
            tools = toolkit
        )

############ Tasks ############
    @task
    def market_research_task(self) -> Task:
        return Task(
            config = self.tasks_config("market_research_task")
        )
    @task
    def competitive_intelligence_task(self) -> Task:
        return Task(
            config = self.tasks_config("competitive_intelligence_task"),
            context = [self.market_research_task()]
        )
    @task
    def customer_insights_task(self) -> Task:
        return Task(
            config = self.tasks_config("customer_insights_task"),
            context = [self.market_research_task(),
                       self.competitive_intelligence_task()]
                       
        )
    @task
    def product_strategy_task(self) -> Task:
        return Task(
            config = self.tasks_config("product_strategy_task"),
            context = [self.market_research_task(),
                       self.competitive_intelligence_task(),
                       self.customer_insights_task()] 
        )    
    @task
    def business_analyst_task(self) -> Task:
        return Task(
            config = self.tasks_config("business_analyst_task"),
            context = [self.market_research_task(),
                       self.competitive_intelligence_task(),
                       self.customer_insights_task(),
                       self.product_strategy_task()]
        )
    
    ########### crew ############
    @crew
    def crew (self) -> Crew:
        return crew