---
id: ss-0175-split-merge-correction-notices
revision_promoted: rev0175
title: Split/merge correction notices become packet amendment events
constellation:
- managed-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- diligence-packets
- organizational identity / entity resolution
bottleneck_type:
- identity matching
- correction throughput
- source-of-truth precedence
- appealability / redress
enforcement_surface:
- procurement / framework contract
- audit / attestation / assurance
artifact_type:
- correction record
- notice
- state label
lifecycle_stage:
- dispute
- correct
- restate
- propagate
- archive
failure_modes:
- false-join
- false-split
- nonpropagation
- procedural-debt
refactor_cluster:
- remedy-lifecycle
- provenance-lineage
remedy_role: split/merge correction propagation
remedy_stage:
- correct
- propagate
- archive
consolidation_status: standalone-mechanism
state_family:
- remedy
- provenance
lineage_role: registry-steward and transformer-broker
lineage_stage:
- correct
- supersede
- archive
state_terms:
- source-bound
- lineage-gap
---
# Split/merge correction notices become packet amendment events

## Core claim

Once normalized renewal-history packets, residue inventories, waiver histories, exception lineages, non-comparable-state schedules, source-object identity warranties, and transform-escrow bundles start affecting price, eligibility, insurance, procurement admission, holdbacks, covenants, or supervisory posture, later correction of the packet’s subject graph stops being data housekeeping.

If a broker later learns that one canonical packet subject was really two obligations, that two subjects were duplicates, that a native record was only related but not the same subject, that a source object was transferred, renamed, retired, rejected, withdrawn, or re-keyed, or that a prior relation label should have been “successor,” “duplicate,” “superseded,” “merged-into,” “split-from,” or “related-only” rather than “same-subject,” the old packet has changed economic meaning without any new underlying breach.

That is the speculative claim: **split/merge correction notices become packet amendment events**. The question is no longer merely whether the current normalized packet is accurate. It is who must be told that an earlier relied-upon packet has been amended, which decisions are affected, whether old scores or holdback triggers need restatement, whether previously released money can be reopened, and whether buyers, sellers, insurers, lenders, agencies, auditors, or source vendors receive a dispute window.

## Why this belongs in the archive

The archive’s current lifecycle-governance lane has moved from status-transition notices through convergence gates, gate-expiry disputes, waivers, compensating-control bundles, post-waiver validation, residue inventories, extension-lineage disclosures, renewal-history normalization, normalization-loss warranties, non-comparable-state carve-outs, source-object identity warranties, and transformation-code escrow. That sequence leaves one obvious remaining failure mode: the packet can be perfectly normalized, legally caveated, and replayably produced, yet still need amendment because the broker later corrected the identity graph underneath it.

Official identity-management practice already distinguishes subject correction from ordinary field update. FHIR’s patient-link model separates `replaced-by`, `replaces`, `refer`, and `seealso` relationships so that duplicate, successor, main-source, and overlapping records do not collapse into a single undifferentiated link [S1414]. Its patient-merge operation is even more explicit: one patient is the source, one is the target, references may need to be updated from source to target, source records may become inactive, duplicate content may be de-duplicated or deleted, provenance should be created, and downstream systems may need notification because clients can otherwise miss data or keep using a stale record [S1415]. The point is not healthcare-specific. Mature identity systems treat merge as a consequential event with relation labels, surviving subjects, provenance, reference updates, and notice paths.

FHIR provenance then supplies the evidentiary grammar. Provenance exists to record activities that created, revised, deleted, or signed resource versions, and can point to the versions that mattered for assessing quality, reliability, trustworthiness, or authenticity [S1416]. A brokered diligence packet that amends its subject graph needs the same kind of memory. A later packet cannot merely say “corrected.” It has to say what was corrected, which earlier packet version was relied on, which native records moved, who authorized the correction, what changed in the derived score or warranty boundary, and whether the old version remains historically visible.

Developer platforms already expose relationship changes as named events. GitHub issue-event types include `marked_as_duplicate`, `unmarked_as_duplicate`, `renamed`, `transferred`, `merged`, `closed`, and `reopened` [S1417]. GitHub timeline events are used to show activity and determine notification [S1418]. Jira issue-link types expose directional relationship labels such as `Duplicated by` and `Duplicates`, while Jira webhooks carry issue events and field-level changelog arrays for issue updates [S1419][S1420]. These systems show a pattern the archive can generalize: when object relationships change, serious consumers need an event stream, not only a final object state.

Security-advisory ecosystems show why correction history matters even more when third parties rely on identifiers. NVD’s CVE Change History API is designed to let users monitor when and why vulnerability records change, including modifications, reanalysis, CPE deprecation remaps, and CWE remaps [S1421]. NVD also keeps REJECTED CVE records visible when an identifier was a duplicate, was withdrawn, was incorrectly assigned, or otherwise should no longer be used [S1422]. A rejected identifier is not just gone; it becomes a visible warning that prior reliance may be invalid. That is almost exactly the packet-amendment problem.

Advisory and bill-of-materials formats add the versioning discipline. CSAF tracking metadata carries release dates, current state, versioning, and revision history while keeping the advisory tracking ID stable across versions [S1423]. CycloneDX says that when an existing BOM is modified, its version should be incremented, and when several BOMs have the same serial number, systems should use the most recent version [S1424]. These conventions give the diligence-packet world a ready analogy: stable packet identity does not mean the same version remains authoritative after correction.

Relationship vocabularies and patch formats round out the shape. SPDX defines typed relationships between elements and emphasizes clear directionality [S1425]. JSON Patch defines compact operations such as add, remove, replace, move, copy, and test against target paths [S1426]. A split/merge correction notice therefore does not have to be a vague narrative. It can become a machine-readable amendment: subject A was split into A1 and A2; records X and Y were moved; relation R changed from same-subject to related-only; score denominator changed; residue count moved from one covenant bucket to another; this earlier packet version is superseded for specified reliance purposes.

That is why the thesis belongs here. The archive already has the original production problem: how a normalized packet is built, warranted, caveated, and replayed. This dossier adds the afterlife problem: how a packet is formally amended when the canonical subject graph itself changes after someone has relied on it.

## Speculative consequences worth tracking

### 1. Correction notices become reliance events

A broker’s quiet database correction will not be enough when prior packets supported price, underwriting, eligibility, holdback release, or covenant compliance. The correction itself becomes a reliance event: a dated, versioned, routed notice that says an earlier packet should be read differently from this point forward or for this reliance class.

### 2. Canonical IDs acquire survivorship rules

Markets will need to know which identifier survives a merge, which retired identifier remains queryable, whether split children inherit the parent’s history, whether duplicate IDs are invalidated or redirected, and whether prior references must be followed automatically. Canonical IDs stop being labels and start having survivorship law.

### 3. Split and merge have asymmetric economics

Merging two subjects may make a prior residue count look smaller, or may concentrate many weak histories into one riskier subject. Splitting one subject may reveal that a seller satisfied one branch but not another, that a holdback should have applied only to part of a bundle, or that a waiver history was wrongly attached to an unrelated obligation. The direction of correction matters.

### 4. Retrospective scores become restatable

If scorecards, residue ratios, extension counts, renewal churn, closure velocity, or accepted-risk inventories were calculated over the wrong subject set, the old score may need a restatement. That creates familiar accounting-like questions: was the restatement material, who must receive it, does it reopen prior approvals, and does it affect compensation or eligibility already granted?

### 5. Reliance graphs become distribution lists

A broker cannot notify everyone unless it knows who relied on which packet version, for which purpose, under which rights. The archive already has notice-routing, delivery attestation, delegate freshness, and propagation-lag concerns. Split/merge corrections add a new reason to maintain a reliance graph: every packet recipient is a potential amendment recipient.

### 6. Materiality thresholds harden

Not every correction should trigger urgent notice. Some remaps only clean up a display name; others move a material finding across a covenant boundary. Contracts may define material amendment thresholds: score delta, holdback delta, residue-age delta, eligibility change, closure-state change, warranty-boundary change, denominator change, or non-comparable-state reclassification.

### 7. Time-travel packet views become expected

A relying party will need to ask: what did the packet say on the closing date, what did the broker know then, what does the corrected graph say now, and when did notice become effective? Current-state dashboards will not satisfy that question. The packet system will need historical views, amended views, and “as-relied” views.

### 8. “Current corrected” and “historically relied upon” diverge

A broker may be correct to update all current packet displays after a merge, but a dispute may turn on the version that was visible at a prior gate. Institutions will need vocabulary for current corrected state, historical relied-upon state, superseded state, invalidated state, and correction-pending state.

### 9. Source vendors become correction witnesses

When a broker changes a canonical identity graph, source-system owners may be pulled in as witnesses: did the native issue really transfer, was the duplicate marker reversed, was the advisory rejected, did the source API remap a deprecated ID, did the source vendor maintain the old identifier as a tombstone, and when was the change published?

### 10. Amendment fatigue creates batching rules

If brokers issue too many correction notices, reliance parties will ignore them. If they issue too few, material corrections will be missed. This will create notice classes: emergency amendment, material restatement, scheduled correction digest, non-material hygiene update, source-vendor correction, broker-discovered correction, disputed correction, and correction-withdrawal notice.

### 11. Unmerge becomes a premium support function

The hard case is not merge; it is unmerge after reliance. If two subjects were wrongly collapsed and later separated, the broker must reconstruct which histories, approvals, waivers, residues, and scores belonged to each branch at each earlier point. The ability to unmerge cleanly becomes part of the broker’s trust premium.

### 12. Correction windows become negotiated

Sellers will not want indefinite reopening of old packets. Buyers and insurers will not want a broker to correct material identity errors without giving them a chance to adjust. Expect windows: time to challenge correction, time to submit native evidence, time to restate score, time to reopen holdback, time to update procurement eligibility, and time after which the amended packet becomes final.

## Likely artifact shape

A mature artifact probably looks like a **packet amendment notice** attached to the corrected packet, the earlier packet version, and the transform-escrow bundle. A minimum useful notice would include:

- **Amendment ID** — stable identifier for the correction event, independent of the packet version and the native source-system event.
- **Affected packet IDs and versions** — every packet, extract, scorecard, warranty schedule, residue inventory, waiver history, or diligence exhibit whose interpretation changed.
- **Correction class** — split, merge, unmerge, duplicate marking, duplicate reversal, transfer, rename, successor map, rejected identifier, withdrawn identifier, retired identifier, source remap, relation-label change, denominator correction, score restatement, or historical-view correction.
- **Subject survivorship** — which canonical subject survives, which subject becomes inactive, which subject is split into children, which source IDs become aliases, which records remain queryable, and whether old IDs redirect, tombstone, or remain historical-only.
- **Before/after graph** — source objects, canonical subjects, relation labels, confidence scores, native namespaces, join keys, and same-subject assertions before and after correction.
- **Patch representation** — machine-readable delta showing add, remove, replace, move, copy, or test operations against the packet graph or derived fields.
- **Reason code** — duplicate discovered, false duplicate reversed, source transfer, native rename, source vendor correction, deprecated-ID remap, rejected identifier, withdrawn advisory, broker false join, broker false split, retention-gap discovery, manual-review outcome, or appeal decision.
- **Provenance** — who initiated the correction, which source events or APIs support it, when it was detected, when it became effective, who approved it, whether source-vendor confirmation exists, and which transform-run or replay evidence was used.
- **Derived-field impact** — score changes, residue-count changes, waiver-history movement, extension-count changes, age-bucket changes, non-comparable-state changes, coverage-ratio changes, eligibility changes, covenant changes, or holdback changes.
- **Reliance-purpose impact** — whether the correction affects procurement eligibility, acquisition diligence, cyber-insurance pricing, lending covenants, regulatory submission, remediation holdback, supplier scorecard, internal audit, or supervisory review.
- **Materiality classification** — non-material correction, disclosure-only amendment, score restatement, covenant-impacting amendment, holdback-impacting amendment, eligibility-impacting amendment, warranty-boundary amendment, or emergency correction.
- **Notice recipients** — buyer, seller, insurer, lender, auditor, agency, procurement platform, source-system vendor, escrow custodian, scorecard consumer, delegated contact, or downstream subscriber.
- **Notice proof** — channel, authentication proof, delivery attestation, recipient scope, delegate freshness, nonreceipt reason code, resend policy, and effective-notice timestamp.
- **Dispute window** — time to challenge the correction, evidence required, who adjudicates, whether old packet reliance is stayed, and whether amended fields are provisional pending appeal.
- **Economic treatment** — no price effect, price adjustment, reserve adjustment, holdback reopening, release suspension, covenant cure period, underwriting repricing, eligibility suspension, or indemnity trigger.
- **Supersession rule** — whether the corrected packet supersedes earlier versions for all purposes, only prospective use, only specified reliance purposes, or only after dispute-window expiry.
- **Rollback or withdrawal path** — how an erroneous correction notice is withdrawn, reversed, replaced, or marked historical-only.

This artifact matters because it gives the market a middle path between silent correction and full relitigation. It lets brokers amend a packet without pretending no one relied on the old version. It lets buyers preserve rights when old scores become wrong. It lets sellers bound retroactive reopening. It lets insurers and lenders ask whether the correction changes the risk they priced. And it lets downstream systems update their own records without guessing whether a source-object change is legally material.

## New bottlenecks exposed

### Amendment-recipient registries

A broker needs to know who has a right to receive each correction. That is not the same as who downloaded the packet. Some parties may have reliance rights; others may be viewers, auditors, vendors, agents, or expired subscribers. Packet infrastructure may need a registry of reliance grants and amendment-recipient scopes.

### Corrected-score restatement policy

A score can be recomputed after every correction, but not every recomputation should reopen a transaction. Markets will need restatement policy: minimum delta, affected denominator, material row class, stale reliance cutoff, and whether restatement is prospective or retroactive.

### Historical-packet supersession

If a corrected packet version exists, what exactly happens to the old one? It may remain visible as the version relied on at closing, be superseded for future use, remain admissible for a dispute about knowledge at the time, or be invalidated for all purposes after a correction notice.

### Correction authentication

A fake correction notice could move money, release a holdback, damage a supplier score, or alter procurement eligibility. The existing archive concerns around notice authenticity, delivery proof, channel trust, and anti-spoofing become relevant again at the amendment layer.

### Cross-broker correction propagation

If multiple brokers normalize the same source universe, one broker’s split/merge correction may need to propagate to others, or at least become comparable. Otherwise one buyer’s packet may show a merged subject while another’s still shows two separate subjects.

## What could falsify or weaken the thesis

- Buyers and insurers treat normalized packets as one-time reports and disclaim all reliance after issuance, limiting the importance of later corrections.
- Brokers refuse to maintain reliance-recipient graphs because the notice burden is too costly or exposes too much downstream use.
- Contracts say identity corrections are prospective-only unless fraud is involved, preventing old scores or holdbacks from reopening.
- Native source systems converge on stable globally unique identifiers and high-quality successor maps quickly enough that broker-level split/merge corrections become rare.
- Market participants prefer broad indemnity pools or insurance adjustments over granular packet-amendment notices.
- Source-system license terms, privacy duties, or security restrictions prevent brokers from disclosing enough before/after graph detail to make correction notices useful.
- Downstream systems consume only current corrected state and ignore amendment history, even when old packets were relied upon.
- Courts or regulators treat broker packet corrections as ordinary data updates rather than as notices with legal effect.

## Research queue

- Which correction type becomes disputed first: duplicate reversal, source transfer, false join, false split, rejected identifier, source-vendor remap, renamed record, or denominator restatement?
- Which relying party demands formal amendment rights first: buyer, insurer, lender, government procurement team, auditor, prime contractor, regulator, or seller?
- Do contracts give buyers retroactive rights after identity correction, or do sellers successfully limit corrections to prospective reliance?
- What threshold makes a correction material: score delta, holdback delta, closure-state change, residue-age change, non-comparable-state reclassification, or eligibility change?
- Do brokers expose before/after graphs openly, or do they hide details behind escrow-access arbitration because native source data and mapping logic are sensitive?
- Do source vendors publish signed duplicate, transfer, rejection, successor, and remap events so brokers can cite authoritative correction evidence?
- Does correction notice delivery reuse ordinary state-transition notice infrastructure, or does it become a separate amendment channel with higher authentication and dispute requirements?
- Do packet consumers build automated correction ingestion, or do amendment notices remain human-readable exhibits attached to transactions?
- Which becomes more valuable: the broker that detects corrections fastest, the broker that minimizes false corrections, or the broker that preserves the cleanest historical packet views?
