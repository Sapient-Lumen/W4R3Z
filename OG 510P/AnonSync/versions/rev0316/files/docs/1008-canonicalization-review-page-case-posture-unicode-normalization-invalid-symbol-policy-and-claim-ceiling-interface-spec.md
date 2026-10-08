# Canonicalization review page — case posture, Unicode normalization, invalid-symbol policy, and claim ceiling

## Purpose

Review the exact comparison and rewrite rules that will govern a proposed path mutation or adoption.

This page exists to answer:

- `which comparison rules matter here?`
- `what will be normalized, rewritten, or rejected?`
- `what claim about safe identity can the product honestly make?`

## Required sections

### 1. Review trigger

Must show:

- operation being reviewed
- current path and candidate path
- trigger reason (`case collision`, `Unicode ambiguity`, `forbidden symbol`, `portability mismatch`, `unknown horizon`, `other`)

### 2. Comparison rules table

Must show separate rows for:

- case handling
- Unicode normalization
- invalid-symbol replacement or rejection
- trailing-dot / trailing-space / suffix rules when relevant
- length / encoding policy when relevant

Each row must publish:

- current effective rule
- origin of the rule
- affected peers or surfaces
- whether the rule changes equality, visibility, or validity

### 3. Candidate outcomes

Must classify outcomes such as:

- accepted unchanged
- accepted but canonicalized
- accepted locally but peer rewrite expected
- accepted locally but peer collision expected
- blocked before apply
- unknown pending stronger horizon evidence

### 4. Safe alternatives

Must offer the cheapest safe alternatives, such as:

- choose a cohort-safe canonical name
- branch locally instead of cohort rename
- narrow the peer horizon and continue with weaker sentence
- stop and repair conflicting existing names first

### 5. Strongest safe sentence

Examples:

- `The candidate is locally acceptable but not cohort-safe under the reviewed case and Unicode rules.`
- `The product can promise only canonicalized equality, not literal raw-name equality.`

### 6. Blocked stronger sentence

Examples:

- `This path will behave the same everywhere because this seat accepts it.`
- `Normalization differences are cosmetic only.`

## Interaction rules

- the primary apply action must render the winning comparison basis inline
- blocked candidates must not offer a destructive fast path as the primary action
- rewritten outcomes must publish the exact resulting canonical or substituted name before apply

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed rules
- winning comparison basis
- candidate outcome class
- safe alternative chosen if any
- claim ceiling
