# Real pilot-record import and normalization workflow

The archive now has realistic service records, but it still does not contain real pilot records.
This surface defines the import lane so the first real records can be tested without turning raw
exports, support notes, logs, or marketing copy into canonical evidence.

## Import stance

Real-record import is a **staging process**, not a paste operation. A local pilot packet may contain
protected details, raw learner traces, vendor claims, staff notes, support-route facts, and security
information that should never enter the public archive or the canonical service-record examples.

The first real import should answer: did real records change decisions, reveal missing fields, or
show that some fields are performative burden?

## Source truth classes

| Code | Meaning | Archive action |
|---|---|---|
| `SRC0` | realistic example or synthetic backtest | Allowed as example only; never evidence of effectiveness. |
| `SRC1` | operator-drafted pilot template | Normalize and review; do not treat as field evidence. |
| `SRC2` | pilot export or local record set | Stage, de-identify, map fields, and compare decision deltas. |
| `SRC3` | record-owner verified pilot packet | May support schema revision or public summary after redaction. |
| `SRC4` | learner/family/teacher-facing record confirmed against notice | Strongest import class, still subject to redaction and scope limits. |
| `SRCX` | conflicting, protected, or unsafe source | Quarantine; do not normalize into examples. |

## Import stages

| Stage | Name | Required output |
|---|---|---|
| `IMP0` | source inventory | List source systems, owners, fields, and protected/security exclusions. |
| `IMP0R` | minimum real-data request | Ask for the smallest owner-reviewed packet that can change a decision. |
| `IMP1` | source data dictionary | Name source-field meaning, sensitivity, owner review, and import action before mapping. |
| `IMP2` | de-identification and minimization | Remove learner identifiers, protected facts, raw traces, and exploit details unless a protected local owner keeps them outside the archive. |
| `IMP3` | field mapping | Use an import map from `examples/import-maps/` or a local equivalent. |
| `IMP4` | schema normalization | Produce a candidate service record with `source_record_status` and `source_record_confidence`. |
| `IMP5` | acceptance and reviewer calibration | Run the acceptance packet and resolve closure-critical disagreements. |
| `IMP6` | decision-delta review | Compare candidate against realistic examples and note which fields changed a decision. |
| `IMP7` | redaction-profile rendering | Generate audience-specific public summaries; suppress any protected or stale claim. |
| `IMP8` | schema or packet revision | Add only fields that prevented overclaiming, protected-route leakage, hidden authority, or learner harm. |
| `IMP9` | release-candidate closure check | Confirm the live queue, receipt, no-fake-import guard, and release-candidate state all agree. |

## Do not import

- raw learner prompts, chat transcripts, or private logs;
- diagnosis, disability, accommodation, language-access, immigration, hardship, discipline, or
  counselling details;
- raw security exploit strings or tool-call payloads;
- vendor marketing phrases as evidence claims;
- small subgroup metrics that could identify learners or protected status;
- old public claims whose evidence clock is stale or expired.

If those facts matter to safety, they remain in local protected or security records and are
represented in the service record as owner, route, stop trigger, or redaction profile.

## Import map contract

`examples/import-maps/lms-pilot-export-normalization-map.json` is a template, not a real export. It
shows how to map local pilot fields into the canonical record while naming manual-review fields and
fields that must not be imported.

A source data dictionary should precede the import map. It states what each local field means, its
sensitivity, and whether it can be mapped, abstracted, kept local, quarantined, or ignored. See
[`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md).

Every import map must include:

- source system and owner;
- target schema version;
- source truth class;
- field mappings for the required top-level service-record objects;
- manual-review fields;
- do-not-import fields;
- redaction-before-commit steps;
- stop conditions;
- the decision-delta questions to answer after normalization.

`tools/check_import_maps.py` verifies the shipped map structure.



## Minimum real-data request and negative fixture preflight

Before requesting a pilot export, use [`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md).
It asks for source provenance, owner-reviewed aggregate metrics, action authority, public-summary
limits, protected/security exclusions, and decision-delta questions rather than raw learner logs.

Before accepting a candidate import, use
[`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md).
The fixture set checks that fake source elevation, protected-route leakage, hidden authority, unsupported
public claims, missing calibration, security payloads, and decision-neutral field creep still fail.

## Readiness manifest preflight

Before any real record is normalized, create or update an import-readiness manifest in
`examples/import-readiness/`. The manifest must state the current `IR0-IR6` readiness state, source
truth class, import map, protected exclusions, decision-delta requirements, and stop conditions.

A manifest can show that the lane is prepared. It does not close `FT-0181` unless it permits closure
from an `SRC2+` source and the queue state matches that claim. See
[`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md).

## Acceptance and decision-delta review

The first real import must pass an acceptance and reviewer-calibration packet before `FT-0181` can
close. The acceptance packet checks source class, dictionary, minimization, schema validation,
decision-delta evidence, public rendering, calibration, and field pruning. See
[`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md).

The first real import must also write a decision-delta note before it changes schema or public examples.
Fields that changed action authority, memory, evidence grade, construct proof, public summary,
rollback, appeal, or protected-route safety may be kept or promoted. Fields that are merely present
in a local export should stay local or be trimmed.

See [`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md).

## Current status of FT-0181

`FT-0181` remains queued. rev0219 supplies the import workflow, schema source-status fields,
redaction profiles, sector adapters, import-map validation, an import-readiness manifest, source
data-dictionary validation, acceptance and reviewer-calibration checks, decision-delta pruning rules,
a minimum real-data request packet, negative import fixtures, a release-candidate open-item freeze,
a no-fake-real-import guard, evidence-watchlist validation, public-summary render smoke tests,
operator handoff, lifecycle/deprecation decision records, evaluator-independence controls, and
closeout-board minutes. No actual local pilot record was available in this session. Closing
`FT-0181` requires at least one `SRC2` or stronger record set, a source dictionary, an acceptance
packet, a decision-delta note, a negative-fixture pass, render checks, a lifecycle decision, a
closure-ready readiness manifest, and closeout-board minutes.

## Current archive bet

Real records should make the schema smaller and sharper, not merely larger. The import lane is
successful when it deletes fields that do not change decisions and adds only fields that prevent
hidden authority, overclaiming, protected-route leakage, or learner harm.

See
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md),
[`service-record-backtest-results-and-field-trim.md`](service-record-backtest-results-and-field-trim.md),
[`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md),
[`sector-adapters-for-service-record-schema.md`](sector-adapters-for-service-record-schema.md),
and `AS-0224`, `AS-0233`, `AS-0234`, `AS-0235`, `AS-0236`, `AS-0237`, `AS-0238`, and `AS-0239`.


## Rev0233 decision-board handoff

After the owner packet workbench accepts or blocks a packet, use [`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md) before changing public summaries, lifecycle records, schemas, validators, or closure artifacts.


## FT-0181 post-board change rule

For the first `FT-0181` packet, normalization is not finished when the record validates. After the owner packet workbench and first-packet decision board, write the post-decision change ticket before service-record, public-summary, lifecycle, schema, validator, or closeout changes. The ticket is the overreach brake: it names allowed changes, prohibited changes, public claim ceiling, rollback owner, rollback triggers, and why `FT-0181` remains live unless a real `SRC2+` closeout path is complete.


## Live-window boundary

If the post-decision ticket stages a bounded service change, normalization is not the final step. Fill the live-window stop and rollback card before real users, dates, tools, memory, source systems, or public claim language expand. The first live window should end with decision readouts and usually `completed_no_closure`, not `FT-0181` closure.
