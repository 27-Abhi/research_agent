from app.tools.search import search_web
from app.tools.summarizer import summarize

def researcher_agent(tasks):
    print(f"[AGENT ENTER] researcher | tasks={len(tasks)}")
    results = []

    for task in tasks:
        print(f"[Researching]: {task}")

        raw = search_web(task)
        summary = summarize(raw)

        results.append({
            "task": task,
            "summary": summary
        })

    print(f"[AGENT EXIT] researcher | results={len(results)}")
    return results
