---
project: Immoral Wealth
status: claim_edge_pilot_and_validator_refactor
claim_kind: archive_refactor_and_claim_migration
route_role: archive_governance_core
canonical_anchor: true
revision_current: rev0358
base_revision: rev0357
codename: claim-edge-pilot-ai-large-load-and-validator-history-refactor
generated_at: 2026-06-18T09:28:19Z
---

# Claim-edge pilot, AI large-load refactor, and validator-history repair — rev0358

## Executive result

Rev0358 moves from “we need claim-level evidence” to a first working pilot: **six locator-bounded verified claim edges** now exist in `cases/VERIFIED_CLAIM_EDGE_LEDGER.json`.

The pilot is deliberately narrow. It verifies load materiality and regulatory salience for the AI/data-center public-backstop case, while also stating the boundary: those facts do **not certify project-level cost shift**, water/local incidence, or enforceable public-upside recovery.

Current live counts: **95 case memos**, **95 scoreboards**, **537 sources**, **367 registered fields**, **50 registered_unused fields**, and **6793 mechanical evidence associations**. Rev0358 also adds **6 locator-bounded verified claim edges** without treating them as case certification.

## Substantive case refactor

The AI/data-center case now has `cases/ai-data-center-grid-water-public-backstop-rev0320-claim-packet.json`, which splits the case into:

1. verified premises: national load materiality, forecast/method uncertainty, federal large-load/co-location regulatory salience;
2. unverified decisive premises: project cost assignment, water/local public-service incidence, and public-upside recovery;
3. the next three edges to build from primary instruments.

## Audit/refactor performed

The validator-history audit found **79** check functions and **47** release-specific checks. Rev0358 patches the most immediate failure mode: the rev0357 check no longer freezes the current archive at zero verified claim edges. The old zero-edge fact remains historical; it no longer blocks forward evidence migration.

## What still blocks certification

No case is certified current. The AI/data-center pilot supports an audit obligation and public-instrument routing. It does not certify burden allocation. Certification remains blocked until primary instruments answer:

- who pays project-caused grid/generation/service costs;
- who bears water/local-service costs and failure risk;
- whether claimed public benefits are enforceable, measurable, and senior to private uptime/financing claims.
