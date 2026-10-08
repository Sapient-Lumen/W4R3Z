
# Freshness Refactor Report

rev0184 executes a focused audit/refactor of the cube's evidence-freshness cluster.

## Audit finding

The archive had a strong but diffuse insight: proof objects decay. But the files used too many near-synonyms without a shared control layer:

- stale;
- expired;
- old;
- cached;
- dormant;
- unsupported;
- unrefreshed;
- unverified;
- unrevoked;
- unreconciled;
- archive-only;
- grace-period;
- challenged.

These are not interchangeable. A stale artifact can still be usable. An expired artifact might be usable under grace. A revoked artifact is different from a superseded one. An archive-only artifact may be admissible for history but not current reliance. A source-unavailable state can justify fallback reliance without validating the underlying claim.

The audit therefore concludes that evidence freshness should be a **model family**, not a proliferation engine.

## Files refactored

rev0184 adds metadata to eighteen existing dossiers:

1. `authority-freshness-guarantees-become-compliance-metrics`
2. `delegate-freshness-proofs-become-a-service-metric`
3. `gate-expiry-disputes-become-a-service-layer`
4. `graceful-degradation-becomes-a-constitutional-design-problem`
5. `history-retention-floors-become-procurement-terms`
6. `portable-validation-reports-become-a-quiet-mutual-recognition-surface`
7. `post-waiver-validation-certificates-become-a-service-tier`
8. `regression-disclosure-windows-become-a-governance-surface`
9. `renewal-history-normalization-services-become-a-quiet-broker-market`
10. `revalidation-windows-become-a-standing-operational-burden`
11. `revocation-propagation-becomes-a-hidden-reliability-bottleneck`
12. `security-feed-uptime-obligations-become-supplier-grade-commitments`
13. `stale-clearances-split-into-distinct-fault-classes`
14. `successor-map-freshness-guarantees-become-a-service-metric`
15. `supported-version-windows-become-quiet-exclusion-regimes`
16. `validation-expiry-dates-become-procurement-terms`
17. `validator-services-become-outsourced-certifiers`
18. `vex-expiry-governance-becomes-a-procurement-term`

Each now has `refactor_cluster: evidence-freshness`, a `freshness_role`, and a `consolidation_status` value.

## What changed conceptually

Before rev0184, a dossier could earn promotion by identifying a new freshness-sensitive artifact. After rev0184, that is no longer enough. The dossier must say which freshness clock matters and what reliance state changes when the clock fails.

The refactor introduces three editorial statuses:

| Status | Meaning | Treatment |
|---|---|---|
| `standalone-mechanism` | introduces a transferable institutional mechanism | keep as dossier |
| `bridge-dossier` | connects the model to an adjacent family | keep but cross-reference |
| `model-substate` | mainly names a state inside the freshness model | keep for now, but candidate for future consolidation |

## Immediate effects

- The cube has a new reusable model: `19-evidence-freshness-model.md`.
- The lifecycle vocabulary is tightened in `21-state-vocabulary-refactor.md`.
- `INDEX/freshness-family-audit.csv` lists the affected dossiers and their roles.
- `INDEX/freshness-state-lexicon.json` provides a machine-readable state vocabulary.
- `INDEX/refactor-actions.csv` records the actual metadata changes.
- Four new dossiers were added only where the refactor exposed missing surfaces: cache-age disclosure, grace-period registries, certificate-renewal automation, and staleness arbitrage.

## Recommended next pruning

The next consolidation pass should consider merging or shortening these into the model unless new evidence surfaces appear:

- `gate-expiry-disputes-become-a-service-layer`
- `revalidation-windows-become-a-standing-operational-burden`
- `stale-clearances-split-into-distinct-fault-classes`
- `history-retention-floors-become-procurement-terms`

They remain useful, but they are increasingly better understood as states and clauses inside the evidence-freshness model.

## What not to do next

Do not add more dossiers with titles of the form “X expiry becomes Y” unless the new file contributes one of:

- a new clock;
- a new relying actor;
- a new fallback constitution;
- a new abuse or arbitrage pattern;
- a new enforcement surface;
- a new global-unevenness burden.
