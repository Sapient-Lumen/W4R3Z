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
An observer report is just an `EvidenceEnvelope` of kind:
- `hfv.observer.report`

It should summarize:
- what verified cleanly,
- what was missing,
- what deadlines were missed,
- and what follow-ups are required (audit escalation, recount triggers, dispute notice).

## Reference tooling (in this repo)
- `tools/observer_verify_packet.py` — stdlib-only packet integrity checks (hashes + digests)
- `tools/envelope_wrap.py` — create placeholder envelopes around payloads
- `tools/jcs_canonicalize.py` — reference JCS canonicalization (subset; see notes)

These tools are **reference implementations**, not production security libraries.
