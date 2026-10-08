# Provenance and Lineage Lifecycle

rev0187 refactors the cube's provenance, custody, transformation, resolver, and lineage layer.

The archive already had strong pieces: source-object identity warranties, source-snapshot escrow, transformation-code escrow, normalization-loss warranties, resolver capture, authoritative rendering, report-signature trust chains, redaction-boundary ledgers, and product biographies. But those dossiers were starting to use `source`, `provenance`, `custody`, `traceability`, `lineage`, `passport`, `wrapper`, `signature`, and `resolver` as if they were interchangeable.

They are not interchangeable. The central object is now:

> **A proof object has lineage only when a relying party can say what subject it refers to, which source state it captured, which transformation produced it, which layer is authoritative, who held custody, what was redacted, which resolver routed access, what changed later, and whether the claim can be replayed or disputed.**

This model treats lineage as a state machine rather than a pedigree label.

## Why this needed a refactor

The cube had recently normalized three adjacent families:

- **freshness** — is the proof current enough to rely on?
- **remedy** — what happens when the proof is challenged?
- **authority** — who may act, disclose, receive, bind, or appeal?

Lineage kept leaking into all three. A stale proof might still have perfect lineage. A fresh proof might have a broken source chain. A person might have authority to submit a record but not authority to transform or redact it. A remedy might correct an outcome but leave the transformation history unreplayable. Without a lifecycle, every new gap in evidence custody became another standalone dossier.

rev0187 makes the reusable object explicit: **provenance state**.

## Canonical lifecycle

| Stage | Question | Typical artifact | Failure if missing |
|---|---|---|---|
| `identify` | What subject, asset, record, claim, dataset, model, product, or media item is being referred to? | persistent identifier, subject binding, product key, dataset ID | subject mismatch; wrong object relied on |
| `capture` | What source state was observed, by whom, and when? | source snapshot, attestation, capture hash, source timestamp | unprovable origin; unverifiable input |
| `bind` | How is the source state tied to the subject and issuer? | identity binding, issuer signature, source-object warranty | forged or orphaned evidence |
| `transform` | What operation changed the source into the relied-on object? | transformation manifest, mapping table, code escrow, job run event | hidden semantic loss; unreplayable normalization |
| `package` | How are readable, machine-readable, signed, and supporting layers bundled? | hybrid wrapper, report package, manifest, BOM | layer divergence; visible/machine mismatch |
| `sign` | Who asserts integrity, authorship, issuer responsibility, or custody? | signature chain, seal, attestation envelope | trust-chain ambiguity |
| `resolve` | How does a verifier reach the current or historical object? | resolver, linkset, registry pointer, successor map | captured routing; dead link; wrong version |
| `disclose` | Which fields are shown to which class of relying party? | disclosure policy, role view, access proof | over-disclosure or under-disclosure |
| `redact` | What was withheld, removed, masked, aggregated, or transformed for confidentiality? | redaction ledger, minimization proof, boundary manifest | laundering by redaction; irreproducible omission |
| `transfer` | How does custody or reliance move to a new owner, broker, registry, service provider, or market? | transfer attestation, custody receipt, successor map | broken afterlife; orphaned reliance |
| `diff` | What changed between two states, packages, manifests, or resolver responses? | claim diff, manifest diff, schema diff, provenance delta | silent mutation; stale comparison |
| `replay` | Can the relied-on result be reconstructed from captured inputs and declared transforms? | replay bundle, deterministic environment, input archive | irreproducible compliance claim |
| `verify` | What checks are sufficient for the reliance purpose? | verifier policy, validation report, trust profile | false confidence; incompatible sufficiency |
| `rely` | What transaction, decision, ranking, import, sale, loan, audit, publication, or remedy uses the object? | reliance receipt, use log, contract exhibit | impossible liability allocation |
| `dispute` | How can lineage be challenged? | custody-break certificate, source-witness request, challenge packet | no repair path for bad lineage |
| `correct` | How is a lineage defect repaired or disclosed? | amended manifest, corrected transform, non-reliance notice | bad prior packets keep circulating |
| `supersede` | Which previous objects remain valid, limited, archive-only, or non-reliance? | successor map, version state, revocation notice | historical confusion |
| `archive` | What must remain available for audit, litigation, repair, recall, or scientific reproducibility? | escrow, retention floor, archival package | evidence evaporates before disputes mature |

## State vocabulary introduced here

The corresponding state vocabulary is in `30-lineage-state-vocabulary.md`. The short form:

- `source-unbound`
- `source-bound`
- `snapshot-captured`
- `custody-escrowed`
- `transform-declared`
- `transform-replayable`
- `normalization-loss-disclosed`
- `wrapper-divergence`
- `signature-chain-valid`
- `signature-chain-broken`
- `resolver-current`
- `resolver-suspect`
- `resolver-successor-declared`
- `redaction-boundary-declared`
- `derived-use-limited`
- `lineage-gap`
- `replay-sufficient`
- `provenance-disputed`
- `archive-evidentiary`

## Design rule for future dossiers

A new lineage dossier should not merely say that something has provenance, traceability, custody, a passport, or a chain of trust. It must identify at least one of the following:

1. a new **subject-binding problem**;
2. a new **capture or custody failure**;
3. a new **transformation or normalization-loss surface**;
4. a new **wrapper-layer divergence**;
5. a new **resolver or successor-map bottleneck**;
6. a new **redaction or disclosure boundary**;
7. a new **diff, replay, or audit sufficiency test**;
8. a new **custody-break or lineage-dispute remedy**.

If it does not do one of those, it should probably be a state inside this lifecycle rather than a standalone dossier.

## Relationship to freshness

Freshness asks whether an object is current enough. Lineage asks whether the object can be trusted as a descendant of a named source state.

A proof can be fresh but lineally defective: an up-to-date passport reached through a captured resolver; a current AI model card whose dataset derivation rights are missing; a newly signed report whose visible PDF diverges from its embedded structured data. A proof can be old but lineally excellent: a properly archived historical state that remains sufficient for a transaction that happened in the past.

## Relationship to remedy

Remedy often begins with a lineage defect: wrong source object, missing witness, bad transform, redaction abuse, resolver drift, signature-chain break, or custody gap. The remedy model handles the clock and outcome. The lineage model supplies the evidentiary claim being challenged.

## Relationship to authority

Authority determines who may capture, transform, disclose, redact, sign, transfer, or correct a proof object. Lineage determines whether those actions are visible and sufficient. A valid delegate can still produce an unreplayable transformation. An unauthorized actor can still leave a complete lineage trail.

## Minimal lineage packet

A reliance-grade lineage packet should include:

- subject identifier and subject-binding method;
- source issuer / source system / capture actor;
- capture timestamp and source-state hash or snapshot handle;
- source-retention and witness-availability rules;
- transformation code, mapping, parameters, and environment;
- declared semantic loss, inferred fields, dropped fields, and non-comparable states;
- human-readable / machine-readable layer precedence;
- signature chain and trust profile;
- resolver, registry, and successor-map state;
- disclosure and redaction boundary;
- transfer or custody receipts;
- diff from prior state;
- replay sufficiency grade;
- dispute and correction route;
- archive-retention obligation.

## Falsifiers

This family weakens if:

- institutions continue accepting provenance labels without requiring source capture, transformation declarations, resolver continuity, or replay sufficiency;
- product passports and content credentials remain consumer-facing labels rather than procurement, customs, audit, repair, resale, or litigation controls;
- AI/data/model documentation does not move toward dataset/model lineage and derived-use terms;
- regulators and buyers treat custody gaps as ordinary caveats rather than priced exceptions;
- resolver and service-provider continuity stay invisible in contracts.

## Refactor posture

This model does not demote the existing provenance dossiers. It gives them sharper roles:

- `source-object-identity-warranties-become-broker-liability-caps` becomes the subject-binding thesis.
- `source-snapshot-escrow-becomes-liability-tail-infrastructure` becomes the capture-retention thesis.
- `transformation-code-escrow-becomes-packet-custody` becomes the transform-custody thesis.
- `normalization-loss-warranties-become-diligence-language` becomes the semantic-loss thesis.
- `resolver-capture-becomes-a-hidden-passport-bottleneck` becomes the routing-power thesis.
- `redaction-boundary-ledgers-become-ai-assurance-controls` becomes the hidden-omission thesis.
- `report-signature-trust-chains-become-interoperability-bottlenecks` becomes the signature-sufficiency thesis.
- The new rev0187 dossiers fill the successor-map, replay-bundle, derived-use-rights, provenance-diff, and custody-break-certificate gaps.
