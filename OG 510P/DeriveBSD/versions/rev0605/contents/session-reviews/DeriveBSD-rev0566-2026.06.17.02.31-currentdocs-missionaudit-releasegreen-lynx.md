# DeriveBSD rev0566 mission audit: current-docs correction and release-critical refresh

Source archive: `DeriveBSD-rev0565-2026.06.16.21.17-archivesnapshot-raceguard-releasegreen-serval(2).zip`  
New linked revision basename: `DeriveBSD-rev0566-2026.06.17.02.31-currentdocs-missionaudit-releasegreen-lynx`  
Internal cube cut observed: `2026-06-16r594`  
Cloudtainer result: release-critical profile completed by resume ledger with `48/48` checks passed and `0` failures.

## Heart of the mission

DeriveBSD is trying to be an evidence-first FreeBSD derivation system, not merely a package manager, a documentation corpus, or a hypervisor wrapper. The mission-bearing loop is:

`typed manifest -> lock -> plan -> artifact -> activate/launch -> rollback/explain receipt`

The strongest form of the idea is that a host generation or microVM workload can be derived, confined, activated atomically, rolled back, and explained with receipts whose trust boundaries are explicit. The BSD-specific center is ZFS boot environments and snapshots, jails, bhyve, pf anchors, Capsicum/Casper, and a store/sandbox/cache/trust pipeline that treats unverified behavior as `unverified` rather than papering over uncertainty.

## What is still missing

The critical missing piece remains a non-simulated FreeBSD host-proof receipt for the removable-media local fallback lane. The archive has strong handoff, preflight, proof-theatre, sealed-import, and import-audit machinery, but it still does not contain the real-host receipt bundle that would prove the lane outside the cloudtainer. This revision does not claim that proof.

The second missing piece is a boring v0 vertical slice: one minimal manifest that becomes a lock, plan, artifact, activation or microVM launch, rollback, and `derive explain` output. Without that, the cube can keep proving its proof system while the user-facing product remains implicit.

The third missing piece is an explicit FreeBSD target matrix. The archive is FreeBSD-first and has a release-floor story, but the host-proof plan should say which release families are acceptance targets, which are legacy floors, and what each must prove.

## What went wrong or wasteful

A concrete drift bug was present in the front-door current docs. `docs/current/cube-schema-audit.md`, `docs/current/cube-schema-refactor-backlog.md`, and `docs/current/cube-hygiene-checkset.md` still described `2026-06-16r591`, while their canonical generated artifacts were already `2026-06-16r594`. The generated JSON was right; the operator-facing summary was stale.

That matters because DeriveBSD's central promise is evidence alignment. A stale current page is not a catastrophic implementation bug, but it is exactly the sort of small mismatch that turns receipts into theatre if allowed to accumulate.

There is also real check-surface cost. The live hygiene manifest now reports `381` top-level check scripts referenced by hygiene, with `48` release-critical checks and `291` deep-contract checks. The tool tree has repeated helper shapes, including `load_json` in `203` function definitions by a simple AST-name count. Some repetition is acceptable for tiny checkers, but unchecked repetition makes release work slower and weakens confidence in what each checker uniquely proves.

## What changed in this revision

This revision corrected the stale current-facing docs so they match the r594 generated artifacts:

- `docs/current/cube-schema-audit.md` now reports r594 and the live schema audit counts.
- `docs/current/cube-schema-refactor-backlog.md` now reports r594 and the live backlog counts.
- `docs/current/cube-hygiene-checkset.md` now reports r594 and the live hygiene manifest counts, including `release_critical_count: 48` and `top_level_check_scripts: 381`.
- `spec/examples/cube.hygiene.run.ledger.json` was refreshed after the doc edits so its cube input fingerprint and rows reflect the revised source/docs/spec/tools/fixtures surface.
- This review, summary JSON, and fresh ledgers were added under `session-reviews/`.

## Validation evidence

Focused schema-cube profile:

```text
result: passed
checks_completed: 3
checks_total: 3
counts: {failed: 0, passed: 3, timed_out: 0}
ledger: session-reviews/DeriveBSD-rev0566-2026.06.17.02.31-currentdocs-missionaudit-releasegreen-lynx-schema-cube-audit-ledger.json
```

Release-critical profile:

```text
result: passed
checks_completed: 48
checks_total: 48
counts: {failed: 0, passed: 48, timed_out: 0}
ledger: session-reviews/DeriveBSD-rev0566-2026.06.17.02.31-currentdocs-missionaudit-releasegreen-lynx-release-critical-ledger.json
```

Note: one continuous cloudtainer command hit the outer command timeout after writing a valid partial ledger. `tools/hygiene.py --resume-ledger` then reused only rows with matching cube, runner, wrapper, release, and tool fingerprints and completed the remaining checks. The final ledger is complete and passed.

Additional focused checks run after the correction included duplicate-key rejection, FreeBSD host-proof bundle validation, hygiene-run ledger validation, and full spec example validation.

## Recommended changes next

1. Put the real FreeBSD host-proof import ahead of all new receipt families. If no FreeBSD host is available, record that as the blocker rather than adding more ceremony.
2. Add a small exact-current-summary checker binding `docs/current/cube-schema-audit.md`, `docs/current/cube-schema-refactor-backlog.md`, and `docs/current/cube-hygiene-checkset.md` to the generated JSON counts. This revision fixed the drift; a checker should prevent the next one.
3. Promote a target matrix for FreeBSD releases and hardware assumptions. The proof lane should say what is expected on production, legacy, and unsupported FreeBSD lines.
4. Define the smallest v0 vertical slice and make each future revision either advance that slice, import real host proof, or delete/retire ambiguity.
5. Consolidate checker helper duplication only where it reduces release-critical runtime and cognitive load; avoid refactors that create another framework.

## Speculation

The promising version of DeriveBSD is an OS whose most important UX is not installation but explanation: an operator can ask why a byte, authority, key, network rule, or workload exists, and the system can answer from signed provenance rather than convention.

The dangerous version is a machine-readable theology of receipts: every turn adds a schema, every schema gets a fixture, every fixture gets a checker, but the physical host path and v0 product path remain unproved. The antidote is not less rigor; it is fewer, sharper proofs tied to real activation, launch, rollback, and import events.
