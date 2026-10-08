# 204 — Well-known Election Stack discovery (bootstrappable, bounded, hard to bury)

**Track:** A (Deployable core)

A recurring failure mode in election comms incidents is **bootstrapping**:

- a voter/observer has only a jurisdiction name and a likely domain
- a platform account is compromised or renamed
- mirrors exist, but “which one is real?” becomes a rumor fight

We already have strong, portable anchors:
- `OfficialChannelDirectory` (docs/203) — *where to look*
- `PublicNoticeFeed` (docs/200) — *what the office most recently said*

This doc adds a small, deterministic **bootstrap surface** that a verifier can fetch with *only the primary domain*:

- `/.well-known/election-stack.json` (machine-facing)

Treat this as a **content-addressed, receipted, gossiped public surface**, like other Track A comms artifacts.

## 204.1 Core idea

Envelope kind: `hfv.public.well_known_discovery`

- payload schema: `schemas/WellKnownElectionStackDiscovery.json`
- drafting template: `artifacts/templates/well-known-election-stack-discovery-payload.json`
- example packet: `artifacts/examples/evidence_packet_well_known_discovery`

The payload is intentionally bounded and points to **digests first** (portable), with stable URLs only as fetch convenience.

## 204.2 Publication contract

Operators SHOULD publish the latest `hfv.public.well_known_discovery` at:

- `<primary_domain>/.well-known/election-stack.json` (served over HTTPS)

Deployments SHOULD additionally publish the same payload via the normal packet/envelope mechanism and show its **short digest** on human-facing surfaces.

Operator digest card (bounded; see `docs/206`):
- `python tools/well_known_discovery_card.py --packet <packet_dir>`
- or: `python tools/evidence_object_card.py --packet <packet_dir>`

Because this is a pointer surface, deployments SHOULD use an explicit short-TTL cache posture (see `docs/205-cache-and-freshness-controls-for-public-surfaces.md`).

Because this is a discovery surface, it SHOULD carry the standard anti-suppression attachments (docs/180):
- `transparency_receipt`
- `gossip_summary`

If different channels serve different well-known payloads, treat that as a split-view incident and prove it with a parity snapshot (`docs/201`).

## 204.3 What belongs in the payload (keep it tight)

Minimum pointers (recommended):
- `official_channel_directory_payload_sha256` (docs/203)
- `public_notice_feed_payload_sha256` (docs/200)

Optional pointers (high leverage, still bounded):
- stable URLs for the above surfaces (and optionally `witness_set_url`)
- `status_board_url` (docs/195)
- `mirror_index_url` (docs/200)
- `keys_url` (docs/71)
- `closeout_index_payload_sha256` (docs/198)
- `public_notice_signing_keyset_payload_sha256` (docs/208)
- `witness_set_payload_sha256` (docs/132)

**Do not embed narratives** here. This object is a map, not a story.

## 204.4 Rollback / rewrite detection

The well-known payload SHOULD chain:
- `previous_discovery_payload_sha256` = digest of the previous payload bytes

This makes “they replaced the bootstrap file” detectable in the same way as feed rewrite/rollback (docs/200).

## 204.5 Relationship to the official channel directory

The directory remains the authoritative *declared* set of official channels (docs/203).

The well-known file is the **domain-first bootstrap**:
- you can discover the latest directory digest without guessing a social handle
- you can discover the latest feed digest without trusting an editable status page

When the well-known object pins payload digests, those digests SHOULD correspond to the latest published directory/feed payload bytes (the example packet set is release-gated for this coherence).

Recommended: include the well-known URL in the directory payload (`discovery.well_known_url`) so other channels can cite it consistently.

## 204.6 Monitor / verifier behavior

A monitor consuming `/.well-known/election-stack.json` SHOULD:
1. validate payload against `schemas/WellKnownElectionStackDiscovery.json`
2. verify digest integrity when the object is published as an envelope/packet
3. compare the well-known payload across official channels (parity)
4. if parity fails, publish:
   - a `hfv.public.surface_parity_snapshot` (docs/201)
   - a `PublicNotice` describing the mismatch and citing the snapshot digest (docs/186)

This turns “I saw a different ‘official’ pointer file” into portable evidence.

## 204.7 Pinned references (cite, don’t bloat)

- `.well-known` URI design pattern: `source: rfc8615_txt`.

