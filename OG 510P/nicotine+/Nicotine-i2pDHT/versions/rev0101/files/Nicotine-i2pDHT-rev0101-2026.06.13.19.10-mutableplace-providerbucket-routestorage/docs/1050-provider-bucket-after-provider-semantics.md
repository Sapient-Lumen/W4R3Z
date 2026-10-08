# Provider bucket after provider semantics

`providerbucket.py` turns a provider semantic proof into local provider-index admission. The bucket is a routing index, not a content store and not content truth.

It checks:

- provider semantic proof accepted
- semantic result is true, not false/unproven/refusal-only
- TTL and region digest are bounded
- bucket capacity pressure becomes sweep/watch rather than silent overflow
- raw content payload storage is quarantined
- provider-false, tombstone, metadata-budget, and region-ledger memory survive
- source/provider/path family diversity is adequate
