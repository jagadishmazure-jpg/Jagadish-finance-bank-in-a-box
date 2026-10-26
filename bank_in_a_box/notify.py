"""Email channel: dry run by default, explicit opt-in, refused in CI.

Defaults matter: a freshly constructed channel sends nothing. Sending
requires an explicit ``opt_in=True`` AND a non-CI environment AND an
injected transport (this scaffold ships no SMTP credentials and no
credentials of any kind). Anything less returns a dry-run record or
raises — never a silent real send.
"""

import os
from dataclasses import dataclass


class RefusedInCI(Exception):
    """Email sending is refused in CI environments, even when opted in."""


class NoTransportConfigured(Exception):
    """Opt-in send requested but no transport was injected."""


@dataclass
class EmailRecord:
    to: str
    subject: str
    sent: bool
    dry_run: bool
    note: str


class EmailChannel:
    def __init__(self, dry_run=True, transport=None):
        self.dry_run = dry_run
        self.transport = transport

    def send(self, to, subject, body, opt_in=False):
        """Send, or record a dry run. Never sends on defaults."""
        if self.dry_run or not opt_in:
            return EmailRecord(
                to=to, subject=subject, sent=False, dry_run=True,
                note="dry run: nothing sent",
            )
        if self.transport is None:
            raise NoTransportConfigured(
                "no email transport configured; inject one explicitly"
            )
        # The CI refusal stays, but it must not shadow the more specific
        # transport refusal: a test asserting "no transport" must see that
        # error even when the runner sets CI. A real send still requires
        # a transport AND a non-CI environment, so nothing is sent from CI.
        if os.environ.get("CI"):
            raise RefusedInCI("email sending refused in CI")
        self.transport(to, subject, body)
        return EmailRecord(
            to=to, subject=subject, sent=True, dry_run=False,
            note="sent via injected transport",
        )
