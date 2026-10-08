# Current public context — rev0071

Observed online on 2026-06-17.

## Stable/release lane

The public Nicotine+ site still identifies 3.3.10 as the current stable version and points testers at the 3.3.11 release candidate. The public NEWS page lists Version 3.3.11 Release Candidate 1 and includes several hardening-adjacent corrections: uncompressed network-message size limits, upload spoofing prevention, username identity correction, distributed-search fixes, and an empty-room search crash fix.

## Security/support lane

The public SECURITY.md says the latest released `A.B.x` series is supported and currently names `3.3.x`. This keeps the strict/front packet target on the 3.3.x support lane unless maintainers say otherwise.

## New public-overlap watch

PR #3781, "Implement safe path joining to prevent path traversal", is open, attached to the 3.3.11 milestone, and was force-pushed again on 2026-06-17. Its file list includes path-joining changes in `pynicotine/downloads.py`, GUI download handling, logging, `userbrowse.py`, `utils.py`, and tests. This is not one of the seven strict/front packets, but it is adjacent to file/path trust boundaries and should influence wording for any future file-path packet.

## Milestone state

The 3.3.11 milestone page shows one open issue/PR and 38 closed items, 97% complete, with PR #3781 as the remaining visible open item.

## Filing implication

Current public context strengthens the same conclusion as rev0053 through rev0070: do not file archived-source claims as live-current claims. First rerun or classify the current source state.
