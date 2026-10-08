# Resilio raw-state cloning, seat duplication, and successor-import gap evaluation

## Why this pass exists

The archive already had strong language for state roots, attach-state review, invocation worlds, durability, and seat lineage.
What it still did not own with one explicit current Resilio memo was the narrower but very practical operator seam:

> if I need to replace a machine, restore from backup, stamp a golden image, or move local sync state elsewhere, what is the honest path — same-world continuation, reviewed successor import, stale backup restore, or unsafe raw clone?

Current official Resilio docs are still useful here precisely because they are blunt.
They still say all of the following:

- `Cloning Sync` is not supported; plain copies, drive cloners, and Time Machine style copies can yield two or more Sync instances that do not transfer to one another and show other strange behavior.
- the `Sync Storage folder` still holds current configuration, auxiliary settings files, shares' database, and related state.
- `Sync Private Identity & Linking My Devices` still says each installation gets its own unique digital certificate and fingerprint, even when two independent installs use the same identity name.
- `Can I change the name of my Sync identity?` still says creating a new identity requires unlinking and generating a new certificate rather than simply editing one field.

That is valuable candor.
It is also a strong non-clone signal, because the ordinary operator answer about `how do I replace or duplicate a seat safely?` still bottoms out in a blunt unsupported-cloning warning plus scattered identity/storage facts rather than one product-owned successor-import contract.

## What current Resilio still gets right

Current official docs still deserve credit for several things AnonSync should borrow more strongly:

- **They admit that opaque state copying is dangerous.**
  The product does not pretend that raw disk-image continuity is an ordinary safe path.
- **They admit that local state is meaningful.**
  The storage folder is documented as containing configuration and share database state rather than treated as mystery sludge.
- **They admit that seat identity is real.**
  A Sync installation is not just a path tree; it has a certificate-backed seat identity with its own fingerprint.
- **They admit that renaming identity is actually identity replacement.**
  The docs still force a new certificate instead of pretending a display-name edit is harmless continuity.

## Where the contract still fractures

The trouble is not that Resilio warns too loudly.
The trouble is that the warning is still too blunt for the real operator choices.
A serious operator usually needs one of these answers:

1. `cold successor import` — carry forward reviewed subject/policy state onto a replacement seat
2. `stale backup restore` — inspect or recover an older state snapshot without claiming present continuity
3. `concurrent duplicate` — block because the copied state would create two runtimes with the same local story
4. `clean seat` — start fresh and then reconnect/redeem/import explicitly

Current official docs still do not give that as one first-class page family.
Instead, the operator must reconstruct it from unsupported-cloning prose, storage-folder explanations, and identity/certificate docs.

## Hard AnonSync decisions locked in here

1. **Raw state cloning is never the normal continuity path.**
   Opaque disk or app-state copies may exist, but they may not silently count as reviewed continuity.
2. **Successor transfer must use a first-class reviewed artifact.**
   AnonSync should support a named successor/export capsule instead of leaving replacement to folklore.
3. **Seat rebirth and subject carry-forward are separate truths.**
   A replacement seat may inherit reviewed subject state while still receiving a new seat handle and explicit predecessor link.
4. **Concurrent duplicate risk gets its own blocking surface.**
   `same bytes on two machines` is not a warning toast; it is a first-class collision review.
5. **Receipts must preserve blocked stronger sentences.**
   The system must record when it refused the stronger claim that a raw clone was just the same seat continuing.

## Borrow, then refuse the clone

AnonSync should borrow Resilio's blunt honesty that opaque cloning is dangerous.
AnonSync should refuse the weaker contract where `unsupported` is the whole answer.

The better product shape is:

- one explicit **Successor capsule** object for reviewed carry-forward
- one explicit **State adoption review** distinguishing cold successor, stale backup, clean seat, and concurrent duplicate
- one explicit **Duplicate seat collision warning** whenever the operator is about to run a copied state world as though nothing changed
- one explicit **Successor activation proof** that shows what really continued and what was reborn
- one durable **State lineage receipt** proving exactly which stronger continuity sentence remained blocked
