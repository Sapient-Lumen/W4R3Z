---
id: ss-migrated-source-object-identity-warranties-become-broker-liability-caps
revision_promoted: pre-rev0182
migration_status: inferred-rev0182
title: Source-object identity warranties become broker liability caps
constellation:
- managed-legibility
- energy-sovereignty
- model-governance
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- identity / credentials / delegated authority
- civic services / casework / appeals
- procurement / purchasing / offtake
bottleneck_type:
- source-of-truth precedence
- admissible evidence
enforcement_surface:
- procurement / framework contract
- platform eligibility
- audit / assurance engagement
artifact_type:
- registry entry
- notice
lifecycle_stage:
- source
- capture
- publish
- rely
failure_modes:
- subject-mismatch
refactor_cluster:
- provenance-lineage
- exposure-liability
lineage_role: source-issuer and verifier-relying-party
lineage_stage:
- identify
- bind
- verify
state_family:
- provenance
- exposure
state_terms:
- source-bound
- source-unbound
- allocated-by-contract
- warranty-breached
- trigger-disputed
consolidation_status: state-family-member
exposure_role: broker and verifier-relying-party
exposure_stage:
- allocate
- condition
- trigger
---
# Source-object identity warranties become broker liability caps

## Core claim

Once renewal-history normalization brokers start producing diligence packets, the most dangerous representation is not always semantic mapping. It is the assertion that several native records describe the **same underlying thing**. A POA&M item, ServiceNow exception, Jira remediation ticket, GitHub alert, cloud finding, Microsoft incident, SBOM component, and provenance subject can all carry internally valid identifiers while still being wrongly joined across systems. If the broker collapses unrelated objects, splits one obligation into several, or loses the native object chain after migration, the packet can be internally consistent and commercially false. In that world, **source-object identity warranties become broker liability caps**.

## Why this belongs in the archive

The archive has already promoted three adjacent layers. **Extension-lineage disclosures become diligence exhibits** says counterparties will inspect the renewal story behind exceptions and residues. **Renewal-history normalization services become a quiet broker market** says those stories need cross-tool translation. **Normalization-loss warranties become diligence language** says the translation’s losses must be represented. The remaining hidden layer is identity: before a field can be mapped, preserved, or declared non-comparable, the broker must decide what the field is attached to.

The source signals are strong because mature data and security ecosystems already distinguish **local identifiers**, **provenance relations**, and **cross-object equivalence**. W3C PROV’s data model has explicit relations for alternate and specialized entities, noting that two provenance descriptions about the same thing may emphasize different aspects [S1378]. NIST’s OSCAL guidance says identifiers support consistent and reliable reference and linking across models, while the OSCAL POA&M reference repeatedly uses UUIDs to make POA&M instances, observations, findings, assets, risks, and items referenceable, often with per-subject consistency across revisions [S1379][S1380]. These are not dashboard conveniences. They are the object handles on which later reliance rests.

Native operational systems show the same pattern. ServiceNow assigns records a `sys_id` and exposes it through URLs or scripts [S1381]. Jira issues can be addressed by ID or key, and its changelog APIs return per-issue and bulk changelog histories with changelog IDs and issue identifiers [S1382]. GitHub’s Dependabot API identifies an alert by an alert number within a repository and then tracks state and dismissal metadata around that alert [S1383]. Google Security Command Center findings are created under a source with a finding name, source ID, resource name, event time, and state [S1384]. Microsoft Graph security alerts carry their own alert ID, incident ID, evidence collection, detector, classification, determination, and correlation into incidents [S1385].

Normalization and lineage layers make the problem harder rather than solving it. AWS Security Lake’s OCSF material stresses common schemas, versioning, and source-identification fields, but those fields help interpret origin; they do not by themselves prove that two records from unlike systems are the same obligation or finding [S1386]. OpenLineage defines dataset, job, and run entities that are uniquely identified through consistent naming strategies, with extensible facets for enrichment [S1387]. SLSA provenance identifies output artifacts by `subject`, records resolved dependencies with URIs and digests, and treats builder IDs and resource descriptors as verification material [S1388]. CycloneDX’s `bom-ref` provides a unique in-BOM reference that can be used elsewhere in the BOM [S1389]. Each ecosystem is building identity discipline, but each is scoped to its own object model.

The speculative move is to see the cross-system join as a warrantable act. A broker that says “these seven rows are the same residue item” has made a representation distinct from every mapped field inside those rows. It may be able to warrant an exact preserved identifier, a same-namespace match, a deterministic foreign-key join, a hash/digest match, a source-declared link, a probabilistic match above a confidence threshold, or only an analyst-labeled association. Each level supports a different liability boundary.

That is why the thesis belongs here. The winning artifact is not merely a normalized table. It is a **source-object identity warranty schedule**: a compact statement that names the native records, namespaces, join keys, match rules, confidence bands, split/merge decisions, collision handling, excluded near-matches, and correction path. Without it, normalization-loss warranties have no reliable subject.

## Speculative consequences worth tracking

### 1. Field warranties depend on object warranties

A field-preservation table is only as strong as the identity join beneath it. If the wrong Jira ticket is attached to a POA&M item, the due-date mapping may be exact and still misleading. Buyers may therefore ask for object-identity schedules before they accept semantic-loss schedules.

### 2. Local IDs remain visible instead of being swallowed

Packets may preserve every native source identifier: `sys_id`, issue ID/key, alert number, finding name, resource name, incident ID, `bom-ref`, package URL, CPE, provenance subject, digest, and source export row. A normalized canonical ID may be useful, but hiding the native IDs makes disputes harder to replay.

### 3. Same-subject claims become graded

Contracts may distinguish source-declared links, exact same-native-ID matches, deterministic crosswalks, hash/digest matches, artifact-equivalence matches, fuzzy title/date/product matches, analyst-confirmed joins, and unjoined but related records. The broker’s liability cap may depend on which grade was used.

### 4. False joins become more serious than omissions

An omitted record may look like a missing-evidence problem. A false join can make a risky object look remediated, make a remediated object look open, attach the wrong owner, duplicate a closure, or shift a breach into the wrong period. Diligence may price false positives and false negatives differently.

### 5. Split/merge events become amendment events

If a broker later discovers that one normalized object was really two source obligations, or two normalized objects were really one obligation, the packet may need a formal amendment: new canonical IDs, revised histories, changed scores, changed residue counts, and downstream notices to relying parties.

### 6. “Related” becomes different from “same”

A cloud finding may relate to a software component, vulnerability, control, ticket, exception, and waiver without being the same object as any of them. Broker packets may need relation labels such as same-subject, evidence-for, remediation-of, supersedes, duplicate-of, blocks, caused-by, accepted-risk-for, and advisory-context-for.

### 7. Identity confidence becomes a liability dial

A broker may offer different prices and liability caps for exact-ID packets, deterministic-join packets, confidence-scored packets, and best-effort analyst-review packets. The warranty may say that joins below a stated confidence are informational only unless the buyer requests manual review.

### 8. Native vendors become identity witnesses

ServiceNow, Jira, GitHub, Google, Microsoft, SBOM, and provenance providers may be pulled into disputes over whether identifiers were stable, reused, redirected, renamed, migrated, duplicated, or deleted. Their API semantics and retention practices become evidence.

### 9. Migration creates identity debt

When organizations migrate ticket systems, merge repositories, rename assets, change scanner vendors, or consolidate cloud accounts, native identifiers may be reissued, redirected, or preserved only as text. Identity warranties may turn migration mapping files into diligence exhibits.

### 10. Object graphs become poisonable

If identity joins influence underwriting, procurement eligibility, holdbacks, or regulatory treatment, actors may have incentives to create duplicate tickets, split findings, rename assets, close and reopen under new IDs, or seed misleading cross-references. Identity-graph hygiene becomes a control surface.

## Likely artifact shape

The mature artifact probably looks like a **source-object identity warranty schedule** attached to a normalized renewal-history or residue packet. A minimum useful schedule would include:

- **Reliance purpose** — procurement screen, acquisition diligence, cyber-insurance pricing, lending covenant, supervisory review, internal audit, or remediation holdback.
- **Native object inventory** — each source system, endpoint, export, table, object type, native identifier, source timestamp, and retention window.
- **Identity namespace declaration** — whether identifiers are global, tenant-local, repository-local, project-local, BOM-local, version-local, or export-local.
- **Canonical subject spine** — the normalized subject ID and the source objects asserted to describe it.
- **Join-key table** — exact IDs, foreign keys, source-declared links, hashes, digests, package identifiers, resource names, issue keys, alert numbers, product identifiers, and analyst-entered references.
- **Relation type** — same-object, same-subject, duplicate-of, supersedes, remediates, evidence-for, affected-by, accepted-risk-for, blocked-by, child-of, parent-of, or related-only.
- **Confidence grade** — exact, deterministic, source-declared, digest-confirmed, strong heuristic, weak heuristic, analyst-confirmed, disputed, or informational.
- **Collision and ambiguity handling** — what happens when one native ID maps to many canonical subjects, many native IDs map to one subject, or a record matches above threshold to several candidates.
- **Split/merge ledger** — when canonical objects were split, merged, retired, remapped, or corrected, with affected packet versions.
- **Unjoined near-match register** — records that look related but were not joined, with reason codes.
- **Identity-loss disclosure** — missing native IDs, migrated IDs, deleted source objects, renamed repositories, recycled keys, incomplete exports, and text-only references.
- **Replay packet** — source extracts, mapping code, matching thresholds, hash policies, namespace rules, manual review notes, and run metadata.
- **Warranty and liability cap** — which join grades are warranted, which are informational, which are seller-supplied facts, and which cap applies to false join, false split, omitted near-match, or stale remap.
- **Correction path** — who can challenge a match, what native evidence overrides the broker, how downstream packets are amended, and whether prior pricing or eligibility decisions are reopened.

This artifact matters because object identity is the load-bearing seam between raw records and institutional reliance. It lets a broker say, “we warrant exact joins, we represent source-declared joins based on supplied data, we disclose heuristic joins, and we cap liability differently for each.” It lets buyers distinguish a bad mapping from a bad join. And it lets sellers avoid treating every possible related record as the same breach.

## What could falsify or weaken the thesis

- Buyers accept normalized scorecards without asking for source-object identity schedules.
- Native platforms converge on stable cross-system identifiers quickly enough that broker joins become routine plumbing rather than a warrantable act.
- Brokers refuse to expose join confidence because the disclosure creates more liability than trust.
- Most disputes center on semantic loss, retention gaps, or current-state accuracy rather than false joins and false splits.
- Data-room practice keeps raw exports available and easy enough to inspect that separate identity schedules feel redundant.
- Insurers, lenders, and procurement teams prefer broad disclaimers over fine-grained object-identity warranties.
- API vendors provide official crosswalks that make third-party identity matching less valuable.

## Research queue

- Which object class produces the first serious dispute: POA&M item, cloud finding, Jira ticket, Dependabot alert, Microsoft incident, SBOM component, vulnerable package, waiver, or accepted-risk record?
- Do buyers demand exact native-ID preservation, or is confidence-scored identity matching enough for portfolio-level use?
- Which relation vocabulary becomes standard: same-object, same-subject, duplicate-of, supersedes, remediates, evidence-for, or related-only?
- How do liability caps differ between deterministic joins, source-declared links, hash/digest matches, and analyst-reviewed joins?
- Do source vendors add export fields specifically to help brokers preserve identity across migrations and data rooms?
- Are split/merge corrections treated as ordinary packet amendments, breach notices, score restatements, or reopening events?
- Does identity poisoning appear as a deliberate tactic once normalized packets affect premiums, procurement eligibility, or payment holdbacks?
