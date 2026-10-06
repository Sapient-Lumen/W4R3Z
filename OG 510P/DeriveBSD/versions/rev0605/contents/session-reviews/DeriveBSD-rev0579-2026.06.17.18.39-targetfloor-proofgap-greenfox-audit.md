# DeriveBSD-rev0579-2026.06.17.18.39-targetfloor-proofgap-greenfox audit

## Intent

This revision spends effort on the riskiest unfinished lane instead of adding a new doctrine family: real FreeBSD host proof. The concrete move is to correct the live supported legacy floor, refresh every schema/example/operator surface that encodes it, and keep the absence of an imported real-host proof visible as the next blocking gap.

## Substantive changes

- Moved the live supported FreeBSD host-proof legacy floor from 14.3-RELEASE / kern.osreldate >= 1403000 to 14.4-RELEASE / kern.osreldate >= 1404000.
- Kept primary production target at 15.1-RELEASE / kern.osreldate >= 1501500.
- Bumped host-proof matrix/bundle and cube generated-artifact cuts to 2026-06-17r605.
- Regenerated host-smoke receipt examples, proof bundle examples, validation fixtures, operator packet, current docs, generated catalog/context/risk/artifact summaries, and synthetic ledger example.
- Refactored the real-host operator-packet guard so its reuse token matches the generated packet and stays constant-bound.
- Reduced docs/00-index.md back under the front-door size budget while preserving changelog release coverage.

## Audit/refactor notes

- The operator packet is now guarded against stale token drift: the checker accepts the exact generated `Do not reuse a handoff directory` wording and still requires the handoff overwrite guard, symlink refusal, sealed-import path, and no simulation flags.
- The front-door index had started to exceed the size budget after the new r605 note. It was compressed without removing changelog release coverage; this is a small anti-sprawl correction rather than another registry.
- Generated doc/catalog/context artifacts were regenerated after the front-door edits so the current-generated surface does not lie about the cube.

## Remaining risk

The big risk did not disappear: this cloudtainer still cannot manufacture a real FreeBSD hardware proof. `validation/freebsd-host-proof-imports/` remains empty, so the next meaningful step is a physical or VM FreeBSD 15.1 primary-production handoff imported through the strict path with no theatre flags.

## Validation

- Release-critical hygiene: 49/49 passed; ledger: `session-reviews/{base}-release-critical-ledger.json`.
- Schema-cube audit profile: 3/3 passed; ledger: `session-reviews/{base}-schema-cube-audit-ledger.json`.
- Python bytecode artifacts cleaned before packaging.
- ZIP integrity is checked after package creation.

## Next best work

Collect one real FreeBSD 15.1 handoff and import it. Do not add more transport hardening or target-matrix ceremony until the cube contains at least one real host proof bundle from outside simulation/refusal paths.
