# Kernel Kit support-bundle risk decision slice

This slice proves the support bundle classifies storage-recovery rows into `retry`, `verify-first`, or `stop/manual-review`.

`retry` is limited to pre-mutation rows with no provider-mutation evidence. `verify-first` is required when OPFS/provider/Service Worker work may have mutated storage. `stop/manual-review` is required when evidence is missing, ambiguous, stale, contradictory, or unclassified.

Primary task: `demo:kernel-kit-support-bundle-risk-decision-proof`.
