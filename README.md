# Long-Context Narrative Consistency Checker 📚

This project checks whether a given **backstory** is actually consistent with the narrative of a **long-form novel**.

The goal is simple:  
don’t guess, don’t hallucinate — **find real evidence in the text and decide based on that**.

This was built during a hackathon under time pressure, with a focus on correctness and clarity rather than flashy generation.

---

## Why this exists

Working with long texts (like novels) is messy.

Important details are spread across chapters, and comparing a short backstory against an entire book directly doesn’t work in practice. On top of that, generative approaches tend to sound confident even when they’re wrong.

So instead of generating explanations, this system:
- breaks the novel into manageable pieces
- retrieves the most relevant parts
- and makes a decision based only on retrieved evidence

If there’s no evidence, it says so.

---

## What the system does (end to end)

At a high level, the pipeline looks like this:

1. Novel text files are ingested from disk  
2. Each novel is split into fixed-size chunks  
3. All chunks are converted into sentence embeddings  
4. A backstory is compared against chunks from the correct story  
5. The strongest matches are aggregated  
6. A consistency decision is produced with a confidence score  

Every step is deterministic and can be inspected.

---

## About Pathway 🧪

Pathway is used for the **ingestion and chunking** part of the pipeline.

Specifically, it handles:
- reading long text files
- tracking file metadata
- creating a clean stream of text chunks

The ingestion logic lives in:
ingestion/pathway_ingest.py


and is executed from `main.py` using:

```python
pw.run()


## 📁 Project Structure


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
└── results.csv # Output (ignored by git)

How to run the project
Requirements

Docker

Build the image
docker build -t narrative-checker .

Run the checker
docker run --rm -v ${PWD}:/app narrative-checker python code/main.py data/novels


This will:

ingest the novels using Pathway

read backstories from test.csv

generate results.csv

Output format 📊

The output file contains:

Column	Description
story_id	Identifier of the novel
prediction	1 = consistent, 0 = inconsistent
confidence	Average similarity score from top-K chunks
rationale	Short explanation based on retrieved evidence
Example
story_id,prediction,confidence,rationale
the_count_of_monte_cristo,1,0.281,The backstory is consistent with key narrative elements found in the source text.
in_search_of_the_castaways,1,0.357,The backstory is consistent with key narrative elements found in the source text.

Interpreting the confidence score

0.20 – 0.30 → weak but plausible alignment

0.30 – 0.45 → moderate narrative consistency

> 0.45 → strong alignment (uncommon for long novels)

Thresholds are intentionally conservative to avoid overconfident predictions.

Design choices

No hallucinated evidence

Retrieval before decision

Deterministic execution

Clear failure modes

Reproducible via Docker