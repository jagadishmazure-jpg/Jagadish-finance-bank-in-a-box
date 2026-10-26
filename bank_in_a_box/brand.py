"""Brand / name check: the blocklist is stored as hashes, never plain names.

A blocklist file that spelled out forbidden real names would itself put
those names into the repo. So this module stores only SHA-256 digests of
normalised (lowercased, whitespace-collapsed) forbidden phrases — real
firms that must never appear as the fictional firm, and education
providers this independent project is not affiliated with — and checks a
document by hashing its word n-grams (1-4 words) the same way.

To regenerate a digest: ``sha256(" ".join(phrase.lower().split()))``.
The test suite asserts the list is non-empty and that a known forbidden
phrase is detected; the probe phrase lives in the test fixture, not in
repo documentation, data, or outputs.
"""

import hashlib

BLOCKLIST_HASHES = frozenset(
    {
        "d7f0bdae2d8f621b95b7b2ce32803d77a50bc5252b044894887ffc537b216d5f",
        "c952a08fdb0ff916b78a489ff321a4eb73d258612ededdd834c5a7c55fbc6c70",
        "17e9b17189f2f67e00b4c8dce8a6bedb38051ee221602fd52c88650ef9f68687",
        "309e31536dcf1556bb6c81b00cd992445b79ad8e89f9c0cd2a1f0675342538b3",
        "2cbb9e58bf3bcbdfe805a2aebb57f84531b114a18e5f0e6377d9f5a7bf86576b",
        "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
    }
)


def _digest(phrase):
    normalised = " ".join(phrase.lower().split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def contains_blocked(text):
    """True if any 1-4 word n-gram of *text* hashes to a blocklisted phrase."""
    words = "".join(
        ch if ch.isalnum() or ch.isspace() else " " for ch in text.lower()
    ).split()
    for size in (1, 2, 3, 4):
        for i in range(len(words) - size + 1):
            if _digest(" ".join(words[i : i + size])) in BLOCKLIST_HASHES:
                return True
    return False
