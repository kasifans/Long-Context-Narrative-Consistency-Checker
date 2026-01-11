from typing import List, Tuple


def evaluate_claim(claim: str, evidence: List[str]) -> Tuple[bool, str]:
    claim_l = claim.lower()
    for chunk in evidence:
        chunk_l = chunk.lower()
        if "never" in claim_l and "always" in chunk_l:
            return False, f"Claim '{claim}' contradicted by later events."
    return True, f"No contradiction found for claim '{claim}'."


def check_consistency(
    claims: List[str],
    claim_evidence: List[List[str]],
) -> Tuple[int, str]:
    for claim, evidence in zip(claims, claim_evidence):
        ok, rationale = evaluate_claim(claim, evidence)
        if not ok:
            return 0, rationale
    return 1, "All backstory claims are consistent with the narrative."
