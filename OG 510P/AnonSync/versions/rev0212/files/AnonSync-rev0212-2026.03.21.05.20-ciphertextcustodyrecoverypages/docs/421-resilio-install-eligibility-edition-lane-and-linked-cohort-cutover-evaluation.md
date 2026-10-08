# Resilio install-eligibility, edition-lane, and linked-cohort cutover evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that Sync v3 is only for personal non-commercial usage while Sync Business remains on v2 and should not be updated in-place to v3
- explicit admission that an unsupported Business-to-v3 update can leave storage bytes intact while losing access to share configuration, which means `files preserved` and `product continuity preserved` are not the same claim
- explicit admission that Sync v3 is not supported on Windows Server, including personal Windows Server scenarios
- explicit admission that current supported-platform truth differs not only by operating system but also by CPU architecture and package lane, with v3 and v2 offering materially different package availability
- explicit admission that NAS install pages repeat the same edition/usage warning instead of one durable central operator page owning it
- explicit admission that mixing v2 and v3 in one linked-device identity constellation can conflict on the applied license and lead to lost access to the UI and share configuration even when storage bytes remain
- explicit admission that the update path itself depends on how Sync was installed: default app install, service install, binary-with-custom-storage launch, or repository package

That is not weak product thinking.
It is useful operational truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading platform requirements, update instructions, FAQ notes, linking docs, Linux package guidance, and NAS-specific install warnings to answer four basic questions:

1. **May this host role and usage class run this release line at all?**
2. **Is this seat allowed to join this linked cohort without version/family skew risk?**
3. **If I cross this update boundary, what product continuity survives: files only, config too, linked identity too, or none?**
4. **Which package or install lane is the right one for this host, and who owns later maintenance?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads host eligibility, edition lane, linked-cohort safety, and update-survival truth across system requirements, update notes, FAQ prose, platform install guides, and identity-linking warnings.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say openly when release eligibility depends on host role, usage class, and architecture**
- **say openly when a linked cohort must move together to avoid control or license breakage**
- **say openly when an update preserves bytes but not control continuity**
- **say openly when install lanes imply different maintenance owners and different cutover rituals**

But AnonSync should refuse four weaker habits:

- learning install eligibility primarily from package tables and platform-specific warnings
- learning cohort safety primarily from identity-linking caveats
- treating `files remain on disk` as good-enough migration honesty
- letting the operator infer maintenance ownership from how the binary happened to be installed last year

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `422` — Install target
- `423` — Linked cohort
- `424` — Upgrade gate
- `425` — Package lane

These pages keep the Resilio candor and reject the scattered operator reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that release eligibility, edition lane, linked-cohort safety, and update survival are real operational truths; refuse any interface contract where `may this seat run this line`, `may this cohort mix versions`, `what survives this cutover`, and `which package lane owns updates` still depends on system-requirements tables, NAS warnings, FAQs, and identity-linking caveats.
