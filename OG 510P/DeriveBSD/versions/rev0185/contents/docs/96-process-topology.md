# Process topology (minimize authority, treat builders hostile)

DeriveBSD’s security posture depends as much on **who can do what** as on cryptography.
This doc defines a recommended *process topology* that minimizes the trusted computing base (TCB).

## Roles (separate by default)

1) **Evaluator** (Spec/Lock/Plan)
   - pure computation; no network
   - produces: Lock, Plan, policy decision record

2) **Fetcher** (inputs)
   - the only component allowed network by default
   - emits: content-addressed inputs with recorded digests

3) **Builder** (realization)
   - runs in jail sandbox; network denied
   - never receives plaintext secrets
   - treated as hostile: outputs must be verified by consumers

4) **Signer / Attestor**
   - holds signing keys (or talks to an HSM)
   - signs artifacts/closure proofs/attestations according to policy

5) **Publisher**
   - uploads blobs + metadata to caches
   - untrusted by clients; must not have signing authority

6) **Verifier / Installer / Launcher**
   - verifies digests, signatures, required attestations, closure proofs
   - performs activation/launch only after verification

7) **Portal / Broker (optional)**
   - mediates narrowly scoped *dynamic* capability acquisition (file handles, export actions, scoped RPC)
   - deny-by-default; emits evidence objects for every grant
   - enables capability-mode adoption without reintroducing ambient authority

8) **Activation broker (optional)**
   - pre-opens and rights-minimizes the handles a service needs
   - hands them off at start and can escrow them across restarts
   - keeps on-demand startup compatible with least authority
   - emits `activation.capset` + `activation.claim` evidence

This separation makes “treat builders hostile” concrete.

## Default constraints

- Evaluator and policy engine are deterministic, data-only.
- Fetcher is narrow, logged, and pins every byte.
- Builder cannot:
  - open network
  - see host secrets
  - mutate host state outside its sandbox
- Signer cannot:
  - fetch from the network (except explicit key distribution)
  - build artifacts

## Interfaces between roles

All inter-role boundaries are file/object boundaries:

- fetcher → store objects (digests)
- evaluator → Lock/Plan + policy decision record (digests)
- builder → store outputs (digests)
- signer → signatures/attestations/closure proofs (digests)

Everything is explainable because boundaries are explicit objects.

Pointers:
- hostile builders: `docs/91-hostile-builders.md`
- verification rules: `adrs/ADR-0009-artifact-verification.md`
- explain contract: `docs/95-explainability-contract.md`
- portals/powerbox: `docs/179-portals-and-powerbox.md`
- activation broker: `docs/196-capability-activation-and-escrow.md`

Last updated: 2026-02-24
