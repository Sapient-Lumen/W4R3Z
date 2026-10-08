# Monitor governance and accountability

**Track:** A (Deployable core)


Monitors (auditors, watchdogs, and public verification services) are required to detect equivocation, suppression, and policy violations. This document specifies how monitors are held accountable so that "monitoring" is not purely ceremonial.

## Threats

* **Paper monitors**: claim to monitor but do not actually check.
* **Cartel monitors**: a small set of monitors dominates public narratives.
* **Selective monitoring**: monitors check only in low-risk periods.
* **Retaliation risk**: monitors with sensitive findings are pressured into silence.

## Normative requirements

### MON-1 Public inspection challenges
The system MUST support **public inspection** challenges where third parties can request proof that a monitor performed specific checks (e.g., consistency proof validation for a checkpoint range, or policy validation for a results package).

Monitors MUST publish signed **Monitor Attestations** (schema `MonitorAttestation.json`) that include:

* the exact checkpoint IDs / hash ranges checked
* verifier build/provenance identifiers
* outputs (OK / violation types)
* reproducible command references

### MON-2 Diversity and redundancy
At least two independent monitor implementations MUST be available and actively used. Monitors SHOULD be run by mutually distrustful entities.

### MON-3 Disclosure safety
The governance process MUST define:

* protected disclosure channel(s)
* coordinated disclosure for high-impact vulnerabilities
* public disclosure deadlines and exceptions

### MON-4 Removal and replacement
Monitor admission/removal MUST be documented similarly to witness policy, with clear triggers for removal (fraudulent attestation, persistent negligence).

## Outputs

* Monitor attestations anchored into the PBB
* Public inspection logs
* Monitor diversity report