# ADR 0198 — Call canary is Python-result evidence only

Accepted: rev0093.

The call canary records the Python fallback/oracle result for an exact native-call vector. It rejects native-result evidence and native execution.

Rationale: result canaries are useful only if they cannot silently become an alternate execution path.
