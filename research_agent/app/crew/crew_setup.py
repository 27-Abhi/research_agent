from app.agents.planner import planner_agent
from app.agents.researcher import researcher_agent
from app.agents.writer import writer_agent
from app.agents.critic import critic_agent

def run_crew(query: str):
    print("[Planning]...")
    tasks = planner_agent(query)

    print("[Tasks]:", tasks)

    print("\n[Researching]...")
    research = researcher_agent(tasks)

    print("\n[Writing report]...")
    draft = writer_agent(research)

    print("\n[Reviewing]...")
    final = critic_agent(draft)

    return final
