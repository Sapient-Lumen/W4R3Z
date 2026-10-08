# U-123 fix-choice production gate — rev0037

## Outcome

Rev0037 revisits the rev0036 blocker: the final maintainer-facing fix strategy for U-123. The key result is a pivot from a narrow identity-only stale-deactivation guard to a two-part production gate:

```text
1. reject/hold a colliding same-user/same-token download TransferRequest before it can replace a different active owner;
2. keep identity-aware deactivation as a defensive cleanup guard so stale callbacks cannot delete a slot owned by another object.
```

This makes the report stronger than rev0036. Rev0036 proved that a stale timeout can delete a newer active mapping if duplicate activation is allowed. Rev0037 shows that allowing duplicate activation is itself too broad once an existing F-connection owner is active: the second request can replace the shared username+token slot before the stale-timeout step.

## New regression target

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py
```

The regression asserts that a second same-user/same-token `TransferRequest` for a different queued download is rejected/left queued while an earlier transfer already owns the active token and F connection. Progress and close callbacks must continue to route to the original active transfer.

## Rerun matrix

| source / patch shape | github-tag-3.3.10 | github-branch-3.3.x | github-branch-master | decision |
|---|---:|---:|---:|---|
| current source + collision regression | expected fail | expected fail | expected fail | confirms active-owner collision is real |
| identity-only deactivation patch + collision regression | fail | fail | fail | rev0036 fix shape is necessary but not sufficient |
| collision rejection + identity guard + collision regression | pass | pass | pass | selected production fix shape |
| selected patch + old current-bug witness | inverted/fails | inverted/fails | inverted/fails | old witness no longer describes fixed behavior |

## Production-gate decision

U-123 is promoted from production-draft to **production-gated maintainer-ready packet** in this cube. That does not mean the issue has been filed. It means the cube now contains a coherent maintainer report, selected patch shape, regression gate, current-source failure evidence, patched-source pass evidence, and public-overlap check.

## Selected fix shape

The selected shape rejects a colliding active token before dequeueing or accepting the second transfer. If the colliding transfer is already queued/failed, the response reason remains `Queued`; otherwise a non-queued remotely initiated colliding request can be rejected as `Cancelled`. Identity-aware deactivation remains as a belt-and-suspenders guard for stale callbacks.

See:

```text
evidence/rev0037-u123-rejection-patch-diff.md
report_drafts/U123-PRODUCTION-READY-MAINTAINER-REPORT-REV0037.md
report_drafts/U123-SELECTED-FIX-SKELETON-REV0037.md
```
