# Workstation finite collection handoff review-path normalization stays relative-clean and NFC-canonical

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already fixed the first retrieve-width cut inside that richer lane, `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` already fixed the first directory-semantics cut, `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` already fixed the first snapshot-representation cut, `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` already fixed the first access-mode cut, `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` already fixed the first member-kind floor, `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` already fixed the first exact manifest-entry floor, `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` already fixed deterministic authoritative manifest ordering, and `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` already fixed the first authoritative compact collection identity.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first cut of the reviewed finite collection handoff now gives `review_path` a tiny portable grammar: collection-relative, clean slash-separated, Unicode NFC text with no leading/trailing slash or dot segments, and collisions after normalization fail closed.**

See also:
- ADR: `adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queueing cut: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve-width cut: `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- manifest-first cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- member-kind floor: `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- manifest-field floor: `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- manifest-order cut: `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- manifest-digest cut: `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The archive now depends on normalized review paths for three already-accepted jobs: exact manifest-entry identity, canonical manifest ordering, and canonical-manifest hashing. If “normalized review path” is still left implicit, honest implementations can still disagree about whether leading slashes, trailing slashes, repeated separators, `.` / `..`, or canonically equivalent Unicode spellings name the same reviewed member.

The higher-leverage move is to keep the first richer lane boring:
**the first reviewed collection lane should define one tiny portable path language up front instead of replaying whatever cleanup rules the source filesystem, UI toolkit, or broker happened to use.**

## Accepted cut

For the first cut of the reviewed finite collection handoff RFC:

- every normalized review path is a **non-empty collection-relative UTF-8 text path normalized to Unicode NFC**
- **`/` is the only separator**; backslash is never a separator
- normalized review paths have **no leading slash** and **no trailing slash**
- normalized review paths have **no empty segments**, **no repeated separators**, and **no `.` / `..` segments**
- **U+0000 NUL is forbidden**
- explicit directories are identified by **member kind**, not by a trailing slash marker
- if two source members collapse to the same normalized review path after normalization, handoff creation must **fail closed**
- review paths are **review/export identity paths**, not destination-placement hints, source writeback handles, or host-specific path-repair requests

That gives the archive a path surface that can actually support canonical ordering and canonical-manifest digesting without pretending the first richer lane is a full filesystem-preservation protocol.

## Why this is the right first cut

### 1) It makes the already-accepted ordering and digest rules real

Canonical ordering and canonical-manifest hashing are only portable if the path bytes they operate on are portable too. This cut finishes that job.

### 2) It keeps path identity separate from placement authority

The first richer lane is a reviewed read-only handoff, not a writeback or destination-layout lane. Treating `review_path` as collection identity rather than placement policy keeps that boundary visible.

### 3) It chooses one Unicode answer instead of inheriting filesystem folklore

Unicode canonical equivalence and cross-filesystem normalization behavior are real sources of drift. Making the first reviewed lane normalize to NFC is cheaper than asking every broker, exporter, and support tool to rediscover those host rules separately.

## What this still does not decide

This doc does **not** finalize the richer lane schema family.
It does **not** decide whether advisory MIME type should become mandatory later.
It does **not** decide whether a later lane should preserve owner/mode/mtime/xattr fidelity or other filesystem metadata.
It does **not** decide whether a later materialization/import lane should preserve raw source filenames as additional advisory metadata.
It does **not** decide whether profile A should ever expose this richer lane under explicit operator posture.

Those remain explicit follow-on questions, but the archive no longer leaves review-path normalization ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r427

For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
