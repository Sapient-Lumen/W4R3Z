# Verification Campaign Workbench Kit — product plan (2026-03-21)

This note sharpens **P-0485 Verification Campaign Workbench Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0485** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should **not** try to become a universal verifier, a new theorem prover, or a complete assurance-case platform.
It should provide one boring, reviewable **verification campaign contract** above today’s verification lanes.

`0.1` should make five things first-class:

1. **obligation inventory** — what exactly was meant to be checked and what evidence classes count;
2. **lane semantics** — what each imported tool lane actually means;
3. **trust ledger** — what trusted assumptions, externals, stubs, waivers, or manual-review escapes exist;
4. **policy evaluation** — why the campaign is green, yellow, or red;
5. **comparability / drift** — whether one campaign can honestly be compared with another.

## What `0.1` should provide other people

- one compact `campaign-manifest.json`
- one or more compact `obligation-record.json` files
- one or more compact `lane-result.json` files
- one compact `trust-ledger.json`
- one compact `policy-evaluation.report.json`
- one compact `campaign-diff.report.json`
- one compact `verify-campaign.json`
- one compact `campaign.summary.md`
- one compact `campaign.diff.md`
- a portable review/support bundle

## Commands worth shipping first

- `cargo verify-campaign init`
- `cargo verify-campaign collect-miri`
- `cargo verify-campaign collect-kani`
- `cargo verify-campaign collect-creusot`
- `cargo verify-campaign collect-prusti`
- `cargo verify-campaign collect-flux`
- `cargo verify-campaign collect-verus`
- `cargo verify-campaign evaluate`
- `cargo verify-campaign diff`
- `cargo verify-campaign bundle`
- `cargo verify-campaign inspect`

## What to import, not reinvent

- raw Miri findings and run context
- Kani harness / contract / stub posture
- Creusot prove / replay context
- Prusti trusted-function and assumption posture
- Flux refinement-check scope
- Verus trusted / external component posture
- shared bundle substrate from **P-0256 Evidence Bundle Core Kit**

## Suggested `0.1` doctor warnings

- `dynamic_lane_claimed_as_proof`
- `new_trust_surface_without_policy_ack`
- `campaign_green_with_manual_review_gap`
- `comparability_drift_hidden_by_summary_only`
- `tool_version_change_without_lane_semantics_refresh`
- `trusted_function_or_stub_missing_ledger_entry`
- `partial_scope_lane_claimed_as_global_green`

## First proving-ground scenarios

1. **Miri dynamic execution is valuable evidence, but it does not satisfy bounded-proof or theorem-proof obligations by itself.**
2. **Kani contract stubbing can reduce proof cost while still adding explicit trust surface that belongs in the ledger.**
3. **Creusot replay/prover context drift can make a campaign only partially comparable, even when proofs still pass.**
4. **Prusti trusted functions and assumptions must visibly affect policy, not hide inside tool logs.**
5. **Flux and Verus can each cover strong but partial slices, so the obligation inventory must stay explicit before a campaign can go green.**

## What to leave for later

- full proof-session IDE workflows
- hosted artifact portals and dashboards
- universal translation between every verification language
- automated synthesis of assurance cases
- bespoke prover orchestration infrastructure
- claims that all lanes can be losslessly compared
