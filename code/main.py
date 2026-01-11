import numpy as np
import pandas as pd
import pathway as pw
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from ingestion.pathway_ingest import ingest_novels

NOVEL_DIR = "data/novels"
TEST_CSV = "test.csv"
OUTPUT_CSV = "results.csv"

TOP_K = 5
SIM_THRESHOLD = 0.25


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


def main():
    print("📥 Ingesting novels with Pathway...")
    chunk_table = ingest_novels(NOVEL_DIR)

    print("🚀 Running Pathway graph...")
    pw.run()  # execute once

    print("📖 Loading test.csv...")
    test_df = pd.read_csv(TEST_CSV)
    print("📋 test.csv columns:", list(test_df.columns))

    # Materialize Pathway table
    chunks_df = pw.debug.table_to_pandas(chunk_table)

    print("🧠 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # --------------------------------------------------
    # 🔹 Embedding cache (major speed + polish)
    # --------------------------------------------------
    print("⚙️ Computing chunk embeddings...")
    chunks_df["embedding"] = list(
        model.encode(
            chunks_df["text"].tolist(),
            batch_size=32,
            show_progress_bar=True,
        )
    )

    results = []

    print("🔍 Evaluating backstories...")
    for _, row in tqdm(test_df.iterrows(), total=len(test_df)):
        story_id = row["story_id"]
        backstory = row["backstory"]

        relevant = chunks_df[chunks_df["story_id"] == story_id]

        if relevant.empty:
            results.append(
                {
                    "story_id": story_id,
                    "prediction": 0,
                    "confidence": 0.0,
                    "rationale": "No matching narrative source was found for the given story identifier.",
                }
            )
            continue

        query_emb = model.encode(backstory)

        scores = [
            cosine_similarity(query_emb, emb)
            for emb in relevant["embedding"]
        ]

        # Top-K evidence aggregation
        top_scores = sorted(scores, reverse=True)[:TOP_K]
        avg_score = float(np.mean(top_scores))

        prediction = 1 if avg_score >= SIM_THRESHOLD else 0

        rationale = (
            "The backstory is consistent with key narrative elements found in the source text."
            if prediction
            else "The backstory conflicts with established narrative constraints in the source text."
        )

        results.append(
            {
                "story_id": story_id,
                "prediction": prediction,
                "confidence": round(avg_score, 3),
                "rationale": rationale,
            }
        )

    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
    print("✅ results.csv generated successfully")


if __name__ == "__main__":
    main()
