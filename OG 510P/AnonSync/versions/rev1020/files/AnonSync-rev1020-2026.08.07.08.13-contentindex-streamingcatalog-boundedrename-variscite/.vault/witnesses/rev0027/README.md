# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0027`
- Timestamp: `2026.03.09.19.58` (America/New_York)
- Codename: `contactapprovalsuccessionkeystone`

## What changed in this revision

This revision continues directly from `rev0026` and does nine things:

1. Pushes the **Resilio Sync** comparison deeper at the authority seam: linked devices automatically broaden visibility, remembered approval can widen future sharing, and own-device meshes still collapse into Owner-like power.
2. Uses **Syncthing** as a cleaner counterexample at two narrow points: introducer behavior is explicit rather than ambient, and pending remote devices are first-class records that can be reviewed or removed.
3. Adds a dedicated **contact / link / approval / succession spec** so relationship memory, pending peer admission, bounded future approval, and device replacement are described together instead of scattered across unrelated objects.
4. Expands the **interface spec** with explicit contact-record, pending-peer, and introduction-policy concepts, plus command families for reviewing or suppressing new peer contact before it turns into trust or share visibility.
5. Extends the **daemon API** with first-class contact and pending-peer resources so future UI/TUI work has a supported queue for unknown or newly introduced peers.
6. Adds new **canonical flows** for reviewing a newly contacting peer without silently linking it, and for allowing bounded introductions inside one trusted constellation without creating ambient auto-add behavior.
7. Tightens the **non-clone rationale** around convenience versus authority: Resilio is still strong, but its linked-device and approval ergonomics remain too broad for AnonSync's least-privilege thesis.
8. Performs some **archive hygiene** by fixing drifted numbering in the flows and requirement lists so later revisions have a cleaner spine.
9. Refreshes the **critical open questions** so the remaining uncertainty now includes bounded introduction policy and approval carry-forward across successor replacement, not just transport mechanics.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

We **should** continue to borrow and reinterpret several of its strongest product ideas:

- legible materialization states
- on-demand file materialization / selective sync
- first-class encrypted-untrusted replicas
- explicit per-peer permissions
- a simple device-linking flow
- explicit pending-peer review before unknown contact becomes trust or visibility
- LAN-only / known-host operation as an explicit policy choice
- transport policies that explain exposure and route choice directly
- temporary speed-management controls that are useful in practice
- bounded future-approval and successor-handoff workflows that stay legible

We **should not** inherit the parts that cut against AnonSync's reason to exist:

- linking behavior that broadens share visibility and future approvals too far by default
- certificate takeover semantics when linking already-initialized devices
- split control surfaces where the best trust model is not uniformly available to config/CLI/API paths
- recovery stories that depend on reinstall rituals or unsupported clone-style workarounds
- transport behavior that is configurable but still partly explained through retained cache state and support-article lore
- a clearnet-first tracker/direct/relay worldview when the product thesis wants Tor/I2P to be first-class route classes
- route controls that still blur together publication, dialing, fallback, and privacy posture across public versus private infrastructure
- operator-facing explanations that still depend too much on peer icons, peer counts, troubleshooting lore, overloaded pause toggles, or delete folklore instead of decision traces, override leases, preservation reports, settlement reports, and retirement records
- hidden service files or magic conflict filenames being part of the effective operator contract
- convenience linking that forces users to trade away least privilege or clean upgrade boundaries
- encrypted-recovery workflows that depend on hidden database continuity and support-article memory instead of supported recovery bundles
- device-list cleanup rituals that blur together “hide this offline thing”, “ignore future contact”, “revoke trust”, and “replace with successor”
- remembered approvals that silently become standing future authority across devices or share classes
- contact/admission behavior where unknown peers, linked-device introductions, and future approval all blur into one convenience channel
- share-governance models where Owner semantics are too coarse, too share-type-dependent, or too hard to hand off cleanly
- read-only / receive-only behaviors where accidental local edits either silently stall, silently persist, or silently auto-revert depending on mode-specific caveats instead of an explicit deviation policy
- path adoption or relocation workflows that silently merge non-empty directories or treat local path rebinding as an implementation detail
- cross-platform path and metadata semantics that surface only as later conflict files, advanced-toggle lore, or implicit downgrade instead of explicit filesystem compatibility reports
- ignore/placeholder behavior that still blurs share-wide namespace announcement, local mount projection, and byte materialization instead of exposing those as separate supported policies
- convergence/status behavior that still makes operators infer “safe to cut over now?” from peer counts, status warnings, clock-skew errors, watcher-failure warnings, and hidden background-task heuristics instead of an explicit settlement report
- privacy-routing support that would remain magical if bundled runtimes, persistence paths, verification surfaces, and manual direct-speed leases were not all first-class inspectable state
- platform ambition that would spread core design attention too early instead of treating Linux as the primary operating environment and naming concrete first-class filesystem tiers

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and non-goals
- `docs/30-interface-spec.md` — CLI/operator interface specification
- `docs/31-daemon-api-spec.md` — local daemon API, events, auth, and compatibility contract
- `docs/32-interface-flows.md` — canonical operator workflows and expected UX semantics
- `docs/33-transport-runtime-spec.md` — bundled transport/runtime/session contract
- `docs/34-linux-filesystem-scope.md` — Linux-first filesystem support tiers and behavioral contract
- `docs/35-embedded-transport-lifecycle.md` — provenance, persistence, update, and shutdown contract for bundled Tor/I2P support
- `docs/36-route-exposure-known-host-and-lease-spec.md` — publication, dialing, peer-pinned direct paths, and temporary direct-route exceptions
- `docs/37-contact-link-approval-and-succession-spec.md` — contact memory, pending peers, bounded introductions, approval scope, and successor continuity
- `docs/40-architecture-decisions.md` — design decisions and tradeoffs
- `docs/50-roadmap.md` — phased roadmap
- `docs/55-critical-open-questions.md` — short list of the biggest unresolved design questions
- `docs/sources.md` — source list used for this revision

## Reading order

Read `10-resilio-sync-evaluation.md` first, then `20-product-direction.md`, then `33-transport-runtime-spec.md`, then `35-embedded-transport-lifecycle.md`, then `36-route-exposure-known-host-and-lease-spec.md`, then `37-contact-link-approval-and-succession-spec.md`, then `30-interface-spec.md`, then `31-daemon-api-spec.md`, then `34-linux-filesystem-scope.md`, then `32-interface-flows.md`, then `55-critical-open-questions.md`.
