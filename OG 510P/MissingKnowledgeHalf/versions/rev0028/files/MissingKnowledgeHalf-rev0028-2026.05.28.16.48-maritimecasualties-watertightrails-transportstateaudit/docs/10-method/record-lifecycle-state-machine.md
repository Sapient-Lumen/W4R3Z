# Record lifecycle state machine

Revision: `rev0002`

This document makes explicit the state machine implied by the seed-spine archive.

## States

```text
seed_mention
  → candidate
  → source_located
  → source_captured
  → extracted
  → reviewed
  → promoted_record
  → linked_record
  → pattern_eligible
  → synthesized
```

Optional exits:

```text
candidate → rejected_with_reason
source_located → insufficient_source
promoted_record → contested
promoted_record → superseded
promoted_record → retired
```

## Gate rules

### seed_mention

A phrase or example exists in the seed document or conversation. It is not a factual record. Promotion requires a named candidate ID and a reason to pursue it.

### candidate

The archive has decided a topic is worth investigating. It still makes no factual claim beyond "worth sourcing." Promotion requires source search.

### source_located

At least one plausible source exists. Promotion requires a source record with permanence fields: identifier, URL or archive pointer, retrieval date, evidence class, copyability, and extraction note.

### source_captured

The source has been captured or stably pointed to. Promotion requires extraction into claim, event, incident, influence, or source fields.

### extracted

Fields have been filled from sources, but the record has not been stress-tested. Promotion requires review for status, ethics, source dependence, and missing counter-sources.

### reviewed

The record has survived a second pass. Promotion requires a revision receipt entry and explicit statement of what would change the record.

### promoted_record

The record can be used as corpus content. It is still corrigible. Next work: link to claims, sources, related cases, genealogy, practice lag, and patterns.

### linked_record

The record participates in the graph. Pattern promotion becomes possible only when multiple linked records justify the pattern.

## Why this matters

The project will contain attractive examples that feel familiar. Familiarity is dangerous. The state machine prevents the archive from confusing cultural fame with evidence.
