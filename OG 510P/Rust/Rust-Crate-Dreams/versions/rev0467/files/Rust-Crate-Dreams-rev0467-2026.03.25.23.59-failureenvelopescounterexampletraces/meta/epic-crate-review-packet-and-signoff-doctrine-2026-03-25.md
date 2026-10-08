# Epic crate doctrine — review packets and signoff rails (2026-03-25)

A worthy Rust crate should increasingly be planned not just as an analyzer, verifier, or policy engine, but as a **review burden reducer**.

That means the crate should hand another team a packet that is:
- small enough to read,
- explicit enough to challenge,
- structured enough to archive,
- stable enough to hand off,
- and honest enough to stay useful when the answer is “unknown”, “manual review”, or “expired”.

## Core idea

A **review packet** is the compact human-and-machine handoff object that sits above:
- raw receipts,
- reviewed evidence bundles,
- promise tiers,
- and policy verdicts.

It should answer:
1. what scope is being approved,
2. what decisive evidence was used,
3. what the current verdict or recommendation is,
4. what remains unknown or refused,
5. what exceptions are active,
6. and when this packet must be revisited.

## Default artifact family

A first credible review-handoff crate family should usually export:

### 1. `review-intake.json`
Minimal request and scoping object.
It should name:
- crate / version / release set,
- requested profile,
- decision scope,
- receiver role,
- imported evidence bundle references,
- and whether fresh collection is allowed or the basis must stay frozen.

### 2. `review-packet.json`
Primary compact machine-readable packet.
It should include:
- decisive evidence references,
- current verdict or recommendation,
- support/conformance summary,
- active unknown / degraded / refused states,
- policy and profile IDs,
- explicit non-claims,
- and cost/risk notes when the decision changes build or review burden.

### 3. `signoff-ledger.jsonl`
Append-only history of human decisions.
Each record should include:
- actor role,
- signoff state,
- timestamp,
- packet hash or packet reference,
- rationale snippet,
- supersedes / superseded-by relation,
- and expiry if applicable.

### 4. `override-register.json`
Visible active exceptions.
It should keep waivers first-class by naming:
- rule or constraint being bypassed,
- who approved it,
- why,
- what compensating controls exist,
- and exactly when the override expires.

### 5. `maintenance-summary.md`
Human summary for the next reviewer.
This should be intentionally short.
It should answer:
- what was approved,
- why,
- what remains open,
- what changed since the prior packet,
- and what triggers reapproval.

### 6. `reapproval-plan.json`
Explicit replay and staleness contract.
It should name:
- expiration windows,
- event-based triggers,
- minimal rerun slice,
- escalation rules,
- and who gets the rerun result.

## Signoff-state vocabulary

A shared review layer should prefer a small vocabulary:
- `draft`
- `ready-for-review`
- `approved`
- `approved-with-expiry`
- `blocked`
- `superseded`
- `stale`

This vocabulary should stay separate from:
- raw evidence states,
- support/conformance tiers,
- and policy verdict vocabulary.

Those layers serve different purposes.

## Theory: why this crate class is worthy

The ecosystem already has many analysis tools.
The missing leverage is often not one more analyzer, but a crate that:
- compresses analysis into durable review objects,
- helps maintenance work become visible rather than tribal,
- lowers reviewer re-entry cost,
- and carries decisions across release, staffing, and policy churn.

That makes the crate multiplicative.
It helps not only the first operator, but every later operator.

## Practice: what a credible `0.1` should do

A worthy `0.1` review-handoff crate should **not** try to solve all governance.
It should:
- support one narrow receiver class,
- support one or two profiles,
- import a bounded evidence basis,
- emit one compact review packet and one human summary,
- preserve signoff history append-only,
- and make expiry/reapproval visible.

It should **not** claim:
- organization-wide workflow orchestration,
- universal policy semantics,
- cryptographic nonrepudiation,
- or deep compliance automation.

Those may become later extensions, but are not needed for a worthy first release.

## Honest refusal boundary

A review-handoff crate should refuse to claim:
- that a human actually approved something unless a ledger record exists,
- that a packet is fresh if the reapproval plan says it is stale,
- that prototype substrate data carry stable semantics when they do not,
- or that an exception is harmless just because it is documented.

## What the crate should provide other people

At its best, this class of crate provides other people with:
- less rereading,
- less hidden exception debt,
- less confusion about what was actually decided,
- less ambiguity about when to rerun,
- and less institutional amnesia.

That is worthy because it turns analysis into repeatable adoption and maintenance behavior, not just a prettier report.
