# rev0183 — Zone Replacement Chain Seal

## Why this was the riskiest next seam

The replacement/prevention surface is one of MTGSim's highest-risk semantic kernels. The previous zone-change replacement scaffold already reran candidate collection after each applied rewrite, but validation mostly checked the first requested destination and the final destination. A corrupted replay/state could still make the linked replacement rows internally discontinuous: pass 2 could claim to rewrite a destination that pass 1 never produced, a pass index could drift, or a row could point back to a movement that did not actually own it in the contiguous replacement range.

That is dangerous because current Comprehensive Rules 616 does not describe replacement choice as a one-shot summary. It chooses one applicable effect, applies it, then repeats using the event as modified by previous replacement/prevention effects. MTGSim's evidence has to preserve that repeated chain, not just the aggregate final zone.

## Online grounding

This pass rechecked the official Wizards rules page and current TXT surface. The public page describes the Comprehensive Rules as the reference for all rules/corner cases and links the current DOCX/PDF/TXT files. The observed TXT was effective June 19, 2026 and includes the replacement/prevention cluster at 614, 615, and 616. Relevant observations for this patch:

- Rule 101.4 defines APNAP ordering for simultaneous choices.
- Rule 616.1 says the affected object controller/owner or affected player chooses among applicable replacement/prevention effects, with APNAP handling if multiple players make such choices simultaneously.
- Rule 616.1f says the process repeats after a chosen effect is applied.
- Rule 616.2 says another replacement/prevention effect can become applicable because the event was modified by a prior effect.

Official rules documents remain metadata-only observations and are not bundled in the shared datacube.

## Code-bearing change

rev0183 strengthens the executable validation of zone-change replacement chains:

- `ZoneChangeRecord` validation now walks the linked `ZoneChangeReplacementRecord` range as a chain rather than as loose rows.
- Each pass must consume the original requested destination or the immediately previous replacement result.
- `pass_index` must match the contiguous range position.
- The affected player on each row must match the moved object's pre-move controller, falling back to owner.
- The same source/definition/source-zone LKI cannot appear twice in one event chain.
- Each `ZoneChangeReplacementRecord` backlink must point to a `ZoneChangeRecord` that actually owns that row in its contiguous range, preventing row splicing.

## Refactor/audit substance

This is intentionally a validator/refactor cut, not a card-breadth expansion. The engine already generated the correct rows for the modeled chain. The audit gap was that consumers could over-trust malformed rows because validation only checked endpoints. The new guard moves trust from prose and aggregate fields to an executable chain proof aligned with the repeated resolver model.

## Remaining risk

The full rule-616 hierarchy is still future work: self-replacement priority, ETB control/copy/back-face tiers, simultaneous APNAP batches, replacement effects from non-battlefield zones, and interactive choices are not implemented here. rev0183 makes the current narrow zone-change chain harder to corrupt and easier to replay while preserving those limits.

Datacube: `MTGSim-rev0183-YYYY.MM.DD.HH.MM-replacementchainseal.zip`
