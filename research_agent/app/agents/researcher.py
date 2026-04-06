from app.tools.search import search_web
from app.tools.summarizer import summarize

def researcher_agent(tasks):
    results = []

    for task in tasks:
        print(f"[Researching]: {task}")

        raw = search_web(task)
        summary = summarize(raw)

        results.append({
            "task": task,
            "summary": summary
        })

    return results



