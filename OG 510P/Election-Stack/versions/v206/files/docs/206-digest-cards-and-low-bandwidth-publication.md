# 206 — Digest cards and low-bandwidth publication (SMS/print/QR)

**Track:** A (Deployable core)

Track A comms surfaces rely on **content-addressed anchors** (digests) that can be checked offline and compared across channels:

- `PublicNotice` (docs/186)
- `PublicNoticeFeed` (docs/200)
- `OfficialChannelDirectory` (docs/203)
- `/.well-known/election-stack.json` bootstrap (docs/204)

In real incidents, many audiences encounter updates through **low-bandwidth** or **high-distortion** channels:
SMS, screenshots, reposts, printed flyers, “someone said on X”, or a cached status page.

This doc defines a *tight* operator practice: publish **digest cards** (short, copy/pasteable text) so the public can
re-anchor claims to verifiable objects even when the channel is hostile or lossy.

## 206.1 Threat model (specific)

1. **Screenshot laundering:** an attacker posts an image of a fake “official update” that cannot be searched/copy‑checked.
2. **Truncation & paraphrase drift:** long statements get shortened, reworded, or translated with meaning changes.
3. **Split-view + selective exposure:** different audiences see different “latest” pointers (docs/201).
4. **Stale-pointer confusion:** caches/proxies replay older bootstrap/feed/directory pointers (docs/205).

Digest cards do not prevent misinformation; they make it **cheap to verify** and **cheap to disprove**.

## 206.2 Minimal digest-card standard (bounded)

A digest card is plain text that MUST include:

- **object type** (what it is)
- **stable identifier** (when available)
- **payload digest** (sha256, ideally full; short form acceptable if space-constrained)
- **verification hint** (where to fetch and what to compare)

Recommended: publish both forms when possible.

- **Full digest** (best): `sha256:<64 hex>`
- **Short digest** (space constrained): `sha256:<12>…<8>` (from the operator card tools)

**Do not publish only a URL.** URLs are editable; digests are portable.

## 206.3 What to publish (the “minimum public anchors”)

During steady-state and especially during incidents, operators SHOULD ensure the public can find:

1. **Latest PublicNotice digest** (the actual statement)
2. **Latest PublicNoticeFeed digest** (what’s most recent)
3. **Latest OfficialChannelDirectory digest** (where to look)
4. **Latest /.well-known digest** (domain-first bootstrap)

Human surfaces (status board / rumor-control page) should display these in a fixed “How to verify” box (docs/195).

## 206.4 Operator ergonomics (stdlib card tools)

Use the card tools to avoid hand-copy errors and to keep output bounded:

- PublicNotice:
  - `python tools/public_notice_card.py --packet <packet_dir>`
- PublicNoticeFeed:
  - `python tools/public_notice_feed_card.py --packet <packet_dir>`
- OfficialChannelDirectory:
  - `python tools/official_channel_directory_card.py --packet <packet_dir>`
- Well-known discovery payload:
  - `python tools/well_known_discovery_card.py --packet <packet_dir>`
- Official surface security snapshot (optional hardening proof):
  - `python tools/official_surface_security_snapshot_card.py --packet <packet_dir>`

Or use the one-command dispatcher:
- `python tools/evidence_object_card.py --packet <packet_dir>`

## 206.5 Print / QR guidance (anti-bloat)

If you print/post physically (poll sites, pressers, office windows):

- Print the **short digest** in text next to any QR.
- Prefer the QR to encode a **stable URL** (e.g., the status board or `/.well-known`) and let the printed digest
  be the authenticity anchor.
- Avoid encoding only a digest in the QR unless you also print an explanation of what it is.

Physical postings are not “trusted”; they are a **fallback discovery surface** that lets the public quickly
find the same digests on multiple channels.

## 206.6 Failure-avoidance rules (common mistakes)

- Do **not** publish vote totals or operational claims without binding them to a digestable object.
- Do **not** publish only screenshots as “proof” (always include text digests).
- Do **not** change digest formatting per channel; keep a consistent label (`sha256:` prefix).
- When a mismatch is alleged, publish a receipted+gossiped parity snapshot and cite it from a PublicNotice
  (docs/201, docs/202).
