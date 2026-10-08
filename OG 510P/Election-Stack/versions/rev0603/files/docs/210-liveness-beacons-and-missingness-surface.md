# 210 — Liveness beacons (independent “missingness” surface for public pointers)

**Track:** A (Deployable core)

Docs `181` and `187` make evidence publication failures **portable** (suppression reports) and **measurable** (coverage reports). A remaining failure mode is *suppression of the bad news about suppression*: if an attacker can selectively block gossip and coverage artifacts for a targeted audience, “missingness” can become invisible.

This doc adds a small, bounded defense-in-depth primitive: **liveness beacons** published by independent watchers/monitors.

## 210.1 New evidence object: LivenessBeacon

- **Envelope kind:** `hfv.coverage.liveness_beacon`
- **Payload schema:** `schemas/LivenessBeacon.json`
- **Example packet:** `artifacts/examples/evidence_packet_liveness_beacon_minimal`
- **Operator card tool:** `tools/liveness_beacon_card.py` (bounded, publishable summary)

A **LivenessBeacon** is a signed, content-addressed record of what a watcher could (or could not) fetch from key public pointer surfaces at a particular time.

Key properties:
- It can carry **negative evidence** (timeouts, DNS failures, HTTP errors).
- It binds observations to **payload digests** when parsing succeeds.
- It is itself **receipted + gossiped** (per attachment registry) to resist selective withholding.

## 210.2 What a beacon should observe (minimal)

A watcher SHOULD include observations for these surfaces (if they exist for the election scope):

1) `well_known_discovery` (docs `204`)
2) `official_channel_directory` (docs `203`)
3) `public_notice_feed` (docs `200`)
4) `public_notice_signing_keyset` (docs `208`)
5) `witness_set` (docs `132`)

**Cohort-shaping note (tight):** to make “diverse watchers that are secretly co-located” easier to detect (docs `127`–`130`), watchers SHOULD:
- include coarse `vantage` metadata (at least ASN + country), and
- reference the watcher program’s cohort constraints via `probe_cohort_plan_payload_sha256` when available.


When `witness_set_payload_sha256` is present in the well-known discovery payload (docs `204`), watchers SHOULD fetch the corresponding WitnessSet object and record its digest as a `witness_set` observation. This makes witness-set drift/capture harder to hide via selective disclosure.

A watcher MAY include additional surfaces as `other` (e.g., results portals, ENR mirrors), but this object is intentionally **small**.

### Freshness header capture (recommended)

When watchers fetch pointer surfaces, they SHOULD record freshness-relevant headers when available:

- `observations[].headers.etag`
- `observations[].headers.cache_control`
- `observations[].headers.age_seconds`
- `observations[].headers.last_modified`

This provides a low-bandwidth signal for **stale-pointer** disputes and replay-by-proxy analysis (`docs/205`) without expanding the pointer surfaces themselves.

Operator note: if a fetch was captured with curl/wget, `tools/http_capture_to_observation.py` can distill it into an evidence-safe `observations[]` snippet (including `sha256:<hex>` and freshness headers).
It also accepts optional request-context flags (`--ua-class`, `--accept-language`, etc) and `--emit-variance-hints` to emit a compact `notes` line (`req[...]` / `vary[...]` / `age[...]`) per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md` (224.2a).
If you retain the raw capture bytes, ship a small capture note per `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`.

### Publishable anomaly notes (optional)

Beacon observations also include an optional short `notes` field. When you need a compact,
comparable label (for dashboards, incident updates, or later aggregation), start the note
with a stable code from `docs/SURFACE_ANOMALY_CODES.md`
(registry: `artifacts/registries/surface-anomaly-codes.csv`).

Format: `code[: context]` (context is optional and can be omitted from public copies).



## 210.3 Cadence and interpretation (normative)

1) **Heartbeat cadence**
   - During quiet periods, watchers SHOULD publish beacons on a coarse cadence (e.g., hourly).
   - On election day and during incidents, watchers SHOULD tighten cadence (e.g., every 5–15 minutes).

2) **Negative evidence is expected**
   - “timeout” / “dns_error” / “tls_error” are not automatically an accusation; they are *inputs* for parity/suppression analysis.

3) **Missing beacons are a signal**
   - If multiple independent watcher identities stop producing beacons for a scope, treat it as potential **verification ecosystem impairment** (catastrophe class 2).

4) **Rollback/rewrites detection**
   - Watchers SHOULD use `previous_beacon_payload_sha256` to form a hash chain. Serving an older beacon as “current” is treated as a public-surface rollback.

## 210.4 How beacons integrate with the existing publication stack

- **PublicationSuppressionReport (docs `181`)**: beacons can corroborate that a surface was unreachable during a deadline window.
- **PublicationCoverageReport (docs `187`)**: a coverage report MAY cite beacon digests as supporting measurement evidence.
- **Audience parity monitoring (docs `104`, checklists)**: beacons provide a low-cost, portable record that can be compared across watcher cohorts.

This object does *not* solve non-existence proofs; it makes “missingness about missingness” harder to hide by adding an additional, independently-produced evidence stream.

## 210.5 Operator workflow: tight diffs across beacons (optional)

When you need a quick, publishable answer to “what changed?” between two beacons (e.g., across time windows, or across watcher identities), use:

- `python3 tools/compare_liveness_beacons.py --a <packet|json> --b <packet|json>`

The comparison is intentionally bounded: it diffs `result` / `http_status` / `payload_sha256` plus the freshness-header subset (`etag`, `cache_control`, `age_seconds`, `last_modified`) and the **anomaly note-code prefix** (if present). It does **not** emit bodies.

Exit codes: 0 (no diffs), 3 (diffs), 2 (parse/load error).
