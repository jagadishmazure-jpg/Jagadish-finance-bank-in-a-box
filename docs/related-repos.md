# Related repos (cross-links, not duplication)

This repo is one of a set of finance builds from the same programme of
work. Each covers a different slice; overlaps are linked here rather
than re-implemented here.

- **finance-compliance-rag** — grounded compliance answers over
  retrieved source documents. This repo's compliance agent checks
  screening flags; it does not do retrieval — that lives there.
- **finance-kyc-aml-pipeline** — customer onboarding screening and
  transaction monitoring pipelines. This repo consumes a screened
  flag; the pipeline that produces it lives there.
- **finance-credit-memo** — credit decision memos (borrower-focused).
  This repo's memo is portfolio-decision focused; the credit memo
  structure lives there.
- **finance-portfolio-risk-agent** — deeper portfolio risk analytics.
  This repo's risk agent is a concentration/loss flag check; fuller
  risk modelling lives there.
- **finance-governance-poc** — governance controls across finance
  agents. This repo's gates and approvals are the memo-local version;
  the cross-agent governance layer lives there.
- **finance-sentiment-analysis, finance-invoice-reimbursement,
  finance-data-validation** — adjacent finance capabilities (market
  sentiment, payables, data quality) that this bank-in-a-box does not
  attempt.

Repo names above are the sibling scaffold names; links to their live
GitHub URLs belong here once each repo is pushed.
