"""Confirmation gates: explicit consent, confidence-checked, unambiguous.

A gate is evaluated exactly once per decision, from a recorded consent
string and a confidence score. It passes only when ALL of these hold:

* consent was actually recorded (absent consent = denied, never assumed);
* the consent is an unambiguous affirmation — a bare "yes";
* confidence meets the threshold (low confidence = denied, re-confirm);
* the consent does not contradict itself — "yes, wait, no" contains both
  an affirmation and a refusal, so it is ambiguous and denied.

Bypassing the gate (finalising without an evaluated gate) raises
:class:`GateNotEvaluated`; it is a different failure from a recorded
refusal, and tests cover both paths separately.
"""

import re

MIN_CONFIDENCE = 0.6

_YES = re.compile(r"\byes\b", re.IGNORECASE)
_NO = re.compile(r"\b(no|nope|stop|wait|cancel|not yet)\b", re.IGNORECASE)


class GateNotEvaluated(Exception):
    """A decision was finalised without any evaluated confirmation gate."""


class GateDenied(Exception):
    """The gate was evaluated and did not pass (reason carried in message)."""


def evaluate_consent(consent, confidence):
    """Evaluate one consent record. Returns "approved" or raises GateDenied.

    ``consent`` is the exact recorded string (or None when absent).
    ``confidence`` is the 0-1 confidence of the consent interpretation.
    """
    if consent is None or not str(consent).strip():
        raise GateDenied("absent consent: nothing was recorded")
    text = str(consent)
    if _YES.search(text) and _NO.search(text):
        raise GateDenied(f"self-contradicting consent: {consent!r}")
    if not _YES.search(text):
        raise GateDenied(f"consent is not an affirmation: {consent!r}")
    if confidence is None or confidence < MIN_CONFIDENCE:
        raise GateDenied(f"low confidence ({confidence}); re-confirm required")
    return "approved"
