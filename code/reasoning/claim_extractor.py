import re
from typing import List


def extract_claims(backstory_text: str) -> List[str]:
    """
    Break a backstory into concrete, checkable claims.

    The idea here is simple:
    - Split the backstory into sentences
    - Throw away anything too short or too vague
    - Keep only statements that can reasonably be checked against the novel

    This intentionally favors precision over recall.
    """

    print("--> [INFO] Extracting factual claims from backstory text")

    # Defensive guard: if the backstory is empty or not a string,
    # there's nothing meaningful we can extract.
    if not backstory_text or not isinstance(backstory_text, str):
        print("--> [WARN] Backstory text is empty or invalid; no claims extracted")
        return []

    # Normalize whitespace first so sentence splitting behaves consistently.
    # Note to self: raw user input can be surprisingly messy.
    text = re.sub(r"\s+", " ", backstory_text.strip())

    # Split on common sentence-ending punctuation.
    # We keep this simple on purpose—overly clever NLP here caused more bugs than it solved.
    sentences = re.split(r"[.?!]", text)

    claims: List[str] = []

    for s in sentences:
        s = s.strip()

        # Skip very short fragments; these are usually noise.
        if len(s) < 20:
            continue

        # Skip hedged or speculative language.
        # Claims like these are hard to verify and often lead to false positives.
        if any(p in s.lower() for p in ["perhaps", "might", "it seems"]):
            continue

        claims.append(s)

    print(f"--> [INFO] Extracted {len(claims)} candidate claims")

    return claims
