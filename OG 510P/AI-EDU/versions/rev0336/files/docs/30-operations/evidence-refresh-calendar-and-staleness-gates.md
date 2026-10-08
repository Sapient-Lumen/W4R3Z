# Evidence refresh calendar and staleness gates

The archive already has an external evidence watchlist. This surface adds the next operating layer:
when a source should be revisited, which archive claims it can affect, and what happens when review
is overdue or the source changes.

This is not a literature review. It is a staleness control for claims that might otherwise stay
public after the external world changes.

## ER states

| State | Meaning |
|---|---|
| `ER0` | no refresh calendar |
| `ER1` | watchlist exists but no claim effects are named |
| `ER2` | sources have due dates, claim families, and stale actions |
| `ER3` | review performed and decision deltas recorded |
| `ER4` | evidence grades or public claims updated after review |
| `ERX` | source is stale, superseded, or no longer supports the claim |

## Calendar row fields

Each row should name:

- the source id from the evidence watchlist;
- related bibliography ids;
- affected claim families, such as learning, workload, access, security, compliance, or public
  summary truth;
- related archive surfaces;
- last checked and next due dates;
- what invalidates the source;
- what to do if the source changes or becomes stale.

## Staleness rule

A stale source should not automatically delete a surface. It should downgrade the affected claim
family until reviewed. For example, an expired workload study should narrow workload claims without
deleting the teacher-facing workflow; a changed security standard should reopen red-team tests
without pretending all public summaries are wrong.

## Release interaction

A release can still ship while a source is scheduled for future review. It should not ship while a
source needed for an active public claim is known stale, superseded, or contradicted without a
decision-delta entry.
