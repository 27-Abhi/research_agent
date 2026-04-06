def save_to_file(content: str, filename: str = "output.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)