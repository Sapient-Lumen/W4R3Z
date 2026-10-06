# RFC-0064: Process topology (role separation and least authority)

Status: draft

## Problem

Security goals like “treat builders hostile” and “minimize TCB” require concrete boundaries.
Without an explicit topology, implementations drift:

- builders grow network access and secret access
- signers become coupled to build systems
- verification happens too late (after activation/launch)

## Proposal

Adopt a default role topology with explicit interfaces:

- Evaluator (Spec/Lock/Plan)
- Fetcher (network)
- Builder (sandboxed; no network; no secrets)
- Signer/Attestor (keys)
- Publisher (no keys)
- Verifier/Installer/Launcher (enforce-before-run)

Each interface is an object boundary (digests + signatures), not an ambient RPC trust boundary.

## Consequences

- easier to harden each role
- smaller blast radius when a role is compromised
- clearer “why” for audits and incident response

Pointer: `docs/96-process-topology.md`
