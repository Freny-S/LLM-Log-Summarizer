def chunk_logs_by_incident(raw_logs: str) -> list[str]:
    """
    Splits a raw log file into incident chunks.
    A blank line = separator between incidents.
    """

    chunks = []
    current_chunk = []

    for line in raw_logs.splitlines():
        if line.strip() == "":
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
        else:
            current_chunk.append(line)
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks