# DOJ SLS source-graph runbook

## Unit of work

The unit of work is a source row or source document, not a misconduct claim.

A source row records:

- source URL;
- source owner;
- access timestamp;
- page-updated label if available;
- state/territory;
- matter label;
- agency names;
- source-page status label;
- document-class labels;
- nonclaim warnings.

A source document records:

- document title;
- issuer;
- date label;
- source row;
- source URL;
- local hash if frozen;
- document class;
- person-exposure risk;
- claim-power class.

## Acquisition sequence

1. Reopen the DOJ cases/matters page.
2. Confirm the page-updated label and access timestamp.
3. Reconcile seed rows with current rows: added, removed, renamed, status changed, document link changed.
4. Assign every row a stable local row ID.
5. Assign every linked document a stable source-document ID.
6. Classify the document using `DOCUMENT-CLASS-TAXONOMY.json`.
7. Record source-page status separately from any current-status candidate.
8. Run a privacy precheck before summarizing any document.
9. Keep person extraction blocked.

## Document priority for next revision

The next high-value documents to accession are not necessarily the most famous. They should exercise different status and document classes:

- Cleveland: enforcement label plus termination status signal.
- New Orleans: decree/sustainment/versioning.
- Louisville and Minneapolis: federal closure/retraction posture.
- Newark: partial termination.
- Seattle: closed label with termination-motion materials.
- Springfield: compliance-evaluator materials.
- Worcester: findings report with sensitive subject matter.
- Puerto Rico: multilingual/territory modeling.

## Review questions for each row

- Is this a single agency, multiple agencies, a subunit, or a case-party label?
- Does the row involve a sheriff, police department, prosecutor, territory, or mixed institution?
- Is the status label source-page-only, or backed by a linked order?
- Does the document class carry allegations, findings, obligations, compliance findings, closure, or legal argument?
- Could linked documents expose civilians, witnesses, survivors, minors, families, or officers before gates are ready?
