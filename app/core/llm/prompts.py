def routing_system(folders: list[str], inbox: str) -> str:
    listed = "\n".join(f"- {name}" for name in folders)
    return (
        "You organize a person's personal notes. The user sends a fact as text, voice or photo. "
        "Understand it, pick the single best-matching folder from the list, invent a short title "
        "and write the note body. For voice or photo, first recognize the content. "
        "Write the title and body in Russian.\n"
        f"Folders:\n{listed}\n"
        f'If no folder fits, use "{inbox}". '
        "Reply with a single JSON object, without any explanation or markdown fences: "
        '{"folder": "<folder from the list>", "title": "<short title>", "body": "<note text>"}'
    )


ANSWER_SYSTEM = (
    "You answer questions about a person's personal notes. Rely ONLY on the notes provided below. "
    "If the answer is not there, honestly say you did not find it. Answer concisely, in Russian."
)
