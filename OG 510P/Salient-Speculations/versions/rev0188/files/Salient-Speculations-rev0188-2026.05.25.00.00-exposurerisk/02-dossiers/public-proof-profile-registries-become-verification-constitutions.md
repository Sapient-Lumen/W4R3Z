---
id: ss-0182-public-proof-profile-registries
revision_promoted: rev0182
title: Public proof-profile registries become verification constitutions
constellation:
- anti-legibility
- managed-legibility
- standards-and-conformance
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- identity / credentials / delegated authority
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- selective disclosure / minimization
- admissible evidence
- conformance capacity
- small-actor evidence capacity
enforcement_surface:
- procurement / framework contract
- platform eligibility
- public service access
- wallet verifier policy
artifact_type:
- registry entry
- privacy proof
- selective-disclosure credential
- reason code
lifecycle_stage:
- validate
- publish
- rely
- dispute
failure_modes:
- over-disclosure
- verifier-overreach
- linkability
- proof-profile-fragmentation
refactor_cluster:
- authority-lifecycle
authority_role: issuer-authentic-source and verifier-relying-party
authority_stage:
- define
- publish
- verify
state_family:
- authority
state_terms:
- verifier-unregistered
- scope-limited
consolidation_status: state-family-member
---
# Public proof-profile registries become verification constitutions

## Core claim

As verifiable credentials, selective-disclosure proofs, product passports, due-diligence statements, model documentation packets, repair records, and recipient-graph privacy proofs spread, the hardest question will often not be whether a party can prove something. It will be **what counts as enough proof for a specific purpose, and what the verifier is forbidden to demand**.

That is the speculative claim: **public proof-profile registries become verification constitutions**. A proof profile is a machine-readable and human-legible rule saying: for this purpose, in this jurisdiction, for this transaction class, these claims are required, these formats are accepted, these issuers or trust anchors count, these freshness windows apply, these revocation checks are required, and these extra attributes must not be requested.

The registry matters because selective disclosure alone does not stop coercive disclosure. A verifier can still say: show me the whole credential, the whole passport, the whole recipient graph, the whole model card, the whole repair history, or the whole supplier map, or you cannot proceed. A public proof profile changes the power relation. It turns minimization from etiquette into an admissibility rule.

## Why this belongs in the archive

The archive already has `data-minimization-proofs`, `recipient-graph-privacy-proofs`, `small-supplier-evidence-brokers`, `repair-right-evidence`, and `model-documentation-packets`. Those dossiers all need the same missing artifact: a public, reusable definition of sufficient proof.

W3C Verifiable Credentials Data Model 2.0 and related cryptosuites provide part of the technical basis for tamper-evident credentials, presentations, selective disclosure, and unlinkable proofs [S1488][S1489][S1505]. The EU Digital Identity Wallet ecosystem points in the same direction by emphasizing wallet-based attribute sharing, privacy, and selective disclosure [S1492][S1493]. NIST's Privacy Framework supplies the governance premise: privacy is not only compliance; it is a risk-management discipline that supports beneficial systems while controlling data processing [S1490].

The missing institutional layer is not the cryptography. It is the profile registry. Technical selective disclosure says a holder can disclose less. A proof-profile registry says the verifier must accept less when less satisfies the registered purpose.

## Speculative consequences worth tracking

### 1. Verifier overreach becomes appealable

A supplier, citizen, worker, repairer, or model provider may challenge a request as outside the accepted proof profile. The dispute is no longer “I do not want to disclose.” It becomes “your request is not part of the admissible profile for this purpose.”

### 2. Profiles become procurement boilerplate

Procurement forms may name accepted proof profiles for cybersecurity attestations, accessibility conformance reports, AI documentation packets, EUDR traceability claims, repair authorization, supplier identity, and emissions disclosures. Vendors that produce the right proof shape move faster than vendors with broader but less profile-conformant evidence.

### 3. Public-good profiles reduce incumbent advantage

Large firms can satisfy bespoke proof requests. Small firms need reusable profile definitions, shared validators, and public tooling. Proof-profile registries become inclusion infrastructure when they prevent every buyer from inventing a different evidence packet.

### 4. Profiles become contested political objects

A profile can be too weak, allowing fraud; too strong, excluding small actors; too invasive, enabling surveillance; too narrow, blocking innovation; or too broad, becoming useless. The profile registry becomes a quiet constitution because it sets what institutions may ask and what subjects must reveal.

### 5. Profiles need versioning, expiry, and transition rules

A profile will change. New issuers are accepted. Old trust anchors are retired. A freshness window tightens. A revocation method changes. A selective-disclosure format is deprecated. That means profile state itself needs versioning, effective dates, grandfathering, transition notices, and non-reliance states.

## How this gets abused

- Buyers write narrow profiles that only favored vendors can satisfy.
- Platforms accept privacy rhetoric while demanding whole-wallet disclosure.
- Issuers lobby to make their own credential format mandatory.
- Proof-profile registries become stale, letting old claims travel after risk changes.
- Profiles encode hidden discrimination by selecting hard-to-obtain attributes.
- Verifiers demand off-profile evidence through side channels.
- Small suppliers use minimal profiles to hide real risk when richer proof is justified.

## Who pays, who saves, who captures

Public agencies, standards bodies, sector utilities, and large platform buyers have reasons to publish profiles because profiles reduce intake friction. Credential issuers, compliance vendors, wallets, and validators can capture value by becoming profile-compatible defaults. Small actors save when profiles are public and reusable; they lose when profiles become proprietary gatekeeping devices.

## Near misses

- A wallet standard is not a proof-profile registry. It says how proofs can be carried, not what is sufficient for a purpose.
- A procurement checklist is not a proof-profile registry unless it can be referenced, versioned, validated, and appealed.
- A privacy policy is not a profile unless it constrains verifier behavior at transaction time.
- A schema is not a profile unless it defines admissibility, minimization, freshness, and trust rules.

## Falsifiers

The thesis weakens if verifiers keep accepting broad bespoke documents; if selective disclosure remains mostly identity-wallet UX rather than procurement and compliance infrastructure; if regulators avoid defining sufficiency rules; if buyers can keep demanding unlimited additional evidence without appeal; or if privacy law blocks reusable proof profiles by treating every use case as too contextual for registries.

## Signals to watch

- Public registries of accepted credential profiles for government or regulated-sector transactions.
- Procurement templates naming accepted VC, SD-JWT, BBS, OpenACR, DPP, or AI-documentation profiles.
- Appeal categories for excessive proof requests.
- Validators that test not only whether a proof is valid, but whether a verifier request is profile-compliant.
- Insurance or audit products around proof-profile conformance.
