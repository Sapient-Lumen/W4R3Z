# P0003 D003 Cold Review / D004 One-Field Shift / Exhaustive-State Audit — rev0065

## Priority decision

The riskiest unfinished internal work was D003's delayed judgment. The creative risk was that D003's relational artifact had become more exact than its poem: two unrelated institutional arguments, familiar room traces, and thirty-one lines delayed the one contradiction that mattered. The bounded refactor risk was equally concrete: the v2 “semantic assertions” could prove selected queries while leaving an unqueried table, row, or column outside the claimed state description.

## D003 cold review

D003 is `revise_not_promote`. It corrected D002's line-table mismatch by storing normalized inspection, response, disagreement, and occupancy relations, rendering through a view, and deriving VACANT through a generated field. That formal success did not solve the poem. HUD damage accounting and Census vacancy classification remained adjacent rather than causal; the rectangle, pinholes, carpet pile, and polished brass were familiar; and the WAL inserted the entire occupancy row, so presence and vacancy arrived together rather than an occupied unit being reclassified while nobody left.

The exact D003 draft, database, WAL, spec, and receipt remain historical inputs. The review is at `poems/P0003/judgments/cold_review_003_on_D003.json`.

## D004 substantive revision

`P0003-D004` removes the HUD branch, all room-trace imagery, and the explanatory ending. Its base database already records persons living in the unit, usual residence here, zero departures, and a VIRTUAL generated status of OCCUPIED. The WAL contains one explicit SQL statement: update the usual-residence field from here to elsewhere. An AFTER UPDATE trigger records the generated transition from OCCUPIED to VACANT. The persons-living field remains YES, the housing-unit row remains present, and the departures table remains empty.

The committed page is eight lines. Its title, “No One Left,” now carries two incompatible readings: nobody departed, yet the status is vacant. D004 is same-turn unjudged; subtraction and formal exactness are not promotion.

## Exhaustive-state refactor

The new v3 WAL spec closes a real verification loophole. A state-contract entry no longer supplies a hand-written query that might omit a column or row. The builder and checker now generate a canonical full-row SELECT for each declared user table, require the declared order to equal that table's primary-key order, include visible generated columns, require every user table exactly once, and compare complete base and committed snapshots. The receipt identifies changed tables (`classification_change`, `housing_unit`) and the unchanged table (`departures`).

This matters to the poem: “DEPARTURES RECORDED | 0” is now supported by an exhaustive zero-row snapshot in both states, not by a selective count alone or a prose label.

## Source and runtime boundaries

Current Census Housing Vacancy Survey definitions provide the narrow classification pressure: an occupied unit's residents ordinarily treat it as their usual residence or have no usual residence elsewhere, while a unit may be classified vacant when entirely occupied by people whose usual residence is elsewhere. SQLite documentation bounds the generated-column, OLD/NEW trigger, WAL-persistence, and runtime behavior.

The packaged runtime is SQLite 3.46.1, within the documented likely affected range for the rare WAL-reset bug. The receipt records one database connection, no concurrent writer, automatic checkpointing disabled, and no checkpoint during the committed transition, so the documented multi-connection write/checkpoint trigger was not exercised. This is a bounded execution profile, not a general safety guarantee.

## Waste corrected

The project did not need another doctrine file. The useful refactor was local to the artifact claim: replace selective state assertions with canonical complete snapshots, wire that gate into the existing WAL validator, and preserve v1/v2 historical compatibility. No new registry class or parallel validation framework was introduced.

A final current-surface pass also found the P0003 row in `registries/poem_index.json` still carrying its inherited `revision: rev0063` even though its current and last-updated fields said rev0065. That field is repaired, the updater now writes row-level revision and turn fields explicitly, and the deep-surface checker now rejects a mismatch. The source-boundary checks were also refactored away from one magic sentence: they now require the same semantic parts—negation, current/live scope, reading-like subject, and claim language—while allowing domain-appropriate wording.

## Boundaries

- D004 has no same-turn literary judgment and no D005 is created.
- P0002-D028 remains terminal; no D029 is created.
- P0002-D010's reader-response log remains empty.
- Source, schema, trigger, state-contract, runtime-profile, and byte verification do not establish literary success.
- The archive makes no determination about any real person, household, or housing unit.

## Next

Cold-review P0003-D004 in a later turn, testing whether the eight-line classification shift and the title “No One Left” survive full disclosure rather than reading as an elegant database demonstration; keep PILOT-0048 open for one real P0002-D010 response; do not create P0002-D029.
