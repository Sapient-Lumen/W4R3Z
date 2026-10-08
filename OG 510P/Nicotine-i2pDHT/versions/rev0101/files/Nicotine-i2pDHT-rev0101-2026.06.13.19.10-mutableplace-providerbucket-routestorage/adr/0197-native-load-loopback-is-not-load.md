# ADR 0197 — Native load loopback is not native load

Accepted: rev0093.

A native load loopback may request that the prior evidence be considered by a future load gate, but it must not grant native load, native dispatch, or native call execution.

Rationale: loopback evidence is attractive because it looks like progress. Treating it as permission would bypass the native branch's Python-oracle and fallback-memory discipline.
