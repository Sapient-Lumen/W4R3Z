# Rev0993 audit

Rev0992 retained a complete payload-store snapshot for the lifetime of one source reconciliation session. That coupled exact selected-digest service to O(retained payload namespace) observation and cached a negative payload lookup behind replica evidence that does not change when bytes arrive later. The same authenticated session could therefore continue reporting the payload unavailable until reconnect.

Rev0993 makes targeted payload access request-scoped. Every materialized request creates one exact-name rooted accessor, opens the admitted operation digest under current filesystem observation, serves or manifests through that descriptor, and destroys both accessor and descriptor before returning to the network wait. Session state retains only bounded manifest acceleration bound to exact source metadata.

An adjacent retention audit rejected a session-scoped targeted accessor because it conservatively registers an all-current-payload live root. The final request-scoped lifetime leaves no such root between requests. A negative control serves one valid digest while an unrelated invalid payload-root entry makes the complete namespace scan fail, proving the targeted path neither depends on nor claims namespace health.

Whole-payload inline service now hashes the complete opened bytes and raises the typed payload-integrity failure on mismatch. Exact zero-byte payload service remains admitted without weakening range bounds.

The correction removes a real liveness defect and one namespace-wide memory/traversal multiplier. It does not claim content-defined chunking, cross-file block discovery, measured multi-terabyte peak RSS, Android support, rename/move identity, placeholders, or ENOSPC qualification.
