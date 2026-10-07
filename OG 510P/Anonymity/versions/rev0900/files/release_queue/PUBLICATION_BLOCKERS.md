# Publication Blocker Ledger

- Generated for revision: `rev0900`
- Checked bundle: `Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`
- Publication authorized: `false`
- Ready to publish: `false`
- Status: `pass`

## Selected dry-run source

- Source: `series/release_and_destination/paperA_release_property_ledger_receipts/paper.tex`
- SHA-256: `565ea8ef40319deea189930a6f223e4b49f9a7f567398ce9f35af8c38fe9a0cd`
- Queue note: `release_queue/published_ready/2026.03.16-paperA-release-property-published-ready.md`
- Prospective target: `published/2026-06-18_privacy_as_a_release_property_for_anonymous_dhts`

## Open blocking gates

### BLK-001 — evidence_pack_resolution

- Status: `pending`
- Detail: attach_evidence_pack_or_record_explicit_waiver
- Required resolution: resolve this freeze-plan gate
- Command: `python3 -B publishing/rebuild_archive_surfaces.py --root .`
- Evidence surface: `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`

### BLK-002 — internal_hostile_arithmetic_vectors

- Status: `pending`
- Detail: No attached evidence-pack manifest, so hostile arithmetic vectors cannot be read.
- Required resolution: resolve this freeze-plan gate
- Command: `python3 -B publishing/rebuild_archive_surfaces.py --root .`
- Evidence surface: `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`

### BLK-003 — external_hostile_reviewer_signoff

- Status: `pending`
- Detail: Publication remains blocked until a named external/adversarial review or countersignature tries the State/MUCC arithmetic and threat-transfer rows; internal vectors and a ready packet are not enough.
- Required resolution: resolve this freeze-plan gate
- Command: `python3 -B publishing/rebuild_archive_surfaces.py --root .`
- Evidence surface: `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`

### BLK-004 — manual_clean_latex_compile

- Status: `pending`
- Detail: source-bound compile evidence exists, but the current publication compile gate remains pending: pending_evidence_pack_attachment
- Required resolution: refresh a current deterministic clean LaTeX compile witness
- Command: `python3 -B publishing/build_freeze_compile_witness.py --root . --force-compile`
- Evidence surface: `reports/freeze_compile_witness.json`

### BLK-005 — explicit_publication_decision

- Status: `pending`
- Detail: A new release_queue/decisions/* publication decision must name the source hash, evidence resolution, hostile-review state, compile witness, and target.
- Required resolution: write a completed publication decision note naming source, hash, target, evidence pack, compile witness, freeze packet, queue note, citation-head update, and receipt obligation
- Command: `python3 -B publishing/check_publication_decision_authorization.py --root . --write-report reports/publication_decision_authorization.json`
- Evidence surface: `reports/publication_decision_authorization.json`

### BLK-006 — metadata_and_provenance_refresh

- Status: `pending`
- Detail: After any freeze, refresh CITATION/RO-Crate/provenance/manifest surfaces before packaging.
- Required resolution: after any gate-closing change, rebuild research metadata, provenance, manifest, schemas, invariants, and packaging surfaces
- Command: `python3 -B publishing/rebuild_archive_surfaces.py --root .`
- Evidence surface: `reports/research_metadata_integrity.json`

## Bound surfaces

- `release_queue/NEXT_RELEASE_FREEZE_PLAN.json` — present, sha256-prefix `2dd21ed04bce4467`
- `reports/publication_rehearsal.json` — present, sha256-prefix `7283942e75d7edb6`
- `reports/freeze_toolchain.json` — present, sha256-prefix `f043d6e652e18217`
- `reports/freeze_compile_witness.json` — present, sha256-prefix `fd6528b9d47dfb22`
- `reports/evidence_pack_integrity.json` — present, sha256-prefix `4c8b71f9390f19e8`
- `reports/freeze_packet_integrity.json` — present, sha256-prefix `7a4b9a2e3d937c2d`
- `reports/publication_decision_template.json` — present, sha256-prefix `627b234b36cfabeb`
- `reports/publication_decision_authorization.json` — present, sha256-prefix `22de0f0c60c820cd`
- `reports/publication_boundary.json` — present, sha256-prefix `10e9bb92a890e526`
- `reports/research_metadata_integrity.json` — present, sha256-prefix `c5d2b19758df605e`
- `reports/archive_packaging_recipe.json` — present, sha256-prefix `f4d2e7a33b73fc1a`
