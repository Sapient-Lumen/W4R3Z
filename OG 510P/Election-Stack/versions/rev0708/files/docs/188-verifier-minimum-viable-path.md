# 188 — Verifier Minimum Viable Path (MVP) — from packet to claim

**Track:** Shared

This doc is a **tight verifier-facing reading + execution path**.


**If independent verifiers disagree:** do not “average” outputs. Treat it as a spec/tool incident and follow `artifacts/playbooks/spec-error-response-playbook.md`.
It does not introduce new primitives. It stitches together the existing contracts so an independent
verifier can answer a single question offline:

> **Did this published evidence packet match its manifest, and was it signed/cosigned by the expected keys
> under the stated policy?**

## Inputs (what you must have)

1. **Evidence packet / bundle** (directory or extracted archive).
2. **Public keys** for the signing/cosigning roles you intend to trust (witness keys, publisher keys, etc.).
3. The **policy** you are evaluating against (e.g., “at least 2-of-5 witnesses from charter X”).

4. (Recommended) A **policy profile file** you can publish alongside verifier output:
   - Template: `artifacts/templates/verifier-policy-profile.json`
   - Schema: `schemas/VerifierPolicyProfile.json` (machine-checked in the release gate).
   - In publishable packet reports (`schemas/PacketVerificationReport.json`), set `policy_profile_sha256 = sha256:…` (preferred) computed over the profile’s **RFC8785-JCS canonical bytes** (see `176`). Compute locally with `python3 tools/policy_profile_digest.py --in <profile.json>`. For older emitters, you may also include a note string like `policy_profile_sha256=sha256:…` so third parties can compare decisions without trusting prose.
   - If you publish verifier output as a packet (recommended), include the canonical profile bytes as a detached object `objects/sha256-<hex>.json` where `<hex>` matches `policy_profile_sha256`.

Normative references:
- Bundle contract: `92-offline-verifier-bundle-spec.md`
- Packets + envelopes: `173-canonical-evidence-envelopes-and-packets.md`
- Canonical bytes-to-sign: `176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
- Required surface: `179-evidence-api-surface.md`
- Walkthrough: `177-observer-kit-offline-verification-walkthrough.md`

TCB note (courtroom-friendly): see `observer-kit/TCB.md` for the minimum components an offline verifier must trust.

## MVP procedure (offline)

### Step 0 — Identify the bundle boundary
- Locate `manifest.json` (or the bundle manifest defined by your deployment).
- Record `bundle_id`, `election_id`, and any referenced checkpoint/receipt identifiers.
- (Recommended) Record both `manifest_sha256` (raw bytes) and `manifest_jcs_sha256` (RFC8785-JCS canonical bytes) when available; this keeps boundary identifiers comparable even if mirrors reformat JSON.


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

### Step 6 — Recommended: verify the verifiers (witness liveness + dissent)

If your verification is meant to be relied on by many voters under pressure, you should also check whether the **verification ecosystem**
itself is behaving like an independent countervailing power (not a quiet captured chorus).

Minimum evidence surface (behavioral, not “trust me”):
- Collect the latest verifier capacity roster packet(s): kind `hfv.verifier.capacity_roster` (see `241`).
- Verify roster integrity as usual and record the report feeds/endpoints you will pull verifier outputs from.
- Collect the latest witness **liveness+dissent** report packet(s): kind `hfv.witness.liveness_dissent_report` (see `135`).
- Verify the packet(s) as usual (hashes + signatures), and record the report period + scope.
- Compare across witnesses: look for **disagreement, refusals, corrections**, and explicit “split-view” notes.

Red flags:
- No liveness/dissent reports exist during a contested window.
- “Independent” witnesses publish identical boilerplate, share a funder/provider, or never issue corrections.
- Mirrors disagree on bytes/digests but nobody publishes a split-view note.

Templates and governance:
- Witness profile template: `artifacts/templates/witness-profile.md`
- Governance + capture resistance: `135-witness-governance-incentives-and-capture-resistance.md`


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
