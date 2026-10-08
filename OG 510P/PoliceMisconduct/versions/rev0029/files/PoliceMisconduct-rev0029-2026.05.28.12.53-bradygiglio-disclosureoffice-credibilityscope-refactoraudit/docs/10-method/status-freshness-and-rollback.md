# Status freshness and rollback

## Problem

A source graph can become misleading even when every row was true at intake time. Status labels, links, court orders, monitor pages, local pages, and press releases change.

## Source-scoped status

Every status label must be bound to:

- source;
- access time;
- status vocabulary used by source;
- whether the status is page-label, press-release signal, court-order status, monitor status, local status, or inferred candidate;
- last verification time.

## Rollback events

A display row must rollback or downgrade if:

- the source page changes materially;
- a linked document disappears or changes;
- a later court order supersedes status;
- a press release contradicts the source-page label;
- a local/monitor source shows partial termination or sustainment not visible on the index;
- a row was multi-agency and displayed as single-agency.

Rollback does not mean deleting history. It means lowering display certainty and adding the later source event.

## Public status copy

The safest default is:

> Source-page status as of ACCESS_DATE: STATUS. Current legal/oversight status not independently verified by this cube.

Only after a current-status check may the display add:

> Current verified status as of CHECK_DATE: STATUS, based on SOURCE_TYPE.
