# Scheduler-policy invocation observation

After the final 213/213 complete registry run, one serial `ctest -R
'(audit|policy)'` invocation was externally terminated while
`anonsync_sync_checkpoint_scheduler_policy_test` was outstanding. There was no
reported assertion or test failure before termination. The same scheduler test
had passed in the immediately preceding complete registry, and the final
post-change two-worker audit/policy selection completed 84/84 in 10.65 seconds.

This record prevents an execution-wrapper or scheduling interruption from being
silently rewritten as either a product failure or an unqualified serial-pass
claim. The release gate relies on the complete registry and final two-worker
audit selection.
