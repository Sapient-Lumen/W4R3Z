# Mission audit — REV0112: self-contained handoff gate

Current package: `CloudtainerML-rev0112-2026.07.06.17.02-selfcontainedhandoffgate-caracara.zip`  
Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

- Upgraded `tools/public_trace_handoff_archive_gate.py` so a handoff manifest must include `public_trace_handoff_toolpack_v1` and a `toolpack_subject_set_sha256`.
- Required tool subjects now include the selector receipt replay gate, selector-entry gate, evaluation verdict tool, provenance verifier surrogate, and handoff archive gate itself.
- Upgraded `tools/public_trace_handoff_archive_audit.py` to build a fixture archive containing trace/provenance/receipts/toolpack files and to prove that tampering, path escapes, missing tool subjects, forged subject-set hashes, and tool tampering block.
- Refactored the current top-level handoff docs so the operator sees one current path rather than stale historical routes.

## Why this is risk-reducing

Rev0111 made the handoff archive portable by digest, but the replay still leaned on current cube tools. That is a subtle false-green risk: an archive could look complete while the real evaluator/verifier/selector code was supplied by a different checkout. Rev0112 binds the archive to the relevant toolchain digests.

## Remaining blockers

- No real public TinyLlama trace NPZ/provenance bundle exists here.
- No accepted real evaluation receipt or selector-entry receipt exists here.
- No named-hardware sparse-vs-dense timing exists here.

This revision is still non-promotional.
