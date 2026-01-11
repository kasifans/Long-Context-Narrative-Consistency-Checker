from typing import List, Tuple


def evaluate_claim(claim: str, evidence: List[str]) -> Tuple[bool, str]:
    """
    Check a single claim against its retrieved evidence.

    This is intentionally conservative.
    We are not trying to prove the claim true in all cases—
    only to catch clear contradictions when they appear.
    """

    # Normalize once to avoid repeating lower() everywhere
    claim_l = claim.lower()

    print(f"--> [INFO] Evaluating claim: '{claim[:60]}...'")

    for chunk in evidence:
        chunk_l = chunk.lower()

        # Simple but effective contradiction heuristic:
        # absolute language in the claim vs absolute language in the narrative
        #
        # Note to self: this looks naive, but in practice it catches
        # surprising contradictions without overfitting.
        if "never" in claim_l and "always" in chunk_l:
            print("--> [WARN] Detected potential contradiction")
            return False, f"Claim '{claim}' contradicted by later events."

    # If we make it here, no hard contradiction was found
    return True, f"No contradiction found for claim '{claim}'."


def check_consistency(
    claims: List[str],
    claim_evidence: List[List[str]],
) -> Tuple[int, str]:
    """
    Check all extracted claims against their corresponding evidence.

    The rule is simple:
    - If any single claim is contradicted → fail fast
    - Otherwise → consider the backstory consistent
    """

    print(f"--> [INFO] Checking consistency across {len(claims)} claims")

    # Defensive guard: mismatched inputs usually indicate an upstream bug
    if len(claims) != len(claim_evidence):
        raise ValueError(
            "[ERROR] Claims list and evidence list are misaligned. "
            "Each claim must have a corresponding evidence set."
        )

    for claim, evidence in zip(claims, claim_evidence):
        ok, rationale = evaluate_claim(claim, evidence)

        # Fail fast on the first clear contradiction.
        # This keeps explanations short and easy to audit.
        if not ok:
            print("--> [INFO] Consistency check failed")
            return 0, rationale

    print("--> [INFO] All claims passed consistency checks")
    return 1, "All backstory claims are consistent with the narrative."
