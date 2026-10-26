"""Demo: build one memo for the synthetic customer CUST-001 and print it.

Offline, stdlib only, no network, no credentials. The memo stays DRAFT
unless the demo is run with ``--finalise``, which still requires a
named approver passed on the command line — there is no default
approver, by design.
"""

import argparse
import sys

from .approvals import make_approval
from .gates import evaluate_consent
from .orchestrator import Orchestrator
from .store import build_database


def main(argv=None):
    parser = argparse.ArgumentParser(description="Merrowgate bank-in-a-box demo")
    parser.add_argument("--customer", default="CUST-001")
    parser.add_argument("--finalise", action="store_true")
    parser.add_argument("--approver", default="")
    parser.add_argument("--consent", default="yes")
    args = parser.parse_args(argv)

    conn = build_database()
    memo = Orchestrator(conn).build_memo("MEMO-001", args.customer)
    if args.finalise:
        if not args.approver:
            print("refused: --finalise needs a named --approver", file=sys.stderr)
            return 2
        gate = evaluate_consent(args.consent, 0.9)
        memo.finalise(make_approval(args.approver, "finalise-memo:MEMO-001"), gate)
    print(memo.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
