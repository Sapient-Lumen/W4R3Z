# Public surface cache + freshness test plan (bounded, parity-oriented)

This is a **small operator artifact** that turns `docs/205` (cache/freshness posture) into a repeatable test plan.
It is designed to avoid archive bloat: capture *only* the signals needed to prove or disprove “stale pointer” disputes.

**Related:** `docs/200`, `docs/203`, `docs/204`, `docs/205`, `docs/206`, `docs/201`, `docs/202`, `docs/210`.

## 0) Scope (surfaces that must be freshness-sensitive)

Fill this table for each election scope.

| Surface | URL hint (public) | Target TTL | Revalidation | Notes |
|---|---|---:|---|---|
| `well_known_discovery` | `/.well-known/election-stack.json` | ___ min | `ETag` / `Last-Modified` | |
| `official_channel_directory` | (from well-known) | ___ min | `ETag` / `Last-Modified` | |
| `public_notice_feed` | (from directory) | ___ min | `ETag` / `Last-Modified` | |
| `public_notice_signing_keyset` | (from directory/feed) | ___ min | `ETag` / `Last-Modified` | |

**Rule of thumb:** machine-facing pointer surfaces SHOULD use minutes-scale TTLs, not hours (see `docs/205`).

## 1) Header capture (single vantage, baseline)

For each surface above:

- [ ] Capture a raw response once (keep locally; do not publish the body):
  - [ ] `curl -sS -i <URL> > capture.txt` (or equivalent)
  - [ ] Distill to a bounded observation snippet with `tools/http_capture_to_observation.py` (status + safe headers + `sha256:<hex>` digest; provide `--observed-at` or accept the UTC default).

- [ ] Confirm `Content-Type: application/json` (or an unambiguous JSON type).
- [ ] Record these headers (verbatim) in your monitoring notes:
  - [ ] `Cache-Control` (or equivalent policy)
  - [ ] `ETag` (if present)
  - [ ] `Last-Modified` (if present)
  - [ ] `Age` (if present)
- [ ] Confirm policy is **explicit** (avoid accidental “forever caching”). (`source: rfc9111_txt`)
- [ ] Confirm revalidation works:
  - [ ] a conditional request (`If-None-Match` / `If-Modified-Since`) produces `304` when unchanged, and `200` when changed.

## 2) Multi-vantage freshness sanity (parity signal)

Run these checks from multiple networks/regions (monitors/witnesses):

- [ ] Fetch each surface from ≥3 vantages within a short window.
- [ ] Compare:
  - [ ] `ETag` / payload digest (expected: consistent)
  - [ ] `Age` (expected: bounded and not wildly divergent)
  - [ ] `Last-Modified` vs declared `generated_at` (expected: not obviously stale)

If any mismatch is observed:
- [ ] produce a **`hfv.public.surface_parity_snapshot`** capturing the conflicting payload digests (`docs/201`), and
- [ ] (if disputed) issue a **PublicInspectionChallenge** for independent corroboration (`docs/202`).

## 3) Rotation drill (pre-election + incident rehearsal)

This drill makes “cache purge + pointer update” disputes measurable without leaking sensitive internals.

- [ ] Update one pointer surface (e.g., `OfficialChannelDirectory`) in a controlled window.
- [ ] Ensure `previous_*_payload_sha256` chain is correct so rollback is detectable (`docs/200`, `docs/204`).
- [ ] Observe propagation:
  - [ ] vantages should converge to the new payload within **TTL + small slack** (document your slack target).
  - [ ] any cohort that does not converge triggers a snapshot + PublicNotice.

## 4) Publishable evidence outputs (keep it small)

- [ ] Watchers publish **LivenessBeacons** (`hfv.coverage.liveness_beacon`) on cadence appropriate to the risk window.
  - [ ] Populate `observations[].headers.etag/cache_control/age_seconds/last_modified` when available (schema supports this).
  - [ ] Include coarse `vantage` metadata (ASN + country) and the probe cohort plan digest when available (`docs/210`).
- [ ] When a stale-pointer dispute is live:
  - [ ] publish a **PublicNotice** that cites the snapshot digest(s) (`docs/186`, `docs/201`), and
  - [ ] link audiences to a **digest card** view of the current pointer digests (`docs/206`).

## 5) Notes (do not bloat)

Keep “notes” field entries short: record *only* what you would want in court to explain which cohort saw which pointer and when.
