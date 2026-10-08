# 203 — Official channel directory as evidence (where to look, verifiably)

**Track:** A (Deployable core)

When an election office says “check our official site / follow our official account”, the hard part is:
**how does an outsider know which surfaces are *actually* official**, especially under impersonation, handle changes, takedowns, and platform compromise?

This doc defines a tight, bounded evidence object: a **content‑addressed directory of official public channels** for a jurisdiction/election.

It is intentionally small:
- it is a *map*, not a narrative
- it is publishable, receipted, and gossiped (anti selective disclosure)
- it is designed to be cited by digest from every other public surface

## 203.1 Threats this mitigates

1. **Impersonation & lookalike accounts** (copycat domains/handles, ad-hoc “official” pages).
2. **Handle / domain churn** (platform renames, account recovery, domain migration).
3. **Channel takeover** (an official social account is compromised; the website remains intact or vice‑versa).
4. **Split‑view comms** (one audience sees a “new” official handle or status page; another does not).

This object doesn’t “solve” those threats alone; it provides a **stable, verifiable anchor** that other proofs can bind to.

## 203.2 Minimal contract

### Envelope kind
Register and publish the directory under:
- **kind:** `hfv.public.official_channel_directory`
- **payload schema:** `schemas/OfficialChannelDirectory.json`

The directory envelope SHOULD carry the standard anti‑suppression attachments (see `docs/180`):
- `transparency_receipt`
- `gossip_summary`

Operator ergonomics (bounded digest card; see `docs/206`):
- `python tools/official_channel_directory_card.py --packet <packet_dir>`
- or: `python tools/evidence_object_card.py --packet <packet_dir>`

### Payload shape (bounded)
See:
- schema: `schemas/OfficialChannelDirectory.json`
- drafting template: `artifacts/templates/official-channel-directory-payload.json`
- example packet: `artifacts/examples/evidence_packet_official_channel_directory`

Minimum fields:
- `directory_id` (stable series id)
- `generated_at`
- `election_scope` (election id + jurisdiction)
- `channels[]` entries that reference canonical `channel_id` values from `artifacts/registries/official-channels.csv`

Optional but high‑leverage:
- `discovery.well_known_url` pointing to `/.well-known/election-stack.json` (docs/204) so outsiders can bootstrap discovery from the primary domain.
- `discovery.public_notice_signing_keyset_payload_sha256` for the latest allow-list of keys authorized to sign PublicNotices (docs/208).
- `previous_directory_payload_sha256` + `sequence` for rollback/rewrites detection
- `discovery.*` pointers (e.g., where the current `PublicNoticeFeed` lives; see `docs/200`)

## 203.3 How it gets used in the comms spine

Treat the directory as **the “where to look” root** for public comms:

- **Website / status board / rumor control page:** display the *short digest* of the latest directory payload alongside the latest PublicNotice digest (see `docs/195` and `docs/200`).
- **Social posts and email alerts:** include the directory short digest (or a stable pointer to the directory packet) the same way we include PublicNotice digests (`docs/186`).
- **Corrections and migrations:** publish a new directory payload (chained via `previous_directory_payload_sha256`) and cite it from a `PublicNotice`.

Why bind it this way?
- If a platform account is compromised, other channels can still point to the newest directory digest.
- If a new “official” handle appears, observers can demand to see it *in the directory* (and see the receipt/gossip proof).

## 203.4 Operational guidance (keep it small)

- Keep `channels[]` tight: list **only the surfaces you are willing to defend as official**.
- Order `channels[]` by `channel_id` ascending (stable diffs; avoids accidental “implied priority”).
- Prefer **stable identifiers** in `identifier` (domain:…, email:…, @handle) and stable landing URLs.
- Avoid embedding long instructions; put operational playbooks elsewhere and cite them.
- Treat the directory as a freshness-sensitive pointer surface; use an explicit short-TTL cache posture (see `docs/205-cache-and-freshness-controls-for-public-surfaces.md`).
- If you need to justify controls for a channel (SPF/DKIM/DMARC, CAA/CT, DNSSEC), publish an `OfficialSurfaceSecuritySnapshot` (`docs/199`) and cite its digest from a `PublicNotice`.

## 203.5 Verifier / monitor checks (recommended)

A verifier or monitor consuming this directory SHOULD:
1. Validate the payload against `schemas/OfficialChannelDirectory.json`.
2. Verify that each `channel_id` appears in `artifacts/registries/official-channels.csv` (unknown ids should be surfaced, not silently accepted).
3. If `previous_directory_payload_sha256` is present, check the chain for unexpected rewrites (same pattern as `PublicNoticeFeed`; `docs/200`).
4. On incidents or disputed comms, request independent parity snapshots of the directory surface and/or latest feed (`docs/201`, `docs/202`).

## 203.6 Why this is a separate kind (and not “just a PublicNotice”)

A directory is a **structural discovery surface**:
- it is referenced constantly
- it benefits from hash‑chaining for rewrite detection
- it should remain small and machine-checkable

`PublicNotice` remains the narrative artifact; the directory is a pointer map.


## 203.7 Pinned references (cite, don’t bloat)

If you want external grounding for the “make official comms discoverable and hard to spoof” theme, prefer citing lockfile ids (see `docs/191`):

- `eac_incident_response_comms_guide_pdf`
- `eac_enhancing_election_security_public_comms_2024_pdf`
- `cisa_rumorcontrol_page`
