# rev0225 late-change notice dispatch and remedy lock

rev0224 fixed the ingress problem: a revocation, supersession, correction, authority withdrawal, hash mismatch, challenge, or rollback signal could no longer remain an informal note. rev0225 fixes the next operational failure mode: a retained signal could still be handled silently.

The new object is `schemas/live-receipt-late-change-notice-dispatch-record.schema.json`, prepared by `tools/prepare_live_receipt_late_change_notice_dispatch_record.py` and audited by `tools/audit_live_receipt_late_change_notice_dispatch_record.py`.

The record is deliberately narrow. It proves either that no live late signal exists and no notice is required, or that a live late signal has affected-party notice, public freeze notice, retained delivery proof, accessible notice channel, remedy or appeal window, redaction boundary, and an explicit no-silence-as-waiver lock. It cannot continue publication, continue reliance, upgrade reliance, increment the floor, or turn notice silence into acceptance.

## Risk closed

The risky shortcut was:

`late-change ingress -> private/internal handling -> continued publication or unexplained freeze`

That shortcut fails both directions. Continuing publication after a late signal is unsafe. Freezing publication without notice, accessible explanation, and remedy route is also unsafe. The new dispatch object forces the middle step into a public-shell, non-host-retained, affected-party-notice record.

## New executable path

`evidence drop -> pilot -> LEAP candidate -> challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import readiness gate -> actual import gate -> floor activation record -> quorum participation record -> computed floor -> floor recompute receipt -> publication rollback adjudication -> late-change ingress -> late-change notice dispatch`

The live receipt floor remains zero / stayed. No genuine late signal or notice dispatch is claimed.

## Audit/refactor note

rev0225 also refactors the graph and invariant report so late-change notice dispatch appears as its own terminal replay node. This keeps late-signal capture from becoming silent freeze bureaucracy and keeps publication/reliance continuation blocked until recompute plus rollback adjudication are rerun after notice disposition.
