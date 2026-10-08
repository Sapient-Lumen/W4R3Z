# Rev0859 sanitizer scope

The GCC 14 ASan+UBSan lane enables `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`. Runtime uses leak detection and halt-on-error for
ASan and halt-on-error with stack traces for UBSan.

Generated command evidence binds instrumentation for:

- `sync_manifest_stream_decoder.cpp`;
- the focused decoder executable and link;
- `sync_domain.cpp`;
- `sync_peer_ingestion.cpp`; and
- the final `anonsync_core` executable link.

Instrumented runtime passes 74 decoder checks, 34 manifest-validation checks,
49 peer-ingress lifecycle checks, and 604 domain-model checks: 761/761 total.
Twenty-five repeated rounds of both focused leaf executables add 50/50 process
runs and 2,700 check observations.

The bundled SQLite amalgamation is not claimed instrumented. This is a focused
changed-boundary and integrated-consumer lane, not full-project sanitizer
coverage. ThreadSanitizer is not claimed.
