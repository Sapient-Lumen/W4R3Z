# Resilio evaluation: placeholder materialization, pin truth, and source-byte witness fragmentation

Current official Resilio docs are still candid that **seeing a file name, having bytes locally, asking for future local residency, and proving that some peer still has the bytes** are not the same truth.
That candor is worth borrowing.
The page contract is still too fragmented to clone.

## Why this seam matters

A sync runtime that supports placeholders is no longer dealing with one simple `file present` bit.
A visible file row may be only a placeholder.
A file may be hydrated locally for now.
A subfolder may be hydrated in a way that also auto-hydrates later arrivals.
A local delete may merely revert to placeholder.
A different delete may remove the file from every peer.
And a visible placeholder may outlive all actual source bytes, producing a ghost-demand problem.
If the product does not own these distinctions in one place, operators overclaim offline safety, delete the wrong thing, or discover too late that no peer still has the data.

## What current official Resilio docs still distinguish well

Current official docs still preserve all of these as separate operational truths:

- `Selective Sync` is configurable when first connecting, after connection, and as the default mode for linked-device arrivals.
- Turning Selective Sync on does not mean everything suddenly becomes the same class: current full files can stay full while new files arrive as placeholders.
- `.rsls` placeholders are zero-byte local stand-ins that only represent names and basic metadata, not actual file bytes.
- Double-clicking a placeholder and `Sync to this device` are fetch actions, not mere open actions.
- Hydrating a subfolder is stronger than hydrating one file, because later files added under that hydrated subfolder are also auto-downloaded there.
- `Remove from this device` reverts only the local copy to a placeholder, while `Remove from all devices` or a system delete on a placeholder with write access can remove the file everywhere.
- Resilio explicitly warns that if every peer turns the file back into a placeholder, only placeholders remain and there may be no actual file left anywhere.
- Resilio separately warns that a Selective Sync mesh can advertise a file and later lose all source bytes before another peer fetches it, yielding the `no source peers online for too long time` / ghost-file condition.
- Power-user preferences separately govern whether `Remove from all devices` is available and whether local placeholder removal is forced to recreate a placeholder instead of propagating deletion.
- Removing a Selective Sync share from Sync removes the placeholders from that device's filesystem entirely.

That is strong semantic candor.
AnonSync should borrow it directly.

## Why the current contract still should not be cloned

Current official Resilio docs still make one ordinary operator answer depend on several article families.
To answer:

> is this entry merely visible, hydrated for now, committed to stay locally resident, guaranteed to auto-hydrate future arrivals, or still missing any proven source of bytes?

a user still has to merge:

- Selective Sync setup docs
- synchronization mode docs
- RSLS / placeholder behavior docs
- ghost-file warning docs
- mobile placeholder notes
- power-user preference docs

The distinctions are good.
The workflow ownership is still scattered.

## The AnonSync decision

AnonSync should make **materialization class and source-byte witness** first-class product structure.
That means:

1. **visible placeholder, hydrated local copy, locally pinned residency, subtree pin with future-arrival commitment, and fully-synced subject are separate modeled states**
2. **delete-local, revert-to-placeholder, and delete-everywhere are separate intents with separate rights and survivor maps**
3. **placeholder visibility is weaker than source-byte witness, and source-byte witness is weaker than offline guarantee**
4. **ghost-file risk must become a first-class watch state rather than an obscure error after demand fails**
5. **every serious materialization action needs one receipt preserving what was visible, what bytes became local, what future-residency promise was made, what source witness existed, and which stronger sentence remained blocked**

## Replacement page family required

This seam adds five more product-owned pages:

- **Materialization contract sheet**
- **Hydration review**
- **Local residency review**
- **Source-byte witness watch**
- **Materialization lineage receipt**

## Strongest non-clone line

> Borrow Resilio's candor that placeholders, hydrated bytes, subtree auto-hydration, delete-local vs delete-everywhere, and ghost-file demand failure are materially different truths — but refuse any product contract where the operator still has to reconstruct materialization class, source-byte witness, and offline-safety ceiling from separate Selective Sync, RSLS, warning, and power-user pages.
