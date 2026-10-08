# 425 — Portable appeal packets and log retention

## One-line thesis

Contestability fails when the evidence trail is scattered or ephemeral; every consequential AI-assisted decision should leave behind a portable review packet built from logs, provenance, and operator actions.

## Why this matters

Many public appeals fail before anyone weighs the merits because the underlying record is weak:

- logs were never enabled,
- records are spread across systems that cannot be joined,
- no one can show which workflow version ran,
- operator overrides are missing,
- the explanation given to the person cannot be tied back to durable evidence,
- by the time a complaint arrives, critical records are gone.

Official guidance points toward a tighter evidence rule. The EU AI Act requires high-risk systems to technically allow automatic event logging over the lifetime of the system, requires logging sufficient for traceability, and requires providers and deployers to retain logs under their control for at least six months unless other law applies. It also provides for access to documentation and logs on reasoned request by competent authorities. NIST’s AI RMF playbook likewise pushes organizations to document data provenance and to respond to and document detected or reported negative impacts.

The archive should therefore prefer a **portable appeal packet** over a merely latent backend audit trail.

## Pattern pack

### 1. Define a minimum decision packet for consequential uses

Every consequential AI-assisted decision should generate a review packet containing, at minimum:

- a stable decision or case identifier,
- date and time of processing,
- workflow or model version,
- relevant policy or ruleset version,
- input categories actually used,
- output or score returned,
- any confidence bands or thresholds applied,
- human actions taken after the output,
- the notice or explanation shown to the affected person.

This does not require dumping all raw data into the packet. It requires preserving the chain that lets reviewers reconstruct what happened.

### 2. Treat log retention as a floor, not the whole answer

A minimum retention rule is not enough if complaints typically arrive later or if records become incoherent across systems. The archive should insist that operators:

- keep logs for at least the applicable legal minimum,
- freeze relevant evidence when a complaint, appeal, incident, or litigation hold begins,
- preserve join keys across workflow components long enough for review.

A right to explanation without preserved evidence is a brittle right.

### 3. Join logs, provenance, and human interventions into one reviewable packet

Appeal packets should not be raw machine logs alone. They should join three layers:

- **system trace**: what the system did,
- **provenance trace**: what data, configuration, and version context applied,
- **human trace**: what staff accepted, rejected, edited, or overrode.

This prevents the familiar defense that “the model did X” while the real harm came from workflow logic or operator practice.

### 4. Make the packet exportable across oversight channels

The same core packet should be usable by:

- internal reviewers,
- supervisors,
- ombuds or inspector functions,
- courts or tribunals where lawful,
- regulators or market-surveillance authorities where relevant.

That means using durable identifiers, date-stamped fields, and a stable schema rather than internal screenshots and improvised notes.

### 5. Distinguish public explanation from full internal evidence, but keep them linked

Not every internal detail should be sent directly to the affected person, but the public-facing explanation and the internal packet must be joinable. Each explanation should reference:

- the decision identifier,
- the packet version,
- the reviewing office,
- how additional records may be requested under the applicable regime.

This allows privacy, security, and legal constraints to be managed without severing accountability.

### 6. Preserve evidence of material changes

A packet should show whether the system or workflow had materially changed since prior approvals or audits, including:

- model or ruleset changes,
- threshold changes,
- new input fields,
- changed fallback or override rules,
- changed population or service context.

Otherwise reviewers evaluate a decision as if it came from a different system than the one actually used.

### 7. Use packet completeness as a deployment gate

A service should not be allowed to rely on automated assistance in consequential decisions if it cannot generate a minimally complete packet on demand. The archive should treat missing packet machinery as a **stop-ship problem**, not a documentation backlog.

## Guardrails

- Minimize and protect sensitive data while preserving reviewability.
- Record enough to reconstruct the decision, not everything imaginable.
- Keep redactions reviewable and documented.
- Ensure packet extraction can happen without vendor-only intervention.
- Test packet production during pilots, incidents, and mock appeals.

## Failure modes

- **vanishing evidence**: logs exist briefly, then disappear before challenge.
- **split-brain records**: no one can join model output, workflow state, and human action.
- **explanation without proof**: the user gets a rationale that cannot be tied to durable records.
- **vendor bottleneck**: packet extraction depends on the supplier’s goodwill or billable time.
- **retroactive reconstruction**: staff manually rebuild a packet after the fact from memory.

## Practical tests

A packet regime passes when it can answer yes to all of the following:

1. Can the service export a stable packet for any challenged consequential decision?
2. Does the packet include system, provenance, and human-action traces?
3. Are logs retained long enough and frozen when review begins?
4. Can oversight bodies obtain the relevant records through a defined path?
5. Can the public-facing explanation be linked back to the evidence packet that supports it?

## Compression rule for the archive

If a service cannot produce a **portable packet showing what ran, on what basis, under whose authority, and with what human intervention**, it is not yet genuinely contestable.
