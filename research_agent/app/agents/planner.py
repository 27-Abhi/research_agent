from app.utils.llm import call_llm
import json

def planner_agent(user_query: str):
    print(f"[AGENT ENTER] planner | query={user_query!r}")
    prompt = f"""
    You are a planner agent.

    Break the following topic into 5-6 structured research tasks.

    Return ONLY a JSON list.

    Topic: {user_query}
    """

    response = call_llm(prompt).strip()
    if response.startswith("```"):
        response = response.strip("`")
        response = response.replace("json", "", 1).strip()

    try:
        tasks = json.loads(response)
        if not isinstance(tasks, list) or not tasks:
            return [user_query]

        normalized = []
        for item in tasks:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    normalized.append(text)
                continue

            if isinstance(item, dict):
                candidate = (
                    item.get("task")
                    or item.get("title")
                    or item.get("name")
                    or item.get("description")
                )
                if candidate:
                    normalized.append(str(candidate).strip())
        final_tasks = normalized or [user_query]
        print(f"[AGENT EXIT] planner | tasks={len(final_tasks)}")
        return final_tasks
    except Exception:
        print("[AGENT EXIT] planner | fallback=single_query")
        return [user_query]
