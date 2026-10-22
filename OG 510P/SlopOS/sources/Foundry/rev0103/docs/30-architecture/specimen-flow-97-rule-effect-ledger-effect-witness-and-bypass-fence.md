# Specimen flow 97 — rule-effect ledger, effect witness, and bypass fence

## Pressure

Specimen 96 proves that a rule was evaluated against a specific carrier/context. The next laundering move is to treat that evaluation result, selected rule, output decision, checker success message, warning, audit-only observation, default outcome, or skipped/deprecated rule as if it actually changed the carrier, export, projection, warning, quarantine, or no-op state.

## New nouns

- **Rule-effect ledger** — a compact record that links a rule-evaluation trace to the semantic effect that was bound, partially bound, quarantined, refused, no-effect, or informational for the same carrier/context.
- **Effect witness** — scoped evidence that a named effect was applied, partial, refused, missing, bypassed, quarantined, or superseded, with context echo and evidence refs.
- **Bypass fence** — a refusal card for paths that skip the effect ledger/witness, widen context, turn weak observations into enforcement, or launder effect residue into authority.

## Fixture commitment

`fixtures/specimen-97-rule-effect-binding/fixture.json` carries six rule-effect ledgers, seven effect witnesses, and eight bypass fences. The checker refuses dangling source trace/witness/fence refs, context echo drift, selected-rule-as-effect, weak-result laundering, missing effect witnesses, missing bypass fences, wrong-scope effects, and authority/public-release/audit/repair/lifecycle/sibling laundering.

## Refactor twin

This pass also adds `fixtures/reference-integrity-index/index.json` and `tools/check_foundry_reference_integrity_index.py`. The index is intentionally small: it ties source fixture collections, id fields, listed ids, and referencing fixture collections together so cross-specimen chains fail when an id is renamed, dropped, or reused without updating the machine-readable reference map.

## Non-goals

This specimen does not make Foundry an enforcement runtime, policy engine, authorization layer, admission controller, mutation engine, feature-flag system, audit product, public-release approval system, compliance engine, repair workflow, lifecycle authority, sibling-verdict engine, or governance registry.
