import re
from typing import List


def extract_claims(backstory_text: str) -> List[str]:
    text = re.sub(r"\s+", " ", backstory_text.strip())
    sentences = re.split(r"[.?!]", text)

    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20:
            continue
        if any(p in s.lower() for p in ["perhaps", "might", "it seems"]):
            continue
        claims.append(s)

    return claims
