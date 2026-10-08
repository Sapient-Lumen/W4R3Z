# FT-0181 workbench review record

Use this only after `make owner-field-next` sees a valid review brief created from `workbench-seed.json` and emits an `owner-workbench-review` command. The review record is local and minimized. It is not source acceptance, custody evidence, closure evidence, or public-summary support.

## Command shape

A proceed-capable review must look like this, with the counts adjusted after the human workbench review. The review brief writes the same skeleton but does not choose the route or counts:

```bash
make owner-workbench-review \
  SEED=scratch/.../workbench-seed.json \
  DECISION=proceed-decision-board \
  SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED \
  REVIEW_BASIS=owner-attested-aggregate \
  SURVIVING_FIELD_COUNT=1 \
  DECISION_CHANGED_COUNT=1 \
  LOCAL_ONLY_FIELD_COUNT=0 \
  TRIMMED_FIELD_COUNT=0 \
  REASK_FIELD_COUNT=0 \
  REVIEWER_ROLE_COUNT=2 \
  CONFIRM=human-reviewed-minimized-workbench-record
```

For a clarification route, use `DECISION=reask-owner`, `REVIEW_BASIS=needs-clarification`, and set `REASK_FIELD_COUNT` to the number of unclear fields. The router can then source one bounded `REASK_AWAITING_REPLY` clock from `workbench-review.json`.

## Review brief before this record

`make owner-workbench-review-brief SEED=scratch/.../workbench-seed.json` prepares a scratch-local one-screen reviewer handoff and bounded command skeletons. It is not the review, not evidence, not acceptance, and not closure. Use it to avoid reconstructing commands by hand; then run exactly one filled command below after human review.

## Allowed decisions

| Decision | Use when | Next route |
|---|---|---|
| `proceed-decision-board` | the local review is minimized, one service, a pre-acceptance `SRC2-CANDIDATE-NOT-ACCEPTED` or stronger real source class is named, and at least two reviewer roles are represented | first-packet decision board only |
| `reask-owner` | one or more rows need bounded clarification | one bounded re-ask contact clock |
| `block-overbroad` | the reply requires a broad export or merged data lake | block without widening |
| `block-protected` | protected facts cannot be separated | keep local/quarantine |
| `block-security` | security payloads or credentials cannot be abstracted | keep local/quarantine |
| `block-evidence` | evidence is usage, satisfaction, memory, vendor claim, or otherwise weak | suppress claim |
| `no-change-trim` | fields do not change a decision | trim and keep `FT-0181` live |

## Do not include

Do not include owner answer text, raw CSV rows, learner identifiers, names, emails, messages, essays, screenshots, gradebook rows, protected support facts, small cells, credentials, exploit strings, prompts, vendor dashboards, or public claim copy. The record stores counts and route classes only.

## Boundary

A workbench review can route to the first-packet decision board or one bounded re-ask. It cannot close `FT-0181`, upgrade source truth, convert a candidate source class into acceptance, prove service impact, authorize a public claim, or replace custody/acceptance gates.
