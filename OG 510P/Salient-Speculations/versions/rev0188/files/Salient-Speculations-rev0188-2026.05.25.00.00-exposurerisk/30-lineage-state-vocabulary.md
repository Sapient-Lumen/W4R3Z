# Lineage State Vocabulary

This file normalizes state terms for the provenance, custody, transformation, resolver, and lineage family.

Use these terms when a dossier concerns the origin, custody, transformation, packaging, signature, routing, redaction, diffing, replay, correction, or archival afterlife of a proof object.

## Core states

| State | Definition | Use when |
|---|---|---|
| `source-unbound` | The proof object has not been reliably tied to the claimed subject, source system, issuer, asset, dataset, media item, model, or product. | subject mismatch, false match, orphaned proof |
| `source-bound` | The claimed subject/source relation is established strongly enough for the reliance purpose. | source-object identity, issuer binding, asset identity |
| `snapshot-captured` | A source state was captured with timestamp, hash, witness, or retention handle. | source escrow, due diligence, evidence preservation |
| `custody-escrowed` | A source, transform, package, or history is held by an escrow/custodian for later audit or dispute. | liability tail, regulator access, escrowed evidence |
| `transform-declared` | The operation converting source to relied-on object is named and versioned. | mapping, normalization, rendering, summarization |
| `transform-replayable` | The transform can be rerun from captured inputs to reproduce the result within tolerance. | audit, litigation, regulator review, model-data lineage |
| `normalization-loss-disclosed` | Semantic loss, inference, dropped fields, widened/narrowed meaning, or non-comparability is disclosed. | crosswalks, mappings, packet normalization |
| `wrapper-divergence` | Human-readable and machine-readable layers disagree or have uncertain precedence. | embedded XML/PDF, hybrid reports, digital labels |
| `signature-chain-valid` | Signature, seal, issuer, or trust profile validates for the specified reliance purpose. | report signatures, content credentials, product passports |
| `signature-chain-broken` | The chain of signatures, certificates, seals, timestamps, or trust profile checks fails. | trust-chain disputes, expired or revoked signers |
| `resolver-current` | Resolver response points to the expected current object for the reliance purpose. | product passports, Digital Link, registry pointers |
| `resolver-suspect` | Resolver response may be captured, stale, hijacked, wrong-granularity, or service-provider-controlled. | passport routing, default-link disputes |
| `resolver-successor-declared` | A successor resolver, service provider, registry, or endpoint is declared and mapped. | migrations, acquisitions, insolvency, registry updates |
| `redaction-boundary-declared` | Withheld, masked, aggregated, or minimized fields are declared with policy and audit boundary. | privacy-preserving evidence, AI assurance, legal privilege |
| `derived-use-limited` | A derived dataset, model, feature, output, embedding, summary, or redacted object carries use restrictions. | AI training, data spaces, licensing, contract exhibits |
| `lineage-gap` | A material custody, source, transform, signature, resolver, or retention segment is missing or unverifiable. | custody-break certificates, caveats, holdbacks |
| `replay-sufficient` | Captured inputs, transform, environment, and logs are sufficient for an agreed replay standard. | audit replay, regulatory review, forensic reconstruction |
| `provenance-disputed` | Origin, custody, transform, redaction, routing, or replay sufficiency is challenged. | appeals, litigation, source-witness requests |
| `archive-evidentiary` | Object is retained not for current use but for historical reliance, litigation, repair, recall, or audit. | historical state views, retention floors, liability tails |

## Stage terms

Use these as `lineage_stage` values:

- `identify`
- `capture`
- `bind`
- `transform`
- `package`
- `sign`
- `resolve`
- `disclose`
- `redact`
- `transfer`
- `diff`
- `replay`
- `verify`
- `rely`
- `dispute`
- `correct`
- `supersede`
- `archive`

## Role terms

Use these as `lineage_role` values:

- `source-issuer`
- `subject-owner`
- `transformer-broker`
- `custodian-escrow`
- `resolver-operator`
- `registry-steward`
- `signer-sealer`
- `redactor-minimizer`
- `verifier-relying-party`
- `recipient`
- `auditor-regulator`
- `rights-holder`
- `small-supplier-evidence-broker`
- `adversary-forger`

## Distinctions from nearby vocabularies

### Lineage versus freshness

Freshness is about age and current status. Lineage is about descent from source state through controlled transformations and custody.

### Lineage versus authority

Authority says who was allowed to act. Lineage says what that act did to the object and whether it can be inspected later.

### Lineage versus remedy

Remedy is the challenge process. Lineage supplies the evidence defect being challenged.

### Lineage versus authenticity

Authenticity can be a signature check. Lineage includes source binding, transform, redaction, resolver routing, diff, replay, and archive state. A signed object can still have bad lineage.

### Lineage versus traceability

Traceability often means following a chain. Lineage asks whether the chain is sufficient for a specified reliance purpose.

## Red flags

Avoid saying “provenance attached” without specifying:

- source object;
- capture method;
- transform;
- custody holder;
- signature / trust profile;
- resolver route;
- disclosure/redaction boundary;
- diff from prior state;
- replay sufficiency;
- dispute/correction path;
- archive retention.

That checklist is the minimum bar for future lineage-family dossiers.
