# Structural audit — rev0280

Theme: stabilization-to-recovery pathways.

## Main finding

rev0279 could route people from impact to intake, but it still left a gap between first assistance and durable outcome. rev0280 adds explicit pathway fields for housing transition, student stability, chronic care, nutrition, utility arrears, deadline tolling, and no-wrong-door benefit sequencing.

## Added cube checks

- Every survivor-facing service floor should expose a stabilization pathway or explain why it is not people-facing.
- Every temporary housing pathway should expose an exit destination class and unresolved-need fallback.
- Every school/child packet should check immediate enrollment, transport, meals, records, and disability support.
- Every health/care packet should check medicine, device, dialysis, oxygen, records, transport, and follow-up.
- Every nutrition packet should check the next-cycle food path, not only first distribution.
- Every utility packet should check arrears, shutoff, reconnection, and medical-baseline status.
- Every legal/benefits/aid packet should check whether disaster conditions paused or reopened deadlines.
- Every casework packet should show accepted referrals, benefit sequencing, and closure or reopen reason.

## Mechanical validation performed

- Numbered Markdown files run from `00` through `396` without gaps.
- `cube/index.csv` has one row for every numbered Markdown file.
- Source register resolves through `S713`.
- All new source IDs `S698`–`S713` are cited in numbered notes.
- Numeric `routes_to` targets resolve.
- All cube CSVs parse cleanly.
- Citation footers remain terminal.

