# 188 — Verifier Minimum Viable Path (MVP) — from packet to claim

**Track:** Shared

This doc is a **tight verifier-facing reading + execution path**.

It does not introduce new primitives. It stitches together the existing contracts so an independent
verifier can answer a single question offline:

> **Did this published evidence packet match its manifest, and was it signed/cosigned by the expected keys
> under the stated policy?**

## Inputs (what you must have)

1. **Evidence packet / bundle** (directory or extracted archive).
2. **Public keys** for the signing/cosigning roles you intend to trust (witness keys, publisher keys, etc.).
3. The **policy** you are evaluating against (e.g., “at least 2-of-5 witnesses from charter X”).

Normative references:
- Bundle contract: `92-offline-verifier-bundle-spec.md`
- Packets + envelopes: `173-canonical-evidence-envelopes-and-packets.md`
- Canonical bytes-to-sign: `176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
- Required surface: `179-evidence-api-surface.md`
- Walkthrough: `177-observer-kit-offline-verification-walkthrough.md`

## MVP procedure (offline)

### Step 0 — Identify the bundle boundary
- Locate `manifest.json` (or the bundle manifest defined by your deployment).
- Record `bundle_id`, `election_id`, and any referenced checkpoint/receipt identifiers.

### Step 1 — Hash integrity
- Verify every `files[i].sha256` matches the bytes on disk.
- If present, verify `files[i].bytes` matches file size.

Outcome: a portable statement that “these bytes match this manifest.”

### Step 2 — Manifest signature(s)
- Canonicalize the manifest *exactly as specified* for that manifest type.
- Verify the Ed25519 signatures (or the declared algorithm suite) against trusted public keys.

Outcome: “these bytes were attested by key(s) K under algorithm suite S.”

### Step 3 — Policy evaluation (thresholds, roles, and time)
Using the deployment’s policy artifacts (witness charter / key registry / rotation schedule):
- Check **threshold** (e.g., M-of-N) and **role constraints** (e.g., “at least one civil-society witness”).
- Check key validity windows and rotation rules.

Outcome: “the attestation satisfied policy P at time T (or not).”

### Step 4 — Envelope/API surface sanity
For each evidence object kind the verifier claims to implement:
- Validate that the envelope kind is in the registry (`178-…` + `179-…`).
- Validate the envelope canonicalization and signature bytes-to-sign rules.

Outcome: “the packet’s typed evidence objects are well-formed and signature-verifiable.”

### Step 5 — Optional: receipts, inclusion, and gossip attachments
If the packet includes transparency receipts, inclusion proofs, or gossip attachments:
- Verify receipt signatures.
- Verify inclusion/consistency proofs *for the included checkpoint(s)*.
- Check that “receipt semantics tier” matches what the publisher promised.

Outcome: “the publication claims are anchored to a verifiable log checkpoint.”

## Output (what to publish as a verifier)

A verifier report should be a **small, reproducible artifact**, not an essay:
- bundle_id, election_id
- hash of the canonical manifest payload
- keys that verified + policy evaluated
- pass/fail with a minimal reason code

Use a packet-scoped report payload for the actual bundle check:
- `schemas/PacketVerificationReport.json` (kind: `hfv.verifier.packet_verification_report`)
- Publishable guidance: `docs/193-publishable-verifier-reports.md` (use `observer_verify_packet.py --public`)

Separately, publish an implementation-scoped `VerifierReport` (tool identity + conformance):
- `schemas/VerifierReport.json` (kind: `hfv.verifier.report`)

Operationally: a `VerifierReport` can reference or attach one or more packet reports when publishing
via `EvidenceEnvelope` attachments.

## Non-goals (what this MVP deliberately does not do)

- Decide whether a system is “secure” in general.
- Validate ballot correctness or tally correctness.
- Provide offensive guidance on how to defeat monitoring.

