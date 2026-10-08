# rev0057 patch-queue coherence refactor

The audit/refactor pass in rev0057 separates the new patch queue from adjacent evidence layers that were easy to over-merge.

| Area | Kept separate from | Decision |
| --- | --- | --- |
| Source-bundle selected-stack patch queue | Archived source-anchor trace | Patch queue records generated diffs and patch hashes; rev0051 source anchors remain line-level evidence only. |
| Source-bundle selected-stack patch queue | Current web marker snapshot | Patch queue is generated against the uploaded archived source bundle, not web-visible current branch state. |
| Source-bundle selected-stack patch queue | Fresh current checkout filing gate | The queue can be applied to the uploaded archived lanes; live external filing still needs fresh checkout identity and rerun. |
| Search source-admission patch | Search parser-budget patch | The lane stack contains both for integration, but filing bundles remain split. |
| Public path traversal watch | Strict private packets | PR #3781/#3723 stay public-watch-only and are not part of the rev0057 strict patch queue. |

The refactor preserves the four current filing bundles:

```text
1. U-123 transfer-session identity
2. PB-01 peer primary-election compatibility
3. FileSearchResponse source-admission series
4. FileSearchResponse parser-budget series
```

No new private row was opened and no production-gated packet was retired.
