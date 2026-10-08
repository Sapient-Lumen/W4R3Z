# 193 — Publishable verifier reports (small, comparable, privacy-safe)

**Track:** Shared

See also: `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` (how to wire publishable reports into rumor-control + status-board pages via digest links).

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


## v839 authentication-status rule

Every publishable `PacketVerificationReport` MUST be read as a pair: `status` plus `authentication_status`. The stdlib reference tool emits `authentication_status: HASH_ONLY_NOT_AUTHENTICATED`, even when `status: PASS`, because it does not verify signer identity, trust roots, revocation, key rotation, or local authority.

Use `docs/839-verifier-authentication-status-boundary-and-hash-only-no-go.md` before describing a report as “verified.” A hash-only PASS is evidence of packet integrity checks, not evidence that an election office, reviewer, witness, build system, or publisher authenticated the packet.

## Publishable problem codes

Verifier failures should be expressed as **short codes** so ecosystems can compare results.

Source of truth: `artifacts/registries/verifier-problem-codes.csv`.

Authoritative list (generated): `docs/VERIFIER_PROBLEM_CODES.md`.

## Verifier profiles (capability claims, not essays)

Problem codes describe *what failed* for a specific packet. Profiles describe *what the implementation claims to support* (kinds and surfaces), using small, stable identifiers.

- Registry: `artifacts/registries/verifier-profiles.csv`
- Human index (generated): `docs/VERIFIER_PROFILES.md`

Implementation-scoped `hfv.verifier.report` MAY include:
- `supported_profiles[]` — profile IDs the verifier claims
- `verifier_profiles_sha256` — optional comparability pin for the registry bytes

This keeps claims compact while enabling cross-verifier comparisons and “minimum bar” discussions without inflating Track A.


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

Optional publishable lint summary (recommended when the packet will be published):
- `python3 tools/observer_verify_packet.py <packet_dir> --json --public --lint-public`

When `--lint-public` is enabled, the tool runs the conservative publication-hygiene linter and adds only stable codes:
- `public_artifact_lint_failed` (FAIL)
- `public_artifact_lint_warn` (WARN)

Optional (mirror-equality check, when `--verify-public-fingerprint` is used; DOC:docs/226...):
- `public_fingerprint_mismatch` (FAIL)
- `public_fingerprint_file_invalid` (FAIL)
- `public_fingerprint_file_missing` (WARN)
- `public_fingerprint_unavailable` (WARN)

Details are intentionally not embedded in the report payload; run `tools/public_artifact_lint.py --packet <packet_dir>` to inspect findings locally.

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
- `verifier_profiles_sha256` (sha256 of `artifacts/registries/verifier-profiles.csv`)
- `envelope_kinds_sha256` (sha256 of `artifacts/registries/envelope-kinds.csv`)
- `attachment_requirements_sha256` (sha256 of `artifacts/registries/envelope-attachment-requirements.csv`)
- `receipt_profiles_sha256` (sha256 of `artifacts/registries/receipt-profiles.csv`)


Optional bundle-boundary comparability (recommended when the checked packet uses a JSON manifest):
- `manifest_sha256` pins the **exact raw bytes** of `manifest.json` (strongest identity).
- `manifest_jcs_sha256` pins the **RFC8785-JCS canonical bytes** of the manifest JSON value (formatting-independent).

Publishing both keeps mirrors comparable even if a CMS reflows whitespace, while preserving an exact-bytes pin for integrity proofs.
Additionally (recommended): publish a machine-readable policy profile alongside the report and pin it in `PacketVerificationReport.policy_profile_sha256` (preferred):
- Template: `artifacts/templates/verifier-policy-profile.json` (schema: `schemas/VerifierPolicyProfile.json`)
- Set `policy_profile_sha256 = sha256:<hex>` referencing the profile’s **RFC8785-JCS canonical bytes** (see `176`). You can compute it locally with `python3 tools/policy_profile_digest.py --in <profile.json>`. For older emitters, you may also include a note string like `policy_profile_sha256=sha256:<hex>`.
- If you emit a **minimal report packet** (`--emit-evidence-object`), also ship the profile bytes as a detached, content-addressed object `objects/sha256-<hex>.json` where `<hex>` matches `policy_profile_sha256`. The reference tool does this automatically when you pass `--policy-profile <profile.json>` (not just `--policy-profile-sha256`).
- For index-only scans, the `EvidenceEnvelope.subject` SHOULD also repeat `policy_profile_sha256` (digest only).

When publishing a report, keep these fields (or cite them alongside the card) so readers can confirm the exact public-surface bytes used (see `docs/PUBLIC_SURFACES.md`).

Helper (copy/paste pins from local bytes, no network):
- `python3 tools/public_surface_pins.py` (or `--json`)
  - Use `--all` to include a few additional stable registries (e.g., official channel directory registry, attachment requirements, tool maturity); publish only the pins you actually rely on.

Operator note: the card tools emit a bounded warning to stderr if a report’s declared pins do not match the local registry bytes.

A publisher or witness can then wrap the payload in an `EvidenceEnvelope` of kind
`hfv.verifier.packet_verification_report` (detached payload), and publish it like any other evidence.

For convenience, the reference tool can also emit a **minimal report packet** (envelope + detached payload + manifest):
- `python3 tools/observer_verify_packet.py <packet_dir> --emit-evidence-object <out_dir>`
  - emitted payload is **always public-safe** (sanitized path + codes-only)

Example packet (minimal): `artifacts/examples/evidence_packet_packet_verification_report_minimal/`.



## Distribution (where verifier output lands) + capacity (who will publish)

Publishable reports only help if audiences can **find them** during a contested window.

Recommended minimal practice (Track A pilot friendly):
- publish a verifier capacity roster **before polls close**: kind `hfv.verifier.capacity_roster` (DOC:`241`; schema `schemas/VerifierCapacityRoster.json`; template `artifacts/templates/verifier-capacity-roster-payload.json`),
- link the roster digest from the official status/rumor-control surface (`195`) and mirror indexes (`200–205`),
- ensure at least two rostered verifiers publish replayable `hfv.verifier.packet_verification_report` objects for each public packet you ship.

This is an anti-theater surface: if a roster exists but no replayable reports appear, treat it as a failure signal.

## Non-goals

- This doc does not prescribe a specific signature suite or publication medium.
- This doc does not require publishing sensitive local debugging context.

See also: `188-verifier-minimum-viable-path.md` and `179-evidence-api-surface.md`.
