# MTGSim rev0164 — Committed Declaration Snapshot Seal

## Mission-risk addressed

rev0163 made failed paid-action rollbacks independently challengeable by carrying a compact rollback declaration snapshot. The matching success path still relied on a terminal `PaidActionTransactionRecord` linking outward to a separate `PaidActionDeclarationRecord`. That was correct inside a live `GameState`, but weaker for detached transaction review: the final receipt sealed a declaration hash without carrying the declaration payload that lets an offline verifier recompute it from the same terminal row.

rev0164 closes that success-side replay gap. A committed paid-action transaction now embeds `committed_paid_action_declaration_snapshot`, a compact copy of the committed declaration/cost-lock record. The linked declaration remains the canonical journal row; the snapshot is a self-contained verifier surface on the terminal transaction receipt.

## Code changes

- Bumped `kPaidActionTransactionRecordSchemaVersion` to `4`.
- Added `committed_paid_action_declaration_snapshot_present` and `committed_paid_action_declaration_snapshot` to `PaidActionTransactionRecord`.
- Included the committed snapshot fields in the stable transaction identity hash under the new v4 salt.
- Populated the committed snapshot from the linked declaration immediately before sealing the terminal transaction hash.
- Hardened validation so committed receipts must carry a snapshot that recomputes `paid_action_declaration_hash`, matches transaction identity, preserves placement/hash links, preserves phase spans, and distinguishes zero-cost/no-payment successful casts from paid actions with a nonzero payment span.
- Preserved rollback hygiene: rollback receipts still use `speculative_paid_action_declaration_snapshot`; validators now reject rollback rows that carry a committed snapshot.

## Audit/refactor note

The validation audit deliberately avoided creating a new registry layer. The key refactor is conceptual and executable: a terminal transaction receipt should be able to prove the declaration/cost-lock payload it seals whether it committed or rolled back. The validator now has symmetric snapshot checks for both outcomes while still preventing speculative rollback payloads from leaking into committed rows and committed snapshots from leaking into rollback rows.

## Online research and speculation

- Wizards' public rules page still presents the Comprehensive Rules as the authoritative corner-case reference and links DOCX/PDF/TXT surfaces: https://magic.wizards.com/en/rules
- The local manifest remains metadata-only and pinned to the packaged 2026-04-17 ledger source until a dedicated refresh/diff revision. The online observation during this pass continued to treat the 2026-06-19 Comprehensive Rules TXT/PDF as the current external rules source.
- OpenSpiel's model of `State`, legal actions, `ApplyAction`, `Child`, serialization, observations, and chance outcomes remains the right comparison point for future agent/search APIs: https://openspiel.readthedocs.io/en/latest/concepts.html and https://openspiel.readthedocs.io/en/latest/api_reference.html
- LLVM libFuzzer's emphasis on deterministic, fast, in-process fuzz targets reinforces the current cloudtainer priority: keep the MTGSim fuzz/action harness centered on compact transition receipts and low-overhead corpus cases, not broad subprocess-heavy scenario sweeps: https://llvm.org/docs/LibFuzzer.html

## Evidence

- Release all-in-one smoke: `reports/harness/cpp_allinone_release_rev0164_smoke.json` (`337/337`, 0 failures).
- Rule coverage: `reports/rules/rule_coverage_rev0164_latest.json` after metadata refresh.
- Datacube audit: `reports/audit/datacube_audit_rev0164_latest.json` after build payload cleanup.

## Next risk

The next high-risk seam is export/access. The C++ struct now contains enough success/rollback declaration payload to challenge terminal receipts, but CLI/trace export surfaces should expose those snapshots in a stable text/JSON shape so agents do not need to link against private C++ structs.
