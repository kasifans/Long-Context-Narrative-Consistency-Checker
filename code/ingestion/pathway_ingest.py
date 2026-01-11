import os
import pathway as pw


def ingest_novels(novel_dir: str, chunk_size: int = 400):
    """
    Ingest novels from a directory, derive a clean story_id from filenames,
    chunk text deterministically, and return a Pathway table with:
      - story_id
      - text (chunk)
    """

    # Read files with metadata (Pathway filesystem reader)
    files = pw.io.fs.read(
        novel_dir,
        format="plaintext_by_file",
        mode="static",
        with_metadata=True,
    )

    # Convert metadata path JSON -> Python string
    novels = files.select(
        path_str=pw.apply(str, pw.this._metadata["path"]),
        text=pw.this.data,
    )

    # ✅ OS-safe story_id extraction (Windows + Linux + Docker)
    novels = novels.select(
        story_id=pw.apply(
            lambda p: os.path.splitext(os.path.basename(p))[0],
            pw.this.path_str,
        ),
        text=pw.this.text,
    )

    # Chunk text into fixed-size word windows
    def chunk_text(text: str):
        words = text.split()
        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    # Apply chunking and flatten into rows
    chunks = novels.select(
        story_id=pw.this.story_id,
        chunk=pw.apply(chunk_text, pw.this.text),
    ).flatten(pw.this.chunk)

    # Final schema used downstream
    return chunks.select(
        story_id=pw.this.story_id,
        text=pw.this.chunk,
    )
