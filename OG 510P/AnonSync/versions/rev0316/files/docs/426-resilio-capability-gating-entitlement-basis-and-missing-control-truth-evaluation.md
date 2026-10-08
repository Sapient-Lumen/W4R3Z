# Resilio capability-gating, entitlement-basis, and missing-control truth evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- repeated per-feature honesty that some capabilities are fully available in Sync v3 while Sync v2 requires licensed Home Pro or Business entitlement for the same feature families
- explicit scope differences inside the product itself, such as Standard folders being available in Free and Pro while Advanced folders remain a Pro / trial capability in v2 and a v3 capability
- explicit admission that local shares are desktop-only, Pro-only, and can simply stop syncing when the trial expires, the license expires, or the license is removed
- explicit admission that Business licensing has a single current license owner, that applying the key on another identity steals ownership, and that linked devices under that owner inherit Pro while unlinked devices require separately shared seats
- explicit admission that if the Business owner expires, shared seats expire with it, which means capability loss can propagate across several seats at once
- explicit admission that a device can revert to Free and require either key re-application or owner-side seat re-sharing to regain Pro functionality
- explicit admission that some seat / host combinations may still accept a license file yet immediately stop sharing and linking because the effective entitlement does not actually match the host role

That is not weak product thinking.
It is useful operational truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require hopping across feature pages, license pages, troubleshooting notes, family/business distinctions, and version FAQ prose to answer four basic questions:

1. **Why is this capability available on this seat but missing on that one?**
2. **What exact basis makes this seat currently entitled: local key, linked-owner inheritance, shared seat, family allowance, or non-commercial v3 posture?**
3. **If a capability is disabled or absent here, is the blocker version, entitlement, host role, subject class, or current surface?**
4. **If the seat just lost Pro behavior, what exactly stopped, what remains intact, and what recovery path is actually correct?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads capability availability and entitlement basis across Selective Sync, My Devices, User Management, folder-type comparison, single-file sharing, local-share, licensing, license-loss, server-warning, and v3 FAQ pages.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say openly when capability families depend on release line, seat role, and entitlement**
- **say openly when entitlement basis depends on who currently owns the license or shared seat**
- **say openly when a control is absent because of surface, subject-class, or host-role mismatch rather than pretending it never existed**
- **say openly when capability loss changes live behavior without pretending bytes or history disappeared**

But AnonSync should refuse four weaker habits:

- learning capability availability primarily from repeated footnotes on unrelated feature pages
- learning entitlement provenance primarily from licensing support notes and error articles
- learning why a control is absent only by comparing one surface against another or against memory
- learning post-expiry behavior only after a seat has already fallen back and lost the affordance

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `427` — Capability availability
- `428` — Entitlement basis
- `429` — Gated action
- `430` — Pro-function loss

These pages keep the Resilio candor and reject the scattered operator reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that feature availability, entitlement provenance, missing-control causes, and Pro-function loss are real operational truths; refuse any interface contract where `why is this here`, `why is this missing`, `what exact right do I currently have`, and `what just stopped working` still depends on per-feature availability footnotes, license-owner lore, troubleshooting pages, and version FAQ fragments.
