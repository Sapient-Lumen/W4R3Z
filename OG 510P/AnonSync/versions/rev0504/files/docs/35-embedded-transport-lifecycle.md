# Embedded transport lifecycle

This document makes the bundled-runtime story more exact.
It is not about whether Tor/I2P are first-class anymore.
That decision is already made.
It is about the operational contract created by bundling them.

## Why this document exists

The previous revision made runtime/session objects explicit.
What still needed tightening was:

- what persistent state is expected
- how bundled privacy runtimes are updated
- how provenance is surfaced
- whether graceful shutdown and long uptimes are part of the contract
- how much implementation detail should leak into the operator surface

## V1 stance

For v1, the archive should assume:

- Linux is the real supported operating environment
- Tor support should prefer an in-process Rust-native story where feasible
- I2P support may require a bundled helper/router runtime behind a stable boundary such as SAM
- bundled transport updates should ordinarily ship with normal AnonSync releases
- no silent transport-specific auto-update path should be assumed for v1

This is the conservative trust model.
It also matches the practical fact that I2P's own update spec says the router update mechanism lives in the web router console and that there is currently no provision for updates of an embedded router lacking that console.

## Persistence contract

Bundled privacy transports are not “pure stateless dependencies.”
At least for I2P, the archive should assume real benefit from preserved router/runtime state between runs.

Implications:

- the daemon should expose the persistence directory used by the transport runtime
- operators should be able to tell whether the runtime is starting from empty state or warm reused state
- destructive cleanup of persistent runtime state should be a supported, explicit action, not an undocumented filesystem ritual
- persistence policy belongs in backup/recovery documentation later, not just in implementation notes

## Session and uptime contract

The archive already decided that I2P sessions should usually be long-lived and few in number.
This document adds the lifecycle corollary:

- transport warming is a normal supported action
- long-lived readiness is preferable to repeated cold start/stop churn
- helper-style runtimes should support graceful shutdown
- the UI/CLI should show whether a transport is merely present, warmed, or actively serving routes

If a privacy transport works poorly with short uptimes, the product should say so instead of hiding it.

## Provenance and verification contract

Bundled privacy support must be inspectable like any other security-relevant dependency.
The interface should therefore surface at least:

- integration kind (`native`, `embedded-helper`, `external`)
- version/build identifier
- digest or equivalent local integrity summary
- signer/provenance summary when available
- update mode (`daemon-release-only`, `independent-payload`, `external-managed`)
- persistence path and runtime path when those differ
- last verification time and degraded verification findings

The important design principle is simple:

> bundled privacy support should feel inspectable, not magical.

## Update governance contract

For v1, the safest archive rule is:

- no hidden updater for embedded privacy runtimes
- transport payload changes normally arrive with an AnonSync release
- the daemon exposes the payload/build facts it believes locally
- the operator can verify those facts without mutating durable policy

That does not forbid future independent payload updates.
It only says the archive should not adopt that extra trust and rollback complexity casually.

## External-runtime escape hatch

The packaged experience should remain self-contained.
However, the archive should leave room for an explicit expert mode later where an operator points AnonSync at an external transport runtime.

Rules for such a mode:

- it must be explicit, not silent fallback
- the interface must say clearly that the runtime is external-managed
- provenance and update responsibility must remain visible
- the core session/route model should not fork just because the runtime origin changed

## What the interface must let an operator answer

From supported CLI/API surfaces alone, an operator should be able to answer:

- what exactly shipped for Tor and I2P on this host
- whether the transport runtime is native or helper-based
- where any persistent transport state lives
- whether the runtime is using reused or fresh state
- whether transport updates come only with daemon releases or through another mechanism
- whether the runtime is degraded because of bootstrap, verification, persistence damage, or policy disablement

## Summary rule

Bundling Tor and I2P is not just a packaging choice.
It creates a lifecycle contract.
For v1, that contract should be conservative, inspectable, Linux-first, and honest about persistence, provenance, and temporary direct-speed exceptions.
