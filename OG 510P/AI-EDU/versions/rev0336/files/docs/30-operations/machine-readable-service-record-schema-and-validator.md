# Machine-readable service-record schema and validator

This surface makes the service-intake packet checkable without turning the archive into a database
product. The schema is deliberately small: it validates that a service record has enough fields for
human review, public summary, renewal, and retirement. It does **not** validate that a local decision
is wise, lawful, pedagogically effective, or complete.

## Files

| File | Role |
|---|---|
| `schemas/ai-service-record.schema.json` | JSON schema for compact AI education service records. |
| `examples/service-records/*.json` | Realistic example records used for lint and backtesting. |
| `tools/check_service_records.py` | Validator for required fields, enumerated codes, public-summary limits, and high-risk invariants. |

Run:

```bash
python3 tools/check_service_records.py
```

The full lint suite runs the same check.

## Record families

The schema supports four overlapping record families.

| Family | When it applies | Extra check |
|---|---|---|
| ordinary pilot | any recurring AI service | owner, non-use case, fallback, stop trigger, and next review must exist |
| high-stakes service | assessment, eligibility, discipline, protected support, public benefit, or official records | record owner, contestability, and human fallback must be named |
| agentic workflow | queue, notification, write, tool, or workflow action | action ceiling, red-team date, rollback route, and incident reconstruction must exist |
| public-facing pilot | affected users receive a public summary | claim limits, optional/required status, human contact, alternative path, and last review must be present |

A single record may be all four.

## Minimum invariants

Every valid service record must include:

- an accountable institutional owner and educational owner;
- intended use and explicit non-use cases;
- the highest `AA0-AA6` action authority the workflow can actually exercise;
- the highest memory class and protected-record route, if any;
- claim-family evidence entries with `EV0-EV7`, expiry dates, and public claims to remove if weak;
- construct, cognitive-effort, disclosure, and proof fields when learner work or assessment is touched;
- accessibility, protected-route, and no-penalty fallback fields;
- security posture, red-team or abuse-test date where relevant, and rollback / incident routes;
- workload and hidden-labor fields;
- decision, stop triggers, next review, and learner-safe continuity plan;
- a public summary that does not expose protected facts when public summary is enabled.

## What the validator refuses

The validator fails records that do any of the following:

- omit the `public_claim_to_remove_if_weak` field from an evidence claim;
- make public claims while the public-summary object is incomplete;
- use `AA3` or higher without rollback and incident-reconstruction routes;
- use protected support without a named protected-route owner and non-misuse boundary;
- touch official records without contestability and a human record owner;
- claim launch or renewal without at least one stop trigger and a next review date;
- leave evidence-expiry dates blank or malformed.

## What the validator cannot prove

The schema cannot prove that evidence is strong, a construct map is valid, a public summary is
understood, or a legal compliance floor has been met. It only blocks records that are too thin to
review. Human owners still need the service-BOM, action-authority register, claim-family matrix,
construct crosswalk, security posture, and implementation stop rules.

## Schema posture

The schema should stay **conservative and boring**. Add a required field only when realistic
records show that the field changes a decision, prevents overclaiming, preserves a protected route,
or avoids learner harm. Otherwise keep the detail in the local packet, security report, legal note,
or evidence appendix.

## Current archive bet

A schema-backed record will help teams reuse the archive without copying long prose. The best use is
not automatic approval; it is automatic refusal of incomplete records.

See
[`ai-service-intake-and-decision-record-template.md`](ai-service-intake-and-decision-record-template.md),
[`service-record-backtest-results-and-field-trim.md`](service-record-backtest-results-and-field-trim.md),
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md),
[`../20-governance/evidence-expiry-and-renewal-clocks.md`](../20-governance/evidence-expiry-and-renewal-clocks.md),
and `B275`, `B276`, `B280`, `B281`.
## Rev0215 overlay

Schema version `1.1` adds `publication_and_adapters` so each record states:

- whether it is a realistic example, operator draft, template, pending real import, or imported real pilot record;
- the source-confidence class, so examples are not mistaken for field evidence;
- the sector adapters that apply;
- the public-summary redaction profiles available for publication;
- the default redaction profile; and
- the real-record import status.

The field is deliberately about provenance and publication safety, not approval. A valid `1.1` record
can still be rejected, narrowed, paused, or retired by human reviewers.


## Rev0216 import-readiness and rendering checks

Schema version `1.1` remains unchanged. rev0216 adds validation around the schema rather than
expanding it:

- `schemas/pilot-import-readiness.schema.json` documents the manifest used to prove an import lane is
  ready without claiming that a real import has happened;
- `tools/check_import_readiness.py` checks that `FT-0181` cannot close from `SRC0` examples or `SRC1`
  templates;
- `tools/check_public_summary_renders.py` renders each service record through its referenced
  redaction profiles and checks for forbidden phrases, visible human-contact routes, and weak/stale
  claim phrases.

The schema stays boring; the validators carry the next layer of operational honesty.

## Rev0217 import-calibration checks

Schema version `1.1` still remains unchanged. rev0217 adds more checks around the schema instead of
promoting pre-import process fields into every service record:

- `schemas/pilot-source-data-dictionary.schema.json` and `tools/check_import_data_dictionaries.py`
  validate source-field meaning, sensitivity, owner review, and import action before field mapping;
- `schemas/real-import-acceptance.schema.json` and `tools/check_real_import_acceptance.py` validate
  acceptance packets, reviewer calibration, closure blocks, and `FT-0181` closure conditions;
- `tools/check_no_fake_real_import.py` blocks service records from claiming real pilot import status
  unless closure-ready readiness and acceptance gates exist;
- `schemas/external-evidence-watchlist.schema.json` and `tools/check_evidence_watchlists.py` keep
  external evidence updates tied to bibliography ids and affected archive surfaces.

The service-record schema should not absorb every operational preflight artifact. Dictionaries,
acceptance packets, readiness manifests, and watchlists stay separate so real records can be imported
honestly without making every ordinary service record heavier.
