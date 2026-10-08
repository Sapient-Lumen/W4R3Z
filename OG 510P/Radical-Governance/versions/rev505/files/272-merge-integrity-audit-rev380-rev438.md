# Merge Integrity Audit — rev380 worked examples × rev438 mainline

**Purpose:** document the structural checks performed on the rev380→rev438 merge so later maintainers do not have to re-derive whether the merge was safe.

## Verdict

**Status:** structurally sound.

The merged archive preserves the full rev438 mainline while appending the rev380 worked-example layer as `235..270`, with a legacy-number crosswalk at `271`. No rev438 memo was overwritten.

## What was checked

1. **Base preservation.** Every markdown memo present in rev438 remains present in the merged archive; only `00-README.md`, `75-archive-map-and-entry-points.md`, and `102-revision-log.md` were modified from rev438, and those modifications were merge-related only.
2. **Worked-example preservation.** The full rev380 worked-example block `143..178` was carried into the merged archive as `235..270`.
3. **Link integrity.** Explicit markdown links in the merged archive resolve to existing files.
4. **Internal renumbering.** References inside the appended worked-example memos were rewritten from legacy numbers to merged numbers where needed, avoiding accidental collision with rev438’s own `143..178` memos.
5. **Legacy recovery.** `271-worked-example-legacy-number-crosswalk.md` maps every old worked-example number `143..178` to its merged location `235..270`.

## Merge shape

- **Base archive:** rev438
- **Imported layer:** rev380 worked-example memo block
- **Imported range:** legacy `143..178`
- **Merged range:** `235..270`
- **Recovery aid:** `271-worked-example-legacy-number-crosswalk.md`

## Practical guidance for future edits

- Cite the worked-example layer by the **merged numbers** (`235..270`) going forward.
- When encountering older notes that cite rev380 worked-example numbers (`143..178`), resolve them through `271` rather than renumbering old prose by hand.
- Treat this as a **number-safe graft**, not a semantic deduplication pass; if later maintainers want deeper fusion, they should consolidate by topic rather than by number.

## Remaining caveat

The merge is structurally clean, but it intentionally does **not** collapse conceptual overlap between the newer thematic memos in rev438 and the worked-example training layer imported from rev380. That was the right call for salience preservation, but later editorial work could still tighten cross-references or consolidate repeated framing.
