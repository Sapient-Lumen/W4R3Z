# Workstation first richer data-transfer RFC target is reviewed finite collection handoff

**Tier:** C (Profiled richer-lane prioritization)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` already froze the ordinary workstation transfer baseline as complete enough to implement, and `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md` already fixed that any future richer lane must mint a distinct artifact family instead of widening ordinary `ui.datatransfer.*`.

This doc makes the next small but high-leverage prioritization cut explicit:
**if practice later forces one richer workstation transfer lane, the first RFC target should be a reviewed finite collection handoff rather than replay-friendly clipboard history, persistent document-tree authority, or quiet source-writeback convenience.**

See also:
- ADR: `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- next directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- next snapshot-representation cut: `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- next directory-semantics cut: `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- ordinary baseline stop-point: `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- distinct-family intake rule: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- host/UI boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- open questions / risk register: `docs/266-open-questions-and-risk-register.md`

## Why this needs a hard decision

Once the ordinary lane is frozen, “richer lane later” is still too vague. The archive needs one explicit queue head, or else every practical pressure point starts arguing that the ordinary baseline should quietly grow one more exception.

The most credible next pressure is not “make clipboard history richer.”
It is:
- send a few selected files together,
- hand off a reviewed folder-shaped artifact set,
- or let bounded drag/drop-like workflows move a finite set of filesystem objects without reopening ambient namespace authority.

That is a real ergonomic gap, but it still admits a narrower answer than persistent document trees or write-enabled shared folders; the first cut should stay read-only only.

## Accepted prioritization

If the workstation archive invests in one richer lane next, it should be:

- a **reviewed finite collection handoff**
- for a **finite selected set** of files and/or directories
- on a **distinct artifact family** (not ordinary `ui.datatransfer.*`)
- now concretely on the accepted `ui.collection.handoff.grant` / `ui.collection.handoff.manifest` / `ui.collection.handoff.receipt` stack in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` rather than on a still-provisional richer-family placeholder
- **session-bounded** rather than persistent
- **read-only only in the first cut**
- aimed first at **B/C/D** practical file-handoff pressure
- with profile scope now made explicit in `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`, so A stays on rollout/support/import-export/breakglass-shaped answers instead of inheriting this lane by default
- and with the first implementation now made narrower again in `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`, so top-level basename collisions fail closed instead of turning the first trusted review surface into a rename/disambiguation editor
- and with review-surface compaction now made explicit in `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`, so the first trusted UI may use bounded deterministic path-compression without changing the explicit authoritative manifest

The point is to make “send these selected objects there” work without collapsing into:

- persistent directory authority
- ambient shared mounts
- quiet source writeback
- background sync / watcher semantics
- or generic document-provider authority as the first richer answer

## Why this is the right first richer lane

### 1) It solves the next practical gap

Ordinary `ui.datatransfer.*` already covers bounded one-shot payload transfer. The next missing ergonomic step is usually a **small selected set of filesystem objects**, not an open-ended authority surface.

### 2) It stays audit-friendly

A finite collection handoff can keep membership, lifetime, destination, and access mode reviewable. Persistent tree grants and write-enabled directory shares are harder to explain and easier to launder.

### 3) It matches outside ecosystem pressure without copying the broadest parts first

Other ecosystems already separate narrow selected-object sharing from broader document-provider or persistent-tree authority. The right lesson is not to clone every broader lane immediately; it is to start with the **smaller selected-set handoff** before broader persistent authority.

## What this does not decide yet

This doc does **not** accept the richer lane itself.
It does **not** choose final schema names.
It does **not** settle receipt granularity or the smallest exact per-member field set beyond the newer member-kind floor in `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`.
A write-enabled receive exception is no longer left open inside the first cut: `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` now defers writable receive to a later separate RFC/ADR decision.
The profile-scope question is no longer left open either: `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` now fixes this richer family to B/C/D and keeps A out of scope unless a later distinct lane is justified. The first-implementation collision answer is no longer left open either: `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now keeps trusted-UI aliasing out of the first implementation, so multi-root basename collisions fail closed until a later explicit aliasing lane is earned. The first review-surface compaction answer is no longer left open either: `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` now allows bounded deterministic path-compression of ancestor-only directory runs while keeping the authoritative manifest fully explicit and ancestor-closed.

Those remaining details are intentionally pushed into `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md` so the archive can keep moving without pretending the whole richer lane is already closed. `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` already makes one next-step RFC cut explicit, though: the first cut should stay single-retrieve by default and auto-stop after the first successful retrieve.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
