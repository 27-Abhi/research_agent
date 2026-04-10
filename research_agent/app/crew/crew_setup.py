import os
from typing import Any

from app.agents.critic import critic_agent
from app.agents.planner import planner_agent
from app.agents.researcher import researcher_agent
from app.agents.writer import writer_agent


def _manual_pipeline(query: str) -> str:
    print("[PIPELINE] mode=manual")
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


def _coerce_crewai_output(result: Any) -> str:
    if result is None:
        return ""
    if hasattr(result, "raw"):
        return str(result.raw)
    if hasattr(result, "output"):
        return str(result.output)
    return str(result)


def _run_crewai_pipeline(query: str) -> str:
    from crewai import Agent, Crew, Process, Task

    print("[PIPELINE] mode=crewai")
    llm_backend = os.getenv("LLM_BACKEND", "ollama").strip().lower()
    ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:1B").strip()
    ollama_base = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat").strip()
    ollama_base = ollama_base.replace("/api/chat", "")
    crew_llm = f"ollama/{ollama_model}" if "/" not in ollama_model else ollama_model
    if llm_backend == "ollama":
        os.environ.setdefault("OPENAI_API_KEY", "not-needed-when-using-ollama")
        os.environ.setdefault("OLLAMA_BASE_URL", ollama_base)
        print(f"[CREWAI] llm={crew_llm} | base={ollama_base}")

    planner = Agent(
        role="Research Planner",
        goal="Break user topic into clear research tasks.",
        backstory="You design concise task plans for research workflows.",
        llm=crew_llm,
        allow_delegation=False,
        verbose=True,
    )

    researcher = Agent(
        role="Web Researcher",
        goal="Produce structured research notes with facts and source URLs.",
        backstory="You collect relevant web information and organize it clearly.",
        llm=crew_llm,
        allow_delegation=False,
        verbose=True,
    )

    writer = Agent(
        role="Report Writer",
        goal="Convert notes into a coherent markdown report.",
        backstory="You transform rough research notes into readable reports.",
        llm=crew_llm,
        allow_delegation=False,
        verbose=True,
    )

    critic = Agent(
        role="Report Critic",
        goal="Refine report quality, clarity, and structure.",
        backstory="You review drafts and improve readability and factual caution.",
        llm=crew_llm,
        allow_delegation=False,
        verbose=True,
    )

    planner_task = Task(
        description=(
            "Topic: {topic}\n"
            "Create 5 to 6 research tasks as a JSON list of short strings.\n"
            "Return JSON only."
        ),
        expected_output="A valid JSON list of research tasks.",
        agent=planner,
    )

    research_task = Task(
        description=(
            "Using the planner output, research the topic and produce structured notes.\n"
            "Include short source URLs for key claims when available.\n"
            "Use markdown sections."
        ),
        expected_output="Research notes in markdown with source references.",
        agent=researcher,
        context=[planner_task],
    )

    writer_task = Task(
        description=(
            "Turn research notes into a complete markdown report with headings:\n"
            "Introduction, Key Findings, and Conclusion."
        ),
        expected_output="A complete markdown report.",
        agent=writer,
        context=[research_task],
    )

    critic_task = Task(
        description=(
            "Improve the draft for clarity and structure.\n"
            "Remove repetition and keep claims grounded in provided research."
        ),
        expected_output="A polished final markdown report.",
        agent=critic,
        context=[writer_task],
    )

    crew = Crew(
        agents=[planner, researcher, writer, critic],
        tasks=[planner_task, research_task, writer_task, critic_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs={"topic": query})
    return _coerce_crewai_output(result).strip()


def run_crew(query: str) -> str:
    use_crewai = os.getenv("USE_CREWAI", "1").strip().lower() not in {"0", "false", "no"}

    if use_crewai:
        try:
            output = _run_crewai_pipeline(query)
            if output:
                return output
            print("[CREWAI] Empty output, falling back to manual pipeline.")
        except Exception as exc:
            print(f"[CREWAI] unavailable/error -> fallback manual | reason={exc}")

    return _manual_pipeline(query)
