# 177 — Observer Kit: Offline Verification Walkthrough

**Track:** Shared

See also: `179-evidence-api-surface.md` (minimal verifier surface).

## Goal
Enable an independent observer (human or LLM) to verify an election evidence packet **offline** from a directory of files.

This doc is intentionally procedural. It answers:
- what files you should expect,
- what you can prove,
- what you *cannot* prove without additional lanes (e.g., coercion resistance).

## Minimal packet layout (recommended)
A public packet directory SHOULD look like:

- `manifest.json` — `EvidenceBundleManifest`
- `objects/` — content-addressed bytes (`sha256-<hex>.*`)
- `envelopes/` — `EvidenceEnvelope` JSON objects
- `README.txt` — how this packet was produced, contact, mirroring guidance (optional)

## Step 0 — Trust anchors you must choose
Offline verification requires you to pick:
- which issuer keys you trust for which roles (registry, pinned keys, or external PKI),
- which transparency log / witness set you accept as authoritative for “publication promises.”
- which official comms surfaces you treat as “official” (if the publisher provides a channel registry: `artifacts/registries/official-channels.csv`)

This archive does **not** assume a single global trust anchor; it assumes observers can compare competing anchors.

## Step 1 — Verify content addressing
For every file in `objects/`:
- compute sha256 and confirm it matches the filename’s digest.

If an object’s hash does not match, the packet is corrupted.

## Step 2 — Verify envelopes (structural + digest binding)
For each file in `envelopes/`:
1. Validate JSON against `schemas/EvidenceEnvelope.json`.
2. Recompute:
   - `payload_digest` from the inline or detached payload using `docs/176`.
   - `tbs_digest` from the envelope header using `docs/176`.
3. Reject if any digest mismatches.

(Signature verification is a separate step; stdlib-only tools can still confirm the **bytes-to-be-signed**.)

## Step 3 — Verify the manifest
1. Validate `manifest.json` against `schemas/EvidenceBundleManifest.json`.
2. Confirm every manifest artifact points to objects that exist (or record what is missing).
3. If the manifest promises deadlines (MMD-style), record any missed deadlines as **suppression** evidence.

## Step 4 — Verify publication / anti-split-view (when receipts exist)
If the packet includes:
- log inclusion proofs,
- witness cosignatures,
- consistency proofs,
- gossip digests,

then you can prove:
- whether the publisher equivocated,
- whether different audiences were shown different histories,
- whether monitors ignored required challenges.

Packets without receipts are still useful, but they are weaker.

## Step 5 — Produce an observer report
For **publishable** results, produce a packet-scoped verifier report payload and (optionally) wrap it as evidence:
- kind: `hfv.verifier.packet_verification_report`
- schema: `schemas/PacketVerificationReport.json`
- reference tool: `python3 tools/observer_verify_packet.py <packet_dir> --json --public`

You can then wrap the JSON payload in an `EvidenceEnvelope` (detached payload) and publish it like any other evidence.
See `docs/193-publishable-verifier-reports.md`.

## Reference tooling (in this repo)
- `tools/observer_verify_packet.py` — stdlib-only packet integrity checks (hashes + digests)
- `tools/envelope_wrap.py` — create placeholder envelopes around payloads
- `tools/jcs.py` and `tools/jcs_canonicalize.py` — RFC8785-JCS canonicalization (number formatting compatible with JSON.stringify; disallows NaN/Infinity)

These tools are **reference implementations**, not production security libraries.

## Quick-check: PublicNotice packets

If the packet includes an `hfv.public.notice` envelope, a verifier can quickly extract a
copy/pasteable digest summary (useful for rumor-control parity checks):

- `python tools/public_notice_card.py --packet <packet_dir>`

This confirms the payload + TBS digests recompute cleanly (docs/176) and prints a short form
for human comms surfaces. It does not verify signatures.

## Quick-check: VerifierReport packets

If you have an implementation-scoped verifier report packet (`hfv.verifier.report`), you can print a
copy/pasteable verifier card (useful for publishing verifier identity + conformance alongside packet reports):

- `python tools/verifier_report_card.py --packet <verifier_report_packet_dir>`

This recomputes payload + TBS digests (docs/176) and prints the `tbs_digest` that packet reports can reference via
`verifier_report_tbs_digest` (see `docs/193`).
