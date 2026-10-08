# FT-0181 first pilot sprint execution pack

This surface converts the ready-but-not-closed import lane into the smallest real action that can
move `FT-0181`. The copyable execution handoff lives in
[`ft0181-owner-import-action-kit.md`](ft0181-owner-import-action-kit.md). The first
sendable owner ask is [`ft0181-eight-row-owner-reply-sheet.md`](ft0181-eight-row-owner-reply-sheet.md) plus the fillable CSV template `templates/ft0181-eight-row-owner-reply-template.csv`, with explanatory fallback in [`ft0181-owner-field-request-and-micro-packet.md`](ft0181-owner-field-request-and-micro-packet.md),
and the arrival review begins only after receipt in
[`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md).
It is not another approval layer. It tells the maintainer which single pilot to request first, what
to collect, what to refuse, and how to decide whether a field survives contact with real records.

## Default target

Start with **one service, one owner path, one date range, one minimized `SRC2+` packet, and the lowest-friction service that can prove the import pipeline.**

| Candidate | Why it might be first | Why it might not be first | Rev0242 posture |
|---|---|---|---|
| `AIEDU-SR-003` capped assignment-reminder workflow | Staff-facing, draft-only, reversible, and measurable with aggregate reminder, discard, correction, fallback, incident, and review-time counts. It tests action authority without asking first for raw learning traces. | Roster/submission status can become learner-level surveillance or penalty infrastructure if the owner asks for rows or full exports. | **Default first contact.** Send the eight-row owner reply sheet and keep it aggregate-only. |
| `AIEDU-SR-001` advising navigation assistant | Can provide aggregate correction, route, and fallback counts without proving a learning claim. | Record, deadline, aid, credit, and eligibility adjacency can make the first packet too high-stakes. | Fallback only if it can stay aggregate, no protected-route facts, no deadline/credit/aid decision details. |
| `AIEDU-SR-004` middle-school hint tutor sandbox | Tests the archive's hardest substantive claim: hints must preserve independent effort and show learning signal, not just usage. | Minor-facing data raises privacy, consent, family-notice, small-cell, and raw-trace risk. | Reserved for later unless a teacher owner already has an aggregate no-trace packet ready. |
| `AIEDU-SR-002` accessible-format support assistant | Tests protected-route separation. | Protected support facts are exactly what should stay out of the archive. | Do not use as first import unless the support office owns a fully abstracted packet. |

The preferred first target is therefore `AIEDU-SR-003`, not the hint tutor. This is a substance-over-doctrine correction: the first real import should prove the pipeline with the safest real packet, not prove the hardest learning claim first. Use [`ft0181-first-contact-reminder-workflow-packet.md`](ft0181-first-contact-reminder-workflow-packet.md) as the first contact.

If the reminder-workflow owner can only provide raw roster rows, full LMS dumps, gradebook screenshots, message bodies, protected-route facts, or vendor telemetry, block or fall back to `AIEDU-SR-001`; do not widen the request and do not switch to `AIEDU-SR-004` unless the teacher owner already has aggregate no-trace evidence.

## Rev0316 substance track

Keep `AIEDU-SR-003` as the first `FT-0181` owner-contact target because it is the safest import
packet. In parallel, stop letting the import rail consume all attention: prepare the
[`teacher-tutor-augmentation-micro-pilot.md`](teacher-tutor-augmentation-micro-pilot.md) as the
first learning-oriented cycle. It is not `FT-0181` evidence unless a real owner later returns an
accepted `SRC2+` packet, but it gives the archive a concrete pedagogical thing to run.

The priority split is now explicit:

| Track | Next real move | Claim boundary |
|---|---|---|
| `FT-0181` owner-contact rail | send or route-block the `AIEDU-SR-003` aggregate owner packet | proves nothing until real owner material returns |
| pedagogical substance rail | run or prepare `AIEDU-SR-005` teacher/tutor move-coach micro-pilot | produces local owner judgment only; no public learning claim yet |

## Minimal packet to request

Ask the record owner for the eight-row reply sheet or its fillable CSV twin and nothing broader. Use the owner packet workbench only after a packet returns. The request is capped by the packet ceiling in `examples/real-data-requests/ft0181-minimum-real-data-request.json`.

| Field | Acceptable form | Refuse |
|---|---|---|
| service/source/date | service, accountable owner path, source system or local record set, and one short date range | multiple services, merged data lake, or technical export prerequisite |
| aggregate workflow counts | eligible, draft-reminder, human-sent if any, discarded/corrected, fallback/manual-route, and incident count above thresholds | named rows, screenshots, small cells, or gradebook rows |
| action boundary | draft-only, no automatic send, no durable write, no penalty, and no protected-status inference | uncertain authority boundary or product brochure as evidence |
| fallback/rollback/stop | human fallback, rollback owner, incident class labels if any, and one stop condition | vendor-only rollback or incident detail requiring raw payloads |
| workload | one workload signal or explicit unknown, with method note if known | staff-surveillance residue or unreviewed “time saved” claim |
| guidance | training or use-guidance note, or explicit unknown | broad compliance claim unsupported by owner-held records |
| public claim ceiling | language the owner would be comfortable saying now without learning/safety/access/workload/compliance/scale/effectiveness claim | testimonial, marketing, or unsupported effectiveness claim |
| redaction and attestation | assertion that raw/protected data stayed local and packet is real operational material | mock, rehearsal, vendor-only, or owner-unreviewed analytics export |

## Sprint sequence

| Step | Action | Output | Stop if |
|---|---|---|---|
| `SP0` | Name the pilot lane and owner. | one service ID, one record owner, one service owner, one reviewer pair | ownership is ambiguous |
| `SP1` | Send the eight-row owner reply sheet or fillable CSV. | one sendable request with source class `SRC2` or stronger | the owner says raw traces or a full export are required |
| `SP1.5` | If a CSV returns, run `python3 tools/receipt_owner_reply_csv.py returned-owner-reply.csv --output scratch/field/ft0181/owner-reply-receipts/returned-owner-reply.receipt.json`, then `python3 tools/triage_owner_reply_csv.py returned-owner-reply.csv --json` and follow `next_action`. | local receipt plus workbench, one re-ask, or outcome note selected | any survivor row is copied before receipt/triage or outside the router |
| `SP2` | Build the source data dictionary before mapping. | field meanings, sensitivity, import action, and owner review | field meaning is unknown or protected details are needed |
| `SP3` | Stage the packet in custody, then map fields. | normalized candidate and do-not-import list | protected route, security payload, or small-cell leakage appears |
| `SP4` | Run acceptance, public render, lifecycle, and decision-delta review. | reviewer-calibrated accept/reject/narrow decision | reviewers disagree on closure-critical source class or claim grade |
| `SP5` | Trim the schema-facing record. | keep only fields that changed a decision; mark others optional, local, or pruned | the import mostly proves that the request was too broad |
| `SP6` | Decide queue posture. | closeout remains not-ready, or `FT-0181` closure packet becomes eligible | any required closure evidence remains missing |

## Field survival rule

A real field survives only if it changes at least one of these decisions:

| Decision changed | Example surviving field |
|---|---|
| action authority or rollback | unauthorized reminder-send attempt, rollback success, human-click boundary |
| evidence grade or expiry | transfer result, delayed-check result, reviewer-calibrated workload method |
| construct or cognitive effort | hint-before-attempt rate, independent-attempt requirement failure |
| public claim | opt-out or no-learning result that removes a broad public claim |
| protected-route separation | confirmation that support facts stayed out of ordinary metadata |
| safety or security stop | answer-giving, prompt-injection success, leakage class, false penalty class |

Fields that merely make a local export look complete should be pruned or left local. The first real
import should make the schema smaller and sharper, not larger and more ceremonial.

## Claim minimums for the first import

| Claim family | Minimum evidence that can move the claim | Non-evidence |
|---|---|---|
| `CL-LEARN` | aggregate transfer, delayed check, misconception correction, or teacher-rated independent explanation sample | usage, satisfaction, or answer volume |
| `CL-TASK` | completion, false reminder, error, or turnaround measure with fallback count | “worked well” summary |
| `CL-WORKLOAD` | preparation plus review plus correction time, not just drafting time | gross time saved without rework |
| `CL-ACCESS` | fallback use, opt-out, accessibility issue, no-penalty route, or aggregate subgroup access above threshold | protected support details |
| `CL-SAFETY` | incident class counts and stop-trigger result | no incidents reported without reporting route |
| `CL-SECURITY` | prompt-injection, excessive-agency, tool-boundary, or rollback result | moderation policy alone |
| `CL-CONTEST` | correction/appeal availability, response time, reversal or no-penalty result | generic support email |

## Why this is the current priority

Recent state-guidance analysis suggests many education systems are still exploratory and only some
are moving toward systematic evidentiary evaluation; the first import should therefore be a local
feedback loop, not a scale claim. Federal education guidance continues to allow AI uses inside
existing statutory and regulatory constraints, and 2026 federal priority language emphasizes
accessibility and universal design. For minor-facing or mixed-age tools, children's privacy and
retention/deletion expectations make the aggregate-only packet more than a preference. See `B284`,
`B285`, and `B286`.

## Closure boundary

Completing this sprint pack does **not** close `FT-0181`. It is only the route to obtain the real
`SRC2+` material that the existing closure checklist requires. If no owner-reviewed packet arrives,
the correct result is still: ready to import, not closure-ready.

See
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md),
[`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md),
[`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md),
[`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
[`ft0181-closure-evidence-checklist.md`](ft0181-closure-evidence-checklist.md),
`FT-0181`, `OQ-0103`, `AS-0233`, `AS-0234`, `AS-0274`, `AS-0275`, and `AS-0276`.


## Field survival shortcut

Before adding a received field to any schema or public example, classify it through the survival
sheet in [`ft0181-owner-import-action-kit.md`](ft0181-owner-import-action-kit.md). Keep fields that
change authority, evidence, construct, public claims, protected-route safety, security handling,
access, or burden. Leave local-only facts local. Trim fields that merely arrived because a local
export happened to contain them.

## Rev0249 local receipt correction

The request record selects `AIEDU-SR-003` as the default first contact and carries an `outreach_preflight` plus `owner_reply_intake` guard. Rev0249 keeps outcome-specific next-action routing and adds a local receipt/fingerprint before staging, so returned CSVs are fingerprinted without copying raw answers and then land in a minimized note before the workbench, the one re-ask message, or the outcome-note template before any larger gate opens. The first ask remains sendable, staff-facing, draft-only, aggregate, answerable in about ten minutes, and not dependent on a technical export owner. It should not request completed downstream artifacts such as a workbench, decision board, live-window card, readout, closeout minutes, or signoff quorum. Those gates remain necessary after a real packet returns; they are not owner-send fields.


## Rev0251 workbench seed note

If the owner returns the fillable CSV, first run `make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply` from the same scratch root that contains the active contact-status clock, then execute only its emitted `make owner-reply-intake ... SOURCE_CONTACT_STATUS=...` command before any workbench copy/paste. If the bundle returns `PROCEED-STAGED`, rerun `make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake` and execute only the emitted workbench-seed command. The bundle and seed keep receipt, triage, hashes, source-contact-status trace, and the routed local artifact together in scratch or an external local path; they do not copy owner answers into metadata, accept evidence, close `FT-0181`, or support public claims.
