# REV0106 audit — evidence-summary obligation refactor

## What moved

`tools/validate_archive.py` no longer owns the full evidence-summary semantics block. The following responsibilities moved to `tools/evidence_summary_semantics.py`:

```text
evidence class catalog consistency
forbidden obligation evidence-class lookup
evidence summary minimum-item checks
redacted external-reference semantic guardrails
evidence input duplicate/name checks
obligation reference checks
met-obligation evidence usability checks
non-provenance guard checks
assessment/evidence-summary conclusion binding checks
```

The validator still supplies the schema callback for embedded `redacted-external-evidence-reference` validation.

## Why this was worth doing

Evidence summaries are a high-leverage boundary: they are retained, replayed, queried through discovery, and referenced by authorized-verifier challenges. A `result: met` statement is only meaningful when its cited evidence is actually usable. This revision hardens that boundary without creating new profile vocabulary or registry machinery.

## New invariant

A met obligation result must not rely on evidence whose item state contradicts the met result:

```text
presence must be present
value_state must not be ignored/conflicting/withdrawn
used_for must not be not_used
redacted evidence must have a salted commitment
```

## Regression strategy

The new negatives are patch-derived from a known-good P3 satisfied evidence summary. This reduces copy-drift: each fixture differs by one usability defect plus a note.
