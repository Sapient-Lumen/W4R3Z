# Audit — rev0963

Rev0963 closes an operability gap in the bounded corrupt-payload quarantine. Ordinary owner status now exposes the complete retained diagnostic set as exact expected/observed SHA-256 pairs and sizes, including after restart, without adding a second list command or query-time filesystem traversal.

The shipping C++ owner retains one fixed-width projection of at most sixteen entries. Complete writable store observations and exact preserve/release operations prepare the same canonical projection. A mutation forgets stale presentation truth before rename or unlink and publishes its successor only after the existing durability, pathname, lease, and rooted-authority cutpoints. The status accessor and readiness predicate remain owner-thread-bound and filesystem-cold.

The adjacent audit rejected a draft `quarantine-list` path because it duplicated complete namespace ownership in a read-oriented query. It also corrected two false lifecycle assumptions: service readiness now requires one initial complete payload-store observation handed into ordinary convergence with no duplicate snapshot, and the I2P stale-session test waits for an acknowledged control FIN rather than assuming ordering between separate TCP streams. The folder-wake oracle now distinguishes one current catalog path from two immutable retained payload objects after create-then-edit.

Mechanical evidence: 197/197 structural checks; 576 payload-store checks; status schema v10 process oracles; fresh 527-edge GCC and 238-edge Clang sanitizer product graphs; 258/258 GCC registry tests; independent 39/39 GCC and 39/39 ASan/UBSan product lanes; exact 14-file source reconstruction.

Nonclaims remain explicit. This is diagnostic evidence discoverability, not user version history, Archive browsing, restore, authenticity, retention age, reachability, automatic collection, quota eviction, or garbage collection. It does not defend against hostile same-UID code or establish universal filesystem power-loss semantics.
