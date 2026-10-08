# Cube deep audit rev0246 — proceed-staged note before workbench

## Finding

Rev0245 made every returned owner CSV classifiable and routed each outcome to a next artifact. The
remaining risk was the apparently successful path. `PROCEED-STAGED` still jumped straight from a
CSV triage result into the broader owner packet workbench, where a maintainer could accidentally
copy too much, add a new field, or treat a first reply as stronger evidence than it is.

This was a substance risk, not a registry risk. The archive needed a small staging landing pad, not
another governance family.

## Change made

Rev0246 adds one local generated landing artifact for `PROCEED-STAGED`:

- `templates/ft0181-proceed-staged-note-template.md` defines the note shape.
- `tools/stage_owner_reply_csv.py` generates the note only when the triage result is
  `PROCEED-STAGED`.
- `tools/check_owner_reply_staging.py` self-tests safe staging, blocked-staging refusal, and
  `--output` behavior.
- `tools/triage_owner_reply_csv.py` now routes `PROCEED-STAGED` to the staging-note template before
  the workbench.
- `owner_reply_intake` now names the staging tool and template, and the ready-request validator
  checks both.

The generated note preserves the eight owner answers, repeats the source/claim boundary, and names
`docs/30-operations/ft0181-owner-packet-workbench.md` as the next artifact only after the note
exists.

## Refactor principle

A successful first reply must have a narrow holding form before the workbench:

1. triage the returned CSV;
2. generate the proceed-staged note only if the triage is `PROCEED-STAGED`;
3. copy only minimized surviving rows into the workbench;
4. keep all source-truth, public-claim, lifecycle, custody, and closure upgrades downstream.

No first owner reply may skip directly to public claims, live-window work, closeout, or closure.

## Waste removed

The old successful path still required a human to decide what to copy into the workbench. That was a
quiet source of waste because a maintainer might respond by adding yet another interpretation sheet.
Rev0246 keeps the work small: one command, one generated note, then the existing workbench.

The audit also found root-history drift: README and CHANGELOG both had duplicate `rev0245` headings,
with one section actually describing rev0244. Rev0246 corrects that version-label drift while
preserving the old audit surfaces as history.

## Still missing

No owner has been contacted. No filled CSV has returned. No proceed-staged note has been generated
from real evidence. No `SRC2+` packet has been accepted. The new staging path only prevents the
first viable reply from being over-copied or over-claimed once it arrives.
