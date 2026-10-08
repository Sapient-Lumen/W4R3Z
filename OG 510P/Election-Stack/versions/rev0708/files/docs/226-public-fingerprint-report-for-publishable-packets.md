# 226 — Public fingerprint report for publishable packets (mirror equality checks)

**Track:** A (Deployable core)

When a dispute bundle or other publishable packet is mirrored, forwarded, or re-hosted, reviewers often need a fast way to answer:

> *“Are we looking at the same publishable packet surfaces?”*

This doc defines a **digest-only “public fingerprint”** report intended to be included alongside publishable packets.

It is **not** a replacement for packet verification (`DOC:docs/173...`, `DOC:docs/193...`), and it is **not** a content-addressed object in the canonical `objects/` store.
It is a *convenience comparability artifact* for humans and low-friction mirroring.


## 226.1 What the public fingerprint covers (bounded)

The fingerprint is computed over a **bounded** subset of packet files that are intended to be publicly shareable:

- packet root small text/json surfaces (e.g., `claim.md`, `README.*`, `capture-note.md`, `redaction-log.md`)
- `manifest.json` (if present)
- `envelopes/*.envelope.json`
- `objects/*.json` (**JSON only**; excludes non-JSON/binary objects)
- `notes/**/*.md|txt`

JSON files are canonicalized using **RFC 8785 (JCS)** before hashing (`source: rfc8785_txt`) so mirrors that reformat JSON do not create spurious fingerprint drift.


## 226.2 How to generate (operator recipe)

1) Run publishable packet preflight (`DOC:docs/173...`):
   - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public`

2) Generate the public fingerprint report:
   - Preferred (stable file output):
     - `python3 tools/public_fingerprint_report.py <packet_dir> --write-default --stable`
   - Or one-command (preflight + fingerprint + stable file output):
     - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --public-fingerprint --public-fingerprint-out public-fingerprint.json --public-fingerprint-stable`

3) Publish/ship `public-fingerprint.json` *alongside* the packet.

4) When receiving a mirrored packet, verify the shipped fingerprint matches the packet bytes:
   - `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --verify-public-fingerprint`

Or compare two packet directories directly (tight diff on mismatch):
- `python3 tools/compare_public_fingerprints.py <packet_a_dir> <packet_b_dir>`

Notes:
- The report’s `public_fingerprint_sha256` is the stable comparison value.
- `--stable` omits `generated_at` so the *file bytes* are stable across regenerations.
- If you store `public-fingerprint.json` in the packet root, the fingerprint tool excludes it from the hash to prevent self-inclusion drift.
- If fingerprint inputs exceed the max-bytes bound (or a JSON surface can’t be JCS-canonicalized), `tools/observer_verify_packet.py` will surface stable WARN codes (`public_fingerprint_input_truncated`, `public_fingerprint_json_canonicalize_failed`) to keep mirror-equality checks honest.


## 226.3 What this prevents (tight)

- **Mirror drift ambiguity:** quick equality check before deeper review.
- **“Same claim, different bundle” confusion:** claim/capture-note/redaction-log changes are visible without shipping large artifacts.
- **Formatting-only diffs:** JCS-canonicalized JSON hashing avoids “pretty-print drift”.


## 226.4 Relationship to other artifacts

- Dispute bundles: `DOC:docs/222...`
- Publication hygiene / redaction: `DOC:docs/189...` and `DOC:docs/225...`
- If you need a digest over *everything* in a directory tree (including binaries), use `tools/bundle_hash_report.py`.
- If you need a tight *difference* report between two packets' public surfaces, use `tools/compare_public_fingerprints.py`.
