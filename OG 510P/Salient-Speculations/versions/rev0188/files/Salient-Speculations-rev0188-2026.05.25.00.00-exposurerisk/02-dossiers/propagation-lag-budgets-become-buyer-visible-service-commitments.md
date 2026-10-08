---
id: ss-migrated-propagation-lag-budgets-become-buyer-visible-service-commitments
revision_promoted: pre-rev0182
migration_status: inferred-rev0182-targeted
title: Propagation-lag budgets become buyer-visible service commitments
constellation:
- managed-legibility
- operational-resilience
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- recipient-scope precision
- state freshness
enforcement_surface:
- procurement / framework contract
- underwriting / insurance renewal
- audit / assurance engagement
artifact_type:
- notice
- audit log
- reason code
lifecycle_stage:
- route
- publish
- rely
failure_modes:
- nonpropagation
- stale-state
source_refs:
- S1227
- S1228
- S1229
- S1232
- S1233
- S1234
- S1235
- S1236
- S1237
- S1238
---
# Propagation-lag budgets become buyer-visible service commitments

## Core claim

Once consequential notice, approval, override, escalation, deprovisioning, and continuity workflows depend on **delegate changes, role removals, group-membership edits, downstream SaaS provisioning, mailing-list refresh, queue-owner rewiring, or cross-tenant sync**, the scarce object is no longer only post-incident proof that propagation lag existed. It becomes the **portable promise of how much lag another institution should expect and what remedy applies if that window is missed**. A future institution will increasingly want more than “changes are eventually consistent” or “sync runs periodically.” It will want a compact timing bundle: **change class, included downstream systems, excluded surfaces, normal sync cadence, maximum convergence window, revocation-lag ceiling, manual-expedite path, verification method, logging surface, and breach remedy**. At that point, **propagation-lag budgets become buyer-visible service commitments**.

## Why this belongs in the archive

The archive’s current lifecycle-governance lane already runs through **preliminary-final-effective state machines become procurement calendars**, **provisional-use policies become procurement boilerplate**, **grandfathering clauses become price terms**, **state-transition notice services become a quiet vendor market**, **notice-authenticity proofs become an assurance layer**, **delivery attestations become an evidentiary service tier**, **nonreceipt reason codes become a liability grammar**, **escalation-path liveness checks become a compliance service**, **delegate-freshness proofs become a service metric**, and **delegate-change propagation delays become a standing incident class**. That sequence explains how consequential states become publishable, routable, trustworthy, receipt-bearing, diagnosable, live-routed, freshness-attested, and finally reconstructable when downstream systems had not yet converged. It still leaves one sharper commercial bottleneck under-described: **when propagation timing is already known to vary, who sells a warranted window that another institution can schedule around?**

Current identity and provisioning systems already expose timing as an explicit operational parameter rather than a hidden implementation detail. Google Cloud says IAM changes are eventually consistent, gives distinct propagation-time estimates for policy edits versus group and nested-group changes, notes that removals usually propagate more slowly than additions, and explicitly says those estimates can inform how administrators modify access [S1227]. AWS says IAM changes take time to become visible from all endpoints because of replication and caching, recommends verifying propagation before production workflows depend on the change, and Amazon EC2 documentation goes further by recommending that administrators allow five minutes for policy changes to propagate before testing updates [S1228] [S1232]. Microsoft’s Azure RBAC troubleshooting guidance says role changes can take up to ten minutes to take effect and, in some management-group/data-plane cases, several hours [S1233]. These are already proto-budgets: disclosed windows that other workflows are expected to respect.

Provisioning platforms expose the same move even more directly. Microsoft says provisioning synchronizations typically occur every twenty to forty minutes after the initial cycle completes [S1234], and its cross-tenant synchronization guidance says subsequent cycles occur approximately every forty minutes [S1235]. Its entitlement-management material says some assignment and resource-role changes can take up to twenty-four hours in Microsoft Entra ID, plus additional propagation time to other Microsoft Online Services or connected SaaS apps [S1229]. GitHub’s enterprise troubleshooting guide treats this cadence as concrete enough to name externally, stating that the default SCIM provisioning interval for Entra ID is forty minutes [S1238]. Atlassian lets administrators choose automatic sync intervals of every one, two, four, or twenty-four hours, with changes applying on the next sync [S1236]. Okta likewise lets administrators schedule incremental and full imports hourly, daily, or weekly, and explicitly frames the schedule as an operator-controlled timing choice rather than as an invisible background process [S1237]. That is already a market signal: **customers are not only consuming eventual consistency, they are being asked to choose, tolerate, and operationalize timing windows**.

Taken together, these materials suggest the next bottleneck above propagation-delay forensics: **propagation timing becomes contractible**. Once downstream convergence is slow enough to document, configurable enough to select, and consequential enough to monitor, buyers will increasingly stop treating it as mere backend texture. They will ask which surfaces are inside the declared window, whether removals have a tighter ceiling than additions, what happens to emergency revocations, what logs prove convergence, which customer actions can force an out-of-band sync, and what credits, liability carve-outs, or workflow holds apply if the window is breached.

So this belongs in the archive because it names the layer above incident reconstruction: **lag becomes something another institution may buy, compare, and rely on in advance**. Once published sync cadences and convergence windows begin shaping staffing handoffs, approval deadlines, deprovisioning safety, incident escalation, and effective-date cutovers, propagation timing starts looking like SLA language, procurement exhibits, exclusion clauses, premium support tiers, and eventually a first-class service commitment.

## Speculative consequences worth tracking

### 1. Convergence windows become quoted fields

Vendors may increasingly publish separate timing commitments for direct policy edits, group changes, revocations, downstream SaaS provisioning, and emergency override paths instead of hiding them inside generic “eventual consistency” language.

### 2. Revocation lag gets tighter treatment than addition lag

Because removals are often more safety-critical than grants, institutions may increasingly demand stricter ceilings, different monitoring, and faster breach escalation for revoke/remove paths than for add/grant paths.

### 3. Coverage maps become procurement artifacts

Buyers may increasingly ask which downstream systems are inside the propagation budget, which are merely best effort, which require the next scheduled sync, and which remain excluded from any timing commitment.

### 4. Manual expedite paths become premium features

“Sync now,” on-demand provisioning, emergency revoke paths, and privileged cutover acceleration may increasingly be sold as higher-tier reliability features rather than as buried admin conveniences.

### 5. Budget breaches become evidentiary events

A missed convergence window may increasingly generate the same kind of logs, incident tickets, service credits, and customer-facing explanations that uptime or latency breaches already generate.

### 6. Workflow design starts waiting on convergence proof

Higher-consequence actions may increasingly pause on a convergence checkpoint rather than proceed the moment the source-of-truth changes, especially for approvals, privileged access, and regulated notice.

### 7. Timing asymmetry becomes a competitive metric

Vendors may increasingly compete on ninety-fifth-percentile revocation lag, downstream-app convergence coverage, and manual-expedite success rates, not only on average sync speed.

## What could falsify or weaken the thesis

- Buyers remain content with rough guidance, admin docs, and best-effort sync controls, without pushing propagation timing into procurement or contract terms.
- Propagation timing stays too tenant-specific, topology-specific, or workload-specific for vendors to warrant in a meaningful cross-customer way.
- On-demand sync, manual retry, and emergency workarounds solve most real disputes cheaply enough that formal budgets never become important.
- Downstream systems converge quickly enough in practice that timing windows stop mattering outside niche identity-governance edge cases.
- Regulators, auditors, and insurers continue focusing on whether the source record changed, not whether the declared propagation window was satisfied.

## Research queue

- Which budget becomes the headline metric: max revocation lag, max add-user lag, max downstream-app convergence time, or percentage of covered systems within window?
- Which domain buys first: privileged-access governance, enterprise SaaS administration, cyber incident response, regulated notice, or cross-tenant collaboration?
- What counts as a sufficient commitment bundle: cadence, max window, included surfaces, excluded surfaces, manual-expedite path, monitoring logs, and breach remedy?
- How should vendors price asymmetry between grants and revocations, or between direct bindings and nested/group-derived bindings?
- When does a workflow need convergence proof instead of just a published window: emergency revocation, approval delegation, payment release, customer offboarding, or legal-notice reliance?
