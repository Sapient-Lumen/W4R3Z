# meta-0466 — Affected-person evidence receipt pilot and build registry refactor

## Change summary

This note records the rev0786 turn from mission diagnosis into the first bounded affected-person proof pilots.

## Substantive priority

The risky work is claimant and household outcome proof, not another doctrine family. Rev0786 adds the evidence-receipt spine, UI and housing tests, and reader-visible patches to notes `914` and `929` while explicitly refusing to mark field validation complete.

## Audit/refactor

The full build step list now lives in `tools/build_steps.py` and is imported by `tools/build_all.py`. The new `tools/build_evidence_receipts.py` follows the same deterministic generated-output convention as the test matrices. Lint now treats the receipt source, schema, generated surfaces, and source-key/note references as checked artifacts.

## Validation target

`make lint` must pass from the working tree and clean ZIP extraction. Generated `EVIDENCE_RECEIPTS.md` must not claim field validation, and `GAP-029` / `GAP-031` must remain live as in-progress pilots.
