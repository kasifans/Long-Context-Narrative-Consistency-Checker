# Long-Context Narrative Consistency Checker

A reproducible system for evaluating whether a proposed backstory is **consistent with the narrative of long-form novels**.  
The project combines **Pathway** for scalable ingestion, **semantic embeddings** for retrieval, and a **deterministic scoring strategy** to produce explainable, conservative predictions.

---

## 🔍 Problem Statement

Evaluating narrative consistency in long texts is challenging due to:
- The size of source documents (entire novels)
- Fragmented narrative evidence
- The risk of hallucinated or unverifiable conclusions

This project addresses the problem by **retrieving concrete narrative evidence** from the source text and making **threshold-based, explainable decisions** rather than generative guesses.

---

## 🧠 High-Level Approach

1. **Ingest** raw novel text files using Pathway
2. **Chunk** each novel into fixed-size semantic segments
3. **Normalize** story identifiers from filenames
4. **Embed** narrative chunks using Sentence Transformers
5. **Compare** a proposed backstory against relevant chunks
6. **Aggregate** top-K semantic evidence
7. **Predict** consistency with a confidence score and rationale

The system is designed to **fail safely** and avoid hallucinations.

---

## ✨ Key Features

- 📥 Pathway-based ingestion for long documents  
- 🧩 Deterministic chunking and story grouping  
- 🧠 Sentence-level semantic similarity (no generation)  
- 📊 Conservative confidence scoring  
- 📝 Human-readable, policy-style rationales  
- 🐳 Fully Dockerized for reproducibility  

---

## 📁 Repository Structure


├── Dockerfile
├── README.md
├── requirements.txt
├── code/
│ └── main.py
├── ingestion/
│ └── pathway_ingest.py
├── data/
│ ├── novels/ # Input novel text files
│ └── test.csv # Backstory test cases
└── results.csv # Output (ignored via .gitignore)