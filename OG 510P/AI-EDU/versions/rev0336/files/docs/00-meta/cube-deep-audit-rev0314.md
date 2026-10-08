# rev0314 cube deep audit

## Audit focus

This pass audited the returned-evidence entry chain, not the doctrine layer. The question was: if a real owner CSV appears, can a stale local contact-status file make that CSV look properly sourced?

## Finding

`owner_contact_status_integrity_error()` validated the contact-status shape, clock bounds, status class, and non-evidence effects. When used by returned-CSV intake, workbench seed, and router tooling, it did not reopen the referenced `send-log.json` or `reask-log.json`. Positive validator fixtures had normalized around this by writing hand-made status records with checker-scratch source references.

## Refactor

The guard now re-reads the source artifact when `archive_root` is supplied. It requires the source reference to resolve under `scratch/field/ft0181/`, requires the expected artifact type, validates the source send/reask log, and checks `sent_date` and `response_due_date` against the source artifact.

A shared validator helper now builds positive contact-status fixtures through real packet/send-log/status builders in field-lane validation scratch. Checker scratch remains available for negative tests and outputs, not as a positive source chain.

## Waste avoided

This avoids a high-cost false path: spending a session processing a returned CSV under a contact clock whose source send/reask artifact was missing, stale, or produced by a validator. The correction is executable in the returned-evidence path rather than another registry rule.
