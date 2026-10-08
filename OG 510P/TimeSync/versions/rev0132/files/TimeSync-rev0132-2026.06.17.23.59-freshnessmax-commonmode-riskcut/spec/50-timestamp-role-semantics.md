# 50 — Timestamp role semantics for aggregate correction lifecycle

rev0086 separates aggregate publication event time from aggregate artifact creation time and lifecycle-check times.

## Problem

Older aggregate examples used nearby names such as `issued_at`, `record_issued_at`, `assessment_time`, `authorization_checked_at`, `lifecycle_checked_at`, `revocation_checked_at`, and `last_notification_at`. Those are not interchangeable. Lifecycle and notification checks must not appear to happen after the artifact that reports them.

## Roles

The archive now treats the following roles distinctly:

```text
publication_event_at
aggregate_record_created_at
authorization_checked_at
lifecycle_checked_at
revocation_checked_at
notification issued_at
last_notification_at
assessment_time
```

`aggregate_record_created_at` is the artifact creation time for aggregate verifier audit summaries. It is the latest time by which embedded authorization, lifecycle, revocation, and notification observations must already be known.

`publication_event_at` is the event time of the correction, withdrawal, supersession, reconciliation, or aggregate publication. It can be earlier than artifact creation.

`assessment_time` remains profile/local-assessment time and is not reused as an aggregate audit artifact time.

## Ordering rules

For aggregate verifier audit summaries:

```text
publication_event_at <= aggregate_record_created_at
authorization_checked_at <= aggregate_record_created_at
lifecycle_checked_at <= aggregate_record_created_at
revocation_checked_at <= aggregate_record_created_at
notification.issued_at <= aggregate_record_created_at
last_notification_at <= aggregate_record_created_at
```

Notification observations must also satisfy:

```text
last_notification_at >= notification.issued_at
```

and policy delay limits must be respected when a current notification posture is claimed.

## Privacy and redaction

A record may use bucketed or redacted timing where the schema permits it. Redaction does not allow a record to claim current interpretation from checks that occurred after the aggregate artifact was created.

## Boundary

These timestamps are semantic roles. They are not a publication repository, external notification log, legal-service record, incident clock, or proof that an external system behaved correctly. They constrain only TimeSync aggregate interpretation.
