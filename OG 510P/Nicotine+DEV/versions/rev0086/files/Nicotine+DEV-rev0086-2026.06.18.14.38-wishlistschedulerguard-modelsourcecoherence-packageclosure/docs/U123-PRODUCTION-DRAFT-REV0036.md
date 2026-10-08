# U-123 production-draft packet — rev0036

## Outcome

Rev0036 completes the requested U-123 production-draft pass. It adds a fixed-behavior regression skeleton, a maintainer-ready report draft, an identity-guard simulation, and a coherence split that keeps U-123 separate from PB-01, SEARCH-RESP-01, and lower-value media-parser rows.

Status remains conservative:

```text
strict report-candidates: 3
production-draft packets: 1 (U-123)
production-ready disclosure texts: 0
```

The draft is ready for maintainer-style review, but the cube still marks it not production-ready because the final fix strategy and issue/PR framing are not locked.

## New artifacts

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_fixed_regression.py
report_drafts/U123-DUPLICATE-TRANSFER-TOKEN-PRODUCTION-DRAFT-REV0036.md
report_drafts/U123-MAINTAINER-FIX-SKELETON-REV0036.md
evidence/rev0036-u123-current-and-fixed-regression-rerun.txt
evidence/rev0036-u123-identity-guard-simulation.txt
evidence/rev0036-u123-source-trace.md
evidence/rev0036-web-public-overlap-u123.md
data/rev0036_u123_production_readiness.csv/json
data/rev0036_u123_regression_summary.csv/json
data/rev0036_u123_coherence_refactor.csv/json
tools/probe_rev0036_u123_packet.py
```

## Rerun summary

```text
current-behavior witness:
  github-tag-3.3.10:   OK / 1 unittest
  github-branch-3.3.x: OK / 1 unittest
  github-branch-master: OK / 1 unittest

fixed-behavior regression on current source:
  github-tag-3.3.10:   expected failure / missing active username+token map entry
  github-branch-3.3.x: expected failure / missing active username+token map entry
  github-branch-master: expected failure / missing active username+token map entry

identity-guard simulation:
  github-tag-3.3.10:   OK / 1 unittest
  github-branch-3.3.x: OK / 1 unittest
  github-branch-master: OK / 1 unittest
```

## Report invariant

```text
A stale timeout/deactivation callback for Transfer object A must not delete active_users[username][token] when that slot now points to Transfer object B.
```

## Why this is not yet production-ready

The report text is now concrete enough for maintainer review, but the final filing should choose one fix framing:

```text
- identity-checked deactivation;
- duplicate same-user/same-token activation rejection;
- explicit local session/generation ID.
```

Any of these can satisfy the regression if they preserve legitimate queue, retry, resume, and duplicate-F-init handling.
