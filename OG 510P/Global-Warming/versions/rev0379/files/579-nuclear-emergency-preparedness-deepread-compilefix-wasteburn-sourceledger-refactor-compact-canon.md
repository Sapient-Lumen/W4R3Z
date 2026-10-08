# 579 — Nuclear emergency preparedness: deep read, compile repair, waste burn, and source-ledger sync audit

Revision: rev0372  
Base revision: rev0371  
Created: 2026-06-12T17:25:00-04:00  
Claim posture: **capture-ready / submission-packet-ready / response-intake-lockbox-ready / docket-release-watch-open / EOF-LER-watch-open / ANS-transition-gate-open / package-hygiene-repaired / claim-frozen / no local readiness conclusion**

## Purpose

This revision is a cloudtainer hygiene and deep-read correction pass. It does not add real Beaver Valley readiness evidence and it does not close any emergency-preparedness blocker. It repairs package integrity defects and records where future work should reduce waste.

## What was found

1. **The active hotpath is conservative and useful.** Rev0371 correctly treats notices, route pages, fixtures, no-record responses, docket watches, and lockbox scaffolds as acquisition controls rather than readiness evidence.
2. **Two historical validators were syntactically broken.** `tools/validate_nuclear_emergency_bvps_rehydration_conflict_repair_rev0353.py` and `tools/validate_nuclear_emergency_bvps_warroom_packout_rev0344.py` contained broken newline string literals. They were repaired here and a package-wide syntax validator was added.
3. **Root/cube identity had drifted.** The root manifest was rev0371, but `cube/manifest.json` was rev0369 and both schema files were rev0368. Rev0372 synchronizes root/cube manifest, schema, and validation-rules metadata and adds a sync validator.
4. **The source ledger is stale for latest authority-boundary/context sources.** `S1356`, `S1357`, and `S1358` exist in `sources/register.md`, `cube/source.csv`, and recent index rows, but are absent from `cube/source-use-ledger.csv`. This revision records the sync fault; it does not fake edge rows.
5. **The cube carries heavy historical luggage.** The current package is useful, but full-cube scans are wasteful: large historical CSV matrices, many SQLite mirrors, and exact duplicate clusters should not be on the default operating path.
6. **The real evidence gate remains open.** No real or lawfully anonymized BVPS exercise evidence packet has been imported. No static archive can infer local readiness from the FEMA exercise notice, NRC route pages, daily reactor status, or a records-response scaffold.

## Corrective actions in rev0372

- Repaired the two syntactically invalid historical validator scripts.
- Added `tools/validate_tools_compile_rev0372.py` to check every tool script with Python syntax compilation without writing bytecode.
- Added `tools/validate_manifest_schema_sync_rev0372.py` to prevent root/cube manifest/schema/rule drift.
- Added `tools/validate_cloudtainer_deepread_rev0372.py` to bind the deep-read audit and claim-freeze invariants.
- Added `cube/cloudtainer-deepread-audit-rev0372.csv`, `cube/cube-waste-audit-rev0372.csv`, `cube/source-use-ledger-sync-audit-rev0372.csv`, and `cube/resource-manifest-delta-rev0372.csv`.
- Updated the root README and root/cube manifest, schema, and validation-rules files to point at this revision.

## What should change next

- Make the active hotpath the default target and require explicit opt-in for the historical cube luggage.
- Backfill `source-use-ledger.csv` and `source-edge-table.csv` from the canonical index/source register rather than adding hand-written source rows.
- Add a validator that fails when root and cube copies of `manifest.json`, `schema.json`, or `validation-rules.json` disagree.
- Keep the global-warming doctrine layer separate from the BVPS evidence-hotpath layer so the package does not silently become a single-facility nuclear emergency-preparedness archive.
- Continue claim freeze until real evidence artifacts are hashed, scoped, custodially identified, adjudicated, and mapped to proofcut rows.

## Non-closure invariant

This revision is package repair. It is not proof that Beaver Valley emergency planning, EOF backup power, alert/siren transition, ANS performance, public communication, local route execution, or public protective action readiness is adequate.
