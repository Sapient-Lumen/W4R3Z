# rev0305 field execution risk burndown

| Risk | rev0305 control | Residual boundary |
| --- | --- | --- |
| Container UTC date rolls past the operator's local session date. | Shared operator-local date helper with `CUBE_AS_OF_DATE`, legacy `FT0181_AS_OF_DATE`, `CUBE_OPERATOR_TIMEZONE`, and America/New_York default. | Human operators must still set explicit dates when recording events that happened on a different day. |
| First-contact response clock drifts by one day. | Packet prep and router recommended commands now use `operator_due_date_iso(7)`. Validator checks the June 16 -> June 23 default. | A prepared packet is still not a sent request. |
| Same-session route block is rejected because packet `created_at_utc` has moved to the next UTC day. | Prepared packet manifests include `operator_local_date`; route-block checks use it before UTC fallback. | A route block still requires explicit human confirmation and never creates a send clock. |
| Field lane is hard to inspect without scanning scratch manually. | `make owner-field-report` writes a local scratch hygiene report with router outcome, artifact counts, legacy scratch residue, and executed-date warnings. | The report is not evidence, custody, public support, or closure. |
| Future revisions create needless current-revision copies of older gate notes. | Context-pack field-lane pointer now uses latest-existing fallback. | If a gate's behavior changes, the maintainer must still write a substantive note. |
| The archive slips into doctrine instead of action. | No new schema/branch/open-question surface was added; changes are concentrated in live clock defaults, field-lane reporting, and docs that explain the executable risk. | The real blocker remains outside the archive: real owner send/return/review. |

## Current lowest-waste path

Run:

```bash
make owner-field-work
```

For reproducible operator-local sessions, run:

```bash
CUBE_AS_OF_DATE=2026-06-16 make owner-field-work
```

To inspect the live lane without creating evidence, run:

```bash
make owner-field-report
```

Then execute only the router-emitted bounded command if and only if the human or
owner precondition has actually occurred.
