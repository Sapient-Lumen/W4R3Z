# P0003 D004 Candidate Freeze / Poem-Index Canonicality Audit — rev0066

## Priority decision

The highest-risk unfinished internal task was no longer another revision. It was deciding whether D004 had earned a stop. Revisions D001–D003 each solved a technical problem while leaving the page behind. D004 concentrated the work to one exact event: people remain, departures stay zero, and a single usual-residence update changes the generated classification from OCCUPIED to VACANT.

The later-turn review promotes D004 to an **internal anthology candidate, not evidence**, and freezes the lineage. No D005 is created. This is forward motion because it ends the internal rewrite treadmill rather than rewarding continued motion.

## Why D004 passes internally

D004 survives the criterion-first and order-swapped controls. Against D003 in either order, it wins by removing the unrelated inspection branch and realizing the occupied-to-vacant transition D003 only described. Against D001 in either order, it wins because the database/WAL split is not replaceable proof apparatus: removing the sidecar removes the committed state itself.

The residual danger is real. “No One Left” may over-prime the double reading, and `CURRENT STATUS | VACANT` may land as a solved logic puzzle. That is now an external-reader question, not a reason to manufacture D005 without evidence.

## Reader access without another bureaucracy stack

The revision adds one offline HTML reader edition and no new response registry, rubric, identity field, or pilot queue. It discloses the mechanism before the poem, presents the verified database-alone state, and reveals the paired-WAL state on action. The page is explicitly a presentation, not an SQLite execution or a response.

## Refactor: all-poem alias truth

The incoming `registries/poem_index.json` still contained stale P0002 aliases even though earlier validators passed:

- `current_draft_path` pointed to D026 while the terminal head was D028;
- `current_packet` and `current_material_packet` pointed to packet 027;
- `metrics_path` pointed to metrics 027;
- `non_claim` still described D023 as same-turn unjudged.

This is not harmless history. Those fields are named as current and can route an LLM or future script to the wrong evidence. Rev0066 repairs them and extends the existing deep-surface checker across **every poem-index row**, not only the global-head owner. For any row with a parseable head, all present draft, packet, metrics, and head aliases must agree with the head-derived paths. A present non-claim must name that row’s head.

The same gate now verifies that `STATE.anthology_top_5` contains only actual anthology-candidate records with existing candidate packets. This removes terminal non-candidate D028 from the anthology list and adds D004 behind D010.

## Current runtime boundary

The packaged Python runtime remains SQLite 3.46.1. Current official SQLite release material says the WAL-reset corruption bug is fixed in the 3.53 line and recommends upgrading from affected versions. The preserved D004 build still used one connection, no concurrent writer, disabled automatic checkpointing, and no checkpoint during the transition; the candidate freeze does not rebuild or mutate those bytes.

## Refactor discovered during clean-room validation: creation identity is not current routing

The first rev0066 validation pass found a deeper defect than stale aliases. Several validators assumed that every file named by a `current_*` pointer must be rewritten to mention the newest cube revision. That rule is destructive for a frozen candidate: it would require changing the exact rev0065 draft, packet, metrics, spec, and receipt after the review claimed their bytes were preserved.

Rev0066 now separates two facts. Immutable source files retain their creation revision and must match the hashes recorded by the later-turn review/candidate packet. Mutable routing surfaces—STATE, proof status, pilot queue, reader wrapper, descriptors—must identify rev0066. The same repair restores `proof_status.current_draft` to the draft ID rather than a filesystem path and returns PILOT-0048 to the one canonical `recommended_next` status.

## Boundaries

- D004 is an internal candidate, not evidence_candidate or admitted.
- No D005, P0002-D029, or reader response is created.
- The P0002-D010 response count remains zero.
- The reader edition is a presentation of verified states, not the canonical artifact and not a response instrument.
- No real household or housing unit is classified.

## Next

Keep P0003-D004 frozen and obtain one real non-identifying disclosed-reader response for P0002-D010 before starting another candidate apparatus; create P0003-D005 only if later external pressure identifies a concrete line or mechanism failure, and do not create P0002-D029.
