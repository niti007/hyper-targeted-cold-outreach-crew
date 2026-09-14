"""CrewAI crew definition: 3 agents, 3 sequential tasks, structured outputs."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from cold_outreach.llm import get_llm
from cold_outreach.models import ColdEmail, ICPProfile, OutreachAngle


@CrewBase
class OutreachCrew:
    """Hyper-targeted cold outreach crew: research -> angle -> email."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def icp_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["icp_scout"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            llm=get_llm("researcher"),
            verbose=True,
        )

    @agent
    def angle_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["angle_strategist"],
            llm=get_llm("strategist"),
            verbose=True,
        )

    @agent
    def email_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config["email_copywriter"],
            llm=get_llm("copywriter"),
            verbose=True,
        )

    @task
    def research_icp_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_icp_task"],
            agent=self.icp_scout(),
            output_pydantic=ICPProfile,
        )

    @task
    def match_offering_task(self) -> Task:
        return Task(
            config=self.tasks_config["match_offering_task"],
            agent=self.angle_strategist(),
            context=[self.research_icp_task()],
            output_pydantic=OutreachAngle,
        )

    @task
    def write_email_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_email_task"],
            agent=self.email_copywriter(),
            context=[self.research_icp_task(), self.match_offering_task()],
            output_pydantic=ColdEmail,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
