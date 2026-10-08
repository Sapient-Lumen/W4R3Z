# 578 — Nuclear emergency preparedness: response intake, docket proof, and hotpath pruning

## Why this revision exists

Rev0370 made request packets and public-meeting lockboxes artifact-ready. The next failure mode is more practical: a response arrives, a meeting note is taken, or a docket item appears, and the cube accidentally treats a partial, oral, duplicate, route-only, or nonresponsive artifact as readiness proof.

Rev0371 therefore adds the missing receiving end of the pipeline:

1. **Response intake contract.** Every incoming record must have a sidecar, file hash, linked request/dispatch, custodian or route, received timestamp, artifact class, redaction state, scope, and explicit claim limit before it can even become candidate evidence.
2. **Docket/release watch.** EOF/LER and FEMA/public-report follow-up now have concrete watch queries and release routes. A search result or route page is a pointer only; it cannot close a blocker.
3. **Hotpath prune.** Active work should run from a bounded current-risk capsule. Rev0371 prunes duplicate historical aliases from the hotpath source list and rebuilds the SQLite/capsule from the manifest rather than from memory.

## Operational rule

A response can do one of four things: become candidate evidence for a specific proofcut class, create a follow-up task, document nonresponse/no-records, or be rejected as route-only/summary-only/unhashable/out-of-scope. None of those states is a readiness conclusion by itself.

Automatic rejection applies when an artifact is missing sidecar metadata, lacks a stable hash, lacks a custodian/source, is a public route page only, does not map to a blocker/proofcut class, or tries to assert broad readiness without evaluated objective scope and deficiency/ARCA/corrective-action state.

## Claim discipline

Current claim state: **capture-ready / submission-packet-ready / response-intake-lockbox-ready / docket-release-watch-open / EOF-LER-watch-open / ANS-transition-gate-open / claim-frozen / no local readiness conclusion**.

No real or lawfully anonymized Beaver Valley evidence packet has been imported. Request drafts, public notices, route pages, lockbox templates, docket searches, and fixture responses remain acquisition controls only.
