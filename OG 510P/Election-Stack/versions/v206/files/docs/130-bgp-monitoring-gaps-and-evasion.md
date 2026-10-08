# 130 BGP Monitoring Gaps and Evasion: Implications for Election Evidence

**Track:** A (Deployable core)


This system uses network measurements and monitoring to detect selective suppression and split-world behavior. However:

> Absence of evidence in public BGP monitors is not evidence of absence.

## 130.1 Threat: attacks that evade route monitoring

Attackers can craft BGP attacks that:
- affect many ASes, but
- avoid propagation to common monitor infrastructures / route collectors, or
- exploit filtering behaviors (e.g., uRPF interactions) to cause persistent DoS without obvious alarms.

## 130.2 Implications

- Treat BGP monitoring as **supplementary**, not authoritative.
- Prefer **data-plane evidence**: multi-vantage HTTP/DNS/OHTTP reachability + content hash parity.
- Use cohort shaping detection to ensure evidence is not “quietly correlated.”

## 130.3 Requirements

- URPs MUST include at least one data-plane measurement type (HTTP or TLS fetch) that yields a verifiable content hash.
- Dispute playbooks MUST include a “monitoring evasion” branch: if BGP monitors show nothing, escalate to additional data-plane measurements and cohort rotation rather than declaring “no routing attack.”
