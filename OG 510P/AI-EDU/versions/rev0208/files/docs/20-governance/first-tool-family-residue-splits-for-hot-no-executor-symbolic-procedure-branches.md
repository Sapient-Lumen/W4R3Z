# First tool-family residue splits for hot no-executor symbolic-procedure branches

This document closes the next narrower governance gap inside the archive's only slightly portable hot direct-production mathematics branch.

The archive already made one asymmetric call: among the first hot direct-production child branches, only `SR-MATH-PROC-01A2` looked stable enough to harden at all, and even then only inside **published no-calculator / no-executor course families**. That was a real improvement, but it still left one blurry residue: the archive had not yet said which hotter mathematics cases truly belong inside that thin inherited family and which should stay outside it because tool use is part of the claim rather than an optional aid.

Three failure modes matter here:

- **no-calculator laundering** — once one published no-executor family hardens, institutions start treating every controlled quantitative task as if the same hot branch now travels automatically;
- **device-required collapse** — families where calculator or graphing-device use is expected get folded into a no-executor symbolic row merely because the task is timed or supervised;
- **tool-integrated overreach** — graphing, statistics, modeling, CAS, or programming-mediated quantitative work gets spoken about as if it were only a stricter version of handwritten symbolic procedure.

Current official signals point in the same direction. College Board's current AP calculator policy still says calculators may be used on **all or some parts** of listed exams and on no others; it still says Calculus AB, Calculus BC, and Precalculus continue to have parts where no calculator is allowed even when Desmos is built into Bluebook for the permitted parts. At the same time, AP Statistics and AP Physics 1 still publish calculator-permitted quantitative exam surfaces. Together those signals support a tighter archive rule: the first truthful residue split inside hot no-executor symbolic procedure is not every exam brand, but a compact distinction between **declared no-executor symbolic families** and hotter quantitative families where device use is expected or tool integration is part of the task. See `B199`, `B200`.

## Relationship to the row-governance canon

This document does not replace:

- [`reusable-starter-override-rows.md`](reusable-starter-override-rows.md)
- [`promotion-splitting-softening-and-retirement-rules-for-reusable-starter-override-rows.md`](promotion-splitting-softening-and-retirement-rules-for-reusable-starter-override-rows.md)
- [`first-child-splits-for-still-live-reusable-starter-override-rows.md`](first-child-splits-for-still-live-reusable-starter-override-rows.md)
- [`first-hardening-judgments-and-protected-access-carveouts-for-child-and-writing-override-rows.md`](first-hardening-judgments-and-protected-access-carveouts-for-child-and-writing-override-rows.md)
- [`first-stakes-sensitive-child-branches-for-direct-production-override-rows.md`](first-stakes-sensitive-child-branches-for-direct-production-override-rows.md)
- [`first-hardening-and-locality-judgments-for-hot-direct-production-child-branches.md`](first-hardening-and-locality-judgments-for-hot-direct-production-child-branches.md)

It adds one thing only:

- the **first tool-family residue split** inside `SR-MATH-PROC-01A2`, so the archive stops pretending that every hotter mathematics branch either inherits the thin no-executor hardening or stays one undifferentiated local blob.

## Small tool-family residue grammar

| Code | Meaning | Default archive action |
|---|---|---|
| `TF1-DECLARED-NX` | the family publicly declares a no-calculator / no-executor symbolic part under controlled conditions | the thin `HP1-FAMILY` hardening may travel inside that named family |
| `TF2-DEVICE-EXPECTED` | the family expects calculator or graphing-device use for the quantitative task even though the task may still be timed, supervised, or gateway-bearing | do **not** inherit the no-executor hot row; keep family-local or manual handling |
| `TF3-TOOL-INTEGRATED` | graphing, CAS, statistics, modeling, or programming-mediated tool use is part of the construct itself rather than a removable aid | keep local/manual until a different reusable child row is explicitly published |

The archive is deliberately not naming timer-by-timer or brand-by-brand variants here. It is only publishing the first truthful tool-family boundary.

## First residue splits inside `SR-MATH-PROC-01A2`

| Parent row | New child row | Meaning | Default outcome | Portability judgment |
|---|---|---|---|---|
| `SR-MATH-PROC-01A2` | `SR-MATH-PROC-01A2A` | hotter no-executor symbolic procedure inside a publicly declared no-calculator / no-executor family | `live_or_supervised_surface_required` | `HP1-FAMILY` |
| `SR-MATH-PROC-01A2` | `SR-MATH-PROC-01A2B` | hotter timed / gateway / controlled quantitative work inside a calculator- or device-expected family | `local_or_manual_review` | `HP0-LOCAL` |
| `SR-MATH-PROC-01A2` | `SR-MATH-PROC-01A2C` | hotter graphing / CAS / modeling / programming-mediated quantitative work where tool integration is part of the claim | `local_or_manual_review` | `HP0-LOCAL` |

## Row notes

### `SR-MATH-PROC-01A2A` — the thin inherited family really is the no-executor symbolic one

This child row is the archive's current best example of a hot direct-production mathematics branch that can travel at all. The reason is narrow: some named families already publish the no-calculator / no-executor claim openly, so a controlled symbolic-procedure branch does not need to be rediscovered from scratch at each site. The branch still stays family-bound. It is not a general mathematics rule. See `B199`, `B200`.

### `SR-MATH-PROC-01A2B` — calculator-expected quantitative work is not a weaker no-executor branch

This residue stays local because the presence of a calculator or graphing device is not a small operational detail; it changes the truthful task shape. Timed or supervised quantitative work in AP Statistics, AP Physics, or similar families may still be hot, but it is not the same hotness as no-executor symbolic procedure. The archive would rather keep this family local for now than pretend the no-executor child row travels farther than it really does. See `B200`.

### `SR-MATH-PROC-01A2C` — tool-integrated quantitative work should not be smuggled into the symbolic branch

Graphing-heavy, CAS-heavy, modeling-heavy, or programming-mediated quantitative work remains even less plausible as inherited residue under the symbolic no-executor row. Here the tool is closer to part of the assessed practice than to an optional extra aid. The archive is therefore keeping this branch local or manual-review until a genuinely different reusable row earns publication.

## What the archive is now making explicit

### The first hot mathematics hardening line was real, but it was not the whole family

The archive is no longer satisfied with saying only that `SR-MATH-PROC-01A2` hardens narrowly by family. That was true, but incomplete. The hardening line now has a clearer object: **declared no-executor symbolic families**. Device-expected and tool-integrated quantitative families do not inherit that same hotter row merely because their tasks are also timed or supervised.

### Hot mathematics now has a thin child map, not one portable row plus residue fog

The archive now publishes one thin inherited child row and two residue branches. That keeps the archive honest without exploding the row set. It is enough to stop over-generalization while still postponing a separate reusable quantitative-tool family until there is better evidence.

### This is still not a universal schoolwide math rule

Nothing here says all mathematics should split into handwritten work versus tool work, or that every gateway quantitative task deserves a central hot row. The archive is still making a bounded claim about a small reuse scope where current public exam-family rules already publish the difference.

## What the archive is **not** doing yet

The archive is still refusing three wider moves:

- it is **not** publishing one inherited hot quantitative row for all calculator-expected assessment families;
- it is **not** publishing one inherited graphing / CAS / modeling row across school, higher-ed, and professional-gate mathematics;
- it is **not** deciding the first modality-, age-, sector-, or exam-family child splits for the still-local hot decoding and hot final-writing branches.

## Current archive bet

The archive's current best guess is that the first truthful residue split inside the only slightly portable hot direct-production mathematics branch is a **tool-family split**.

`SR-MATH-PROC-01A2A` now names the thin inherited branch the archive was already implicitly pointing at: hotter symbolic procedure inside publicly declared no-calculator / no-executor families. `SR-MATH-PROC-01A2B` and `SR-MATH-PROC-01A2C` keep calculator-expected and tool-integrated quantitative families outside that inheritance for now.

That claim is now canon, but still live. The next narrower problem is no longer whether the hot no-executor mathematics residue needs any tool-family split at all; it is where the still-local hot decoding and hot final-writing branches deserve their first modality-, age-, sector-, or exam-family child splits, and whether any calculator-expected quantitative family eventually deserves a reusable hot row of its own rather than permanent tool-family-local handling. See `OQ-0005`.
