# 205 — Cache and freshness controls for public surfaces (anti stale-pointer / anti replay)

**Track:** A (Deployable core)

The comms spine in Track A relies on small machine-facing surfaces that point to **content-addressed anchors**:

- `OfficialChannelDirectory` (docs/203)
- `PublicNoticeFeed` (docs/200)
- `/.well-known/election-stack.json` bootstrap (docs/204)

Those anchors are designed to be **portable** (digests) and **rollback-detectable** (hash chaining). But deployment reality introduces a second failure mode:

- caches, CDNs, proxies, and browsers can serve **stale pointers** long after operators rotated them
- attackers can exploit stale caches to create “the official bootstrap file says X” confusion

This doc provides a tight, operator-usable cache/freshness posture for **public surfaces** so staleness becomes detectable and operationally bounded.

## 205.1 Threat model (specific)

1. **Stale-pointer amplification:** a long-lived cache serves an old `/.well-known` payload; a subset of users keep seeing outdated digests.
2. **Replay-by-proxy:** an intermediary selectively replays older JSON to a region/cohort (split view).
3. **Rollback masking:** operators publish a new chained payload, but a cache serves a previous payload that still validates locally.

Hash chaining helps detect rewrites if you can fetch multiple versions; the goal here is to make it **likely** that clients see the latest version, and **easy** to prove when they do not (docs/201).

## 205.2 Operator guidance (minimal, high leverage)

### A. Make machine-facing JSON explicit and short-lived

For machine-facing discovery surfaces (`docs/200`, `docs/203`, `docs/204`), deployments SHOULD:

- serve `Content-Type: application/json`
- set **explicit** cache policy with a short TTL (minutes, not hours)
- include validators (`ETag` and/or `Last-Modified`) so clients can revalidate cheaply

Practical minimum: publish with a small `max-age` and `must-revalidate` to avoid “forever cache” behavior.

### B. Prefer “digests displayed on humans surfaces” over long TTLs

Human-facing pages (status boards, rumor-control pages) MAY be cached more aggressively, but they SHOULD display:

- the latest `PublicNoticeFeed` digest
- the latest `OfficialChannelDirectory` digest
- (optionally) the latest `/.well-known` payload digest

This turns a cached page into a **pointer** that a verifier can independently fetch/compare.

Operator note: prefer using bounded **digest cards** (docs/206) when you copy/paste digests across channels.

### C. Use the hash chain as the rollback detector (don’t fight your CDN)

For any chained surface (`previous_*_payload_sha256` fields in docs/200 and docs/204):

- keep at least the previous payload fetchable for a short window (hours/days) so monitors can prove rollback
- when a cache is suspected, publish a `surface_parity_snapshot` (docs/201) and reference it from a `PublicNotice` (docs/186)

Do **not** grow the discovery payloads to include logs or history. Keep them bounded; rely on the chain + receipts.

## 205.3 Monitor / verifier guidance

Monitors SHOULD treat machine-facing surfaces as **freshness-sensitive**:

- re-fetch the same surface from multiple networks/regions if a mismatch is reported
- compare across official channels (docs/201)
- treat a payload with an unexpectedly old `generated_at` as a **signal**, not an automatic failure (policy choice)

When a mismatch exists, the publishable output should be:

- a `surface_parity_snapshot` (docs/201)
- optionally an inspection challenge escalation if disputed (docs/202)

## 205.4 Operator artifact: cache + freshness test plan (recommended)

If you want cache/freshness posture to be **mechanically repeatable** (and court-explainable), use the bounded checklist:

- `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`

It pairs:
- the cache semantics posture in this doc,
- **LivenessBeacon header capture** (`observations[].headers.*`) as the low-bandwidth freshness signal (`docs/210`), and
- **parity snapshots** as the portable “who saw which pointer?” dispute artifact (`docs/201`).

Practical note (bounded): store one raw fetch capture locally for each surface (curl/wget), but publish only the safe signals.
If a dispute is likely, also keep a small `capture-note.md` using `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`.
`tools/http_capture_to_observation.py` converts a capture into a schema-shaped `observations[]` snippet (status + `sha256:<hex>` digest + freshness headers) without shipping the body; it defaults `observed_at` to “now (UTC)” if you don't supply one.

## 205.5 Pinned references (cite, don’t bloat)

- HTTP caching semantics: `source: rfc9111_txt`.
