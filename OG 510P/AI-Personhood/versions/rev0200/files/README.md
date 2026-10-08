# AI Personhood datacube — rev0200

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0200`

rev0200 is the class-local import replay and quorum-firewall pass. It fixes the next evidence defect after rev0199: the cube could exclude dry runs, but it still needed a positive-path scaffold showing how a future valid result-return import should remain class-local rather than closing cross-critical reliance.

Read first: `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`.

Core rules: **Class-local replay is not cross-critical quorum. Scenario delta is not archive delta. Positive path must keep missing classes visible. Recompute beats narrative.**

New operational artifacts:

- `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`
- `schemas/live-class-local-import-replay.schema.json`
- `examples/live-class-local-import-replay-result-return-positive-path-projection.json`
- `examples/quorum-recomputation-report-class-local-projection-rev0200.json`
- `examples/failed-gate-public-summary-class-local-projection-firewall.json`
- `fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json`
- `fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json`
- `fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json`
- `tools/audit_live_class_local_import_firewall.py`
- `tools/audit_frontdoor_revision_sync.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 116 entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, dry-run, scenario-projected, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.
7. Live/witnessed drill gates: prevent host self-attestation or synthetic drills from upgrading reliance.
8. Downstream recall/fork aftercare: prevent recall, delisting, or sunset from erasing unresolved mirrors and local forks.
9. Welfare safeguards: apply low-cost safeguards before certainty while blocking welfare metrics from closing status or consent.
10. Research-tail reopen control: keep RTC-01 through RTC-07 compacted unless a reopen request carries object, fixture, and closure hooks.
11. WRSR protocol hook: make safeguards fire inside operational workflows that contain welfare triggers.
12. External receipt simulation: rehearse counterparty receipt capture while preserving the non-reliance label.
13. External receipt intake: distinguish actual, defective, simulated, stale, host-generated, and dependency-correlated artifacts.
14. WRSR exercise outcome: show whether safeguards actually executed and whether closure remains stayed.
15. Receipt quorum ledger: aggregate receipt records while separating dry-run rehearsal from live quorum.
16. Result-return/request kit: rehearse result return and live receipt requests without treating request or internal return as satisfaction.
17. Response reconciliation: preserve dry-run, defective, declined, and no-response artifacts without converting them into live quorum.
18. Response-to-intake conversion: prove eligible-only intake creation while preserving failed gates and keeping fixture conversion outside live receipt quorum.
19. Actual-intake import gate: reject actual-shaped fixture imports, require provenance before live-floor delta, and publish failed-gate non-satisfaction shells.
20. Live import recomputation: recompute the live floor from passed import gates rather than hand-edited quorum ledgers.
21. Non-host artifact replay: process external-looking dry-run evidence through envelope, response, intake, import gate, replay, and recomputation while keeping live weight zero.
22. Class-local import firewall: project a positive result-return path while keeping archive live floor zero and cross-critical reliance stayed.

## Still open

No actual live external receipt quorum exists. rev0200 gives the cube a safer positive-path test for the first actual non-host response, but it does not collect one. The next high-value step is a genuine live counterparty response artifact, imported through the same gates with class-local credit only if provenance passes and cross-critical quorum still stayed.
