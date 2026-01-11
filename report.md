# KDSH 2026 Project Report  
## Narrative Consistency Checker  
**Track A: Systems Reasoning**

---

## 1. The Problem

Checking whether a backstory fits into a 100,000-word novel is inherently difficult.
Feeding an entire book such as *The Count of Monte Cristo* directly into a language
model is impractical due to context limits and often leads to hallucinated answers.

Instead of relying on generation, we built a system that retrieves concrete narrative
evidence first. Our pipeline identifies the specific parts of the novel that are
relevant to a backstory and bases its decision strictly on those retrieved text
snippets.

---

## 2. Our Approach (The Tech Stack)

We implemented a deterministic, retrieval-first pipeline inspired by RAG systems.
However, rather than generating text, our system focuses on **retrieval and
verification**.

Transparency was a core design goal: if the system predicts that a backstory is
consistent, it must surface the exact narrative evidence supporting that decision.

### Pipeline Overview

- **Ingestion (Pathway):**  
  Pathway is used to stream raw `.txt` novel files. This allows us to process very
  large texts efficiently without loading entire books into memory.

- **Chunking:**  
  The continuous text stream is split into fixed-size segments (chunks), which serve
  as the basic retrieval units.

- **Embedding:**  
  Each chunk is converted into a vector representation using SentenceTransformers.

- **Retrieval:**  
  The system searches for chunks that are semantically similar to the given backstory.

---

## 3. Handling Long Context

The primary technical challenge is scale.

**Why it is hard:**  
In long novels, the relevant plot point may appear as a single paragraph buried among
hundreds of pages of unrelated content. Direct comparison dilutes the signal with
noise.

**Our solution:**  
We apply fixed-size window chunking to convert the long-context problem into a
search problem. Each chunk can be independently retrieved and evaluated.

**Stability:**  
Pathway’s streaming execution allows this process to run inside a standard Docker
container without requiring specialized hardware.

---

## 4. Signal vs. Noise (Decision Logic)

The system distinguishes signal from noise using semantic similarity.

- **Cosine Similarity:**  
  The backstory embedding is compared against all chunk embeddings from the same
  novel.

- **Top-K Filtering:**  
  Only the most similar chunks are considered as potential evidence.

- **Final Verdict:**  
  The similarity scores of the top matches are averaged. If this value exceeds a
  conservative threshold (chosen to avoid false positives), the backstory is marked
  as consistent (`1`); otherwise, it is marked inconsistent (`0`).

For explainability, the system includes a short snippet from the highest-scoring
chunk in the final rationale.

---

## 5. Limitations

This approach has several known limitations:

- **Chunk Boundaries:**  
  Important narrative information may be split across adjacent chunks.

- **Semantic vs. Logical Reasoning:**  
  The system relies on semantic similarity and may miss contradictions that are
  purely logical (e.g., incorrect dates).

- **Paraphrasing Sensitivity:**  
  If a backstory uses language very different from the novel, similarity scores
  may be lower even when the content is correct.

These trade-offs were accepted in favor of interpretability and robustness.

---

## 6. Reproducibility

The entire pipeline runs inside Docker with all dependencies pinned in
`requirements.txt`. No external APIs or black-box services are used.

Given the same inputs, the system produces the same `results.csv` on every run,
ensuring full reproducibility.
