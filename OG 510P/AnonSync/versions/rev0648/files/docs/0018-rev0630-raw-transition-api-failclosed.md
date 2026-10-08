# rev0630 — raw terminal-transition API fail-closed

rev0629 required the command-line terminal effect transition path to use a signed RS256 intent under a digest-pinned transition trust profile. During rev0630 audit, the underlying public helper `run_sqlite_effect_transition_command(...)` still accepted raw effect key, prepared sequence/hash, terminal state, result digest, and reason. That meant an embedder could bypass the signed intent path even though the CLI had been closed.

rev0630 changes that helper to fail closed. Terminal SQLite/WAL state may now be appended only through `run_sqlite_effect_signed_transition_command(...)`, which verifies the transition trust-profile digest pin and signed payload binding to the prepared ledger head, effect transition head, prepared row sequence/hash, effect key, terminal state, result digest, and reason.

The older transition-chain and pending-effect recovery selftests were refactored to create selftest trust profiles and signed intents. They no longer depend on the raw helper for a successful terminal transition. The transition selftest additionally asserts that the raw public API rejects a seemingly valid unsigned terminal transition.

Capability metadata advances to v25 with `ledger_effect_transition_raw_public_api_disabled=true`; normal sqlite-wal runs reject downgraded capability manifests rather than accepting old v24 evidence.

Remaining caveat: this is still local operator authorization evidence. It does not prove downstream delivery, distributed exactly-once semantics, HSM key custody, or multi-node consensus.
