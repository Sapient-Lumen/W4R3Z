# Resilio mixed-version capability-floor, platform-gating, and license-conflict fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `FAQ Resilio Sync 3.0.0` docs still say Sync v2 and v3 preserve synchronization compatibility
- those same current FAQ docs still say devices linked under one identity should all be updated to v3 to avoid license conflicts
- current identity-linking docs sharpen that again: they still say linking devices where v2 and v3 are mixed is highly inadvisable because applied licenses can conflict and access to UI and shares configuration may be lost, even though stored files are not affected
- current supported-platforms docs still say the v3 platform envelope is narrower than v2 in important ways: v3 is not supported on Windows Server, while current v2 docs still list Windows Server 2008 R2 and newer; current v2 docs also still list FreeBSD and wider CPU coverage that v3 no longer lists
- current `Selective Sync` docs still say the feature is fully available in v3 but in v2 is available only in licensed editions
- current installation and NAS-package docs still say Sync Business must remain on v2, the latest available v2 release is 2.8.1 for that lane, and attempting to install v3 over a Business installation is unsupported and can lose access to configured shares until reinstall

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **can these peers still exchange bytes at all?**
2. **what major-version floor governs the cohort's safe feature envelope?**
3. **which peers are blocked not by reachability but by platform class or product lane?**
4. **which features are present in some seats but not safely claimable for the whole cohort?**
5. **which upgrade moves are actually forbidden because of business/NAS posture rather than mere lag?**

Current Resilio docs still spread those answers across FAQ, identity-linking, supported-platforms, feature pages, and installation articles.

So a user can learn all the pieces and still not get one stable product answer to:

> this cohort still syncs, but what is the strongest truthful sentence about what the whole group can safely do, which members set the floor, and which upgrades are blocked by license or platform lane rather than simple staleness?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow five habits directly:

- **say openly when wire compatibility survives but cohort capability does not fully survive**
- **say openly when mixed majors are byte-compatible but identity-linked administration is unsafe**
- **say openly when platform class narrows the cohort's future upgrade lane**
- **say openly when a feature is only locally available and cannot be safely promised cohort-wide**
- **say openly when a node is held on an older lane by product policy rather than operator neglect**

But AnonSync should reject five weaker habits:

- one optimistic `compatible` sentence that hides linked-family license conflict risk
- version badges that do not publish the effective cohort floor
- feature marketing that does not publish seat-class and platform gates
- upgrade prompts that ignore NAS / Business immobility
- capability claims derived from a strongest node instead of the weakest governing node

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1259` — Capability-floor contract sheet
- `1260` — Version interlock review
- `1261` — Feature envelope proof
- `1262` — Capability-floor timeline
- `1263` — Capability-floor lineage receipt

These pages keep the Resilio candor and reject the scattered-capability-floor semantics problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that wire compatibility, linked-identity safety, platform support, feature entitlement, and upgrade lane are different truths; refuse any interface contract where the operator must reconstruct the cohort's real capability floor from several FAQ, platform, identity, and installation articles instead of one explicit capability-floor object.
