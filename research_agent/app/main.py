from app.crew.crew_setup import run_crew
from app.tools.file_writer import save_to_file

if __name__ == "__main__":
    query = input("Enter topic: ")

    result = run_crew(query)

    print("\nFinal Report:\n")
    print(result)

    save_to_file(result)
    print("\nSaved to output.md")
