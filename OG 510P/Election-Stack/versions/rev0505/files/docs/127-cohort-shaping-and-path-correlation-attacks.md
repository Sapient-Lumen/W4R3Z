# 127 Cohort Shaping and Path-Correlation Attacks (Availability/Evidence)

**Track:** A (Deployable core)


This document treats **multi‑vantage measurement evidence** (URPs, parity reports, ATL entries) as an attack surface.

## 127.1 Threat: cohort shaping

An attacker tries to ensure that “diverse” probes are **effectively co‑located** in the routing system, so the evidence still looks multi‑vantage while sharing one or two hidden failure domains.

Common techniques include:

- **Selective routing / selective announcements**: Anycast and multi‑site services can deliberately announce prefixes to only some regions/ASes; attackers can also shape reachability via routing policy and selective propagation.
- **Hijacks/diversions that evade monitoring**: Attackers can craft BGP attacks that avoid being observed by public route collectors/monitors, while still affecting many ASes.
- **Stealth DoS via uRPF interactions**: hijacking techniques can trigger filtering decisions that block legitimate traffic in ways that may look like benign “network issues.”
- **Probe platform bias**: Probe distribution is often **skewed by ASN/region**; naïve random sampling can concentrate in a few eyeball networks.
- **Measurement interference/noise**: concurrent measurements can add noise and variance, letting attacks hide inside “normal jitter.”

## 127.2 Security goal

Make “multi‑vantage outage evidence” **representative and adversary‑resistant**:

- **Detect** when the cohort collapses into correlated paths/failure domains.
- **Prove** the cohort selection process and constraints (auditability).
- **Respond** by rotating cohorts and escalating to cross‑platform / independent probes.

## 127.3 Requirements (normative)

### Cohort diversity constraints

Cohort selection MUST satisfy constraints published in a signed `ProbeCohortPlan`:

- Cap the maximum share of probes from a single ASN (e.g., ≤ 15%).
- Require a minimum number of distinct ASNs and countries (configurable).
- Require a minimum path diversity score (see §127.4) for key targets.

### Rotation and unpredictability

- The system MUST support cohort rotation on a published cadence (e.g., hourly during election week).
- The specific cohort for time window *t* SHOULD be derived via a public randomness beacon / committed seed to limit pre‑computation by attackers.

### Cross‑platform redundancy

For high‑stakes events (election day), URPs MUST include at least **two** independent classes of vantage:
- (A) external measurement platform(s) (e.g., RIPE Atlas), AND
- (B) operator‑controlled probes in independently hosted networks, AND
- (C) optional corroboration datasets (non‑authoritative, used for context only).

### Noise and interference controls

Measurement schedules MUST include interference controls:
- limit concurrent measurement load per probe
- prefer randomized backoff
- record platform load signals in evidence bundles when available

## 127.4 Path‑correlation detection

Define a *Path Correlation Report* for each target and window:

- Extract AS‑paths from traceroute (best‑effort).
- Compute similarity metrics (e.g., Jaccard on AS‑sets; LCP length on AS‑sequence).
- Flag “collapse” when:
  - cluster size ≥ threshold, OR
  - entropy of ASN distribution drops below threshold, OR
  - path diversity score falls below threshold.

When collapse is detected, the system MUST:
1) issue a `CohortShapingAlert` anchored into ATL and PBB checkpoints, and
2) rotate the cohort and re‑measure, and
3) include both pre‑ and post‑rotation evidence in the same public bundle.

## 127.5 Limits and honest claims

- This mitigates *evidence capture* and *representativeness disputes*.
- It does NOT prevent routing attacks; it makes selective suppression and “it worked for me” disputes **provable** and improves confidence in evidence.
