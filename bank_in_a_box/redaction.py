"""PII redaction for agent outputs and memo text.

Checklist (all four are tested, not just the easy two):

* card numbers — 13-19 digits, optionally spaced or dashed
* email addresses
* phone numbers
* Social Security-style numbers (``NNN-NN-NNNN``)

Redaction runs on every finding summary before it reaches a memo, and
again on the rendered memo text, so a careless agent string cannot leak
through either layer. Synthetic seed data still goes through the same
path: the rule must not depend on the data being "only fake".
"""

import re

_CARD = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE = re.compile(r"\b(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ])\d{3}[-. ]\d{4}\b")


def redact(text):
    """Replace PII in *text* with labelled placeholders."""
    if not isinstance(text, str):
        return text
    text = _CARD.sub("[CARD REDACTED]", text)
    text = _EMAIL.sub("[EMAIL REDACTED]", text)
    text = _SSN.sub("[SSN REDACTED]", text)
    text = _PHONE.sub("[PHONE REDACTED]", text)
    return text


def contains_pii(text):
    """True if any checklist pattern is still present in *text*."""
    return bool(
        _CARD.search(text)
        or _EMAIL.search(text)
        or _SSN.search(text)
        or _PHONE.search(text)
    )
