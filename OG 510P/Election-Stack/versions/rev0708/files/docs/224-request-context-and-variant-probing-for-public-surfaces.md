# 224 — Request context & variant probing for public surfaces (split‑view root causes)

**Track:** A (Deployable core)

Split views are not always “channel A is compromised.”
They are often **request-context variants**:

- cache or CDN behavior (`DOC:docs/205-cache-and-freshness-controls-for-public-surfaces.md`)
- `Accept-Language` / locale variants
- mobile vs desktop rendering
- geo / ASN / DNS resolver differences
- WAF blocks, bot mitigation, or “challenge pages” (`DOC:docs/202-public-surface-challenges-and-escalating-split-views.md`)

The stack already has **hashes-first** evidence objects for parity (`DOC:docs/201-public-surface-parity-snapshots.md`) and
reproducible raw-capture pins (`DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`).
This doc adds a small discipline: **record enough request context** to make “you fetched different bytes” claims debuggable
*without* bloating bundles or adding new schemas.


## 224.1 The invariant

When you publish or litigate a parity/split-view finding, you want a third party to be able to say:

- *Given the same request context, would I likely see the same bytes?*

A capture note or snapshot that omits request context can be attacked as:

> “You used a different language / UA / cache-bypass / network; your bytes aren’t what the public saw.”


## 224.2 Minimal request-context fields (bounded)

Record **only** a small, publishable subset (no cookies/tokens):

### A. Request hints (what the client asked for)
- `ua_class`: coarse class, not the full UA string (examples: `desktop_chrome`, `mobile_safari`, `cli_curl`)
- `accept_language`: primary BCP47 tag only (e.g., `en-US`, `es`, or `none`; do not include q-weights)
- `cache_bypass`: `none|no-cache|force-refresh` (what you *attempted*)
  - `none`: default request (no special cache headers)
  - `no-cache`: request `Cache-Control: no-cache` (optionally `Pragma: no-cache` for legacy intermediaries)
  - `force-refresh`: stronger bypass attempt; avoid publishing cache-busting query values; record only the fact you attempted it
- `cookies`: MUST be `none` for public captures; if a cookie was present, record `present_redacted` (never values)

### B. Network hints (where you asked from)
- `geo_hint`: coarse only (e.g., `country=US`, optional `region=US-CA` per ISO 3166-2)
- `asn_hint`: optional ASN number if known (e.g., `asn=15169`)
- `resolver_hint`: `system_resolver|public_resolver|pinned_resolver` (names OK; transcripts optional, usually private)

### C. Response variance hints (what the server *said* varies)
- `vary`: copy the **response** `Vary` header if present (bounded)
- `age`: response `Age` if present (bounded)

Do **not** paste full request/response header dumps into notes by default.
If you must retain full headers, keep them as detached raw capture bytes and pin by digest (`DOC:docs/223...`).


## 224.2a Canonical compact encoding (req[] / vary[] / age[])

To keep request-context and variance hints **copy/pasteable** across artifacts, use this compact, bounded notation
See `DOC:docs/232-compact-request-context-notes.md` for the syntax + canonicalization contract (and test vectors).

in `observations[].notes` and (optionally) in capture notes:

- `req[ua=<ua_class>;lang=<accept_language>;cache=<cache_bypass>;cookie=<cookies>;geo=<geo_hint>;asn=<asn_hint>;resolver=<resolver_hint>]`
  - omit keys you do not know; keep values coarse
  - `cookie` MUST be `none` or `present_redacted` (never values)
- `vary[<vary_names>]` (response `Vary`, bounded and canonical: lower-case, comma-separated, no spaces; tools may dedupe+sort tokens; omit if absent)
- `age[<Age header>]` (response `Age` seconds, bounded; omit if absent)

Example:

- `req[ua=desktop_chrome;lang=en-US;cache=no-cache;cookie=none;geo=country=US;asn=15169] vary[accept-language,user-agent] age[120]`

Operator helpers can emit this automatically when you pass request-context flags:
- `tools/http_capture_to_parity_observation.py` (parity snapshots)
- `tools/http_capture_to_observation.py` (liveness beacons)

## 224.3 Where to record it

### A. Capture notes (preferred)
Add a short “Request context” section to `capture-note.md`:

- `TEMPLATE:artifacts/templates/public-surface-capture-note.md`

This is the best place to pin request context because it can also pin the raw capture file digest.

### B. Parity snapshots (schema-safe)
`PublicSurfaceParitySnapshot` has no structured request-context field.
When context is load-bearing, encode it compactly in `observations[].notes`:

- `req[ua=desktop_chrome;lang=en-US;cache=no-cache;geo=US;asn=15169]`
- `vary[accept-language,user-agent]`

Keep it short; omit fields that are unknown.


## 224.4 Variant-probing recipe (tight, one axis at a time)

When you suspect a split view, probe **one axis at a time** so you can classify the root cause.

**Record each probe** as a parity/beacon observation with a compact `req[...] vary[...] age[...]` note (224.2a), so a third party can see *what changed* without seeing raw headers.

Suggested order (tight):

1. **Baseline:** pick the context that matches the audience you care about (often a “normal” browser request). Record `req[...]` (at least `ua`, `lang`, `cache`, `cookie`).
2. **Cookies / challenge gating:** repeat with cookie state flipped (`cookie=none` vs `cookie=present_redacted`).  
   If bytes change only with cookie presence, suspect bot mitigation / consent/challenge flows (`DOC:docs/202...`).
3. **Cache bypass:** repeat with header-level bypass (`cache=no-cache` or `cache=force-refresh`).  
   If bytes change only here, treat primarily as a cache/freshness issue (`DOC:docs/205...`).
4. **Language:** repeat with a second primary `lang` tag (e.g., `en-US` vs `es-US`).
5. **UA class:** repeat with a different coarse UA family (desktop vs mobile; browser vs CLI).
6. **Vantage / resolver:** repeat from a second network and/or resolver class (`resolver=system_resolver` vs `public_resolver`) when feasible.

Stop condition: when you find an axis that flips bytes, **hold others constant** and take 1–2 confirming repeats (to rule out transient cache).

Checklist (optional): `CHECK:artifacts/checklists/split-view-variant-probing-checklist.md`.


## 224.5 Size and safety rules

- Prefer **digests** + bounded context lines.
- Never include cookies, bearer tokens, or auth headers (`DOC:docs/189-sensitive-material-and-secrets.md`).
- Record only coarse geo/ASN hints (avoid per-user identifiers).
- Use the capture-note quickcheck: `CHECK:artifacts/checklists/public-surface-capture-note-quickcheck.md`.


## 224.6 Pinned references (cite, don’t bloat)

- HTTP semantics (`Vary`, `Accept-Language`, status codes): `source: rfc9110_txt`.
