# Mission audit — REV0113

## What changed

rev0113 targets the riskiest remaining handoff boundary from rev0112: the archive was described as self-contained, but the bundled gate and replay verifier still assumed the presence of `CUBE-META.json` and the current cube checkout when executed directly from the archive. That could let a package pass inside the cube while failing for the next operator after extraction.

## Concrete correction

- Patched `tools/public_trace_handoff_archive_gate.py` to load metadata from `PUBLIC_TRACE_HANDOFF_MANIFEST.json` when `CUBE-META.json` is absent.
- Patched `tools/public_trace_selector_receipt_replay_gate.py` with the same standalone fallback.
- Changed the archive gate to import the replay verifier from the extracted handoff toolpack subject, not from the current cube tools.
- Changed tool identity checks from "matches current cube tool" to "matches extracted handoff toolpack subject digest".
- Added `tools/public_trace_standalone_toolpack_audit.py`, which builds a fresh archive fixture, extracts it, runs the bundled gate from inside the extracted handoff directory, and verifies that a tampered bundled replay gate is rejected.

## Research basis

- SLSA build provenance frames provenance as information consumers can verify against expected artifact production and rebuild expectations: https://slsa.dev/spec/v1.2/build-provenance
- in-toto link attestations bind step products in `subject` and inputs in `materials`: https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md
- Hugging Face Hub download docs say `snapshot_download()` uses the latest revision by default and needs an explicit `revision` for fixed snapshots: https://huggingface.co/docs/huggingface_hub/en/guides/download

## Still blocked

This remains a non-promotional evidence-lane hardening rev. It does not supply the real public pretrained trace or named-hardware timing. It prevents one more false-green handoff mode before those runs happen.
