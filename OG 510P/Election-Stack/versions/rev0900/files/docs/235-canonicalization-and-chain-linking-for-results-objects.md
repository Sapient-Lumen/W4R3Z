# 235 — Canonicalization & chain-linking for results objects (CRO / ENRUpdate / RRP)

**Track:** A (Deployable core)

Track A treats public results publishing as a cryptographic accountability surface.
This doc is a **tight, implementation-facing contract** for how results objects are canonicalized, hashed, and linked
so that:

- “content-addressed” references are unambiguous across implementations,
- self-referential hash fields are avoided (no impossible-to-construct objects),
- corrections/amendments are **link-forward** and verifiable (see `234`).

This doc is intentionally small; it **does not** define the election’s legal certification process.

See also: `176` (canonicalization rules for envelopes), `63` (ENR security), `68` (results pipeline), `69` (drift), `220–222` (PublicNotice graph resolution).


## 235.1 Normative primitives

### Canonical JSON
All JSON object hashing in this section uses **RFC 8785 (JCS)** canonical JSON to produce stable UTF‑8 bytes. (`source: rfc8785_txt`)

If you cannot use JCS for a particular payload, you MUST declare an explicit alternative canonicalization in a new schema/kind and treat it as a **major** interop change.

### Digests
- Digest algorithm: `sha256`
- Digest encoding: lowercase hex
- Digest string form: `sha256:<hex>`


## 235.2 CRO hashing (avoid self-reference)

`schemas/CanonicalResultsObject.json` includes a required `cro_hash` field.
To avoid self-referential hashing, define:

- **TBS(CRO)** = the CRO JSON value with the `cro_hash` field **omitted**.

Then:

- `cro_hash = sha256( JCS( TBS(CRO) ) )`

Notes:
- Any optional linkage fields (e.g., `prev_cro_hash`) are part of **TBS(CRO)** and therefore affect `cro_hash`.
- If a system emits CRO as XML (ERR CDF XML), it MUST define an XML canonicalization + digest rule in its mapping manifest; Track A’s default is the JSON CRO form.


## 235.3 Chain-linking CRO corrections

CRO publishers SHOULD emit a simple link-forward chain:

- `prev_cro_hash` (optional) — the `cro_hash` of the immediately prior CRO that this CRO supersedes.

**Rule:** if totals change and `prev_cro_hash` is absent, a verifier SHOULD treat the update as *suspicious* unless an equivalent link-forward is provided via:

- an `ENRUpdate` link (`prev_cro_hash` → `cro_hash`), and/or
- a `PublicNotice` correction that references both digests.

This supports the `234` correction discipline without requiring every jurisdiction to adopt the same legal terminology.


## 235.4 ENRUpdate object digest and optional CRO linkage

When an `ENRUpdate` is referenced by digest (e.g., via an envelope `payload_digest` or a release package list), that digest is:

- `enr_update_digest = sha256( JCS( ENRUpdate ) )`

`schemas/ENRUpdate.json` MAY include optional CRO linkage fields:

- `prev_cro_hash`
- `cro_hash`

These fields, when present, MUST be digest strings (`sha256:<hex>`) and SHOULD match the corresponding CRO chain.


## 235.5 ResultsReleasePackage digest conventions (informative)

`ResultsReleasePackage` (RRP) is typically shipped as a **package/manifest** alongside objects.
Different mirrors may reformat JSON, so publishers SHOULD provide at least one formatting-independent identifier:

- `rrp_manifest_jcs_sha256 = sha256( JCS( RRP_manifest_json ) )`

Optionally also provide:

- `rrp_manifest_sha256 = sha256( raw_bytes_as_published )`

**Rule of thumb:** use `*_jcs_sha256` for *cross-mirror equality checks* and `*_sha256` for *exact-byte forensic replay*.


## 235.6 Minimal verifier checks (portable)

A verifier/monitor can treat these as cheap tripwires:

- `cro_hash` recomputes from `TBS(CRO)` under JCS.
- If `prev_cro_hash` is present, it must match a previously observed CRO (or be `GENESIS` in clearly labeled bootstraps).
- If an `ENRUpdate` carries CRO linkage, it must match the corresponding CROs referenced in the release interval.
- PublicNotice `correction` objects should reference both the superseded and superseding digests (digest-first, screenshot-last).
- These semantics are covered by tiny test vectors (`artifacts/test-vectors/results_hash_vectors.json`) and enforced by `scripts/check_results_hash_vectors.py` to prevent silent regressions.
