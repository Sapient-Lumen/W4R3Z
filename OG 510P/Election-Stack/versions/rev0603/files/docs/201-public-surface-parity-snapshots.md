# 201 — Public surface parity snapshots (provable split‑view evidence)

**Track:** A (Deployable core)

A PublicNotice feed (`docs/200`) is a bounded discovery surface.
But *detecting* a split‑view (channel A shows feed digest X, channel B shows Y) still needs a
portable, publishable artifact.

This doc introduces a tight evidence object for that purpose: a **PublicSurfaceParitySnapshot**.

See also: using `PublicInspectionChallenge` to request independent snapshots and escalating mismatches (`docs/202-public-surface-challenges-and-escalating-split-views.md`).

## 201.1 Core idea

Envelope kind: `hfv.public.surface_parity_snapshot` (experimental, additive)

- payload schema: `schemas/PublicSurfaceParitySnapshot.json`
- drafting template: `artifacts/templates/public-surface-parity-snapshot-payload.json`
- example packet: `artifacts/examples/evidence_packet_public_surface_parity_snapshot_minimal`

A parity snapshot is a bounded record of **what each official channel served** for a named public surface
at a point in time (best effort). It is designed to be:

- small (mostly digests + status codes)
- comparable across monitors (same schema, same digest conventions)
- publishable (receipt + gossip attachments, per registry)

Primary use case: proving **split‑view comms** for the “latest PublicNotice feed” surface.

## 201.2 What a snapshot should cover

A snapshot SHOULD name a `subject` such as:

- `surface_kind: "public_notice_feed_latest"` with a stable target path (e.g., `/notices/feed/latest.json`)
- `surface_kind: "status_board"` with a stable target path (e.g., `/status/`)

Pointer/cache disputes (`docs/205`) MAY also snapshot the machine-facing discovery surfaces:

- `surface_kind: "well_known_discovery"` with `stable_target: "/.well-known/election-stack.json"`
- `surface_kind: "official_channel_directory"` with a stable target path (from well-known)
- `surface_kind: "public_notice_feed"` with a stable target path (from directory)
- `surface_kind: "public_notice_signing_keyset"` with a stable target path (from directory/feed)

Each `observation` SHOULD include, per channel:

- `channel_id` (from `artifacts/registries/official-channels.csv`)
- `url` (fetch location)
- `http_status`
- `body_sha256` (digest of raw response bytes)
- when parseable, the served envelope’s `envelope_kind`, `envelope_payload_sha256`, and `envelope_tbs_sha256`

This keeps the snapshot usable even when the response is an error page or a WAF block.

### 201.2a Producing observations from `curl -i` captures (operator workflow)

To avoid hand-editing digests during drills/incidents, you can convert a bounded HTTP capture
into an `observations[]` entry with the stdlib helper tool:

- `tools/http_capture_to_parity_observation.py`

Example (uses RFC2606-reserved placeholder domains; see `231`):

```bash
curl -sS -i https://elections.example/notices/feed/latest.json > capture.txt
python tools/http_capture_to_parity_observation.py --capture capture.txt \
  --channel-id web_primary \
  --url https://elections.example/notices/feed/latest.json \
  --fetched-at 2026-02-25T12:34:56Z
```

The output is a single JSON object (safe, hashes-first) that you paste into the snapshot payload.

Optional: pass `--ua-class` / `--accept-language` / `--cache-bypass` / `--cookies` (and `--emit-variance-hints`) to include a compact `notes` string (`req[...]` / `vary[...]` / `age[...]`) per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md` (224.2a).

If you retain the raw HTTP capture for later dispute/litigation, record its provenance using:
- `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md` (template: `TEMPLATE:artifacts/templates/public-surface-capture-note.md`)

When a mismatch might depend on request context (language/UA/cache/geo), record a bounded request-context line
in the capture note (preferred) or in `observations[].notes` per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`.

### 201.2b Publishable anomaly notes (optional)

`observations[].notes` is a short string field. When you need a comparable, publishable label
for a mismatch or capture oddity, start the note with a stable code from
`docs/SURFACE_ANOMALY_CODES.md` (registry: `artifacts/registries/surface-anomaly-codes.csv`).

Format: `code[: context]` (context is optional and MAY be omitted from public copies).

Example: `surface_etag_divergence: web_primary vs sms_alias`

Example: `surface_effective_state_divergence: channel_A vs channel_B`

### 201.2c Comparing snapshots (tight operator diff)

When you publish or triage multiple snapshots over time, you often need a compact answer to
“what changed between A and B?” without re-reading full payloads.

Use the bounded helper:

- `tools/compare_public_surface_parity_snapshots.py --a <packet|json> --b <packet|json>`

Exit code 0 means no diffs; exit code 3 means diffs (useful in scripts).



## 201.3 Bounded size (don’t bloat)

A parity snapshot payload is intentionally small.

If you need the full raw response for later dispute:
- store it as a detached object in the packet and reference it via an `EvidencePointer` (optional),
- but prefer **hashes first**; attach full bodies only when they are crucial.

Do not embed narratives in the snapshot. Use a `PublicNotice` for narrative.

## 201.4 Chaining snapshots (anti rollback)

Snapshots MAY chain via `previous_snapshot_sha256` (digest of the previous snapshot **payload** bytes).

This turns “they only published the *good* snapshots” into a detectable behavior.

This is the same adversary class as rollback/split‑view attacks in transparency systems.
See CT-style designs: RFC 9162 (`source: rfc9162_txt`).

## 201.5 Publication expectations

Parity snapshots are only useful if they cannot be quietly buried.
Deployments SHOULD treat `hfv.public.surface_parity_snapshot` like other public integrity artifacts:

- require a `TransparencyReceipt` attachment
- require a `GossipSummary` attachment

See: `docs/180` and `artifacts/registries/envelope-attachment-requirements.csv`.

## 201.6 How it gets used in incidents

When a parity failure is detected:

1. Publish the snapshot packet (or publish the snapshot digest references).
2. Issue a `PublicNotice` (`docs/186`) that cites the snapshot digests and states:
   - which channels diverged,
   - which digests were observed,
   - what audiences should treat as authoritative (usually: the feed chain with valid receipts).

This converts “some people saw a different story” into a provable event.

## 201.7 Checklist integration

- Add the “latest PublicNotice feed” location to your parity targets.
- On mismatch, publish a parity snapshot immediately and announce via a PublicNotice.

See: `artifacts/checklists/audience-parity-monitoring-checklist.md` and `docs/200`.
