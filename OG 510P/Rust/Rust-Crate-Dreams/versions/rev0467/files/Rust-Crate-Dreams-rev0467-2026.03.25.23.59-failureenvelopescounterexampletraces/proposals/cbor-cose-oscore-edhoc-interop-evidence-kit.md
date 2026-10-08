---
id: P-0257
title: CBOR/COSE/OSCORE/EDHOC Interop & Evidence Kit — portable, constrained security test suites
status: idea
domains: [security, iot, networking, interop, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc7252
  - https://www.rfc-editor.org/rfc/rfc8949.html
  - https://datatracker.ietf.org/doc/rfc9052/
  - https://datatracker.ietf.org/doc/rfc9053/
  - https://datatracker.ietf.org/doc/html/rfc8613
  - https://datatracker.ietf.org/doc/rfc9528/
---

## Why this is missing
“Constrained security” stacks are a graveyard of partial implementations:
- CBOR encoders that diverge on canonical forms,
- COSE stacks that disagree on algorithm handling,
- OSCORE stacks that differ on option processing and replay handling,
- EDHOC handshakes that break interop at the edges.

CoAP’s motivation is clear: constrained nodes and lossy networks. citeturn2search0  
CBOR is explicitly designed for small code/message size and extensibility. citeturn0search0  
COSE defines signing/MAC/encryption over CBOR. citeturn0search1turn2search1  
OSCORE is application-layer protection for CoAP using COSE. citeturn0search2  
EDHOC is a compact authenticated key exchange intended to establish OSCORE contexts. citeturn0search3

Rust has many relevant crates, but what’s missing is the *conformance/interop harness* and shared evidence artifacts.

## What the crate should provide
A test and evidence “lab kit” that can wrap multiple implementations via adapters.

### Workspace
- `cosekit-ir` — IR for COSE messages/keys/headers + canonicalization helpers
- `cosekit-fixtures` — RFC-derived test vectors + fuzz/minimized corpora
- `cosekit-interop` — adapter traits for “COSE impl”, “OSCORE impl”, “EDHOC impl”
- `cosekit-runner` — scenario DSL + runner + verdict engine
- `cosekit-bundle` — emits `*.cosebundle.zip` (built on P-0256 if it exists)

### `*.cosebundle.zip` contents (high-level)
- handshake transcripts (EDHOC), message traces (CoAP/OSCORE), COSE objects
- decoded + normalized views (to diff across implementations)
- verifier policies (acceptable algorithms, key sizes, etc.)
- redaction preset for identities/keys

### MVP (6–8 weeks)
1. Canonical CBOR + COSE encode/decode harness with a small corpus
2. Adapter for **one** Rust COSE implementation + one “reference” decoder
3. OSCORE message protection/unprotection scenario suite (basic + replay window)
4. Evidence bundle emission + diff (`good run` vs `bad run`)

### De-risk plan
- Start with decode/verify-only: make the runner compare *interpretations* rather than require full feature parity.
- Build corpus from RFC examples + generated edge cases (tagging, bstr wrapping, crit headers).
- Ensure harness supports “constrained” operation modes (no alloc, feature-gated).

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5
