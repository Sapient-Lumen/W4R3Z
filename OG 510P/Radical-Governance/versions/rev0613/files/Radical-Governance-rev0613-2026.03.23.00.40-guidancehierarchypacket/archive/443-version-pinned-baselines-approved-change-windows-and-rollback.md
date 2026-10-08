# 443 — Version-pinned baselines, approved change windows, and rollback

## One-line thesis

A public AI service should run from a **named approved baseline** — model version, prompt or policy layer, retrieval corpus, thresholds, integrations, and dependencies — and every material change should move through a documented change window with rollback-ready evidence.

## Why this matters

Many public AI controls are written as if the system stays still after launch. In practice, the live system drifts: a provider updates the underlying model, a prompt layer is edited during an incident, a retrieval source changes, a threshold moves, or a new plugin appears. When these shifts are poorly tracked, teams cannot tell whether a new failure came from policy, data, infrastructure, vendor change, or local configuration. Governance becomes retrospective guesswork.

Current official materials support a tighter pattern. The 2025 NIST Cybersecurity Framework Profile for AI highlights configuration management, including managing configuration drift, as a core mission-assurance concern. NIST’s Generative AI Profile says teams should track and document relevant version numbers, planned updates, hotfixes, and other change-management information. The NCSC’s secure-AI guidance treats secure operation and maintenance as including update management and information sharing after deployment. The GAO Green Book says configuration management controls should develop and maintain operating and security features and control changes to configuration.

The archive should therefore make a practical change-governance move: **no consequential public AI should run as an unnamed moving target**. Teams need a stable approved baseline and a governed path for changing it.

## Pattern pack

### 1. Define one approved operating baseline

For each live use case, maintain a compact baseline record covering at least:

- provider and model version,
- prompt or policy templates,
- retrieval sources or index version,
- threshold and routing settings,
- safety filters and redaction layers,
- connected tools or APIs,
- and fallback configuration.

This is the configuration the service is actually allowed to run.

### 2. Treat vendor updates as local governance events

A hosted-model upgrade or silent provider-side capability shift should not be treated as mere vendor background noise. If the change can affect outputs, latency, routing, safety behavior, or logging, it should trigger local review against the approved baseline.

### 3. Use approved change windows for material modifications

Material changes should pass through a documented window that states:

- what is changing,
- why the change is needed,
- what evidence supports the change,
- who approved it,
- what rollback path exists,
- and what public records or internal dossiers must be refreshed.

### 4. Pin the live system to a recoverable prior state

Teams should be able to answer not only what version is live, but what prior state they can revert to if the change degrades fairness, safety, accuracy, usability, or legal compliance.

### 5. Keep emergency fixes visible

Hotfixes made during incidents or outages should be time-stamped, attributed, and reviewed after the fact. Emergency pressure explains fast changes; it should not erase the need to record them.

### 6. Re-run targeted checks when the baseline changes

A material change should trigger proportionate re-checks such as:

- regression testing against prior failure modes,
- subgroup checks where relevant,
- citation or source-discipline checks,
- operator workflow validation,
- and review of whether notice, impact dossiers, or public registries need refreshing.

### 7. Expose baseline identity to reviewers and operators

Operators, reviewers, and incident leads should be able to see which approved baseline handled a case. Review without baseline identity makes root-cause analysis slower and more political than it needs to be.

## Guardrails

- No consequential live service without a named approved baseline.
- Material changes should move through documented change windows.
- Vendor-side shifts should be treated as governance-relevant when they affect behavior.
- Emergency fixes should be recorded and later reviewed.
- Rollback should be practical, not theoretical.

## Failure modes

- **moving-target governance**: the live system changes faster than the oversight record.
- **vendor drift blindness**: provider changes are ignored because the team did not edit local code.
- **rollback fiction**: the service claims it can revert but cannot reconstruct the previous working baseline.
- **hotfix amnesia**: emergency changes are never fully written down or retrospectively approved.
- **baseline-free review**: incident and appeal reviewers cannot tell which configuration produced the contested output.

## Practical tests

A live service passes this pattern when it can answer yes to all of the following:

1. Does the team maintain a named approved operating baseline for the use case?
2. Are material changes recorded with evidence, approver, effective date, and rollback path?
3. Are vendor-driven changes assessed against the local approved baseline?
4. Can the service revert to a known prior state if a release causes harm or instability?
5. Can reviewers identify which baseline handled a given period or contested case?

## Compression rule for the archive

If a consequential public AI system cannot say **which exact approved baseline is live and how it rolls back**, it is still too change-opaque to govern confidently.
