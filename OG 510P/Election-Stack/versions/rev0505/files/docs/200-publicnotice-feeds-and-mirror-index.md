# 200 — PublicNotice feeds and mirror index (bounded discovery without split‑views)

**Track:** A (Deployable core)

PublicNotices (`docs/186`) make public statements **content‑addressed** and receipt‑backed.
But an attacker can still win by manipulating **discovery and ordering**:

- audiences see different subsets of notices (split‑view comms)
- older notices become “hard to find” (soft suppression)
- a status page quietly rewrites history (rollback / edit‑in‑place)

This doc introduces a **bounded, rollback‑detectable index** for PublicNotices: a PublicNotice feed.

See also: issuing endpoint inspection challenges for feed surfaces (`docs/202-public-surface-challenges-and-escalating-split-views.md`).

For interpreting notice updates and corrections into an effective “current state”, see `220-publicnotice-graph-resolution-and-effective-state.md`.

For a monitor contract that checks integrity + parity + convergence across channels, see `221-publicnotice-monitoring-and-convergence.md`.

Bootstrapping tip: publish the latest feed digest in the domain-first `/.well-known/election-stack.json` surface (docs/204) so observers can discover it with only the primary domain.

## 200.1 Core idea

Envelope kind: `hfv.public.notice_feed`

- payload schema: `schemas/PublicNoticeFeed.json`
- drafting template: `artifacts/templates/public-notice-feed-payload.json`
- example packet: `artifacts/examples/evidence_packet_public_notice_feed`

A PublicNotice feed is itself an evidence object that:
1) lists a **window** of recent PublicNotices (by digest + minimal metadata), and
2) optionally **chains** updates via a `previous_feed_payload_sha256` pointer.

This gives observers a cheap way to answer:
- “What are the most recent official notices?”
- “Did the operator remove/replace a notice from the public narrative?”

The design is intentionally small and mirrors transparency‑log anti‑rollback patterns.
References:
- Certificate Transparency / RFC 9162 model (`source: rfc9162_txt`).
- SCITT architecture notes on transparency services (`source: draft_scitt_architecture_22_txt`).

## 200.2 Bounded size (windowed feeds)

We cannot afford feeds that grow without bound.
Instead, the feed payload is **windowed**:

- Each update publishes a feed that includes the **last N** notices (operator-chosen, e.g. 25–100).
- If `previous_feed_payload_sha256` is present, older windows remain reachable by digest.

The feed remains small per update, while rollback/rewrites remain detectable by the chain.

## 200.3 Rollback / rewrite detection

A feed update SHOULD set:
- `previous_feed_payload_sha256` = digest of the previous feed **payload** bytes.

Observers can then:
- treat any missing link as suspicious
- detect “history rewrite” when a previously seen feed digest disappears or changes

This is the same adversary class as split‑view/rollback attacks in transparency systems.
See: `docs/23` and `docs/31`.

## 200.4 What goes in a feed entry (keep it tight)

A feed entry MUST include:
- `notice_id`
- `notice_payload_sha256` (digest of the PublicNotice payload object bytes)

A feed entry SHOULD include (bounded, operator‑copyable):
- `issued_at` (for sorting)
- `notice_type`
- `title`
- `channels` (canonical IDs from `artifacts/registries/official-channels.csv`)

A feed entry MAY include:
- `notice_tbs_sha256` (digest of the notice envelope TBS; helps verifiers cross‑check)
- `packet_manifest_sha256` (if the notice is published as part of a packet)
- `mirrors` (short list of stable fetch locations)

**Do not embed narratives** in the feed. The notice payload is the narrative.

### Canonical ordering (avoid false split-view alarms)

Because array order is part of the feed digest, verifiers SHOULD treat entry reordering as a rewrite unless the deployment commits to a deterministic rule.

Recommended rule:
- set `ordering` = `issued_at_desc_notice_id_asc`
- sort `entries[]` by `issued_at` descending, tie-breaker by `notice_id` ascending

Legacy feeds that cannot commit MAY set `ordering` = `unspecified`, but monitors should then prefer chain-based rewrite detection over within-feed ordering comparisons.

## 200.5 Publication expectations (anti split‑view)

Because this feed is an operator-facing public surface, deployments SHOULD treat it like a PublicNotice:

- require a `TransparencyReceipt` attachment
- require a `GossipSummary` attachment

See: `docs/180` and the attachment registry `artifacts/registries/envelope-attachment-requirements.csv`.

## 200.6 How operators should publish it

Minimal operator pattern:

1. Publish each `hfv.public.notice` as usual.
2. Update the feed whenever a new notice is issued:
   - append the new entry
   - keep only the last N entries
   - set `previous_feed_payload_sha256`
3. Publish the **latest** feed at a stable path on each official surface (website/status page), and optionally
   publish a content-addressed copy keyed by its digest.

This gives monitors a single “latest index” target while keeping strong anti‑rollback properties.

## 200.7 How monitors/observers should use it

- Poll the stable “latest feed” location(s) across official channels.
- Verify digests and required attachments.
- Compare the observed feed chain and the set of notice digests across channels.

If parity fails (channel A shows a different feed chain than channel B), treat it as a **public incident**:

- publish a `hfv.public.surface_parity_snapshot` capturing what each channel served (docs/201)
- publish a new PublicNotice describing the mismatch
- include the mismatching feed digests and the snapshot digest as references

This turns “they quietly told different stories” into a provable event, and makes the split-view evidence portable.

## 200.8 Relationship to status boards and rumor control

A status board (docs/195) SHOULD:
- render from the latest PublicNotice feed, not from an editable CMS database
- display the latest feed digest (short form) alongside the board

This makes the board a *view* over verifiable statements, not an un-auditable editorial surface.

## 200.9 Cache and freshness notes

Feeds are pointer surfaces; stale caches can become “stale pointers”. See `docs/205-cache-and-freshness-controls-for-public-surfaces.md` for a minimal cache/freshness posture.

