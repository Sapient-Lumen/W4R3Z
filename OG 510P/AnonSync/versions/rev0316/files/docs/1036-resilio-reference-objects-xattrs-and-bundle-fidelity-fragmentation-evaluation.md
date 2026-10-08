# Resilio reference objects, xattrs, and bundle-fidelity fragmentation evaluation

## Why this pass exists

The archive already had strong language for path identity, overlap topology, hidden control substrate, metadata authority, and portability ceilings.
What it still did not own with one explicit current Resilio memo was the narrower but extremely practical seam:

> when the operator is looking at something that visually resembles an ordinary folder or file, is the product actually preserving an ordinary byte object, a filesystem reference object, a metadata-bearing bundle, or only a degraded compatibility residue?

Current official Resilio docs are still candid that this seam is real.
Across its current help center, Resilio still says all of the following:

- on Windows, Sync does **not** support junctions, hard links, or symbolic links, and using them may produce `.Conflict` entries
- on Unix, Sync can synchronize the symbolic-link object itself, but the referenced target folder is **not** synchronized unless it is added separately
- `ignore_symlinks` still exists as a current power-user setting, meaning the product can also deliberately suppress symbolic-link syncing
- extended attributes / alternate streams are synchronized only according to a whitelist kept in hidden `.sync/StreamsList`
- when a peer cannot store xattrs natively, Sync may create stub files in `.sync/Streams` so metadata can still be propagated onward
- current troubleshooting docs still say that if xattr syncing is disabled through `StreamsList`, file bundles such as Pages, Keynote, and macOS apps may sync as plain subdirectories instead

That is valuable candor.
It is also a strong reason not to clone the present interface contract.
One ordinary operator question — `what is this object really, and what fidelity will survive across this cohort?` — still requires combining:

- a symlink support article
- power-user settings
- xattr / StreamsList details
- troubleshooting notes about bundle collapse and compatibility behavior

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Object kind is a first-class contract field.** Ordinary file, ordinary directory, symbolic-link reference, hard-link-style alias, bundle, metadata-bearing object, and compatibility residue may never be flattened into one `item` sentence.
2. **Reference preservation and target-follow are separate verbs.** Preserving a symbolic link object is not the same act as adopting or syncing the referenced target.
3. **Bundle fidelity must be explicit.** If preserving a bundle requires metadata lanes that some peers cannot apply, the interface must say whether the outcome is preserved bundle, propagated metadata with stub residue, or collapsed plain directory semantics.
4. **Platform acceptability is weaker than cohort fidelity.** A thing that is legal on one peer may still be conflict-prone, degraded, or blocked across the cohort.
5. **Receipts must preserve the actual fidelity ceiling.** The product may never let `synced` imply stronger object preservation than the reviewed cohort can honestly support.
