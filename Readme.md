# research_agent

A lightweight multi-agent research pipeline in Python.

It takes a topic, plans research tasks, gathers web results, summarizes findings, writes a report, and reviews it before saving to `output.md`.

## Features

- Planner, Researcher, Writer, and Critic agent flow
- DuckDuckGo search integration via `ddgs`
- Local LLM support with Ollama (default)
- Optional Hugging Face Router support
- Detailed runtime logs:
  - agent entry/exit
  - tool calls/results
  - LLM request/response status

## Project Structure

```text
research_agent/
  app/
    agents/
      planner.py
      researcher.py
      writer.py
      critic.py
    crew/
      crew_setup.py
    tools/
      search.py
      summarizer.py
      file_writer.py
    utils/
      llm.py
    main.py
  output.md
```

## How It Works

1. `planner_agent` creates task list from the input topic.
2. `researcher_agent` loops through tasks:
   - calls `search_web(...)`
   - calls `summarize(...)` on raw search results
3. `writer_agent` turns summaries into a structured draft.
4. `critic_agent` improves clarity/structure and returns final report.
5. Final report is printed and saved to `output.md`.

## Requirements

- Python 3.10+
- Ollama (recommended) if running local LLM backend

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Ollama Setup (Recommended)

Install Ollama and pull a model, for example:

```bash
ollama pull gemma3:1b
```

The project currently defaults to:

- `LLM_BACKEND=ollama`
- `OLLAMA_MODEL=gemma3:1b`

You can switch model any time, e.g. `llama3:latest`.

## Environment Variables

Create/update `app/.env` (do not commit real secrets):

```env
# Backend selection
LLM_BACKEND=ollama

# Ollama config
OLLAMA_URL=http://127.0.0.1:11434/api/chat
OLLAMA_MODEL=gemma3:1b
OLLAMA_TIMEOUT_SEC=600
OLLAMA_MAX_PROMPT_CHARS=12000
OLLAMA_NUM_PREDICT=300

# Optional HF fallback config
HF_API_KEY=your_hf_key
HF_MODEL_ID=meta-llama/Llama-3.3-70B-Instruct
HF_PROVIDER=novita
```

## Run

From the `research_agent` directory:

```bash
python -m app.main
```

Enter a topic when prompted.  
Output is saved to `output.md`.

## Example Logs

```text
[AGENT ENTER] planner | query='hello'
[TOOL CALL] search_web | query='Define Hello'
[LLM REQUEST] prompt_chars=1644
[LLM RESPONSE] status=200 | output_chars=563
[AGENT EXIT] critic | output_chars=994
```

## Troubleshooting

- `402` from HF Router:
  - You are out of Hugging Face credits. Use Ollama or top up credits.
- Ollama `500` / long hangs:
  - Use a smaller model (`gemma3:1b`), reduce output (`OLLAMA_NUM_PREDICT`), or increase timeout.
- `failed to load native root certificate` warning:
  - Usually non-fatal in this workflow; search may still work.

## Notes

- This is a practical starter pipeline, not a fact-verification system.
- For production use, add stronger source filtering, citations, retries, and tests.
