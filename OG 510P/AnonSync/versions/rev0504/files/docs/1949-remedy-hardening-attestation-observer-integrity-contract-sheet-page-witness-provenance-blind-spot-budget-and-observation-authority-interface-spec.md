# Remedy-hardening-attestation observer-integrity contract sheet page — witness provenance, blind-spot budget, and observation authority

## Purpose

This page is the compact contract for deciding whether the current witness set is trustworthy enough to support the sentence the product is trying to say now.
It exists so the product can distinguish `fresh evidence exists`, `capture protocol complete`, `world scope proved`, `retention gap present`, `blind-spot budget exceeded`, `tamper suspicion open`, `trusted for named slice only`, and `broader stronger sentence blocked`.

## Core fields

- observer-integrity identifier
- source policy-conformance receipt identifier
- current witness-set identifier
- current observer-integrity class
- named estate slice or topology slice under observation
- observer surfaces included in the current witness set
- observer surfaces explicitly absent from the current witness set
- capture protocol required for this sentence class
- capture protocol actually satisfied
- restart-confirmed flag
- reproduction-window completeness class
- retention horizon for each witness lane
- rotation-loss risk class
- storage-world identifier
- service-user or principal-world identifier
- world-scope continuity status
- blind-spot axes currently open
- tamper or mutation suspicion status
- manual-forensic dependency status
- highest currently safe evidence-trust sentence
- strongest blocked stronger sentence
- next evidence that upgrades trust now
- next evidence that collapses trust now

## Observer-integrity classes

The page must model at least these distinct classes:

- evidence present, protocol incomplete
- fresh witness, world scope ambiguous
- fresh witness with retention gap
- fresh witness with blind-spot budget exceeded
- calm surfaces only, no authoritative observer set
- trusted witness for named slice only
- trusted witness, but manual-forensic-only dependency remains
- tamper or mutation suspicion under review
- evidence trust restored after re-capture
- broader stronger sentence blocked

## Blind-spot axes

The page must support at least these blind-spot axes:

- history horizon too short
- peer-presence expiry
- log rotation or discard risk
- restart not confirmed after enabling capture
- reproduction window too short
- wrong storage world or service user observed
- platform-surface limitation
- WebUI-versus-desktop feature gap
- manual or script-driven startup ambiguity
- dump or forensic artifact unavailable
- known instrumentation omission

## Fixed rendering order

Every observer-integrity contract sheet must render the same sections in the same order:

1. **Highest currently evidence-trust-safe sentence**
2. **Named slice, witness set, and protocol-completeness class**
3. **Blind-spot and retention ledger**
4. **World scope, tamper state, and manual-forensic dependency**
5. **Next evidence that upgrades or collapses trust**

## Hard rules

The contract sheet must never let an operator hide:

- a fresh timestamp behind an incomplete capture protocol
- a surviving log file behind undisclosed rotation loss risk
- one calm UI surface behind a broader observation-authority sentence
- evidence from one storage world behind `same world proved` wording
- absence of alarms behind `breach would have been visible` wording without blind-spot accounting
