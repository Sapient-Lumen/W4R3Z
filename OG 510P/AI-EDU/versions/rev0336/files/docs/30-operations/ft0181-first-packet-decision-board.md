# FT-0181 first-packet decision board

Use this only after the owner packet workbench and a bounded [`ft0181-workbench-review-record.md`](ft0181-workbench-review-record.md) output. In rev0276 this board must be recorded through `make owner-first-packet-decision ...`, producing a scratch-local `first-packet-decision.json` before any post-decision change ticket. The owner workbench answers whether a packet can land; the review record preserves the bounded local route; this board answers what the packet is allowed to change. The post-decision change ticket then states the exact reversible edit, prohibition, rollback owner, and public-claim ceiling before any lifecycle or public-summary change occurs. A live-window card is required before that edit reaches real users or public-facing operation.

The board is deliberately small. Its goal is to prevent the first real packet from becoming another
intake form, another schema-expansion excuse, or a vague "looks fine" note. A packet is useful only
when it changes a decision, blocks a decision, or proves that a field should not be requested again.

## Entry rule

Open this board only after these five facts are known:

| Fact | Minimum answer |
|---|---|
| selected service | `AIEDU-SR-003` capped reminder workflow by default, `AIEDU-SR-001` fallback, or reserved `AIEDU-SR-004` only with aggregate no-trace evidence |
| source posture | source class claimed by owner, with no `SRC2+` closure unless a real owner-reviewed record exists |
| transfer posture | raw learner traces, protected facts, small cells, and raw security payloads are excluded or kept local |
| packet disposition | a `workbench-review.json` decision exists and is `PROCEED-DECISION-BOARD` |
| review boundary | review state remains `REVIEWED_NOT_ACCEPTED`, acceptance remains `NOT_ACCEPTED`, and the review copies no owner answers |

If any fact is missing, do not write a lifecycle decision or run `owner-first-packet-decision`. Return to the owner workbench and record a bounded workbench review decision: `REASK-OWNER`, `BLOCK-OVERBROAD`, `BLOCK-PROTECTED`, `BLOCK-SECURITY`, `BLOCK-EVIDENCE`, or `NO-CHANGE-TRIM`.

## Five decision slices

Complete one row per slice. The answer can be `no change`, but it cannot be blank.

| Slice | Question | Allowed outputs |
|---|---|---|
| authority | Did the packet change what the service can do, send, write, queue, remember, or roll back? | keep lower ceiling, revise ceiling, block, or no change |
| evidence | Did the packet change a learning, task, workload, safety, access, compliance, or implementation-burden claim? | suppress, downgrade, keep example-only, stage claim with expiry, or no change |
| construct | Did the packet change unaided work, answer-giving, proof, disclosure, or cognitive-effort posture? | add stop trigger, keep teacher review, require unaided segment, fall back service, or no change |
| public | Did the packet change notice, summary, forbidden phrase, redaction profile, or audience adapter? | publish limited, revise claims, suppress, draft only, or no change |
| lifecycle | Did the packet justify sandbox, pilot, watch, deprecate, archive-only, or quarantine treatment? | sandbox, pilot, watch, deprecate, archive-only, quarantine, or no change |

## Packet outcome to decision action

Use this table before touching examples, public summaries, or lifecycle records.

| Workbench outcome | Board action | Public claim action | Schema action | `FT-0181` posture |
|---|---|---|---|---|
| `PROCEED-STAGED` | write all five slices and stage acceptance only if `SRC2+` is real | draft or revise only within evidence family | keep existing fields unless `DD2-DD6` changed a decision | live until acceptance and closeout pass |
| `FALLBACK-SERVICE` | write why the fallback is safer than the default reminder-workflow packet, or why hint-tutor evidence is already aggregate/no-trace | suppress tutor learning claim | do not add fields from a harder service | live; selected service changes |
| `BLOCK-OVERBROAD` | record the minimum packet the owner must resend | no new claim | no schema change | live; return to owner |
| `BLOCK-PROTECTED` | record local protected-route owner only | suppress ordinary public summary | no protected facts in examples | live; keep local or quarantine |
| `BLOCK-SECURITY` | record class, owner action, and safe degradation only | suppress technical details | no payload fields | live; keep local or quarantine |
| `BLOCK-EVIDENCE` | record which claim family is unsupported | remove or downgrade claim | no evidence-field expansion | live; request stronger method or weaker claim |
| `NO-CHANGE-TRIM` | record trimmed fields and future request deletion | no new claim | remove field from future packet request if repeated | live; reduce burden |

## One-hour review run sheet

This is the default first real-packet meeting structure.

| Minute | Work |
|---|---|
| 0-10 | Confirm one service, one owner path, one date range, one source system, and no prohibited transfer. |
| 10-20 | Assign each received field to `SURVIVE-*`, `LOCAL-ONLY`, `TRIM`, or `RE-REQUEST`. |
| 20-35 | Fill the five decision slices and name the before/after decision for each changed slice. |
| 35-45 | Decide public summary action and claim-family evidence grade; suppress unsupported claims. |
| 45-55 | Decide lifecycle posture and whether any schema, validator, or request-field change is justified. |
| 55-60 | Record unresolved blocks, next owner question, and why `FT-0181` does or does not remain live. |

## Exit to change ticket

After the five slices are filled, record the local `first-packet-decision.json`, then write [`ft0181-post-decision-change-ticket.md`](ft0181-post-decision-change-ticket.md) before changing service records, public summaries, lifecycle state, schemas, validators, or closeout posture. A valid board without a change ticket can inform review, but it cannot authorize a concrete change.

The ticket should be small: allowed changes, prohibited changes, public claim ceiling, rollback owner, rollback triggers, and closure boundary. If the ticket cannot name those items, record `blocked_incomplete_board`, suppress the change, and keep `FT-0181` live.

## Decision-delta mini-table

Copy this into the acceptance packet, closeout board, or maintainer note.

```text
Packet ID or owner meeting note:
Selected service:
Workbench outcome:
Source truth class:
Reviewers present:

Authority before -> after:
Evidence claim before -> after:
Construct/proof before -> after:
Public summary before -> after:
Lifecycle before -> after:

Fields kept:
Fields trimmed:
Fields local-only or quarantined:
Fields re-requested:

Next owner question:
Reason FT-0181 remains live or can proceed to closure review:
```

## Schema and validator restraint

Do not add a schema field, validator, or registry row because the first packet contains a field.
Add one only if the decision-delta log shows a `DD2-DD6` effect and the same issue cannot be handled
by a local note, trim rule, public-claim downgrade, or lifecycle decision.

A single first packet may justify removing a future request field when the field is plainly
burdensome and decision-neutral. A single first packet should not harden a new required field unless
it prevents hidden authority, overclaiming, protected-route leakage, raw security import, or learner
harm.

## Closure boundary

This board can turn a landed packet into a decision path. It cannot create `SRC2+` evidence, cannot
replace owner review, cannot close `FT-0181`, and cannot prove learning, safety, access, workload
reduction, compliance, or service effectiveness.
