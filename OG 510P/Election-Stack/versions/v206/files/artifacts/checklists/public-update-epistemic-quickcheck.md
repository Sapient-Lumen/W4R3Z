# Public update — epistemic quickcheck (60 seconds)

Use this before publishing a **PublicNotice** update or a signed **public statement**.

Refs: `219` (this workflow), `218` (tags + confidence), `186`/`195`/`200` (PublicNotice + rumor-control surfaces).


## Scope + timing
- [ ] Update includes **time** (local + UTC) and a **bounded scope** (what is in / out of scope for this notice).
- [ ] If this is a follow-up: it states what **changed** since the prior notice (and references the prior notice_id).


## Epistemic discipline (no overclaim)
- [ ] Every load-bearing statement is tagged as `[TAG|CONF]` using the tag set in `218`.
- [ ] Unknowns that matter are explicitly listed (use `[UNKNOWN|*]`), not buried in prose.
- [ ] Inferences are clearly marked `[INFERRED|*]` and do not masquerade as measurement/observation.


## Reproducibility hooks (no screenshot dependence)
- [ ] Notice includes at least one **reproducibility hook**: notice_id, digest pointer, packet reference, or checkpoint hash.
- [ ] If referencing evidence: it points to content-addressed artifacts (hashes), not screenshots or “trust us” phrasing (`206`).


## Corrections (auditable revisions)
- [ ] If correcting prior statements: it is published as a correction (or superseding notice) and explicitly references the prior notice_id.
- [ ] “Quiet edits” to previously published text are avoided; revisions are traceable (`219.3`).


## Commitment
- [ ] Notice includes a realistic **next update** time (or explicitly states why one cannot be provided).
- [ ] “What we are doing next” names the next evidence object(s) or verification step(s), not vague investigation language.

