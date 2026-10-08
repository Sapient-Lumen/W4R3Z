# 232 — Compact request-context notes (req[] / vary[] / age[])

**Track:** A (Deployable core)

The stack uses a compact, bounded notation inside publishable `notes` fields to record *coarse* request context and response variance hints without shipping full headers:

- `req[...]` — what context the observer requested from
- `vary[...]` — what the server said varies (`Vary`)
- `age[...]` — what the server said about cache age (`Age`)

This notation is intentionally:
- **small** (copy/pasteable)
- **publishable** (no tokens/cookies/headers)
- **stable for comparison** (canonicalization + test vectors)

Primary use sites:
- parity snapshots: `DOC:docs/201-public-surface-parity-snapshots.md`
- capture notes: `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`
- variant probing: `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`


## 232.1 Non-goals

- This is **not** a wire format.
- This is **not** a verifier requirement.
- This does **not** replace raw captures when those are load-bearing (`DOC:docs/223...`).

The goal is to make “you fetched different bytes” objections debuggable with minimal publication bloat.


## 232.2 Syntax (bounded)

A notes string MAY contain these tokens anywhere; tooling extracts them by pattern.
If multiple tokens of the same type appear, **the last occurrence wins**.

### req[]

```
req[ua=<ua_class>;lang=<bcp47_primary>;cache=<cache_bypass>;cookie=<cookie_state>;geo=<geo_hint>;asn=<asn_hint>;resolver=<resolver_hint>]
```

Rules:
- keys are case-insensitive but canonicalization emits **lower-case** keys.
- omit unknown keys (keep the token small).
- do **not** include delimiters (`[ ] ;`) or newlines in values.

Recognized keys (canonical order):
- `ua` — coarse UA class (e.g., `desktop_chrome`, `mobile_safari`, `cli_curl`)
- `lang` — primary BCP47 tag only (no q-weights), or `none`
- `cache` — `none|no-cache|force-refresh` (attempted)
- `cookie` — `none|present_redacted` (**never values**)
- `geo` — coarse hint (prefer `country=US` or `region=US-CA`)
- `asn` — digits only (e.g., `15169`)
- `resolver` — `system_resolver|public_resolver|pinned_resolver`

### vary[]

```
vary[accept-language,user-agent]
```

Rules:
- lower-case
- comma-separated
- no spaces
- tooling may **dedupe + sort** tokens (order is not evidence-bearing).

### age[]

```
age[120]
```

Rules:
- integer seconds (tooling coerces when possible)


## 232.3 Canonicalization contract

Canonicalization is implemented in:
- `TOOL:tools/compact_notes.py`

Contract (for stable diffs and copy/paste hygiene):
- `req[...]` key order is canonical (`ua, lang, cache, cookie, geo, asn, resolver`, then any unknown keys sorted).
- `lang` is coerced to the first BCP47-ish tag (drops q-weights).
- `cookie` is clamped to `none|present_redacted`.
- `geo` and `asn` are coerced toward coarse publishable forms when possible.
- `vary[...]` is lower-cased, whitespace-stripped, and (when tokens look well-formed) deduped + sorted.
- `age[...]` is coerced to integer seconds when possible.

Test vectors (freeze the behavior):
- `VECTORS:artifacts/test-vectors/compact_context_vectors.json`


## 232.4 Emission helpers

Operator-facing tools emit canonical compact notes when you pass request-context flags:
- `TOOL:tools/http_capture_to_parity_observation.py`
- `TOOL:tools/http_capture_to_observation.py`

The shared builder is:
- `TOOL:tools/http_capture_common.py` (`build_request_context_note`)


## 232.5 Safety discipline

- Never include secrets/tokens/cookies/Authorization headers (`DOC:docs/189-sensitive-material-and-secrets.md`).
- Keep values coarse and non-identifying.
- When full headers/bodies matter, attach raw capture bytes privately and pin by digest (`DOC:docs/223...`).
