import pathway as pw


def retrieve_evidence(embedded_table, query_embedding, top_k=5):
    scored = embedded_table.select(
        story_id=pw.this.story_id,
        text=pw.this.text,
        score=pw.apply(
            lambda e, q: sum(a * b for a, b in zip(e, q)),
            pw.this.embedding,
            pw.const(query_embedding),
        ),
    )

    # Pathway sorts ascending → negate score
    ranked = scored.select(
        story_id=pw.this.story_id,
        text=pw.this.text,
        neg_score=-pw.this.score,
    ).sort(pw.this.neg_score)

    return ranked.limit(top_k)
