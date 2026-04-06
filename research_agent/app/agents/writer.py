from app.utils.llm import call_llm

def writer_agent(research_data):
    print(f"[AGENT ENTER] writer | items={len(research_data)}")
    content = ""

    for item in research_data:
        content += f"\n\n### {item['task']}\n{item['summary']}"

    prompt = f"""
    Convert the following research notes into a well-structured report.
    Requirements:
    - Use Markdown headings
    - Keep facts grounded in the notes provided
    - Do not ask for additional input
    - If information is limited, still produce a concise report with "Known Findings" and "Gaps"

    {content}
    """

    report = call_llm(prompt)
    print(f"[AGENT EXIT] writer | chars={len(report)}")
    return report
