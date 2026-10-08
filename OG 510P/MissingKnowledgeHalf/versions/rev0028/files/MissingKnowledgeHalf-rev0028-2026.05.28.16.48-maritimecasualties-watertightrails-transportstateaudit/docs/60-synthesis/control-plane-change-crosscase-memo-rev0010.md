# Control-plane change cross-case memo — rev0010

candidate pattern: software control-plane changes can fail at speed when validation, monitoring, deployment, and rollback are not independent.

## Shared pressure

The four software/IT cases promoted in rev0010 do not share a single mechanism. They share a higher-level epistemic problem: the layer meant to make the system knowable or containable was itself part of the failure boundary.

- Knight Capital: the deployment and alerting controls did not contain a stale code path before automated trading amplified it.
- Northeast Blackout EMS grain: the alarm/monitoring layer failed silently enough that operators did not know they were losing visibility.
- Equifax: public vulnerability knowledge did not become verified remediation in the affected asset, and exfiltration monitoring was inactive.
- CrowdStrike: content validation and rollout control did not prevent a privileged content update from crashing endpoints before recovery became necessary.

## Non-equivalences

Knight is not a breach. Equifax is not merely an outage. CrowdStrike is not malicious exploitation. The blackout EMS record is not the whole blackout. CVE/NVD/KEV are not accident boards.

## What would mature or demote the pattern

Maturation requires counterexamples and a denominator: successful staged deployments, vulnerability-prioritization successes, alarm self-failure caught early, public postmortems with recommendation closure, and incidents where the same fields are absent. Without these, `MKH-PAT-0010` remains a search handle, not a theory.
