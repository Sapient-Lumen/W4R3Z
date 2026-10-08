# Cube deep audit rev0247 — executable smoke path before real owner intake

## Finding

Rev0246 made the successful owner-reply path safer by forcing `PROCEED-STAGED` through a generated
staging note before the owner packet workbench. The remaining risk was operational: the path was
plausible but not rehearsable as one command. A maintainer could still discover only after a real
owner replied that the template, triage tool, staging generator, and route metadata had drifted.

That would waste the rare real owner contact. The archive needed a synthetic smoke path that proves
intake plumbing, while making it impossible to mistake the smoke fixture for evidence.

## Change made

Rev0248 adds a narrow local smoke lane:

- `fixtures/owner-reply-pipeline/ft0181-proceed-staged-smoke.csv` is a clearly labeled `SRC0` eight-row
  fixture shaped like a viable owner reply but marked synthetic and not `SRC2+` evidence.
- `tools/smoke_owner_reply_pipeline.py` runs triage, generates the proceed-staged note in memory or
  to `--output-note`, and emits a summary with `source_truth_class: SRC0-SMOKE`.
- `tools/check_owner_reply_pipeline_smoke.py` verifies the default smoke fixture, optional note
  writing, claim ceiling, and blocked overbroad refusal.
- `Makefile` now exposes `make owner-reply-smoke` for a quick pre-contact rehearsal.
- `owner_reply_intake` now names the smoke tool and synthetic fixture so the ready request records
  how to test the pipe without creating fake evidence.

## Refactor principle

The first real owner reply is scarce. The system should know before contact that this path works:

1. run the synthetic smoke fixture through the same triage and staging code;
2. verify the result is only `SRC0-SMOKE`;
3. confirm the generated note repeats the closure and claim ceiling;
4. use the smoke result only to prove plumbing, never as evidence or public language.

## Audit/refactor fix

The archive index validator said it tracked Markdown, JSON, Python, CSV, and Makefile surfaces, but
its code did not include `.csv` in the enforced suffix set. That meant the fillable owner-reply CSV
and future CSV fixtures could drift out of `ARCHIVE_INDEX.md` without lint noticing. Rev0248 updates
`tools/check_archive_index.py` to enforce CSV coverage and regenerates the index.

## Waste removed

Without this smoke path, the next real owner reply could trigger debugging under pressure or another
manual checklist. Rev0248 makes the rehearsal executable and local. It does not add a new evidence
gate; it protects the existing gate from failing on first use.

## Still missing

No owner has been contacted. No filled owner CSV has returned. No proceed-staged note has been
generated from real evidence. No `SRC2+` packet has been accepted. The smoke fixture is not real
pilot evidence and cannot close `FT-0181`.
