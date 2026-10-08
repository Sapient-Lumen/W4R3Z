# Mission heart audit — rev0022

Timestamp: `2026-06-14T12:26:00-04:00`  
Turn: `14`  
Scope: deep read of `rev0021`, web research pulse `RP-0014`, and a later-turn cold review of `P0001-D010`.

## Heart of the mission

The heart is **not** “make an AI poem that passes as human.” The heart is to build a disclosure-honest, resumable, machine-native poetic workshop where the archive itself becomes a creative instrument.

The project is trying to make machine participation **necessary, visible, and inspectable**. It wants poems whose force depends on computation, branching, addressability, source traceability, revision memory, and disclosure — not poems that merely hide a model behind conventional lyric polish.

In one sentence: **LLMPoetry is a long-horizon research object for discovering whether LLM-assisted poems can become better by refusing concealment and by making their machine procedures matter to the reading act.**

## What is working

- The archive is genuinely resumable: `START_HERE.md`, `STATE.json`, `CONTEXT_PACK.json`, `FRONTIER_TICKET.json`, and `LLM_BROWSE_INDEX.json` give a future LLM a compact boot route.
- The temporal judgment firewall is good and should remain: it prevents same-turn enthusiasm from counting as quality.
- Local formal receipts for D010 pass: branch selector, selector map/vector, loss budget, state switch, ergodic traversal, return diff, and patch application all validate as bookkeeping.
- The legal/ethical posture is unusually strong for a creative AI archive: seed/specimen quarantine, disclosure requirement, quote-search gates, and non-claims are the right instincts.
- The project is already aligned with electronic-literature practice in one important way: it treats the computer/context as part of the literary object rather than pretending the poem is independent of its machinery.

## The cold truth about P0001-D010

D010 is an improvement over D009 because it stops promising a patch and actually applies one. That matters as a formal move.

But D010 should **not** be promoted. It is still mostly a verified substitution game. The patched lines are formally altered, yet the replacements do not create enough semantic, emotional, sonic, or reader-action pressure. The repeated machine-codework vocabulary — pinhole, voltage, motors, coded air, parity, glyph, syntax, spool — has become the project’s new house fog.

D010 proves that the route words can mutate a selected surface. It does not yet prove that the mutation is worth reading.

Verdict recorded separately: `poems/P0001/judgments/cold_review_010_on_D010.json`.

## What has gone severely wrong

### 1. Reentry state drift

Several trusted human-facing surfaces had drifted while validators still passed:

- `docs/00-office/BOOT_CARD.md` still called `P0001-D007` the active draft.
- `poems/P0001/README.md` still called `P0001-D009` the current head.
- `registries/proof_status.json` still said the current draft was `P0001-D008` in several fields.
- `registries/style_firewall.json` still carried `rev0019` / D007-era language.
- `ro-crate-metadata.json` described a D008-era state while root surfaces had moved to D010.

This is more dangerous than an ordinary stale comment, because future operators are explicitly told to trust compact surfaces first. A stale boot card can route the next model into the wrong poem state while all checksum/form validators report success.

**Correction in this revision:** add `tools/check_surface_freshness.py`, wire it into `make surface-freshness`, `make validate`, and `make doctor`, and update the stale reentry surfaces.

### 2. The form ratchet became self-protective

From D001 through D010, every cold review diagnosed “not enough pressure” and answered by adding another mechanical layer. That has produced a strong laboratory notebook, but it risks becoming a bureaucracy that immunizes weak lines from judgment.

A receipt should be a trellis, not the fruit.

### 3. Metadata standards are partly decorative

The cube carries `ro-crate-metadata.json`, `datapackage.json`, and `croissant-lite.json`, but these are mostly lightweight descriptors. That is acceptable only because the files say so. The project should not imply full RO-Crate, Croissant, or Data Package compliance unless external validation/tooling is added.

### 4. Quote-search and source durability are shallow

Draft-stage quote-search receipts are useful, but they do not capture search result pages or durable web snapshots. If a future poem uses documentary claims or rare phrasing as evidence, source capture should move beyond receipt-only URLs.

### 5. The reader-facing object is missing

The apparatus is all here, but the reading experience is not. A reader has to inspect markdown and JSON by hand. That means the poem’s claimed machine-native action is still mostly operator-facing, not reader-facing.

## What should change next

1. **Freeze P0001 as a laboratory family unless the next move is a reader-facing state object.** Do not create D011 by adding yet another receipt layer.
2. **Build one accessible object view** that toggles closed, open, traversal, and patched states and links each visible transition to its receipt. If this view is dull, the form family is probably exhausted.
3. **Add external/disclosed reader judgment before any quality claim.** LLM cold review can triage, but it should not be the evidence layer.
4. **Introduce source/material pressure in P0002.** A new pilot should need an external object, dataset, place, measurement, archive, or interface constraint; otherwise the machine lexicon will keep recycling itself.
5. **Separate current surfaces from historical strata.** Keep history, but make one canonical current path and make drift fail validation.
6. **Add schema validation and path-reference validation.** The cube contains schemas but does not fully use them.
7. **Prune generated reports or mark them historical.** Some stale reports are harmless history, but they should not be mistaken for current state.
8. **Keep the filename law.** Every linked revision should follow `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`; this revision uses `LLMPoetry-rev0022-2026.06.14.12.26-missionheart-surfacefreshness-d010review-hardwater.zip`.

## Speculation

The best future for this project is not a single impressive poem soon. It is a long workshop that gradually discovers what kinds of machine-native constraints still matter after disclosure, after quote search, after external readers, and after the novelty of receipts wears off.

P0001 may become valuable as a beautiful failure: a complete record of how formal verification can outrun poetic necessity. That is not wasted if the lesson is used. The next success probably comes from narrowing the machine procedure, increasing worldly/source pressure, and making the reader experience the transform directly instead of asking them to admire the audit trail.
