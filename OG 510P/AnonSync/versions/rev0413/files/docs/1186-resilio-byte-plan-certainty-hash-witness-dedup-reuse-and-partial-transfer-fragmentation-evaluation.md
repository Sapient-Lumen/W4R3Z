# Resilio byte-plan certainty, hash witness, dedup reuse, and partial-transfer fragmentation evaluation

## Why this pass exists

The archive already had transport, interface, overlap, materialization, and health doctrine.
What it still lacked was one tighter current Resilio pass about a narrower operator question:

> when the product implies `this should not re-download`, what truth actually exists: piece-delta transfer, local block reuse, archive-assisted rename reuse, pre-seeded byte match, or only optimistic transfer intent?

Current official Resilio docs are unusually useful here because they are candid about the real mechanics while still leaving the operator to reconstruct them across FAQ, troubleshooting, rename/archive behavior, and partial-download cleanup notes.

Today those docs still show that:

- ordinary file change transfer is piecewise rather than whole-file, but whole-file resend can still happen when changes shift all pieces.
- background work includes `checking file blocks`, `copying local file blocks`, `hashing file`, and hashing of local files for pre-seeded folders on receiving peers apart from read-only peers.
- deduplication can avoid re-download by copying matching local file blocks piece by piece, but it may increase local disk usage while it does so.
- rename or move reuse depends on Archive being present because the receiver checks Archive for the same hash and reuses the bytes under the new name instead of re-transmitting them.
- partial-download residue has its own cleanup path: stuck `.!sync` files can remain in `.sync` and may require delete-plus-restart if resume does not continue.

That is a very good operator-truth corpus.
It is also a strong reason not to clone the exact page contract.

## What current Resilio still gets right

### 1) It admits that `changed file` does not always mean `whole file again`

The current FAQ is explicit that only changed pieces are transferred in the ordinary case.
That candor is worth keeping.

### 2) It admits that there are several local byte-reuse paths

The current troubleshooting article is unusually explicit that deduplication can copy local file blocks instead of re-downloading and that pre-seeded receiving peers may spend real time hashing local files before they know what can be reused.
That distinction is materially useful.

### 3) It admits that rename reuse is hash- and archive-dependent

The rename article does not pretend that a new name is just metadata.
It says the receiving peer checks Archive for the same hash and only then reuses the old bytes under the new name.
That is a sharper contract than a generic `renames are cheap` statement.

### 4) It admits that partial-transfer state is not the same thing as resumability proof

The current troubleshooting docs still describe stuck `.!sync` residue and a manual cleanup boundary.
That is useful because it keeps `there are partial bytes` separate from `the transfer will definitely resume correctly`.

## Why AnonSync still should not clone it

### 1) Piece-delta, local block reuse, rename reuse, and pre-seeded reuse are still too easy to confuse

Resilio's current docs still make an operator pull these truths from several pages.
AnonSync should not let one optimistic label like `won't redownload` hide the actual reuse basis.

### 2) Hashing work and byte-certainty are still too easy to confuse

A peer that is hashing local files or checking local blocks is not yet a peer that has proven reusable bytes.
AnonSync should keep `hashing`, `candidate match`, and `reused bytes proven` distinct.

### 3) Archive-assisted reuse still hides a prerequisite

The current rename behavior is useful, but it still leaves the operator to remember that Archive being enabled is what makes the cheap rename path possible.
AnonSync should not let rename reuse appear unconditional.

### 4) Partial local residue still does not answer the survivor question

A leftover `.!sync` file is not the same truth as durable partial progress, safe resume, or safe cleanup.
AnonSync should review that boundary explicitly instead of leaving it in troubleshooting prose.

## Hard decisions now locked for AnonSync

1. **Byte-plan certainty is a first-class contract object, not a speed hint.**
2. **Piece-delta transfer, local block reuse, archive-assisted rename reuse, pre-seeded byte match, and full redownload are separate truths.**
3. **Hashing is weaker than byte witness, and byte witness is weaker than `no re-download required`.**
4. **Partial local residue is weaker than resumability proof, and resumability proof is weaker than survivor safety.**
5. **Every serious transfer-affecting action needs one receipt that preserves reuse basis, witness grade, fallback-to-redownload class, and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Byte-plan contract sheet**
- **Hash and pre-seed review**
- **Reuse-basis review**
- **Partial-transfer survivor proof**
- **Byte-plan lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that changed-piece transfer, local dedup reuse, archive-assisted rename reuse, pre-seeded hashing, and stuck partial residue are different truths. But it still makes one ordinary operator answer — `why does this claim it should not re-download, what witness actually supports that, and what residue survives if resume fails?` — depend on several pages instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
