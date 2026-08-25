"""
The packing rule, restated.

`patch_packing.py` decides how chapters are grouped; this works the same rule
out independently, so the request count a reader is shown can be checked against
the rule rather than against the code that produced it.
"""

from typing import List

PATCH_OVERHEAD_TOKENS = 500      # room for the prompt wrapped around every patch
CHAPTER_SEPARATOR_TOKENS = 50    # the marker joining two chapters within a patch


def patches_by_rule(token_counts: List[int], limit: int) -> List[List[int]]:
    """
    How `patch_packing.py` says these chapters should be grouped.

    A restatement of the documented rule — 500 tokens of room for the prompt, 50
    for each separator, and an oversized chapter gets a patch to itself — so the
    request count a reader is shown can be checked against the rule instead of
    against the implementation of it.
    """
    patches: List[List[int]] = []
    current: List[int] = []
    total = PATCH_OVERHEAD_TOKENS

    for tokens in token_counts:
        separator = CHAPTER_SEPARATOR_TOKENS if current else 0
        if current and total + separator + tokens > limit:
            patches.append(current)
            current, total = [tokens], PATCH_OVERHEAD_TOKENS + tokens
        else:
            current.append(tokens)
            total += separator + tokens

    if current:
        patches.append(current)
    return patches

