---
id: P-0237
title: IPFS CID/CAR Canonicalization & Interop Evidence Kit
status: idea
domains: [content-addressing, ipfs, storage, formats, interop, testing, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://docs.ipfs.tech/concepts/content-addressing/
  - https://github.com/multiformats/cid
---

# Problem

Rust has many partial crates around multihash/multibase/multicodec and various IPFS-adjacent formats, but teams still hit “mismatched CID”, “wrong codec”, and “CAR differs” problems that are painful to reproduce across implementations. The ecosystem lacks a **canonical, testable CID toolbox** plus a **portable evidence bundle** for interop debugging. citeturn0search1turn0search5

# What it provides

1. `cidlab` workspace (crates):
   - `cidlab-cid`: CID parsing/formatting with strict/lenient modes and explicit policy (CIDv0↔CIDv1).
   - `cidlab-canon`: canonical string form rules (multibase choices, lowercase policy, stable codec display).
   - `cidlab-car`: CAR reader/writer + deterministic ordering helpers (for reproducible artifacts).
   - `cidlab-fixtures`: curated golden vectors + fuzz corpus + minimization hooks.
   - `cidlab-evidence`: capture “inputs → computed CID → decoded components → roundtrip outcomes”.

2. Evidence bundle format: `*.cidbundle.zip`
   - `manifest.json`: codecs + hash alg + version policy
   - `inputs/`: bytes + labeled sources
   - `results.json`: decoded components (multicodec/multihash/multibase) + canonical forms
   - `roundtrip.ndjson`: step-by-step transformations with “explain”
   - `diff.md`: human summary + likely causes

3. CLI: `cidlab`
   - `cidlab inspect <cid>`
   - `cidlab car verify <file.car>`
   - `cidlab bundle make ...` / `cidlab bundle diff ...`

# Minimum lovable MVP (4–8 weeks)

- CID parser/inspector + canonical form + golden vectors (CID + multihash).
- Minimal CAR read/verify (structure + CID consistency checks).
- Bundle emit + bundle diff.

# De-risk plan

- Start with CID correctness and explainability (it’s the “knife edge” most teams cut themselves on).
- Add CAR support second; keep deterministic output as a core invariant.

# Non-goals

- Not an IPFS node.
- Not a pinning service.
- Focus is **format correctness + reproducible interop evidence**.
