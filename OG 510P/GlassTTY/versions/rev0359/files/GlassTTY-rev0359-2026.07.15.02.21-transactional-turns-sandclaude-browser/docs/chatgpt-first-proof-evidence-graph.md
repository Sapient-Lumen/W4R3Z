# ChatGPT first-proof evidence graph

The proof cube should be read as an event graph, not as a bag of JSON files. Derived ledgers are useful only when they can be traced back to a small set of ordered events.

## Canonical event spine

```text
SourceReviewed
ArchivePackaged
ExtensionBuilt
NativeHostInstalled
BrowserProfileOpened
RouteWitnessCaptured
PromptWritten
PromptReadbackVerified
OperatorSubmitAttested
ConversationRouteObserved
LatestTurnRead
TurnPairWitnessed
GenerationSettled
BundleAuditRendered
EvaluatorVerdictIssued
PrivacyReviewCompleted
SupportClaimProposed
SupportClaimPublished
```

## Required event fields

Every event should carry enough identity to prevent cross-run stitching:

```text
event_id
attempt_id or run_id
surface_key
tab_id
url
conversation_route_path
route_posture
actor
input_artifact_hashes
output_artifact_hashes
timestamp
schema_version
redaction_state
```

## Governance separation

Evidence capture stays small, typed, and local-reviewable. Support/publication governance consumes evaluator verdicts and redaction reviews; it must not be interleaved with first proof capture. A green local proof is a prerequisite for support widening, not support widening itself.

## Current rev0324 stance

The archive now includes a local bundle-audit command that renders action nodes, sequence edges, attempt summaries, and evaluator-registry health before the evaluator verdict. It still intentionally carries the stop sign: no live ChatGPT checkpoint proof has been captured inside this package.

## Rev0324 audit/refactor note

The proof evaluator now derives top-level required-check aggregation from one registry partition: attempt-scoped evidence checks plus global-only checks. This prevents future schema additions from being silently omitted from the payload-level merge layer. The bundle-audit command consumes the same evaluator helpers and renders the pre-verdict evidence graph without approving publication or support widening.
