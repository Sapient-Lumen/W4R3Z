
# Evidence plan page — artifact families, preconditions, and claim budget interface spec

## Purpose

Give the operator one durable page that answers:

- what diagnostic question this evidence effort is trying to answer
- which artifact families are requested and why
- what preconditions or disruptions collection requires
- what stronger questions remain out of scope
- what manifest the product expects to exist later

This page exists so `send logs`, `collect a dump`, and `run iperf3` stop being article folklore and become reviewable product state.

## Inputs

- incident identifier
- current incident brief and leading explanation
- symptom bookmark and latest capture receipt if any
- witness set and participant duties if any
- candidate artifact families by platform and incident kind
- current subject scope
- current export/redaction posture
- current claim ceiling

## Primary questions this page must answer

1. What exact question is this package meant to answer?
2. Which artifact families are requested, optional, or excluded?
3. What preconditions or disruptions must be satisfied first?
4. What is the narrowest honest package that could answer the current question?
5. What stronger question would still require a wider or different package?

## Layout

### A. Plan strip

Fields:

- incident headline
- target diagnostic question
- leading explanation
- package strategy (`minimal`, `targeted`, `broad`, `forensics`)
- current claim budget

### B. Question-to-artifact table

Columns:

- artifact family (`recent-logs`, `extended-logs`, `crash-material`, `core-dump`, `network-benchmark`, `event-slice`, `config-summary`, `other`)
- why it is requested
- participant / platform scope
- duty level (`required`, `optional`, `excluded-for-now`)
- strongest question it could answer
- stronger question it still cannot answer

### C. Preconditions and disruption card

Rows may include:

- restart required
- reproduction required
- dwell floor required
- crash must occur
- Sync must be shut down
- hidden-path or elevated access needed
- log-size increase recommended
- mobile limitations or unsupported adjustments

### D. Narrowest honest package card

Show:

- smallest defensible artifact set
- what exact conclusion it could support
- what contradiction would force widening
- what collection cost or disruption widening would impose

### E. Expected manifest card

Show the manifest the product expects later:

- expected member classes
- expected time window
- expected sensitivity envelope
- expected completeness verdict
- link to open artifact capture matrix and evidence manifest

## Required interactions

- `Confirm evidence plan`
- `Promote artifact family to required`
- `Downgrade artifact family to optional`
- `Exclude artifact family for now`
- `Mark precondition satisfied`
- `Open artifact capture matrix`
- `Open evidence manifest`
- `Issue evidence export receipt`

## Guardrails

- Never request an artifact family without naming the question it serves.
- Never merge `collected` and `meaningful` into one state.
- Never hide disruptive preconditions such as shutdown, restart, or crash-waiting.
- Never let `broad package` sound stronger than `targeted package` without stating what additional question it answers.
- Never let later export proceed without a reviewed plan version.

## Output

A reviewed evidence-plan object that makes diagnostic question, artifact families, preconditions, and claim budget explicit before collection or export.
