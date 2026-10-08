# Split policy — rev0004

The cube keeps two conceptual documents:

1. **Strict/high-quality lane**: only source-locked, deduplicated, impact-bounded, evidence-supported items. This may remain empty.
2. **Audited backlog lane**: everything else, still ranked, clustered, and annotated with why it is not promoted.

A finding should be demoted or kept in backlog if any of the following apply:

- the source trace is not yet checked in current/future lanes;
- public issue/PR/release overlap is plausible;
- exploitability depends on a weak or local-only precondition that is not clearly explained;
- the issue is a duplicate, an architecture wish, or a broad remediation theme rather than a distinct reportable finding;
- a dynamic reproduction is needed and not yet performed.
