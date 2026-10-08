# Remedy-hardening-attestation affected-party-closure review page — have the affected parties actually been reached and has the remedy been accepted, contested, or left pending?

## Purpose

This page is the operator-facing review that answers the practical closure question after operational remediation: did the people or systems that materially relied on the stale truth actually receive the corrective account, and is the outcome accepted, contested, or still awaiting acknowledgement?

## Primary review prompts

The review must answer these prompts in order:

1. **Who materially had to be told before any closure sentence is allowed?**
2. **Which delivery attempts actually landed, and which remain unproven, bounced, or unknown?**
3. **Who merely received notice, who had to acknowledge, and who has already acknowledged?**
4. **Which objection windows are open, closed, paused, or reopened?**
5. **Is the current state accepted, contested, silent-but-open, or uncontested for each named cohort?**
6. **What is the strongest sentence the product may say right now?**

## Review sections

### 1. Materially affected cohort map

Show:

- required human or system cohorts
- named parties already identified
- unknown cohort risk
- parties whose notice is contractually or regulatorily mandatory

### 2. Delivery ledger

Show:

- every delivery attempt
- channel used
- proof class for that attempt
- whether the attempt counts toward required notice
- parties still not reached

### 3. Acknowledgement and acceptance board

For each named cohort, show:

- acknowledgement required or not
- acknowledgement present, refused, or missing
- explicit acceptance, explicit contest, or silent state
- current objection deadline
- reopen trigger if the matter had closed previously

### 4. Closure sentence chooser

The review must output one and only one primary sentence class such as:

- remedy issued, affected-party notice pending
- delivery proven, acknowledgement pending
- acknowledged for named cohort, objection window open
- accepted for named cohort only
- uncontested for named cohort after objection lapse
- contested by named cohort
- reopened after prior closure sentence

## Hard rules

The review must never let an operator hide:

- unknown materially affected parties behind a low visible contest count
- silent parties behind a single successful delivery channel
- live objection windows behind completed operational remediation
- one cohort's acceptance behind another cohort's open contest
- past acceptance behind a newly opened contest or new evidence packet
