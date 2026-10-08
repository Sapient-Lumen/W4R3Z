# Resilio attribute-plane locality, hidden whitelist, and courier-residue evaluation

## Purpose

The archive already knew that xattrs and alternate streams matter.
What it still lacked was one evaluation page for a narrower operational question:

> when object meaning depends on metadata channels, where does current Resilio actually place the control, and what kind of seat is a platform-limited peer in practice?

Current official Resilio docs make this sharper than a generic `metadata is tricky` note would.
They still say xattrs sync only according to a whitelist stored in hidden `.sync/StreamsList`, that the file is editable, that unlisted xattrs are ignored, that `IgnoreList` does not govern xattrs, and that unsupported targets may carry those channels through hidden `.sync/Streams` stubs instead of storing them natively.
That is honest capability.
It is not yet a clean public contract.

## What Resilio gets right

Resilio is usefully candid that:

- metadata channels are real and can matter to object meaning
- channel scope may be selective rather than global
- some targets can preserve channels natively while others cannot
- platform limits do not always force total failure because courier-style fallback exists
- narrowing metadata carriage can alter visible object behavior, not just invisible fidelity

Those are valuable truths.
AnonSync should borrow that candor.

## Where the contract is still too hidden

Current Resilio still spreads one ordinary operator answer across several pages:

- `Alt Streams and Xattrs in Sync` for whitelist and courier-stub behavior
- `.sync` internals for where the controlling files live
- IgnoreList docs for the separate exclusion plane
- shell / troubleshooting notes for visible bundle-shape fallout when xattr syncing is disabled

That means a user can still end up reconstructing the real contract only after they have already accepted an object into a lower-fidelity lane.

## Non-clone conclusion

AnonSync should **not** clone any contract where:

- channel scope lives primarily in a hidden share-local text file
- normal exclusion policy and metadata policy are separate but not publicly distinguished
- unsupported seats silently become courier seats with hidden residue
- visible object-shape consequences only become clear after metadata carriage narrows
- the product keeps saying `synced` after object meaning has already moved into a weaker lane

## Better AnonSync rule

AnonSync should publish one public answer to four questions before apply:

1. **Which metadata channels are in scope?**
2. **Why are they in scope — visible policy, inherited legacy, or hidden local carry?**
3. **Is each seat a native preserver, a courier-only relay, or a reduced-fidelity holder?**
4. **Could this choice change visible object shape or behavior?**

That rule is stricter than Resilio's current help-center contract while still borrowing the useful capability behind it.
