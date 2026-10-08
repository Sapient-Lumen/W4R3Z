# 193 — Publishable verifier reports (small, comparable, privacy-safe)

**Track:** Shared

## Purpose

Verifier output is part of the evidence ecosystem. If verifier results are not publishable,
verification can be captured quietly ("it failed on my machine") or suppressed.

This doc defines a **size-disciplined** and **privacy-safe** way to publish verifier results:

- **Small:** report is kilobytes, not a rehosted packet.
- **Comparable:** stable problem codes, not essays.
- **Privacy-safe:** no local paths, hostnames, or internal URLs.

## Two report types (do not conflate)

1. **Packet-scoped report** (what happened for a specific packet):
   - kind: `hfv.verifier.packet_verification_report`
   - schema: `schemas/PacketVerificationReport.json`

2. **Implementation-scoped report** (what the tool claims to implement):
   - kind: `hfv.verifier.report`
   - schema: `schemas/VerifierReport.json`
   - template: `artifacts/templates/verifier-report-payload.json`
   - example packet (minimal): `artifacts/examples/evidence_packet_verifier_report_minimal/`

Packet reports answer: *"Did these bytes match the manifest and registries, under this verifier's rules?"*
Implementation reports answer: *"What is this verifier, and what does it claim to support?"*

## Publishable problem codes

Verifier failures should be expressed as **short codes** so ecosystems can compare results.

Source of truth: `artifacts/registries/verifier-problem-codes.csv`.

Authoritative list (generated): `docs/VERIFIER_PROBLEM_CODES.md`.

Quick operator UX:
- `python3 tools/observer_verify_packet.py --list-codes`
- `python3 tools/observer_verify_packet.py --explain <code>`

Optional human-facing card (implementation-scoped reports):
- `python3 tools/verifier_report_card.py --packet <verifier_report_packet_dir>`

Optional human-facing card (packet-scoped reports):
- `python3 tools/packet_verification_report_card.py --packet <packet_verification_report_packet_dir>`

One-command convenience (auto-detects kind and prints the right card when available):
- `python3 tools/evidence_object_card.py --packet <packet_dir>`

Guidance:
- `problems[]` strings MAY include local context after `:` (e.g., `payload_digest_mismatch:envelopes/x.json`).
- Public reports SHOULD publish **codes only** (no context) unless the context is itself non-sensitive.

## How to produce a publishable packet report (reference tool)

Reference checker: `tools/observer_verify_packet.py`.

To emit a packet report payload JSON:
- `python3 tools/observer_verify_packet.py <packet_dir> --json --public`
- optionally also write it: `--out <path>`

`--public` performs two privacy hardening steps:
- `packet_dir` is reduced to a basename (no absolute paths)
- `problems[]` are reduced to codes only

Additionally, public mode collapses any unrecognized codes to `unknown_problem_code` so published reports stay comparable.

Optional linkage (recommended): include `verifier_report_tbs_digest` in the packet report payload so readers can fetch/compare the implementation-scoped verifier report (`hfv.verifier.report`).

Reference tool support:
- `python3 tools/observer_verify_packet.py <packet_dir> --public --verifier-report-envelope <path/to/verifier_report_envelope.json>`
- or set it directly: `--verifier-report-tbs-digest sha256:<hex>`

Release gate note: the problem-code registry is treated as a public surface and is linted for strict formatting and sorted order.

Optional comparability pins (recommended): include the sha256 of the registries used to interpret the report.

Both report types MAY include these pins. For `hfv.verifier.report` (implementation-scoped), authors SHOULD include them so readers can confirm the exact public-surface bytes the verifier claims to target.

The reference tool populates these optional fields automatically in the PacketVerificationReport payload when the files exist:
- `verifier_problem_codes_sha256` (sha256 of `artifacts/registries/verifier-problem-codes.csv`)
- `envelope_kinds_sha256` (sha256 of `artifacts/registries/envelope-kinds.csv`)

When publishing a report, keep these fields (or cite them alongside the card) so readers can confirm the exact public-surface bytes used (see `docs/PUBLIC_SURFACES.md`).

Helper (copy/paste pins from local bytes, no network):
- `python3 tools/public_surface_pins.py` (or `--json`)

Operator note: the card tools emit a bounded warning to stderr if a report’s declared pins do not match the local registry bytes.

A publisher or witness can then wrap the payload in an `EvidenceEnvelope` of kind
`hfv.verifier.packet_verification_report` (detached payload), and publish it like any other evidence.

For convenience, the reference tool can also emit a **minimal report packet** (envelope + detached payload + manifest):
- `python3 tools/observer_verify_packet.py <packet_dir> --emit-evidence-object <out_dir>`
  - emitted payload is **always public-safe** (sanitized path + codes-only)

Example packet (minimal): `artifacts/examples/evidence_packet_packet_verification_report_minimal/`.

## Non-goals

- This doc does not prescribe a specific signature suite or publication medium.
- This doc does not require publishing sensitive local debugging context.

See also: `188-verifier-minimum-viable-path.md` and `179-evidence-api-surface.md`.
