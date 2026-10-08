# Cube deep audit rev0232: first-packet landing and startup slimming

## Audit finding

The riskiest unfinished work is no longer whether the archive has enough controls for `FT-0181`. It
is whether the first real owner packet can land without being delayed by generic pilot doctrine,
release-control surfaces, or a broad export request. Rev0231 made the owner ask narrow. The remaining
execution gap was that the archive still lacked a single packet workbench that a maintainer could use
when the owner actually replies.

The second drag was startup posture. The compact context pack still pointed maintainers through
several generic release-control and pilot-packet surfaces before the first-packet artifacts. That is
safe, but it invites the archive's old vice: reading governance scaffolding instead of getting one
reviewable packet staged.

## What changed

Rev0232 adds `docs/30-operations/ft0181-owner-packet-workbench.md`. It is a one-page field form plus
arrival triage, field-survival ledger, first-review decision table, reviewer mini-calibration, and
dry-run rehearsal outcomes. Its purpose is not to add a new approval layer. Its purpose is to make the
first owner reply immediately classifiable as `PROCEED-STAGED`, fallback, block, local-only, or trim.

The import dictionary and import map were also made more concrete. They now mirror the owner packet
instead of a generic LMS export: selected service, date range, source owner path, action ceiling,
aggregate counts, aggregate learning/task signal, answer-giving or false-reminder stop counts,
workload-review minutes, public notice text, local-only protected facts, local-only security payloads,
and trimmed vendor success claims.

The context-pack generator was slimmed so first-read context favors the FT-0181 packet lane over
release-control reference surfaces. Release controls remain in the archive and lint plane, but they
are no longer treated as first-start reading for the next import attempt.

## Substantive posture change

The lane now distinguishes three useful non-closure outcomes:

| Outcome | Why it is progress |
|---|---|
| `FALLBACK-SERVICE` | proves the hint-tutor path cannot stay aggregate-only and moves the first import to the capped reminder lane without widening scope |
| `BLOCK-OVERBROAD` | records that a full export is unsafe or wasteful, preventing export residue from becoming schema debt |
| `NO-CHANGE-TRIM` | proves fields arrived but did not change authority, evidence, construct, public claim, protected-route safety, security handling, rollback, or stop decisions |

These outcomes matter because a blocked or trimmed packet may be the first honest field result. The
archive should not treat only successful normalization as progress.

## External-risk posture

The current public environment still supports a narrow first import. State and sector guidance for
AI-in-education evaluation remains uneven and often exploratory, federal education guidance keeps AI
uses tied to existing statutory and regulatory requirements, and children's privacy rules keep raw
minor-facing data hard to justify when aggregate evidence can answer the decision question. That
points toward owner-reviewed, aggregate packets and away from raw learner traces or vendor-scale
claims.

## Refactor judgment

No new validator was added. The better refactor was to remove generic first-read weight and make the
existing dictionary/map/request/acceptance lane more concrete. This avoids turning every human
workflow gap into a new machine-control gap.

## What still has not happened

No real `SRC2+` pilot packet has arrived. `FT-0181` remains live. Rev0232 improves the chance that a
real packet can be received safely, but it does not prove learning outcomes, safety, access,
compliance, workload reduction, or service effectiveness.

## Next useful pass

The next pass should either process a real owner packet or run the workbench against a specific blank
owner-contact scenario and record which of the rehearsal outcomes occurred. Do not add a new control
unless the packet actually reveals a false-closure, leakage, hidden-authority, overclaim,
stale-evidence, or burden-creep failure that the current lane cannot represent.
