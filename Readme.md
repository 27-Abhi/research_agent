## this is a project for me to learn agentic ai
Starting off with a research agent
you give it any topic to research as input

1) planner
planner takes the user input. plans the required items and flow.
handover to reseacher agent.

2) researcher
uses llm/webscaping to extract informaiton of the related topic.
handover to writer agent.

3) writer
use the researcher's work to write/structure the paper.

4) critic
feedback mechanism to rate the work


research_agent/
│
├── app/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   ├── critic.py
│   │
│   ├── tools/
│   │   ├── search.py
│   │   ├── summarizer.py
│   │   ├── file_writer.py
│   │
│   ├── crew/
│   │   └── crew_setup.py
│   │
│   ├── main.py
│
├── requirements.txt
└── README.md