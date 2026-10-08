# Sanitizer scope

Rev0843 configured GCC 14 with `ANONSYNC_ENABLE_SANITIZERS=ON` and executed both
changed focused boundaries under AddressSanitizer and UndefinedBehaviorSanitizer,
with leak detection, halt-on-error, and abort-on-error enabled:

- `anonsync_sync_bounded_regular_file_test`: 27/27;
- `anonsync_sync_bounded_regular_file_syscall_test`: 26/26.

This is exact runtime coverage of the extracted descriptor owner, pathname
adapter, link policies, limit frontiers, live descriptor lifetime/offset checks,
and deterministic `pread` failure scripts. It is not a full-project sanitizer
claim and does not cover Windows runtime behavior.
