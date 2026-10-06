# Singularity lessons: manifest-based programs + contract channels (SIPs)

Singularity (Microsoft Research) is a useful “alternate universe” reference point:
**push isolation and least authority up the stack**, then make *interfaces* as explicit as binaries.

DeriveBSD is hardware-isolated by default (jails + microVMs), so we do *not* want SIP-style
"everything in one address space". But Singularity’s *program model* has two lessons that
translate extremely well to DeriveBSD’s archive goals:

1) **Programs have manifests** that fully describe identity + dependencies.
2) **Communication happens over typed, contract-checked channels**.

Both are directly aligned with DeriveBSD’s "Spec→Lock→Plan→Artifact" posture.

## Lesson 1: the manifest is the stable unit of identity

Singularity treats an application/program as a security principal, and uses a manifest to enumerate:
- the program’s constituent binaries/modules
- dependencies and version bounds
- the “surface area” it expects (channels/endpoints)

### DeriveBSD mapping

We already have the right shape:
- `derive.unit` / component descriptors (`docs/297-component-descriptors-and-compiled-runtime-manifests.md`)
- promise profiles (`docs/232-service-promise-profiles.md`)
- workload identity leases (`docs/181-workload-identity-and-secretless-deploys.md`)

**Tightening suggestion:** treat the compiled runtime manifest as the *only*
blessed source of truth for:
- process graph (what runs)
- crossings (what talks to what)
- authority needs (filesystem/net/dev/portals)

Then every “run” becomes:
- *manifest digest* + *policy decision* + *lease grants* → *receipt*

This makes “application as principal” feel natural without needing SIPs.

## Lesson 2: contract channels are a better default than “stringly RPC”

Singularity’s “contract-based channels” idea is broader than any one RPC system:
- define a channel protocol as a contract
- ensure both sides agree on the contract
- (optionally) verify the contract at build-time and/or runtime

### DeriveBSD mapping

DeriveBSD already wants a single crossing primitive:
- object-capability RPC (`docs/183-object-capability-rpc.md`)
- qrexec-style policy as the front door (`docs/135-qrexec-style-rpc-policy.md`)

**Add one missing piece:** a first-class notion of a *channel contract* as an input to policy.

In practical terms (v0):
- define each RPC interface using a schema/IDL (Cap’n Proto, protobuf, JSON schema, …)
- include the interface digest in the unit’s runtime manifest
- make policy rules key on `(caller, callee, contract_digest, method)`

This does two things:
- prevents accidental "RPC surface drift" without review
- makes cross-compartment calls **diffable** (“what new methods became possible?”)

If we ever want extra hardening:
- require a **conformance test receipt** for a contract before promotion (`docs/166-test-receipts-and-promotion-gates.md`)
- treat contract upgrades like schema evolution (`docs/42-schema-evolution.md`)

## Implementation posture (don’t over-commit)

- Don’t chase SIP isolation.
- Do steal *manifest discipline* and *contract discipline*.
- Make contracts visible in blast-radius diffs (`docs/106-blast-radius-diff.md`).
- Treat RPC surface changes as policy-review events.

## References

- Singularity project (overview): https://www.microsoft.com/en-us/research/project/singularity/
- “An Overview of the Singularity Project” (MSR TR-2005-135): https://www.microsoft.com/en-us/research/wp-content/uploads/2005/10/tr-2005-135.pdf
- “Singularity: Rethinking the Software Stack” (OSR 2007): https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/osr2007_rethinkingsoftwarestack.pdf

Last updated: 2026-02-27
