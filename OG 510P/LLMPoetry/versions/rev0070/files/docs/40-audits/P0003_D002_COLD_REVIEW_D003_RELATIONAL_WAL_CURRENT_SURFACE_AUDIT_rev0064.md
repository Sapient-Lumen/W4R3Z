# P0003 D002 Cold Review / D003 Relational WAL / Current-Surface Audit — rev0064

## Priority decision

The highest-risk unfinished internal work was D002's delayed judgment, not another registry. The second risk was that the poem claimed a record-world the database did not model. P0002-D010's one-reader response remains an external dependency and is kept open without fabrication.

## D002 cold review

D002 is `revise_not_promote`. It improved D001 by making the WAL a one-row dissent against a shared clean inspection and by replacing the explanatory ending with official form and vacancy pressure. It still stored an ordered sequence of pre-rendered lines. Disclosure therefore exposed a formal mismatch: the artifact did not know what an inspection item, disagreement, cost, normal-wear classification, or occupancy fact was. Its zero-cost conflict remained passive, and the Census close was appended rather than derived.

The exact D002 draft, database, WAL, spec, and receipt remain historical inputs. The review is at `poems/P0003/judgments/cold_review_002_on_D002.json`.

## D003 substantive revision

`P0003-D003` stores no poem-line table. Its main database contains normalized STRICT relations for inspection items and response state, plus empty disagreement and occupancy relations. A named SQL view renders the surface. The base state remains a GOOD inspection with normal wear and total correction cost zero.

The paired WAL performs eight logical changes: one response update, six disagreement-detail inserts across three items, and one occupancy insert. It does not alter the inspection rows. The occupancy relation computes `VACANT` through a VIRTUAL generated column from persons-present and usual-residence-elsewhere facts. The visible poem is therefore rendered from the record rather than stored as a disguised list of lines.

The main database SHA-256 remains unchanged before checkpoint. D001 and D002 hashes remain preserved. D003 is same-turn unjudged; the relational improvement is a formal fact, not a quality verdict.

## Source pressure

The revision makes normal wear and zero correction cost the hinge rather than background metadata. HUD form and special-claims guidance provide the inspection/disagreement and normal-wear/correction distinction. Census definitions provide the vacant-yet-present classification. SQLite documentation bounds the behavior of views, generated columns, and the persistent database/WAL pair.

## Runtime compatibility risk

The packaged Python runtime reports SQLite 3.46.1. Current SQLite WAL documentation describes a rare affected-version race whose trigger requires concurrent write/checkpoint activity. The D003 receipt records one connection, zero concurrent writers, disabled automatic checkpointing, and no checkpoint during the committed transition. The build therefore does not exercise the documented trigger, but the archive now states the compatibility boundary instead of treating its runtime as current or universally safe.

## Severe current-surface fault and refactor

Rev0063 validation passed while `REENTRY_CONTRACT.json` still routed through P0002-D023, `LLM_BROWSE_INDEX.json` carried a D022 risk and RP-0052, `REPLAY_CAPSULE.json` called P0002-D028 current, and the global poem index still marked P0002 as the global head. These were not harmless historical notes; they were current-facing routing errors.

Rev0064 makes `STATE.read_first` canonical for every `read_first` and `must_read` surface, requires current pulse alignment, validates current risk and replay prose against the resolved head, validates nested current surface paths, and requires exactly one `global_current_head` owner in the poem index. Misleading P0002 “current” aliases are renamed as terminal-head or reader-target surfaces.

## Boundaries

- D003 has no same-turn literary judgment and no D004 is created.
- P0002-D028 remains terminal; no D029 is created.
- P0002-D010's reader-response log remains empty.
- Source, schema, runtime-profile, and byte verification do not establish literary success.
- The archive does not make legal or housing claims beyond bounded source descriptions.

## Next

Cold-review P0003-D003 in a later turn, testing whether zero-cost normal wear, the relational view, and the generated vacant-yet-present classification survive disclosure; keep PILOT-0048 open for one real P0002-D010 response; do not create P0002-D029.
