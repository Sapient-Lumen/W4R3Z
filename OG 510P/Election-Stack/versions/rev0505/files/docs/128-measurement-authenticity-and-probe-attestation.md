# 128 Measurement Authenticity and Probe Attestation

**Track:** A+C (Core + North Star)


Multi‑vantage evidence can be attacked at the **measurement layer** (fabricated results, compromised probes, or compromised measurement controllers).

## 128.1 Threats

- **Compromised probe** reports false reachability.
- **Compromised measurement controller** fabricates results or suppresses “bad” results.
- **Platform-wide manipulation** (insider, legal compulsion, supply chain).
- **Replay** of old “healthy” results during an outage.

## 128.2 Principles

1. Prefer **redundancy** and **cross‑validation** over trusting a single platform.
2. Make measurement pipelines **reproducible** (raw inputs + hashing + tool versions).
3. Where possible, use **remote attestation** for operator‑controlled probes.

## 128.3 Requirements

### Evidence structure

Every URP MUST include:
- raw result references (or raw results) with hashes
- time window definition
- tool version, config hash, and cohort plan hash

### Cross-validation

URPs SHOULD include at least two independent measurement sources.
If only one source is available, the URP MUST be labeled `SINGLE_SOURCE` and MUST trigger increased skepticism thresholds in dispute resolution.

### Operator-controlled probes

If the operator runs its own probe fleet, the fleet SHOULD support:
- secure boot and measured boot
- signed measurement agent
- optional hardware-backed remote attestation to prove the agent and config match a published build

## 128.4 Attestation profile (optional)

This pack defines a profile for probe attestation that is **publicly verifiable**:
- publish probe identity keys and firmware hashes (privacy-preserving)
- publish signed attestations bound to a measurement batch
- auditors can verify “this batch came from this build/config”

## 128.5 Limits

Remote attestation increases confidence but adds complexity and supply-chain dependence.
In high-stakes deployments, **diversity** (different HW vendors, different hosts, different admins) matters as much as cryptographic attestation.
