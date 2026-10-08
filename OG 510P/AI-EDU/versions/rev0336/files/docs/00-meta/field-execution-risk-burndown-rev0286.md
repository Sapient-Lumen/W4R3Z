# rev0286 field-execution risk burn-down

## Highest remaining risks

The live rail is now narrower and more executable than the surrounding doctrine.
The largest completion risks are no longer missing policy language; they are
handoff failures where a local artifact can look like enough progress.

| Rank | Risk | rev0286 response |
|---|---|---|
| 1 | Terminal live-window card is treated as a readout or action dispatch. | Added `owner-live-window-readout` and router routing from terminal cards to the readout artifact. |
| 2 | Readout is treated as public language, service-record mutation, lifecycle movement, or closure. | Readout guard sets no-service/no-public/no-lifecycle/no-closure firebreaks and routes only to post-readout dispatch. |
| 3 | Nonterminal card receives an end-of-window readout. | Readout recorder rejects `staged` and `active` cards. |
| 4 | Aggregate claims exceed the source card. | Readout counts cannot fall below source card readout count and source truth must match the card. |
| 5 | New doctrine grows to compensate for no real owner packet. | The first action remains `make owner-field-next`; new work is executable scratch tooling, not another branch family. |

## What is now safer

A maintainer who reaches a terminal window state now has one concrete next
command rather than an open-ended instruction. The command produces a bounded
`live-window-readout.json` that preserves source-card hash lineage and stops at
post-readout dispatch.

## Still missing

No real owner has been contacted in this cloudtainer, no real CSV has been
received, no `SRC2+` packet has been imported, and no terminal real window has
occurred. The next true completion risk outside the archive remains field
execution: accountable route, human send, send log, contact clock, returned
owner CSV, bounded intake, and owner-reviewed activation.

## Bias rule

Do not add more doctrine because the readout gate exists. Run the router, execute
one emitted command, rerun the router, and stop whenever the current scratch
artifact says no evidence, no public claim, no lifecycle move, or no closure.
