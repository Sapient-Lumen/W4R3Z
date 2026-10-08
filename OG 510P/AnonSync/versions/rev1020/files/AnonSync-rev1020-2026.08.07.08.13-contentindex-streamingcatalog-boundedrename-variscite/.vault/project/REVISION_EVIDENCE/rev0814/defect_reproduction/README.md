# Parent defect reproduction

The exact rev0812 parent was copied to an isolated source tree. Only the new
catch-and-commit regression body in
`tests/sync_checkpoint_owner_fence_sqlite_test.cpp` was added; production code
remained unchanged. The focused target built successfully and exited non-zero:
44/45 checks passed.

The failing assertion was:

`caught late reset failure cannot commit the destructive DELETE prefix`

The fixture obtains a reset permit, advances sticky-mode evidence after permit
issuance, invokes the reset, catches the expected late compare-and-swap failure,
and commits the caller's outer transaction. Rev0812 commits the earlier DELETE
and foreign-key cascades. Rev0814 wraps the whole permit-authorized transition in
one typed nested savepoint, so the destructive prefix is rolled back while
unrelated earlier outer-transaction work remains committable.

`caught-late-reset-failure-regression.patch` is the exact test-only delta and
`parent-regression-run.log` is the negative result.
