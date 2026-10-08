# Selection & sortition integrity (random selection as legitimacy infrastructure)

See also: `143-deliberative-systems-and-citizens-assemblies.md` (deployment) and `145-intensity-voting-quadratic-and-allocation.md` (hybrids).
**Problem:** Any system that claims legitimacy via *representation* or *impartiality* can fail quietly if the **selection process** is biased, gamed, coerced, or non-auditable. “Random” that is not **verifiable** becomes theater.

This memo defines a minimal, portable **Selection Integrity Protocol (SIP)** for:
- citizens’ assemblies / juries / panels / oversight boards
- audit sampling (procurement, benefits, policing, taxation, inspections)
- scarce-resource allocation (when lotteries are legitimate)
- appointment pools (where final choice is constrained but not fully random)

It is designed to compose with: legitimacy receipts (`106`), deliberation binding (`111`), information interfaces (`115`), and rulemaking change control (`118`).

---

## The Selection Integrity Protocol (SIP)

### SIP-0: Public selection definition
Before any draw, publish a **Selection Definition**:
- **Population frame:** who is eligible, with explicit inclusions/exclusions.
- **Representation target:** stratification variables (if any) and quotas/weights.
- **Selection method:** pure lottery vs stratified lottery vs two-stage invite/confirm.
- **Consent & safety:** how contact/consent is obtained; safety accommodations; anti-coercion plan.
- **Disqualification rules:** conflicts-of-interest, incapacity, legal ineligibility.
- **Publication scope:** what will be disclosed and what will be protected (privacy-by-design).

*(Representative deliberative best-practice emphasizes transparent recruitment + stratified random sampling against census-like data.)* [BIB-OECD-RDP-EVAL-2021]

### SIP-1: Randomness source must be independently verifiable
Use a **public randomness beacon** or equivalent verifiable source:
- **Unpredictable** before the time of draw.
- **Publicly replayable** after the draw (anyone can recompute).
- **Tamper-evident** (hash-chained / signed records).
- Prefer multiple independent sources combined (defense-in-depth).

Candidate sources:
- NIST Randomness Beacon (signed, hash-chained pulses). [BIB-NIST-BEACON] [BIB-NIST-IR8213]
- Distributed randomness beacons (threshold / multi-party). [BIB-DRAND] [BIB-DRAND-FC23]

### SIP-2: “Draw Receipt” is mandatory
Every selection produces a **Draw Receipt (DR-*)**:
- Selection Definition hash
- Randomness source identifiers (beacon, pulse/round number, signatures)
- The seed derivation function (explicit)
- The sampling algorithm version (explicit)
- A privacy-preserving commitment to the selected set (e.g., salted hash list)
- A public reproducibility link / instructions

This is the selection analog of a Decision Receipt (`106`) and Rule Change Receipt (`118`).

### SIP-3: Stratification without bias
Stratified selection is legitimate only if:
- the stratification variables and target distribution are published in advance,
- the *invitation and acceptance* process is auditable (nonresponse is the classic failure mode),
- the algorithm minimizes unequal selection probabilities subject to representation constraints.

See fair panel-selection approaches that explicitly trade off representativeness and equal probability. [BIB-FLANIGAN-FAIR-ALGO-2021]

### SIP-4: Anti-coercion & anti-buyout
Selection is vulnerable to “soft coercion”:
- employer pressure, community intimidation, bribery, threats
- stigmatization, doxxing, retaliation

Minimum protections:
- protected communication channel + confidentiality options
- anti-retaliation remedies + interim protection (see service clocks `108`)
- rotate and randomize sensitive oversight roles (limits targeting)
- publish aggregated stats, not individual identities by default

### SIP-5: Replacement rules that don’t reintroduce bias
If selected participants decline or become ineligible:
- use **pre-drawn alternates** from the same randomness event (or a documented reseed rule),
- preserve stratification targets,
- log replacements with **DR-appendix** entries.

### SIP-6: Eligibility frame audits
The selection frame itself can be captured (e.g., who is “on the list”).
- publish frame construction rules,
- run periodic frame audits (random checks),
- provide contestability: “I should be eligible / I should not be listed.”

---

## Selection modalities (when each is appropriate)

### A. Pure lottery (impartiality)
Use when fairness is “equal chance” and demographics are not a legitimacy requirement
(e.g., audit sampling, some scarce-resource allocations).

### B. Stratified lottery (microcosm legitimacy)
Use for citizen assemblies / panels where representativeness is the legitimacy anchor. [BIB-OECD-RDP-EVAL-2021]

### C. Two-stage: random invite → consent → stratified final set
Often necessary in practice; legitimizes only with audited nonresponse controls and transparent algorithms.

### D. Constrained appointment (bounded discretion)
When you *must* appoint (specialized expertise), constrain the discretion:
- publish an eligibility pool and criteria,
- use random shortlists,
- bind appointments with `ADR-*` / appointment receipts (`113`, `115`).

---

## Failure modes & circuit breakers

| Failure mode | Symptom | Default breaker |
|---|---|---|
| Frame capture | suspicious eligibility shifts | freeze + independent frame audit |
| Nonresponse bias | representation targets drift | extend recruitment, oversample, or rerun draw |
| Randomness dispute | “rigged” accusations | publish DR-*; third-party replay verification |
| Coercion | withdrawals clustered around a faction | anonymity option + interim protection |
| Silent substitution | replacements without receipts | invalidate decision unless DR-appendix exists |

---

## Minimal metrics (publishable, low-bloat)
- **Selection reproducibility:** % of draws with complete DR-*.
- **Nonresponse rate** by stratum; deviation from target distribution.
- **Replacement rate** and reasons.
- **Contest outcomes:** eligibility challenges and corrections.
- **Coercion signals:** withdrawals after contact events (privacy-preserving aggregation).

---

## Bibliography keys added/used
- [BIB-NIST-BEACON], [BIB-NIST-IR8213]
- [BIB-DRAND], [BIB-DRAND-FC23]
- [BIB-OECD-RDP-EVAL-2021]
- [BIB-FLANIGAN-FAIR-ALGO-2021]
