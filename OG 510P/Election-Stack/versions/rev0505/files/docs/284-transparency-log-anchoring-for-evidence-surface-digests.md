# Transparency-log anchoring for evidence-surface digests

**Track:** Shared / Evidence surfaces


**Purpose.** Provide an optional, *digest-first* way to make evidence-surface digests (AuLD, ICLD, HoldCapsule summaries, Disclosure Packets) **publicly or jointly auditable** without publishing raw logs.

This document is a small *bridge* between the Election Stack's evidence-surface pattern and well-known transparency-log designs (append-only Merkle logs with inclusion proofs). It does **not** require any specific log product.

## When to use

Use transparency-log anchoring when any of the following are true:

- You need **cross-organization** verification that a digest existed at (or before) a time.
- You anticipate **dispute resolution** where "who knew what when" matters.
- You want **public accountability** without leaking raw data.
- You need a way to **detect retroactive edits** to incident/decision summaries.

Do **not** use this to "publish everything." The stack remains digest-first: raw logs remain controlled (see docs/282).

## Minimal model

A transparency log provides:

- **Append-only** commitments (typically via a Merkle tree) and a signed log root.
- **Inclusion proofs** that a submitted entry is in the log at a particular tree size/root.

The Election Stack uses it only for **hashes and bounded metadata**.

### What gets anchored
Anchor only:

- the **sha256** (or agreed hash) of the HFV / digest document, and
- a small non-sensitive envelope: `kind`, `schema_version`, `generated_at_utc`, and a non-identifying scope label.

Do not anchor raw log excerpts, PII-bearing fields, or sensitive identifiers.

## Template field

Evidence-surface HFVs MAY include:

```json
"transparency_log": {
  "mode": "<none|internal|public>",
  "provider": "<optional: log name>",
  "entry_id": "<optional: UUID / index / handle>",
  "submitted_at_utc": "<optional: RFC3339 UTC>",
  "log_root": "<optional: root hash / signed checkpoint ref>",
  "inclusion_proof_ref": "<optional: where to find the proof in the disclosure packet or evidence bundle>",
  "notes": "<optional: bounded>"
}
```

Guidance:

- `mode=internal` means a jointly operated or restricted log (e.g., multi-party oversight).
- `mode=public` means a publicly readable log.
- `inclusion_proof_ref` should point to a controlled-disclosure layer (docs/282) if proofs are sensitive.

## Operational pattern (digest → anchor → disclose)

1. **Produce** the HFV/digest (AuLD/ICLD/HoldCapsule summary) and compute its hash.
2. **Submit** the hash + minimal envelope to the log; capture the returned handle.
3. **Record** the handle and checkpoint/root reference in the HFV `transparency_log` block.
4. If challenged, **disclose** inclusion proofs via a Disclosure Packet (docs/282) rather than pasting proofs into public channels.

## Failure modes and cautions

- **Correlation risk:** even a hash can become identifying if the envelope leaks too much. Keep envelope minimal.
- **Split-brain logs:** require a signed checkpoint/root and store it alongside your own evidence bundle.
- **Key compromise:** if a log's signing key is compromised, treat it like a compromised attestor and escalate (docs/280 + docs/282).
- **Re-org / rollback:** avoid "mutable" logs. If a log supports rewrites, it is not a transparency log for our purposes.

## Sources

- xref: rfc6962_html (Merkle transparency-log pattern and inclusion proofs)
- xref: sigstore_rekor_overview (modern, widely used transparency-log system)
- xref: trillian_transparent_logging (implementation notes for transparent logs)
- xref: ietf_scitt_about (interoperable transparency building blocks)

