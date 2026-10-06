# Workload identity + secretless deploys (SPIFFE/SPIRE-shaped lane)

Static secrets are one of the fastest ways immutable systems rot back into ambient authority.
DeriveBSD should bake in a **workload identity primitive** so secrets and privileged operations can be granted **just-in-time** and **least-privilege**, across jails and microVMs.

This doc proposes an **optional lane** that becomes extremely valuable the moment you have:
- more than one environment (dev/stage/prod)
- more than one trust domain/team
- any compliance requirement that asks “who accessed what, when, and why?”

The product-shape default is now fixed separately in `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`: fleet and factory shapes treat short-lived workload identity as the baseline, workstation AppVM/dev-service identity stays separate from human login/account authority, and general OS keeps static-token workflows as explicit adapters rather than ambient defaults.

## The problem

Even with good “secrets by reference” discipline, systems tend to drift toward:
- long-lived tokens baked into images
- shared credentials mounted into multiple compartments
- "control-plane can read everything" architectures

The missing piece is a reliable answer to: **what is this workload, right now, and can it be trusted to hold this capability?**

## DeriveBSD direction

Introduce a host-local **Workload Identity Agent (WIA)** (service-jail or dedicated microVM) that issues **short-lived identity documents** to workloads.
The WIA’s job is to:

1) **attest the node** (host identity; optional measured-boot evidence)
2) **attest the workload** (closure/runtime digest + compartment identity)
3) **issue a short-lived identity** (mTLS cert and/or JWT) over a local Workload API
4) **emit evidence** about issuance and renewals

This is intentionally SPIFFE/SPIRE-shaped:
- the identity is a stable **workload identifier** (SPIFFE ID semantics)
- credentials are short-lived (SVID-style)
- the API is local-only (uds/vsock), so the “bottom turtle” stays small

### What counts as “workload attestation” in DeriveBSD?

DeriveBSD has unusually strong primitives to anchor identity:
- `deployment.ref` (what this host is meant to be running)
- `closure.proof` digests (what bytes are allowed)
- runtime manifest digests (the VM/jail contract)

In the simplest form, a workload is identified by selectors like:
- `closure_digest`
- `runtime_manifest_digest`
- `instance_name` / `compartment_id`
- optional `channel` / `namespace`

The WIA can refuse to issue identity if the workload doesn’t match a known derived plan.

### How this replaces “secrets in images”

Instead of shipping long-lived credentials, workloads use identity to obtain:

- **brokered operations** via the factotum-style credential broker (`docs/151-factotum-style-credential-broker.md`), e.g.
  - "fetch this Git ref"
  - "sign this digest"
  - "get a short-lived cloud token scoped to X"
- **secret material** only when unavoidable (and ideally short-lived), authorized by policy

The important shift: *policy binds access to identity + evidence*, not to “who can read a directory on the host”.

## Evidence objects

Identity issuance should be **receipted** so incident bundles and policy can answer:

- what identity was issued?
- to which workload selectors (digest/instance)?
- with what TTL and trust bundle?
- based on which attestation inputs?

Minimal v0.1 objects:

- `workload-identity-lease` (schema: `spec/workload.identity.lease.schema.json`)
  - binds `{subject, spiffe_id, credential_ref, expires_at}`
  - may embed `lease.envelope` for uniform cross-lane lease handling (`spec/lease.envelope.schema.json`)

- `workload-identity-issue-receipt` (schema: `spec/workload.identity.issue.receipt.schema.json`)
  - records issuance/renewal events and optional `attestation_verification` so the issuance receipt, not the verifier result alone, explains why the credential was issued or denied

Compatibility / legacy shape:

- `workload.identity.grant` is an older evidence-object form still kept in the archive
  (`spec/workload.identity.grant.schema.json`, `spec/examples/workload.identity.grant.json`).
  It can be treated as a derived summary of the lease + issuance receipts.

## Integration points

- **Secrets delivery**: extend `docs/63-secrets-sealing-and-delivery.md` with an identity-gated lane.
- **Config/secrets injection**: keep vsock/uds channels, but prefer *identity → brokered fetch* patterns (`docs/28-config-and-secrets-injection.md`).
- **Measured boot** (optional): node attestation inputs and verifier receipts (`docs/176-measured-boot-attestation.md`).
- **Confidential microVM attestation** (optional): treat TEE verifier receipts as first-class workload attestation inputs (`docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`).
- **Capability routing**: derived graphs can declare which broker endpoints a workload may talk to (`docs/140-capability-routing-manifests.md`).
- **Portals/powerbox**: interactive cases can grant additional scoped capabilities (human-approved exceptions) (`docs/179-portals-and-powerbox.md`).

## Remaining implementation questions

- Trust-domain naming + federation: do we standardize a default `spiffe://` trust domain format derived from Derive namespaces?
- Key handling: do workloads generate private keys in-guest, or does the WIA provide a key manager abstraction?
- Offline mode: what’s the smallest viable “air-gap WIA” story?
- Which classic token/file-credential adapters are worth standardizing for profile C without silently weakening A/B/D defaults?

References:
- SPIFFE overview: https://spiffe.io/docs/latest/spiffe-about/overview/
- SPIFFE concepts (SPIFFE IDs): https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
- SPIRE concepts (node + workload attestation plugins): https://spiffe.io/docs/latest/spire-about/spire-concepts/
- Working with SVIDs (X.509-SVID + trust bundle): https://spiffe.io/docs/latest/deploying/svids/


Last updated: 2026-03-07r221
