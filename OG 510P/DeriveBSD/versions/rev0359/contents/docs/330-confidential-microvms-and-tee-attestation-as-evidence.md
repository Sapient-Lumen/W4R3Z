# Confidential microVMs + TEE attestation as evidence (SEV-SNP / TDX / CCA)

Confidential-computing TEEs (e.g., **AMD SEV‑SNP**, **Intel TDX**, **Arm CCA**) can make a microVM's memory and register state confidential/integrity-protected *from the host and hypervisor*.

Most OSes and runtimes treat TEEs as:
- a special VM flag
- a blob of vendor evidence (a “quote/report”)
- an application-specific attestation protocol

DeriveBSD's greenfield advantage is to treat TEE attestation as just another lane in the **evidence spine**:
**requirements → references → evidence → verifier receipts → policy decisions → brokered secret release**.

This doc defines the *shape* of that lane and the “tight” integration points. It does not mandate TEEs.

## Goals

- Make confidential microVMs **operable**: when something fails, the system can answer *what was required, what was presented, what was verified, and why a secret was/wasn’t released*.
- Make vendor formats **adapters**, not “new cores”.
- Bind TEE measurements to **Derive artifacts** (runtime manifests, closure proofs) so the attestation says something meaningful.

## Non-goals

- Standardizing vendor quote formats inside DeriveBSD core evaluation.
- Guaranteeing that a TEE implies “safe” (it only moves the boundary).

## Lane overview

### 1) Reference values: `tee.attestation.reference`

A reference object declares what a relying party will accept:
- tee types (sev-snp/tdx/cca)
- acceptable measurements (launch measurement / MR* values)
- minimum TCB/SVN constraints
- whether debug/test modes are allowed
- optional *init-data policy* hashes (so “guest policy” becomes part of what is measured)

Reference objects should be **signed** (canonical bytes) so policy cannot be quietly weakened in transit.

Schema: `spec/tee.attestation.reference.schema.json`.

### 2) Raw evidence: `tee.attestation.evidence`

The attester (often in-guest agent) produces vendor evidence and records it as a typed evidence object.
The evidence object should be **digest-first**:
- store raw quote/report bytes separately (CAS) and reference by digest
- capture only the minimal extracted claims needed for explainability

Key binding is important: many ecosystems include an ephemeral public key generated inside the TEE and bound into evidence, so later channels can authenticate the workload without shipping long-lived secrets.

Schema: `spec/tee.attestation.evidence.schema.json`.

### 3) Verifier output: `tee.attestation.receipt`

A verifier service evaluates evidence against a reference and emits a signed receipt:
- verdict (pass/degraded/fail)
- reason codes (no secrets)
- optional obligations (quarantine / require-reimage / allow-secret)

Schema: `spec/tee.attestation.receipt.schema.json`.

## Integration points

### Workload identity

The Workload Identity Agent (WIA) can treat a fresh `tee.attestation.receipt` as one of the acceptable *workload attestation inputs*.
This aligns with SPIFFE/SPIRE-style flows but uses Derive evidence objects.

See: `docs/181-workload-identity-and-secretless-deploys.md`.

### Secret release

High-risk secrets should be released only when policy sees:
- identity selectors match a derived plan (closure + runtime manifest)
- the workload presents a valid TEE receipt for the correct reference scope
- the receipt is fresh and time-bounded

See: `docs/63-secrets-sealing-and-delivery.md`, `docs/30-policy-engine.md`.

### Runtime manifests and init-data binding

Confidential-container ecosystems commonly measure "init data" (policy/config) into the guest evidence so the relying party can ensure the guest is running with a known security policy.
DeriveBSD can map this to **runtime manifest digests** and an optional **guest policy** digest:
- manifest digest is embedded into REPORTDATA / TDREPORT reportdata (or equivalent)
- verifier checks those fields and emits them as extracted claims

### Evidence export and privacy

TEE evidence can contain stable identifiers.
Default posture:
- keep full raw evidence local (CAS)
- export only receipts + redacted claim summaries unless policy allows more

See: `docs/251-export-policies-and-support-bundle-portal.md`.

## Practical adapter notes

- SEV‑SNP evidence includes a launch measurement of initial guest state and is signed via AMD’s certificate chain.
- TDX attestation often involves a TDREPORT and quote generation/verification steps.

The archive keeps implementation notes in a backend-facing doc:
- `docs/331-tee-attestation-in-practice-snp-tdx-and-verifier-services.md`

Last updated: 2026-02-26r91
