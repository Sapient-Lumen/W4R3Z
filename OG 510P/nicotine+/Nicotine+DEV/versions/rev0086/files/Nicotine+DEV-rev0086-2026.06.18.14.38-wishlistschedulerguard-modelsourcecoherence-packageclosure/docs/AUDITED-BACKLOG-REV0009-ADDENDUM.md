# Audited backlog addendum — rev0009

rev0009 focused on real forward movement rather than expanding the registry:

1. U-123 was packaged into a maintainer-grade current-behavior reproducer and concise report skeleton.
2. U-269 received a handler-level proof and was intentionally kept out of the strict document.
3. U-270 was demoted from the next strict path because historical release notes overlap search-result socket closing and buffer-empty policy.
4. The transfer/search lifetime cluster was refactored to avoid incoherent multi-fix bundling.

## Queue decisions

| id | rev0009 decision | reason |
|---|---|---|
| U-123 | remains strict report-candidate | local socket-limbo proof plus maintainer reproducer across all three lanes |
| U-169/U-170 | supporting context | overlaps spoofed-user/F-connection themes; do not split from U-123 yet |
| U-269 | source-confirmed backlog candidate | real handler behavior, but public-adjacent and likely idle-timeout-bounded |
| U-270 | public-adjacent backlog | release notes already discuss incoming search-result socket/buffer close policy |
| U-158/U-166 | separate future harnesses | status/queue messages do not share U-123's token-bearing path |

## Files added

```text
data/rev0009_ranked_audit_queue.csv/json
data/rev0009_queue_delta.csv/json
data/rev0009_strict_promotions.csv/json
data/rev0009_coherence_refactor.csv/json
data/rev0009_u123_maintainer_probe_summary.csv/json
data/rev0009_u269_upload_lifetime_probe_summary.csv/json

docs/U123-MAINTAINER-PACKET-REV0009.md
docs/U269-UPLOAD-LIFETIME-HANDLER-PROOF.md
report_drafts/U123-maintainer-report-skeleton.md

evidence/rev0009-u123-maintainer-source-trace.md
evidence/rev0009-u123-maintainer-reproducer-run.txt
evidence/rev0009-u123-probe-rerun.jsonl
evidence/rev0009-u269-source-trace.md
evidence/rev0009-u269-upload-completion-lifetime-probe.jsonl
evidence/rev0009-web-public-overlap-refresh.md

tools/probe_rev0009_u269_upload_completion_lifetime.py
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
```
