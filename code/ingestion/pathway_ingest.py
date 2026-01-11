import os
import pathway as pw


def ingest_novels(novel_dir: str, chunk_size: int = 400):
    """
    Ingest novels from a directory and turn them into clean, chunked rows.

    The goal here is NOT speed or fancy tricks.
    The goal is to safely process very large text files without blowing up RAM,
    while keeping track of which chunk came from which story.
    """

    print(f"--> [INFO] Starting ingestion from directory: {novel_dir}")
    print(f"--> [INFO] Chunk size set to {chunk_size} words per chunk")

    # We use Pathway's filesystem reader because loading full novels
    # directly into memory is a bad idea inside Docker.
    try:
        files = pw.io.fs.read(
            novel_dir,
            format="plaintext_by_file",
            mode="static",
            with_metadata=True,
        )
    except Exception as e:
        # Note to self: Pathway errors here usually mean the directory path is wrong
        # or Docker volume mounting failed.
        raise RuntimeError(f"[ERROR] Failed to read files from {novel_dir}: {e}")

    # Pathway stores metadata paths as JSON-like objects.
    # We convert them to plain Python strings early so downstream logic
    # doesn't have to care about Pathway internals.
    novels = files.select(
        path_str=pw.apply(str, pw.this._metadata["path"]),
        text=pw.this.data,
    )

    # Extract a clean story_id from the filename.
    # This MUST be OS-safe because this runs on Windows locally
    # and Linux inside Docker.
    novels = novels.select(
        story_id=pw.apply(
            lambda p: os.path.splitext(os.path.basename(p))[0],
            pw.this.path_str,
        ),
        text=pw.this.text,
    )

    # Inner helper: split long text into fixed-size word chunks.
    # We do word-based chunking instead of character-based chunking
    # because it behaves more predictably with embeddings.
    def chunk_text(text: str):
        # Defensive check: some classic texts contain odd encodings
        # or empty sections, so we guard against weird inputs.
        if not text or not isinstance(text, str):
            return []

        words = text.split()
        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    print("--> [INFO] Chunking novels into fixed-size segments...")

    # Apply chunking and flatten the result so each row corresponds
    # to one (story_id, text_chunk) pair.
    chunks = novels.select(
        story_id=pw.this.story_id,
        chunk=pw.apply(chunk_text, pw.this.text),
    ).flatten(pw.this.chunk)

    print("--> [INFO] Ingestion and chunking completed successfully")

    # Final schema is intentionally minimal.
    # Anything extra here just makes retrieval slower later.
    return chunks.select(
        story_id=pw.this.story_id,
        text=pw.this.chunk,
    )
