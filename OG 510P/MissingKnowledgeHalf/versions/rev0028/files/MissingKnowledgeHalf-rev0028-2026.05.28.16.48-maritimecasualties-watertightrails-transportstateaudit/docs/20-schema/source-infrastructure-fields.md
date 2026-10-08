# Source-infrastructure fields

Record type: `INF`.

Minimum fields:

- `infrastructure_class`: registry, confidential reporting, voluntary self-reporting, mandatory reporting, accident database, recommendation tracking, lessons-learned system, operating-experience system.
- `jurisdiction_or_scope`: field, country, regulator, institution, industry coverage.
- `signal_capture_model`: how the system receives weak signals, incidents, concerns, near-misses, studies, or recommendations.
- `reporter_protection_design`: confidentiality, de-identification, anonymity, limited immunity, no-blame separation, legal limits.
- `outputs`: database, alert, newsletter, recommendation, closure state, public report, internal action.
- `limitations`: underreporting, selection bias, exclusions, no effectiveness proof, privacy constraints, source rot.
- `pattern_links`: related pattern candidates.
- `query_value`: what this infrastructure makes findable that individual case records do not.

Admission rule: an `INF` record can be promoted from official/institutional sources without importing individual reports. Importing report narratives requires a separate ethics and source-permanence review.
