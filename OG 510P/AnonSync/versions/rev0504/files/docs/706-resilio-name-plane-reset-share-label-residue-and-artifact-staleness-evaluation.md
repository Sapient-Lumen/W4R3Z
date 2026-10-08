# Resilio name-plane reset, share-label residue, and artifact-staleness evaluation

## Why this pass exists

The archive already has doctrine for name planes in the abstract.
What it still did not own tightly enough was a sharper current Resilio seam:

> when a share's visible name is mutable in more than one place, which outward names stay fresh, which are only local residue, and what exact reset or reissue action restores truth?

Current official Resilio docs still make that seam concrete.
They still say all of the following:

- a desktop share can get a custom name in Sync UI without renaming the folder on disk
- that custom name does not propagate to linked devices or other peers
- a different custom name can be inserted while generating a sharing link or QR code
- that sharing-time label does not become the durable share name in preferences
- if the label is changed while sharing by QR, the operator must switch away and back so a new QR code is generated
- disconnecting the share leaves the custom UI name in place until the operator explicitly uses `Reset` in share preferences
- renaming the synced folder itself only affects that device
- the active Sync v3 help-center line still runs through `3.1.2.1076`

That is useful candor.
It is also a strong reason not to clone the page contract.

## What current Resilio gets right

### 1) It admits that `the name` is not one thing

Current docs do not pretend one label governs every audience.
They still distinguish:

- folder basename on disk
- local UI name
- sharing-time artifact label
- peer/device-local visibility of those labels

That honesty is worth borrowing.

### 2) It admits that local residue is real

The current custom-name article is especially useful because it still says disconnecting a share leaves the custom UI name in place and that returning to baseline requires an explicit `Reset` action.
That means name residue is not only cosmetic; it changes what later operators think they are looking at.

### 3) It admits that outward artifacts can go stale

The QR-code note matters more than it first appears to.
Current docs still say changing the name in the sharing view does not automatically mean the displayed QR now represents the new label; the operator must switch views so a fresh QR is generated.
That is exactly the kind of stale outward artifact boundary a serious product should own explicitly.

## Why this is still a strong reason not to clone them

Current official docs still leave one ordinary operator answer too fragmented:

- which name is only local presentation residue
- which name is the on-disk basename for this seat only
- which name was inserted into the currently exported link/QR artifact
- whether that outward artifact is still fresh after later renaming
- what exact reset or reissue action is required to restore baseline truth

That should not require combining a custom-name tip article, local rename/move guidance, and operator memory about whether a QR was regenerated.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that local presentation labels, disk basenames, and outward artifact labels are different planes
- explicit candor that disconnect residue and stale outward artifacts are real states, not edge-case folklore
- explicit candor that reset and reissue are materially different repairs

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on several docs.
The product should not let `rename`, `reset`, `share with name`, or `scan this QR` stand without one owned surface that states:

- active plane and audience now
- whether visible residue is local-only or outwardly published
- whether currently displayed artifacts are fresh or stale under the new name state
- whether the honest next action is relabel, reset, reissue, regenerate, or keep separate
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds four more page-shaped obligations:

1. **Name posture** — which label planes exist now, where they are seen, and whether any are residue.
2. **Name change review** — which plane is changing, who will see it, and whether reset or reissue is also required.
3. **Artifact label freshness** — whether the currently visible link / QR / outward label is still fresh after later rename work.
4. **Name receipt** — what changed, what remained, what reset was still pending, and what outward artifacts remained valid or stale.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that multiple name planes are real and operationally useful; it is also current evidence that the ordinary operator answer about `which name is real here, which one is residue, and did I regenerate the outward artifact after renaming?` still leaks across tips articles and memory instead of one stable product-owned family.
