# First-week build plan after rev0003

This is not a real-time promise; it is the next sequence of revision work.

## Revision lane A — source-document accession

- Pick five status-drift rows: Cleveland, Louisville, Minneapolis, Newark, Seattle.
- For each, pin linked documents.
- Assign source-document IDs.
- Record issuer/date/document class.
- Do not summarize substance yet.

## Revision lane B — status event model

- Create `source_status_event` fixtures.
- Represent source-page status, press-release signal, court-order status, monitor status, local status, and current-status candidate separately.
- Test partial termination and closure.

## Revision lane C — public source-inventory wireframe

- Use synthetic department pages.
- Show warnings and missingness.
- Confirm no person extraction appears.

## Revision lane D — review policy

- Decide whether official PDFs are locally mirrored, hashed, or only locator-pinned.
- Decide document redaction and excerpt policy.
- Decide public correction workflow for agency/source rows.

## Revision lane E — denominator context

- Use BJS CSLLEA as denominator context only.
- Keep collection-year warning visible.
- Do not claim current agency counts unless newer source is pinned.
