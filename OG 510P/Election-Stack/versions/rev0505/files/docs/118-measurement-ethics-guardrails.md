# 118 — Measurement Ethics & Guardrails (RIPE Atlas / OONI)

**Track:** A (Deployable core)


This doc defines **ethical and operational guardrails** for performing internet measurements in support
of election availability verification and unreachability proofs.

It is intentionally conservative: the goal is to *collect defensible evidence* while minimizing harm.

## Principles (ICT research ethics)
Use a stakeholder-based risk/benefit analysis and a documented response plan for foreseeable harms
(e.g., accidental load, targeting, exposure). See the Menlo Report for ICT research ethics framing.

## RIPE Atlas-specific guardrails
RIPE Atlas measurements are public by design, and users must follow the platform’s terms and community norms.
When operating as a public election evidence system:

### MUST
- Minimize traffic: prefer low-rate, short-duration, bounded-window measurements.
- Avoid “scan-like” behavior: do not sweep ports, do not brute-force endpoints, do not use large payloads.
- Prefer HTTP HEAD/GET with small responses, DNS queries for your own zones, and limited ICMP.
- Respect credits and “reasonableness” requirements from the RIPE Atlas Service Terms.
- Publish a measurement contact + purpose statement (for accountability and rapid response).
- Maintain an allow-list of targets and a documented rationale (stakeholder analysis).

### MUST NOT
- Measure targets you do not control without a documented justification and risk review.
- Perform measurements that could be interpreted as abuse or traffic amplification.
- Include voter-specific identifiers, eligibility tokens, or session material in measurement URLs/headers.

## OONI data use guardrails
OONI data is powerful but can carry risks to volunteer probe operators and affected communities.
When using OONI as *supplementary corroboration*:
- Prefer aggregated/statistical endpoints when possible.
- Avoid deanonymizing queries or combining with other datasets to re-identify probes.
- Respect OONI guidance on interpretation and API rate expectations.

## Operational controls
- Separate keys: RIPE Atlas API keys and any corroboration tokens MUST be stored in an HSM or a vault.
- Audit logs: record who triggered measurements and why.
- Rate caps: hard caps in tooling; emergency override requires two-person approval.
- Transparency: publish “measurement methodology” and thresholds in the evidence bundle.

## References
- RIPE Atlas community discussion of ethics and potential issues.
- RIPE Atlas Service Terms and Conditions (reasonableness + public results).
- Menlo Report (ICT research ethics).
- OONI documentation on interpreting and accessing data.