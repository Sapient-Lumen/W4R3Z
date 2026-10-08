# External evidence watchlist and source triage

The archive now carries many evidence and governance claims. Those claims should not depend on a
single frozen bibliography pass. This surface adds a lightweight watchlist so current standards,
security taxonomies, education guidance, and trial results can update evidence clocks without
turning every news item into a new branch.

The rule is: **watch for changes that alter decisions, not for every publication that mentions AI**.

## Watch states

| Code | Meaning | Archive action |
|---|---|---|
| `EW0` | Background source only | Cite if useful; no scheduled watch. |
| `EW1` | Current stable standard or framework | Review annually or when a replacement appears. |
| `EW2` | Active regulatory or official guidance | Review when duties, dates, or scope change. |
| `EW3` | Security taxonomy or adversarial-risk list | Review on major version or new risk class. |
| `EW4` | Education efficacy or workload study | Review when it changes a claim-family grade. |
| `EW5` | Vendor/platform policy or product behavior | Review on deployment, contract, or feature change. |
| `EWX` | Unreliable, marketing-only, or unverifiable source | Do not use for claim elevation. |

## Source triage classes

| Class | Examples | Default use |
|---|---|---|
| `standard` | NIST profile, formal framework, official standard | Risk-management floor or vocabulary. |
| `regulation` | statute, regulator guidance, official compliance FAQ | Compliance floor and expiry trigger. |
| `security` | OWASP or comparable adversarial-risk taxonomy | Red-team checklist and stop triggers. |
| `official_guidance` | education ministry, department, assessment body | Sector adapter or public-summary constraint. |
| `peer_or_independent_study` | RCT, quasi-experiment, independent evaluation | Claim-family evidence grade. |
| `market_signal` | adoption survey, platform change, vendor program | Scoping signal only, not effectiveness proof. |

## Update triggers

A watched source should trigger archive review when it changes any of these:

- whether a use is high-risk, restricted, or prohibited;
- what AI literacy, notice, transparency, or human-oversight duty applies;
- whether a security risk class appears or changes severity;
- whether a learning, workload, access, validity, or safety claim should move up or down an `EV`
  grade;
- whether a public summary must remove a claim or add a limitation;
- whether a sector adapter should become stricter for minors, high-stakes assessment, public routes,
  or protected support.

## Watchlist contract

Watchlists live in `examples/evidence-watchlists/` and declare:

- source id, title, URL, source class, and watch state;
- related bibliography ids and archive surfaces;
- review cadence and next review date;
- invalidation triggers;
- action if changed.

`tools/check_evidence_watchlists.py` verifies that watched bibliography ids exist, referenced
surfaces exist, next review dates parse, and every watched source has an action if changed.

## Current archive bet

External evidence should change evidence grades, expiry clocks, sector adapters, public summaries,
or security tests. It should not automatically spawn prose branches. A watchlist lets the archive
stay current while preserving compression.

See [`evidence-grade-and-claim-strength-ladder.md`](evidence-grade-and-claim-strength-ladder.md),
[`claim-family-evidence-matrix.md`](claim-family-evidence-matrix.md),
[`evidence-expiry-and-renewal-clocks.md`](evidence-expiry-and-renewal-clocks.md), and `AS-0231`.
