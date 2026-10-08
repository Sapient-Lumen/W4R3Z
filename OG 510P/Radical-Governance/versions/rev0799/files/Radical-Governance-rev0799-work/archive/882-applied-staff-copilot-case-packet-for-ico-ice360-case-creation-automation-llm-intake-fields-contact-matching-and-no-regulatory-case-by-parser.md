# 882 — Applied staff-copilot case packet for ICO ICE 360 Case Creation Automation: LLM intake fields, contact matching, and no regulatory case by parser

## One-line thesis

ICO ICE 360 Case Creation Automation is best classified as an intake-to-case-file automation waist: it does not decide outcomes or priority, but field creation, contact matching, data extraction, and queue readiness still need provenance, mismatch review, feedback loops, and source-image continuity because the case file starts where the parser writes.

## Why this matters

Intake automation looks procedural. It creates cases from complaints or queries so staff can begin work faster. That is thinner than a decision system. But the first case record is not trivial. Intake fields can define the complainant, respondent, subject matter, legal route, service clock, and queue. A wrong field can delay a matter, send it to the wrong team, obscure the issue, or make later review harder.

The ICO case is valuable because the public record draws a strong boundary: the automation performs case creation and allocates data to fields; it does not decide outcome or priority. The archive should respect that boundary while still refusing to treat field extraction as invisible clerical work.

## Pattern pack

### 1. Form verdict

| Field | Holding |
| --- | --- |
| form | intake-to-case-file automation waist |
| lower form rejected | ordinary mailbox routing is too thin because the tool parses and structures case data |
| thicker form rejected | automated regulatory decision is too thick while outcome and priority remain outside the automation |
| waist | bridge from email / complaint intake into structured ICE 360 case record |
| live risk | field capture, contact mismatch, queue readiness without provenance |

### 2. Intake docket

Required record fields:

- original email / complaint source;
- parsed fields and confidence class;
- created case ID;
- contact match or unmatched status;
- destination queue;
- field-level provenance;
- case-officer validation route;
- correction and feedback record;
- recurring-mismatch analysis;
- model / prompt / system-change log.

### 3. No-decision boundary

The no-decision claim holds only if:

- automation does not determine outcome;
- automation does not determine priority;
- automation does not close, reject, or deprioritize cases;
- staff can correct fields without friction;
- source material remains attached;
- field errors are sampled and fixed;
- complainants and customers can correct core identity / issue errors through ordinary channels.

### 4. Field capture risks

- **identity mismatch**: the wrong person or organization is linked.
- **issue narrowing**: the complaint category omits a live issue.
- **queue drift**: field extraction effectively routes work even if priority is not formally decided.
- **record invisibility**: later staff see the structured case but not parser uncertainty.
- **feedback evaporation**: officers fix cases manually but the system owner never sees the pattern.

### 5. Chain use

The case activates `813`, `815`, `816`, `817`, `818`, `819`, `820`, `821`, and `823`. It reserves `822` and `824` unless intake fields become contractual, sanctioning, or regulatory-effect triggers.

### 6. Repair surfaces

- algorithmic transparency record;
- source-email / source-image preservation;
- field-provenance ledger;
- contact-matching exception report;
- case-officer validation rule;
- mismatch and correction sampling;
- queue-effect audit;
- model and prompt change log;
- complainant / customer correction path.

### 7. Upgrade and downshift triggers

Upgrade if the parser begins to determine priority, close cases, reject incomplete submissions, recommend outcomes, allocate enforcement track, or suppress human review. Downshift if it only creates a draft intake shell that must be validated before any queue or service clock starts. Pause if source continuity or field-provenance cannot be reconstructed.

### 8. Holding

ICE 360 Case Creation Automation is a legitimate lower-risk staff-facing automation case only while its effect remains case creation and field population. The archive should treat the case as proof that “no outcome decision” is relevant, but not as proof that intake automation has no public-governance consequence.

## Anti-theater tests

This packet fails if “only case creation” makes the first record invisible. The proof surface must show original source, field provenance, correction logs, contact mismatch handling, and queue-effect sampling.
