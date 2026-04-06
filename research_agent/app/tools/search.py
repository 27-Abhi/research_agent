try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_web(query):
    print(f"[TOOL CALL] search_web | query={query!r}")
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    print(f"[TOOL RESULT] search_web | results={len(results)}")
    return results

