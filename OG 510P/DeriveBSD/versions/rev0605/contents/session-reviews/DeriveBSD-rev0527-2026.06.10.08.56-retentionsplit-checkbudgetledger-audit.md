# DeriveBSD rev0527 risk-first session audit

## Session cut

- Revision: `2026-06-10r559`
- Archive focus: `retentionsplit-checkbudgetledger`
- Base: `DeriveBSD-rev0526-2026.06.10.06.23-successorcheckpointsplit-runbudgetledger-postdetachclosure-hare.zip`

## What changed

This cut deliberately avoided adding another doctrine/registry surface. It made one p0 schema-cube split and one hygiene-runner completion fix that reduces the chance of losing work in the cloudtainer.

### 1. Reader-use ledger retention split

`spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json` is now a generic runtime schema. The exact r518 canonical literal surface moved into `spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json`.

The retention checker now validates the canonical receipt against both schemas. Runtime validation remains shape/contract-oriented; exact historical literals remain fixture-only. The positive fixture and negative corpus were revalidated after the split.

### 2. Check-budget ledger evidence

`tools/hygiene.py --max-checks` previously stopped a ledger run deliberately, but the resulting ledger did not explicitly say that the wrapper stopped because of a check-count budget. That made chunked runs harder to distinguish from other incomplete evidence.

The hygiene ledger now records:

- `check_budget_limit`
- `check_budget_status`

The status is `stopped-before-check-budget` for an intentional partial chunk and `completed-within-check-budget` when the selected profile finishes under a check budget. `tools/check_cube_hygiene_run_ledger.py` includes a regression for this path.

## Audit findings

- The retention split did expose a useful boundary: retention expiry remains the next p0 target, so the next pass should check whether expiry/enforcement still freeze exact retention literals in runtime schemas.
- A combined inline-code token in `CHANGELOG.md` caused `check_discovery.py` to treat `tools/hygiene.py --max-checks` as a path. The changelog now splits the file path and CLI flag into separate inline-code tokens.
- `docs/00-index.md` was already at its hard line ceiling. This cut kept the line budget honest by removing nonsemantic blank lines instead of raising the threshold.
- Raw Python generator/checker invocations can still create `__pycache__` in `tools/`. The final package path removes those artifacts and validates with `check_no_python_bytecode_artifacts.py`.
- The post-detach profile is still too large for one comfortable cloudtainer invocation, but rev0526/rev0527 chunking works: the run completed through explicit resume and ended with 39/39 passed.

## Validation evidence

- `session-reviews/DeriveBSD-rev0527-2026.06.10.08.56-retentionsplit-checkbudgetledger-release-critical-ledger.json`
- `session-reviews/DeriveBSD-rev0527-2026.06.10.08.56-retentionsplit-checkbudgetledger-postdetach-ledger.json`
- `session-reviews/DeriveBSD-rev0527-2026.06.10.08.56-retentionsplit-checkbudgetledger-schema-cube-ledger.json`
- `session-reviews/DeriveBSD-rev0527-2026.06.10.08.56-retentionsplit-checkbudgetledger-generated-surface-ledger.json`

## Next best target

Split `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json`, then audit retention-expiry enforcement for hidden exact-fixture coupling before touching launch evidence.
