# DOJ official news bridge method

Official DOJ press releases are useful but dangerous source carriers. They are current enough to catch status drift, but they may summarize legal events and carry the rhetoric of the issuing administration.

## Admission rule

A press release may be admitted as an `official_news_event_nonclaim` if it has:

1. a DOJ URL;
2. a headline;
3. a publication date;
4. an event signal type;
5. explicit `current_legal_status_asserted_by_cube = false`;
6. `person_extraction_allowed = false` and `incident_extraction_allowed = false`.

## Claim-power rule

Press releases can support these weak facts:

- the press release exists;
- DOJ publicly said a status-relevant event occurred;
- the event maps to a matter label or agency label;
- the event creates a recheck obligation.

They cannot, by themselves, support:

- a current legal-status claim;
- a misconduct finding;
- a person-level claim;
- a settlement/admission claim;
- deletion of prior source history.

## Source-family conflict rule

When DOJ's cases page and a DOJ press release point in different directions, treat both as official carriers and open a reconciliation ticket. Do not pick the newer source automatically. The governing evidence is usually a court order, docket entry, consent decree, settlement agreement, or monitor/court page.

## Why this matters

At scale, the cube will ingest many official sources that disagree because one page lags, one press release summarizes, a consent decree terminates in part, or a local/state process continues after a federal process ends. The source graph must preserve those differences instead of flattening them.
