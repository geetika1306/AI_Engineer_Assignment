def chunk_text(
    text,
    max_chars=12000,
    overlap=500
):
    """
    Split long text into overlapping chunks.

    The overlap helps preserve context between
    neighboring chunks and reduces the chance of
    losing information at chunk boundaries.
    """

    if not text:
        return []

    text = text.strip()

    if len(text) <= max_chars:
        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + max_chars,
            text_length
        )

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(
                chunk.strip()
            )

        if end >= text_length:
            break

        start = end - overlap

    return chunks