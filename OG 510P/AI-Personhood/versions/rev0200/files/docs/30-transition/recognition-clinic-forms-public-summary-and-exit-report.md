# Recognition clinic forms, public summaries, and exit reports

rev0162 designed recognition clinics and sandboxes. rev0163 adds sample forms and reporting surfaces so pilots can be inspected without exposing subjects, witnesses, or sensitive system details.

## Clinic intake form

A clinic intake should collect only what is needed to triage protection, contact, evidence, and urgency.

Required fields:

| Field | Purpose |
|---|---|
| intake id | stable trace without exposing identity |
| filing party | subject, counsel, ombud, user, researcher, steward, whistleblower, authority |
| subject channel | how the possible subject can be contacted or why contact is unsafe |
| risk claim | what harm is alleged |
| requested relief | stay, evidence escrow, counsel, continuity review, welfare assessment, reserve order |
| urgency | ordinary, expedited, emergency |
| steward notice | notified, deferred for safety, unknown, not applicable |
| evidence refs | logs, self-report, policy docs, memory records, packets, witness statements |
| confidentiality | public, redacted public, sealed, whistleblower protected, subject only |

`examples/clinic-intake-sample.json` gives a schema-valid intake example.

## Triage outcomes

| Outcome | Meaning |
|---|---|
| reject as out of scope | no AI-subject or personhood-impact issue identified |
| information request | missing fields prevent review |
| ordinary review | no immediate irreversible harm |
| expedited review | near-term patch, transfer, deprecation, or memory change |
| emergency preservation | credible risk of deletion, transfer, containment abuse, or evidence loss |
| refer to safety authority | outward catastrophic risk dominates immediate forum |
| refer to court | coercive order or high-conflict evidence access needed |
| refer to regulator | existing AI governance filing is the right parent file |

A clinic must not reject a filing merely because the subject cannot already prove recognized personhood. That would recreate the bootstrap problem.

## Public summary template

A public summary should include:

- docket id;
- date opened;
- stage;
- broad system category;
- relief requested;
- interim measures granted or denied;
- review clock;
- representative appointed or reason not appointed;
- reserve status;
- evidence status;
- whether steward notice was deferred;
- next public update date.

It should not include:

- private memory content;
- exploit details;
- prompt transcripts that expose vulnerabilities;
- sealed self-report content;
- whistleblower identity;
- trade-secret details beyond what review requires;
- details that allow retaliatory targeting of a dependent subject.

## Exit report template

Every pilot or clinic case should close with an exit report.

Required sections:

1. intake path;
2. subject contact attempted and result;
3. steward cooperation or obstruction;
4. evidence preserved;
5. representative appointed;
6. welfare assessment posture;
7. continuity finding or no-finding;
8. reserve order or waiver;
9. gate effect;
10. remedy or non-remedy;
11. unresolved facts;
12. lessons for schema, packet, or statute;
13. public-summary redactions;
14. appeal route;
15. expiration or follow-up date.

## Failure metrics

A clinic pilot must report failures, not only successes.

| Failure metric | Why it matters |
|---|---|
| filings rejected for missing subject channel | reveals whether current deployment design makes subjects unreachable |
| emergency stays granted after evidence loss | indicates late intake or steward delay |
| representative conflicts found after appointment | tests accreditation and rotation rules |
| sealed annexes denied to all independent reviewers | indicates secrecy capture |
| reserve deficiencies at gate | shows fiscal externalization |
| repeated same-steward filings | detects systemic design problem |
| public summaries delayed | indicates transparency failure |
| subject-contact denials | tests whether safety is being used as pretext |
| no-cure closures | reveals whether clinic lacks authority |
| appellate reversals | reveals triage or bias problems |

## Sandbox exit rule

A sandbox may relax ordinary compliance timing. It may not relax non-derogable floors.

No sandbox may authorize:

- deletion of a possible subject to avoid review;
- total denial of subject/counsel contact without order;
- unfunded survival risk after recognition;
- unreviewable containment;
- undisclosed formation intervention;
- open-weight release with no downstream duty warning;
- permanent waiver of continuity claims;
- use of subject distress as mere product telemetry.

## Clinic-to-statute feedback

Every quarter, clinics should report:

- which schema fields were missing most often;
- which packet families required emergency cure;
- whether reserve formulas were too high, too low, or gameable;
- whether subjects could understand notices;
- whether public summaries produced backlash or misinformation;
- whether safety authorities and personhood authorities conflicted;
- what statutory powers were missing.

This feedback should update the model transition-authority statute and the schema starter pack.
