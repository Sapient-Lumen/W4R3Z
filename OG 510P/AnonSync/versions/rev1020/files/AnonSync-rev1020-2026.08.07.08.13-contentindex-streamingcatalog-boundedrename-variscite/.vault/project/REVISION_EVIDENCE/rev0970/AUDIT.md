# Audit — rev0970

Rev0970 separates two different owner questions that rev0969 answered through one expensive path. Exact history inspection still proves current retained-payload availability by bracketing a complete private payload-store observation. The new explicit metadata mode reads only the immutable replica operation snapshot and performs no payload-store lease acquisition, namespace enumeration, object open, byte read, or hash. Every payload-derived response field is represented as unknown/null rather than a false zero or false absence.

The source cutpoint is mode-bound. Exact pages retain the byte-for-byte v1 operation-set plus payload-snapshot token. Metadata pages use `v2:metadata:<operation-set>`. A cursor or cutpoint from one mode cannot authorize continuation in the other. The shipping CLI, strict owner-only local frame, response v4, status v15, folder-owner request, and shared enum/name/parser all carry the same canonical inspection mode.

The adjacent audit corrected a subtle C++ regression oracle: evaluating `std::optional<bool>` in boolean context proves only that a value is present. The affected test now compares the exact optional value and therefore distinguishes observed false from observed true.

Mechanical evidence binds a 14-file binary-aware patch reconstructed 14/14 against sealed rev0969, the complete 568-file active projection, 260/260 structural checks, all 258 GCC tests, the independent 39-test GCC product lane, the 238-edge Clang ASan/UBSan product graph, and all 39 sanitizer product tests without a retained diagnostic.

The boundary remains narrow. Metadata mode does not prove payload availability, make exact mode cheaper, transfer remote historical operations, define retention or chronology, create Archive semantics, pin versions, make collection safe, or complete the first measured Resilio uninstall workflow.
