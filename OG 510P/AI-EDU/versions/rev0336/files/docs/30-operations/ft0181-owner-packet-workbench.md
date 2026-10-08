# FT-0181 owner packet workbench

This workbench is the thing to use only after the record owner returns the eight-row sheet or CSV and the first triage returns `PROCEED-STAGED`. It is deliberately
smaller than the full service-record schema. Its job is to turn one owner conversation into either a
safe `SRC2+` packet, a recorded fallback, or a useful block.

Use it with [`ft0181-owner-import-action-kit.md`](ft0181-owner-import-action-kit.md). Do not ask the
owner for a broad export first.

## Before opening the long form

Do not paste a returned CSV or email table directly into the full owner packet form. If the reply is a CSV, use the bounded intake bundle first:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
# then execute the emitted make owner-returned-reply-work ... SOURCE_CONTACT_STATUS=... command
```

The returned-reply work session writes a content-minimized receipt, triage JSON, source-contact-status trace, and exactly one routed local artifact: `proceed-staged.md` for `PROCEED-STAGED`, or `outcome-note.md` for `RE-ASK-ONCE`, block outcomes, and `NO-OWNER-PACKET`; when it proceeds, it also creates a `NOT_ACCEPTED` workbench seed and a review brief. The bundle output is local/scratch only; it is not SRC2+ acceptance, closure evidence, or public-summary support. Only a generated `proceed-staged.md` from a real owner reply tied to an active bounded contact clock opens this workbench. If the reply arrives as email text, apply the same eight-row checks manually. First triage the eight rows from [`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md) or `templates/ft0181-eight-row-owner-reply-template.csv`:

| Check | If yes | If no |
|---|---|---|
| Exactly eight row answers or explicit unknowns? | Continue. | `RE-ASK-ONCE` for one or two unclear rows; otherwise block. |
| Any raw learner, protected, small-cell, security payload, or vendor-only material? | Keep local, quarantine, delete, or abstract before workbench use. | Continue. |
| Service, owner, source, and date range named? | Continue. | `RE-ASK-ONCE` or `NO-OWNER-PACKET`. |
| Draft-only/no-write/no-penalty/no-protected-inference boundary confirmed? | Continue. | `BLOCK-AUTHORITY`. |
| Public claim ceiling process-only or weaker? | Continue. | Suppress claim and use weaker public language or `BLOCK-EVIDENCE`. |
| Any credentials, secrets, exploit strings, system prompts, tool payloads, or raw security details? | Quarantine locally and abstract only class/owner action if safe. | Continue. |
| Owner attests that the material is real operational evidence? | Continue. | `BLOCK-EVIDENCE`. |

Only surviving rows from a generated proceed-staged note based on a real owner reply move into the workbench; the local receipt and workbench seed may be cited by hash but should not contribute answer text. Rev0295 adds a review-brief bridge before [`ft0181-workbench-review-record.md`](ft0181-workbench-review-record.md): after a valid `NOT_ACCEPTED` seed, the router now requires a scratch-local review brief and then a human-entered `workbench-review.json` before the first-packet decision board or one workbench-sourced re-ask. Smoke harness output, intake outputs, staging outputs, workbench seeds, and workbench reviews must not be written into archive-controlled directories, copied into evidence custody, or treated as acceptance without later gates. Extra local context stays local unless it changes a named decision.

## Packet rule

The first packet must fit on this page before any source file moves.

| Slot | Required answer | Block if |
|---|---|---|
| selected service | `AIEDU-SR-003` by default, fallback `AIEDU-SR-001`, or reserved `AIEDU-SR-004` only with aggregate no-trace evidence | more than one service is needed to explain the pilot |
| owner path | record owner plus service owner, or one person explicitly serving both roles | nobody can answer field meaning and action authority |
| date range | one short date range | the owner can only describe an indefinite rollout |
| source system | one system or local record set | the packet requires a merged data lake or vendor dump |
| source truth | `SRC2` or stronger before closure review | source is only a template, memory, or vendor claim |
| raw learner data | absent | prompts, chats, essays, screenshots, names, IDs, or recordings are needed |
| protected facts | absent from archive packet | accommodation, diagnosis, support, discipline, hardship, or family facts are mixed in |
| security payloads | abstract class labels only | prompts, exploit strings, keys, tool calls, or payloads are needed |
| public claim | limited to what the packet can support | the owner wants to say the service improves learning, safety, access, or workload without method |

## Owner packet form

Copy this into the owner meeting note or source-intake ticket. Leave unknown fields blank rather than
inventing them.

```text
FT-0181 FIRST OWNER PACKET

Selected service ID:
Fallback service ID used? yes/no:
Source system or local record set:
Date range:
Record owner role:
Service owner role:
Reviewer roles present:
Source truth class claimed by owner:

What the service was allowed to do:
What the service was not allowed to do:
Human owner and rollback route:
No-penalty or fallback route:

Aggregate participation count:
Aggregate opt-out count:
Aggregate fallback or correction count:
Aggregate incident / stop-trigger count:
Aggregate learning or task signal, if any:
Method note for the signal:
Workload estimate with preparation, review, correction, and escalation separated:

Public notice or summary text currently used:
Public claims the owner is willing to remove if evidence is weak:

Fields kept local before transfer:
Fields trimmed because they do not change a decision:
Fields needing re-request because meaning, date range, owner, or source class is unclear:

Reason the packet can proceed:
Reason the packet must fall back, block, or stay local:
```

## Arrival triage

Triage the received packet before mapping it to any schema or public example.

| Question | Pass | Fallback | Block |
|---|---|---|---|
| Is there exactly one selected service? | Continue. | Keep capped reminder first; fall back to advising if reminder rows would expose roster/gradebook/message data; reserve hint tutor unless aggregate no-trace evidence is already ready. | Refuse multi-service packet. |
| Can the owner explain actual authority? | Map authority and rollback. | Use lower authority ceiling. | Block if hidden sends, writes, penalties, or record effects cannot be reconstructed. |
| Can evidence stay aggregate? | Map only the aggregate signal. | Use task or workload signal only. | Block if raw learner work, small cells, or protected cuts are required. |
| Are protected facts separated? | Record abstract protected-route owner only. | Keep support office note local. | Quarantine if protected facts entered ordinary service fields. |
| Are security details abstracted? | Map class, stop trigger, and owner action. | Keep technical evidence local. | Quarantine if raw payloads or credentials are present. |
| Does any field change a decision? | Keep and classify. | Re-request unclear field meaning. | Trim decision-neutral export residue. |

## Field-survival ledger

Every received field must get one row before it is promoted, trimmed, or left local.

| Source field or packet section | Survival class | Decision changed | Target or disposition | Owner/reviewer note |
|---|---|---|---|---|
| selected service ID | `SURVIVE-AUTHORITY` | identifies service and fallback | `record_id` or selected-service note | required |
| action ceiling | `SURVIVE-AUTHORITY` | changes authority and rollback | `authority.max_action_authority` | required |
| aggregate delayed check | `SURVIVE-EVIDENCE` | changes learning claim grade or expiry | `evidence_claims` | only if method is named |
| answer-giving count | `SURVIVE-CONSTRUCT` | changes stop trigger and construct posture | `decision.stop_triggers` | aggregate only |
| public notice text | `SURVIVE-PUBLIC` | changes public summary or forbidden claims | `public_summary` | redact before publication |
| protected support note | `LOCAL-ONLY` | may change protected-route owner | keep local or abstract owner only | no facts in archive |
| exploit excerpt | `LOCAL-ONLY` or `SURVIVE-SECURITY` | changes security class or stop trigger | class label only | no payloads in archive |
| vendor success quote | `TRIM` | no local decision change | do not import | not evidence |
| unclear local metric | `RE-REQUEST` | unknown | ask owner for meaning/method | do not map yet |

## First-review decision

After triage, pick one and record it plainly. Then use [`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md) to decide what the packet is allowed to change.

| Decision | When to use | What changes |
|---|---|---|
| `PROCEED-STAGED` | packet is one service, aggregate/minimized, owner-reviewed, and `SRC2+` | update custody, dictionary, map, acceptance, decision delta, and public-summary draft |
| `FALLBACK-SERVICE` | hint-tutor lane would require raw learner traces or small cells | switch to `AIEDU-SR-003` and treat it as an action-boundary import |
| `BLOCK-OVERBROAD` | owner can only provide a broad export | record block and do not widen request |
| `BLOCK-PROTECTED` | protected facts cannot be separated before transfer | keep local or quarantine; do not normalize |
| `BLOCK-SECURITY` | raw security payloads cannot be abstracted | quarantine; map only class/owner/stop trigger if safe |
| `BLOCK-EVIDENCE` | the signal is only usage, satisfaction, or vendor marketing | suppress learning, safety, access, workload, or effectiveness claims |
| `NO-CHANGE-TRIM` | fields arrive but do not change decisions | trim from future packet and keep `FT-0181` live |

## Reviewer mini-calibration

Use two reviewers when possible. For the first packet, the minimum useful split is:

| Role | Must be able to say |
|---|---|
| record or service owner | what each field means, where it came from, and whether raw/protected/security data was excluded |
| governance reviewer | which fields changed authority, evidence, construct, public claim, rollback, or stop decision |
| protected-route reviewer, when needed | whether support facts stayed local and non-misuse boundaries still hold |
| security reviewer, when needed | whether payloads stayed local and only class labels/stop actions were recorded |

If reviewers disagree on source class, authority, protected facts, security handling, or public claim
limits, use the weaker/lower-risk posture and keep `FT-0181` live.

## Rehearsal outcomes to record even without a real packet

A dry run is useful only if it predicts the most likely field failure. Record one of these before the
next owner contact:

| Rehearsal finding | Correct next move |
|---|---|
| owner likely sends a full LMS or vendor export | send the one-page form again; block broad export |
| owner has only usage or satisfaction counts | treat as task/workload context, not learning evidence |
| teacher has useful observations but only in raw student work | ask for aggregate review summary or fallback service |
| support facts are mixed into ordinary logs | stop and route to protected owner before any archive mapping |
| security evidence requires raw payloads | keep local; record risk class and owner action only |
| no one can name action ceiling | use lower authority ceiling or block until reconstructed |
| no public notice exists | record public-summary gap; do not infer family-facing approval |
| no second reviewer is available | acceptance may improve to `AC2`, but closure stays blocked |

## Closeout boundary

This workbench can upgrade lane readiness and acceptance rehearsal after a proceed-staged note exists. The next required local artifacts are a scratch-local workbench review brief and then a bounded [`ft0181-workbench-review-record.md`](ft0181-workbench-review-record.md) output after human review. Only a `PROCEED-DECISION-BOARD` review can open [`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md), which records authority, evidence, construct, public-summary, and lifecycle effects. None of these surfaces can close `FT-0181`, upgrade a source to `SRC2+`, or prove learning, safety, access, workload reduction, compliance, or service effectiveness.
