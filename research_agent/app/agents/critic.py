from app.utils.llm import call_llm

def critic_agent(report: str):
    print(f"[AGENT ENTER] critic | input_chars={len(report)}")
    prompt = f"""
    You are a critic agent.

    Review the following report and:
    1. Improve clarity
    2. Remove redundancy
    3. Fix structure

    Return only the improved report in Markdown.
    Do not ask for more input.
    If the report is short, improve it directly instead of requesting context.

    {report}
    """
    reviewed = call_llm(prompt)
    lower = reviewed.lower()
    fallback_phrases = [
        "please provide",
        "share the original",
        "need more information",
        "provide the report",
    ]
    if any(phrase in lower for phrase in fallback_phrases):
        print("[AGENT EXIT] critic | fallback=original_report")
        return report
    print(f"[AGENT EXIT] critic | output_chars={len(reviewed)}")
    return reviewed
