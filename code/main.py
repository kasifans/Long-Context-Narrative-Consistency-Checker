import numpy as np
import pandas as pd
import pathway as pw
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from ingestion.pathway_ingest import ingest_novels


# Basic configuration lives here so it’s easy to tweak without
# digging through the logic.
NOVEL_DIR = "data/novels"
TEST_CSV = "test.csv"
OUTPUT_CSV = "results.csv"

TOP_K = 5
SIM_THRESHOLD = 0.25


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    We normalize explicitly to avoid relying on assumptions about
    upstream embedding behavior.
    """
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


def main():
    print("--> [INFO] Starting narrative consistency pipeline")

    # Kick off Pathway ingestion. This handles reading and chunking
    # large novels safely without loading everything into memory.
    print("--> [INFO] Ingesting novels with Pathway (this may take a bit)...")
    chunk_table = ingest_novels(NOVEL_DIR)

    # Pathway graphs are lazy by default, so this call is mandatory.
    print("--> [INFO] Executing Pathway computation graph")
    pw.run()

    # Load the backstory test cases.
    print(f"--> [INFO] Loading backstories from {TEST_CSV}")
    try:
        test_df = pd.read_csv(TEST_CSV)
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to read {TEST_CSV}: {e}")

    print(f"--> [INFO] Detected columns: {list(test_df.columns)}")

    # Convert the Pathway table into pandas so the rest of the
    # pipeline stays easy to inspect and debug.
    print("--> [INFO] Converting Pathway output to pandas DataFrame")
    chunks_df = pw.debug.table_to_pandas(chunk_table)

    # Load the embedding model once and reuse it everywhere.
    print("--> [INFO] Loading SentenceTransformer model")
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to load embedding model: {e}")

    # Precompute embeddings for all novel chunks.
    # This avoids recomputing them for every backstory.
    print("--> [INFO] Computing embeddings for novel chunks")
    try:
        chunks_df["embedding"] = list(
            model.encode(
                chunks_df["text"].tolist(),
                batch_size=32,
                show_progress_bar=True,
            )
        )
    except Exception as e:
        # Some classic texts contain odd unicode characters,
        # so we guard against encoding-related crashes here.
        raise RuntimeError(f"[ERROR] Failed during chunk embedding: {e}")

    results = []

    print("--> [INFO] Evaluating backstories against retrieved evidence")
    for _, row in tqdm(test_df.iterrows(), total=len(test_df)):
        story_id = row["story_id"]
        backstory = row["backstory"]

        print(f"--> [INFO] Processing story_id='{story_id}'")

        relevant = chunks_df[chunks_df["story_id"] == story_id]

        # If we can’t find the novel text, we fail safely.
        if relevant.empty:
            print(f"--> [WARN] No novel text found for story_id='{story_id}'")
            results.append(
                {
                    "story_id": story_id,
                    "prediction": 0,
                    "confidence": 0.0,
                    "rationale": "No narrative source was found for the given story identifier.",
                }
            )
            continue

        # Embed the backstory once per story.
        try:
            query_emb = model.encode(backstory)
        except Exception as e:
            print(
                f"--> [ERROR] Failed to embed backstory for story_id='{story_id}': {e}"
            )
            results.append(
                {
                    "story_id": story_id,
                    "prediction": 0,
                    "confidence": 0.0,
                    "rationale": "Backstory embedding failed due to encoding issues.",
                }
            )
            continue

        # Score each relevant chunk against the backstory.
        scored_chunks = []
        for emb, txt in zip(relevant["embedding"], relevant["text"]):
            sim = cosine_similarity(query_emb, emb)
            scored_chunks.append((sim, txt))

        # Highest similarity first.
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Use the top-K chunks as evidence.
        top_k = scored_chunks[:TOP_K]
        scores = [s for s, _ in top_k]

        avg_score = float(np.mean(scores))
        confidence = round(avg_score, 3)

        prediction = 1 if avg_score >= SIM_THRESHOLD else 0

        # Build a rationale that actually shows what was matched.
        if prediction:
            top_score, top_chunk = top_k[0]
            snippet = top_chunk[:150].replace("\n", " ").strip() + "..."
            rationale = (
                f"Found matching evidence: '{snippet}' "
                f"(Sim: {round(top_score, 3)})"
            )
        else:
            rationale = (
                "No sufficiently similar narrative evidence was found "
                "to support the backstory."
            )

        results.append(
            {
                "story_id": story_id,
                "prediction": prediction,
                "confidence": confidence,
                "rationale": rationale,
            }
        )

    # Write everything out at the very end so partial runs
    # don’t leave confusing artifacts behind.
    print(f"--> [INFO] Writing results to {OUTPUT_CSV}")
    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)

    print("--> [INFO] Pipeline completed successfully")
    print("✔ results.csv generated successfully")


if __name__ == "__main__":
    # Keep the entry point explicit and boring.
    # Side effects on import are a pain to debug.
    main()
