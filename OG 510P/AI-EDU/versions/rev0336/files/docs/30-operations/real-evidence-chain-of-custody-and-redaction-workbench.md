# Real-evidence chain of custody and redaction workbench

## Purpose

When a real pilot packet arrives, the archive needs a narrow custody path before anything is normalized into service records or public summaries. The purpose is not to preserve raw learner data inside the archive. The purpose is to prove that a real source existed, that protected/security fields were handled outside public surfaces, and that every derived claim can be traced to an approved transformation.

## Custody stages

| Stage | Name | Required posture |
|---|---|---|
| `CUST0` | no real data | placeholder only; cannot close `FT-0181` |
| `CUST1` | received | source packet logged outside public archive |
| `CUST2` | quarantined | protected/security fields separated before normalization |
| `CUST3` | mapped | source dictionary and import map agree |
| `CUST4` | redacted | public and reviewer-safe extracts are produced |
| `CUST5` | accepted | reviewers accept derived records and decision deltas |
| `CUSTX` | contaminated | source must be rejected, repaired, or re-requested |

## Non-negotiables

- Raw learner traces, disability/accommodation details, security payloads, and private communications should not be committed to the public archive.
- A hash, receipt, or file name is not evidence by itself; it must connect to a source dictionary, transformation log, acceptance packet, and closeout minutes.
- Redaction must happen before public summary rendering, not after publication.
- A protected-route fact may justify a local support decision without becoming a public service-record field.
- Chain-of-custody records can prepare `FT-0181` for closure but cannot close it while stage is `CUST0`.

## Minimum workbench record

A custody workbench record should name source packet class, custody stage, allowed derived artifacts, prohibited raw fields, transformation approvals, redaction outputs, reviewer access, deletion/retention decision, and whether the record may close `FT-0181`.

Related: [`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md), [`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md), [`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md), [`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md).
