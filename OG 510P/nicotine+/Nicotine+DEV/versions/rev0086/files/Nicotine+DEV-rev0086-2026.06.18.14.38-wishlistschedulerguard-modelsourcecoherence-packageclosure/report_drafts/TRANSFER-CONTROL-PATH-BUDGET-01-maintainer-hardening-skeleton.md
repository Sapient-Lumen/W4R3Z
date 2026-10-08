# TRANSFER-CONTROL-PATH-BUDGET-01 maintainer hardening skeleton

Not production-ready disclosure text.

## Summary

Several peer transfer-control request paths accept virtual path/directory strings before a shared semantic path/component budget is applied:

- QueueUpload
- legacy TransferRequest direction=download
- PlaceInQueueRequest
- FolderContentsRequest

Current behavior allows oversized or extremely deep virtual paths to be parsed and then used for lookup, queue-key construction, logging/plugin context, and response echo. FolderContentsRequest can also echo the requested directory into a compressed FolderContentsResponse.

## Reproducer

Use:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q maintainer_artifacts/transfer-control-path-budget-01/test_transfer_control_path_budget_reproducer.py
```

rev0024 results:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Suggested fix shape

Implement one shared virtual-path parser/policy for transfer-control requests. Reject over-budget strings before lookup, fallback mapping, logging, plugin notification, queue mutation, and response echo. Keep compatibility tests for legitimate legacy paths/backslash behavior.

## Caveat

This is low/medium availability/transfer-control hardening, not RCE and not a peer-only confidentiality issue. PR #3741 and related public discussions overlap the general virtual-path validation theme.
