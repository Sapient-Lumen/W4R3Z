# Structural audit rev0308 — local evidence and closure spine

Created: 2026-06-04T03:46:49-04:00

## Main correction

Rev0307 made emergency preparedness sparse, but sparse applicability alone could still become another template layer. Rev0308 adds one local evidence status row for every sparse emergency service-floor/gate binding. The package now carries 264 local proof slots, each with owner, verifier, freshness SLA, corrective-action pattern, public-safe disclosure rule, and a maturity cap.

No row is treated as site-specific proof. Every local evidence row is deliberately initialized as `not_loaded_site_specific_evidence`, so maturity remains capped at `R2_documented_template_only` until a site/project/jurisdiction supplies artifacts.

## Audit/refactor correction

The delivered rev0307 package did not contain `cube/file-core.csv` even though the validation report claimed a passing file-core check. Rev0308 recreates `cube/file-core.csv` and records the defect in `cube/package-integrity-audit-rev0308.csv`. The new validation report includes a direct file-existence and row-count check.

## Generated-view hygiene

The three 114,494-row universal nuclear crossproduct tables are retained for compatibility, but rev0308 marks them as legacy/generated compatibility surfaces in the resource manifest and adds `cube/nuclear-generated-view-migration-plan-rev0308.csv`. Emergency-preparedness applicability should use the sparse rev0308 view and local evidence overlay, not the universal crossproduct.

## Highest remaining risks

1. Populate local evidence rows with real site/project/jurisdiction artifacts.
2. Build a direct 10 CFR 50.54(q)-style emergency-plan-change/effectiveness table.
3. Build a 10 CFR 50.160 performance-objective metrics table for SMR/non-LWR/NPUF branches.
4. Wire AAR findings into corrective-action closure records with retests.
5. Rebuild the SQLite mirror only after the normalized/sparse layer stabilizes.
