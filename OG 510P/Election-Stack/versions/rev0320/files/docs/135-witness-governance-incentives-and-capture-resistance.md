# Witness governance, incentives, and capture resistance

**Track:** A (Deployable core)


This document specifies how the **witness set** (cosigners / checkpoint notaries / monitors) is governed, funded, rotated, and audited so that it remains **independent, diverse, and hard to capture** over time.

## Threats (governance-level)

1. **Monoculture / capture**: a single stakeholder class (party, vendor, agency, donor) controls a quorum.
2. **Soft capture**: dependence on a shared funder, managed service provider, or shared security team.
3. **Silent non-participation**: witnesses stop cosigning (or selectively cosign) to create delays or split views.
4. **Witness substitution**: a compromised authority quietly swaps the witness list or witness keys.
5. **Collusion with the log**: witnesses see equivocation but do not disclose it.

## Design principles

* **Clients verify policy, not promises**: clients MUST verify that checkpoints are cosigned according to a *published Witness Policy*.
* **Diversity is a requirement**: quorum is invalid unless it satisfies *stakeholder diversity constraints*.
* **Rotation is routine**: rotation is not a crisis action; it is scheduled and auditable.
* **Funding is transparent**: witnesses MUST disclose funding sources and controlling parties.

## Witnesses as countervailing power

Witnesses exist to provide a **structural counterweight** against the election authority and vendors:
they make it harder for any single actor to rewrite history or suppress evidence without producing detectable divergence.
This is a governance function first; cryptography makes it legible.

Practical expectation: honest witness ecosystems **sometimes disagree** (publish anomalies, file dissent, refuse to cosign).
A “perfectly quiet” ecosystem can be a warning sign (see liveness / capture signals below).

## The witness problem is the whole problem (do not underweight this)

Cryptography can make history **legible**, but it cannot create legitimacy on its own.
In contested environments, the decisive question is often:
**who is willing and able to publish independent disagreement** when it matters?

Minimum posture:
- Design for **partial capture** as normal (some witnesses will be compromised, coerced, or simply absent).
- Make **dissent publishable**: refusal-to-cosign and divergence notes must be easy to publish and mirror (not “handled privately”).
- Treat witness membership as a **sybil surface**: require funding/control disclosures and enforce stakeholder diversity constraints.
- Keep bootstrapping explicit: if a jurisdiction cannot name at least a *small* independent witness set it trusts today,
  Track A claims relying on witness countervailing power must be framed as *degraded* until that ecosystem exists.

## Why the CT analogy is necessary but insufficient

Certificate Transparency works partly because major witnesses (browser/OS vendors) have strong, independent incentives: being seen as complicit in misissuance is existential.

Elections invert some incentives:
- the parties with the strongest ability to pressure election administration may also be the ones with the strongest desire to shape the evidence ecosystem.

Therefore, this archive treats witness governance as *institutional engineering*, not just cryptography:
- prioritize **institutional diversity** (civil society, academia, courts, professional associations, cross-jurisdiction partners),
- make conflicts/funding explicit and auditable,
- assume some witnesses can be pressured, and design so *pressure produces loud evidence* (missed cosigns, policy violations, dissenting checkpoints).



## Boundary condition (say it explicitly)

The witness/monitor ecosystem is the **load-bearing social structure** of this design.
Technical receipts and gossip make equivocation detectable *only if* there exist parties with enough independence and incentive to notice and publish the detection.

Where independent institutions are absent or coerced, the stack can still produce evidence,
but immediate institutional action may not follow. This is not a “technical fix” problem; it is a deployment boundary.
In such environments, prioritize evidence that survives for later adjudication (portable packets, mirrored digests, suppression proofs).


## Normative requirements

### WIT-1 Witness Charter
Each witness operator MUST publish a signed **Witness Charter** (see schema `schemas/WitnessCharter.json`) that includes:

* legal entity name, jurisdiction, controlling persons
* operational security contact + incident disclosure commitment
* funding sources and relationships that could create conflicts
* the category(ies) it claims (e.g., "civil society", "academic", "party", "court", "vendor")

### WIT-1b Public profile (human legibility)

Each witness/monitor operator SHOULD publish a **short public profile** (1–2 pages) that makes the representation duty legible:
who they are, what they check, where they publish, and how they handle dissent.

Template: `artifacts/templates/witness-profile.md`.

Profiles SHOULD include a short **representation‑duty statement** and **material floor/accessibility commitments** (see template sections).


This does not replace signed artifacts (charters, COI JSON, keysets); it links to them.


### WIT-2 Conflicts of interest (COI)
Witness operators MUST publish a signed **COI disclosure** (schema `ConflictOfInterestDisclosure.json`) at least:

* 60 days before election open
* immediately upon any material change

### WIT-3 Admission and removal
Witness admission/removal MUST follow a published **admission policy** modeled after public transparency ecosystems:

* published requirements and review process
* probation / staged rollout
* explicit removal triggers (SLA violations, equivocation, refusal to disclose COI)

See `139-ct-policy-inspired-admission-and-removal.md`.

### WIT-3b Governance as evidence (portable surface)
Witness governance must be legible to outsiders. The federation MUST publish the current witness set and any changes as receipted+gossiped evidence objects, so selective disclosure or surprise changes become provable.

- Envelope kind: `hfv.witness.set`
- Envelope kind: `hfv.witness.set_change`

### WIT-4 Diversity constraints
The Witness Policy MUST define **diversity constraints**, e.g.:

* at least 1 witness from each of *k* stakeholder classes
* no more than *x%* of witnesses funded by the same donor
* no more than *y* witnesses hosted by the same cloud provider / MSP

The federation MUST publish a periodic **Stakeholder Diversity Report** (schema `StakeholderDiversityReport.json`) anchored into checkpoints.

### WIT-5 Term limits and rotation
Witness operators MUST have term limits and a rotation schedule:

* default term: 2–4 years
* staggered rotation so quorum availability remains stable
* emergency rotation procedure for compromise

Rotation MUST be published as a signed `WitnessRotationSchedule.json`.

### WIT-6 Incentive model (minimum viable)
Witnesses SHOULD be funded in ways that minimize capture:

* multi-source funding (public funds + multiple private sources) with caps
* fixed-fee contracts not tied to outcomes
* open procurement, public rate cards

When incentives are used (e.g., decentralized trustee selection), the system SHOULD prefer models where **clients choose trustees/witnesses** and incentives are transparent.



### WIT-7 Behavioral health (“liveness beyond cosigning”)
A witness set can be formally present yet substantively captured.

Therefore, deployments SHOULD treat these as **publishable health signals** (measured over time):

- **Dissent / refusal exists:** refusals-to-cosign, anomaly codes, or disagreement notes are publishable and actually appear over time (a perfectly quiet ecosystem is a warning sign).
- **Independent reporting:** each witness publishes at least one signed public summary per election cycle stating what it checked and what it found (including “no anomalies observed” if true).
- **Responsiveness + drills:** during incidents and drills, witnesses publish timely, bounded attestations that can be replayed (`131` / `schemas/MonitorAttestation.json`).
- **Independent vantage:** critical measurements and hosting do not collapse onto a single provider/MSP/security team (treat convergence as an incident trigger).
- **Disclosure liveness:** COI/funding and stakeholder-class evidence stays current; sudden convergence is treated as an incident trigger (WIT‑4 + monitoring).

These signals do not prove honesty, but they make “silent capture” harder to hide.
### WIT-7b Witness liveness score (pragmatic, publishable)

Cosigning is necessary but not sufficient. A simple, publishable **liveness score** helps detect “formal presence / substantive capture.”

A deployment SHOULD define and publish a bounded scoring rule such as:

- +1 if the witness publishes an **independent election-cycle summary** (even “no anomalies observed”), signed and digest-addressed.
- +1 if the witness participates in at least one **challenge / anomaly response** (files an anomaly code, requests clarification, or dissents from an operator claim).
- +1 if the witness publishes a **timely incident attestation** during a stress window (bounded, replayable).
- −1 if the witness repeatedly misses stress-window SLAs or never participates beyond routine cosigns across multiple cycles.

This is not a truth oracle. It is a *behavioral smoke alarm*.

Record per-witness scores (bounded pointers only) in `artifacts/registries/witness-health-log.csv`.

### WIT-7c Stakeholder classes are a target (front-group defense)

“Diversity constraints” can be satisfied on paper while being empty in substance.
Therefore, Witness Policy SHOULD define:

- how stakeholder classes are defined (and who can propose changes),
- what evidence a witness must provide to claim a class (charter, governance, funding, leadership, membership),
- how **front groups** are handled (material misrepresentation → removal trigger),
- an appeals path that is itself published as evidence.


### WIT-7d Automated / AI-run witnesses (non-human operators)

Automation can be a net-positive: it can continuously verify packets, detect anomalies, and publish replayable reports.
But an automated witness is not “independent” by default — it inherits the incentives and control of whoever can update it.

Therefore, any automated/AI-run witness MUST:
- name a clearly accountable controlling party (human + legal entity),
- disclose the automation surface + update authority (what can change, who can change it, and how changes are announced),
- remain subject to the same behavioral health expectations (dissent, independent summaries, responsiveness), not just cosigning.

See also: `139` (admission/removal) and `172.6` (non-human participation as research posture).


### WIT-7e Required public report (compact)

To keep these signals legible without narrative sprawl, publish a periodic **witness health report** as a signed EvidenceEnvelope:

- Envelope kind: `hfv.witness.liveness_dissent_report`
- Payload schema: `schemas/WitnessLivenessDissentReport.json`
- Attachments: `gossip_summary` + `transparency_receipt` (anti selective disclosure)

This report is a compression artifact: it names *who was live*, *who missed cosigns*, and *what dissent/refusal items exist*, with pointers/digests (not long prose).


### WIT-8 Bootstrapping (initial witness set as a named trust assumption)

The **first** witness set is necessarily appointed or invited by someone (often the election authority).
Name this as a trust assumption:

- the design’s value increases as the witness set diversifies beyond the initial trust anchor,
- admission should be staged: start with a conservative quorum, then expand stakeholder classes over time,
- treat early “single-ecosystem” witness sets as *provisional* and publish an explicit expansion plan (rotation schedule + admission roadmap).

## Operational checks

* quarterly: COI refresh + diversity report
* pre-election: witness key validation drill + compromise response tabletop
* election week: daily availability check + cosignature completeness check

## Outputs

* `WitnessCharter` (one per witness operator)
* `ConflictOfInterestDisclosure` (per witness operator)
* `WitnessSet` / `WitnessSetChange` (for membership + policy changes; must be receipted+gossiped)
* `WitnessRotationSchedule` (per election cycle)
* `StakeholderDiversityReport` (periodic)
* `FundingTransparencyReport` (periodic)
* `WitnessLivenessDissentReport` (periodic; `hfv.witness.liveness_dissent_report`)
