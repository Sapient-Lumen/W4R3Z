# Audit — rev0968

Rev0968 makes bounded causal-history pagination fail closed against source change. A first page returns one canonical constant-size cutpoint over the exact active operation set and complete retained-payload snapshot. A later page must provide that same token. A known stale operation set or cursor fails before payload enumeration; a second replica observation brackets the complete payload scan; retained-payload drift fails with a typed stage. The owner remains alive and returns no fabricated replacement token.

The authority audit rejected replica `state_generation` as a page token because it includes liveness writes that do not determine history contents. The exact operation-set digest is the causal input; the payload-snapshot digest is the retained-byte input. This is a fail-closed composition boundary between two owners, not a cross-owner transaction.

An adjacent runtime-oracle audit found that the first process regression treated generic `last_step` as stable historical evidence. Under ASan a legitimate later network step replaced it. The service had already retained the exact `source_changed` class and stage in the historical-status domain. The corrected oracle requires that stable owner result and checks per-step evidence only when the current step names the completed history generation. The implementation also serializes the per-step class and stage instead of carrying dead populated fields.

Mechanical evidence binds a 17-file binary-aware patch reconstructed 17/17 against sealed rev0967, the 568-file active projection, 237/237 structural checks, the complete 258-test GCC registry, independent 39/39 GCC product replay, focused 393-check folder-owner and 115-check local-control suites, a clean-root 238-edge Clang ASan/UBSan product graph, and all 39 sanitizer product tests without a retained diagnostic.

The boundary remains narrow. Source cutpoints do not pin bytes, create chronology, promise retention, provide quotas or garbage collection, browse conflicts, restore directories, or make multiple pages one durable transaction. A changed source requires pagination to restart.
