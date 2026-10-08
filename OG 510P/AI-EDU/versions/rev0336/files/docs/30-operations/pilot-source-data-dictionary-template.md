# Pilot source data-dictionary template

Real pilot import needs a source dictionary before field mapping. The dictionary is not a second
schema and it is not a data dump. It is the short owner-reviewed description of what each local
export field means, whether it is safe to normalize, and which decision it could affect.

The core rule: **unknown source fields do not enter the service record**. They are mapped only after
the record owner, support owner, or security owner can say what the field means and whether it
belongs in the public archive, a protected local route, a security quarantine, or nowhere.

## Dictionary states

| Code | Meaning | Import effect |
|---|---|---|
| `DDICT0` | No source dictionary | Do not normalize real records. |
| `DDICT1` | Operator-drafted field list | May prepare an import map; cannot close `FT-0181`. |
| `DDICT2` | Record-owner reviewed dictionary | May map low-risk fields into a candidate service record. |
| `DDICT3` | Protected/support/security review complete | May normalize with protected and security exclusions applied. |
| `DDICT4` | Dictionary has changed after pilot export | Re-run field mapping and decision-delta review. |
| `DDICTX` | Conflicting, unsafe, or legally constrained dictionary | Quarantine source; do not normalize. |

## Required field classifications

Every local field should be assigned one of these import actions:

| Import action | Meaning |
|---|---|
| `map` | Field may map into a public service-record field after minimization. |
| `abstract` | Field may be represented only as a high-level owner, route, risk, or stop trigger. |
| `keep_local` | Field may matter operationally but must remain in the local protected or operational record. |
| `quarantine` | Field contains protected facts, raw learner traces, exploit details, or conflicting meaning. |
| `ignore` | Field is descriptive, duplicated, stale, or decision-neutral. |

Sensitivity is not binary. A field can be safe in one sector and unsafe in another. Use sector
adapters before publishing summaries for minors, credit-bearing work, public-route recognition, or
protected support.

## Minimal dictionary columns

| Column | Required content |
|---|---|
| source field | Local export field or packet section. |
| meaning | Plain-language meaning and owner interpretation. |
| sensitivity | `public`, `internal`, `protected`, `security`, or `unknown`. |
| import action | `map`, `abstract`, `keep_local`, `quarantine`, or `ignore`. |
| target field | Candidate AI-EDU field, if mapped or abstracted. |
| decision relevance | Which authority, evidence, proof, redaction, continuity, or stop decision could change. |
| owner review required | Record owner, support owner, security owner, assessment owner, or none. |
| notes | Known ambiguity, expiry, or local-only handling. |

## Hard stops

A dictionary blocks import when any of these are true:

- a required source field is `unknown` and would affect authority, memory, evidence, proof, or public
  notice;
- a protected support fact would be mapped as ordinary authorship, misconduct, or performance data;
- a raw learner trace, prompt, chat transcript, diagnostic fact, discipline fact, counselling fact,
  or exploit string is marked `map`;
- owner meaning conflicts across source systems;
- the source owner cannot distinguish vendor-generated fields from local review fields.

## Relationship to import maps

The data dictionary answers **what the source fields mean**. The import map answers **where permitted
fields go**. A real import should have both. If the import map exists without a dictionary, the
archive can still show readiness, but it cannot honestly claim that a real record has been safely
normalized.

## Current archive bet

The first real import is more likely to fail because a field is misunderstood than because the JSON
schema lacks a property. Small dictionaries prevent large false claims.

See [`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md),
[`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
and `AS-0229`.
