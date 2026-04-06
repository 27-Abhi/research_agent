from app.utils.llm import call_llm

def summarize(text: str) -> str:
    text_str = str(text)
    print(f"[TOOL CALL] summarize | input_chars={len(text_str)}")
    prompt = f"""
    Summarize the following content into concise bullet points:

    {text}
    """
    summary = call_llm(prompt)
    print(f"[TOOL RESULT] summarize | output_chars={len(summary)}")
    return summary
