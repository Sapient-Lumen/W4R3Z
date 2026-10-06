# Web Lock strict option guard contract audit slice

Rev0094 adds `facility:web-lock-strict-option-guard-contract-audit`, implemented by `tools/web_lock_strict_option_guard_contract_audit.mjs`.

The audit checks that the strict Web Lock option guard is wired through runtime code, type declarations, release proof, managed Chromium proof, validation docs, manifest rows, impact-map routing, surface inventory, npm current scripts, and Makefile current targets. The audit also rejects regression to `Boolean(ifAvailable)` / `Boolean(steal)` coercion and checks that names are cleaned before `.includes()` is used.

The audit is a static/current-office check. It does not replace the runtime proof or managed Chromium proof, and it makes no cross-browser, OPFS durability, quota, eviction, crash recovery, cryptographic attestation, fairness, starvation-freedom, or production-readiness claim.
