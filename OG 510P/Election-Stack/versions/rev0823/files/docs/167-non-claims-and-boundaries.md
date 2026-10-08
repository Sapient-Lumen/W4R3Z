# 167. Non-claims and boundaries (what we do *not* assert)

**Track:** Shared

This document prevents accidental overreach. It lists what this archive **does not claim** today,
and what would have to become true to promote a boundary into a conditional or hard claim.

Non‑claims are not pessimism; they are **scope integrity**.

## 167.1 Non-claims (current)

### N‑1 Endpoint integrity for uncontrolled clients
We do **not** claim to secure a voter’s personal device against malware, accessibility spyware, or adversarial OS/browser stacks.

- Track A response: assume compromise; use verification patterns and evidence lanes (`06-client-security.md`, `16-client-verification-patterns.md`).
- Upgrade path (conditional): requires attested/managed devices + strong relying party verification (Track C: PO-201).

### N‑2 Coercion resistance for remote voting
We do **not** claim coercion resistance for remote voting in uncontrolled environments.

- Track B may explore mitigations, but must state what coercion models remain unsolved.
- Upgrade path: requires constraints outside crypto (environment control, social/legal enforcement, and/or new coercion‑resistant paradigms).



**Experience note (human reality):** a coerced voter often experiences voting as a performance of compliance under surveillance.
Crypto mitigations can create *windows* of freedom (revote, supervised override), but they only help if the voter:
(a) knows the window exists, (b) believes using it is safe, and (c) can physically access a supervised environment.
Where those conditions fail, coercion succeeds regardless of protocol design.

**Related boundary (privacy):** We also do **not** claim to prevent turnout surveillance or identity leakage
via eligibility/revocation transparency surfaces in remote‑return designs (timing, batch size, geography, log‑joining attacks).
Treat this as Track B research (`docs/75`, `docs/81`, `docs/172.3.1`; hazard **HZ‑026**).


### N‑3 Availability “under any adversary”
We do **not** claim the system will remain available under nation‑state scale disruption, telecom sabotage, or coordinated insider outage games.

- Track A focus: evidence of disruption + graceful degradation + recovery (`109-availability-transparency-log.md`, `87-incident-response-communications-and-public-proof.md`).
- Upgrade path: requires resilient infrastructure + governance + operational redundancy; still unlikely to be absolute.

### N‑4 “The log makes the outcome correct”
We do **not** claim transparency alone guarantees a correct outcome.
Transparency makes *inconsistencies and suppression provable* and supports legitimate remedies.

- Track A focus: dispute‑ready evidence + audits/recounts as the recovery mechanism (`09-audit-recovery.md`).

- Non-claim: Track A does **not** attest the integrity of proprietary voting system software/firmware/update channels.
  If the underlying system is compromised at the supply-chain level, the evidence layer may faithfully record outputs of a corrupted process.
  The recovery mechanism remains the paper ballot of record + audits/recounts; wrapper transparency recommendations increase dispute value (`17-supply-chain-and-build-integrity.md`).

### N‑5 Certification/compliance by default
We do **not** claim certification readiness without a defined conformance profile and mapped test assertions.

- Track A includes alignment work (`19-certification-and-standards-alignment.md`), but conformance is a separate effort.

### N‑6 Dual-use constraints (publication safety)
We do **not** claim this archive is an “attack manual,” nor should it be used to produce operational exploit steps, targeted disruption playbooks, or disinformation campaigns.

- When describing attacks, prefer **capability-level** statements and **defense/evidence** requirements over step-by-step procedures.
- Public artifacts MUST avoid per-voter identifiers and MUST follow a redaction policy where sensitive lanes exist (`92`, `98`, `173`).
- Any live-system testing must be authorized, coordinated, and scoped to avoid public harm; default to simulations and lab harnesses.
- Worked example pattern for **verifiable refusal/non-claim events** (outside elections, but structurally relevant): IETF SCITT individual draft on refusal events (`xref: draft_scitt_refusal_events_02_html`).



### N‑7 Non-human franchise / AI voters
We do **not** claim this archive’s eligibility and identity mechanisms support non-human voters (including AI systems).

- Today, eligibility tokens and registration flows assume **human** identity proofing.
- Extending franchise to non-human persons raises an unsolved **sybil problem** (“one entity, one vote” when entities can be copied or instantiated cheaply) and a creator-control problem.
- Near-term posture: non-human agents may still participate **without suffrage** as monitors/witnesses/verifiers, provided controlling parties and incentives are disclosed and outputs are replayable.
- This is treated as **research** (see `docs/172-open-research-questions-and-experiment-backlog.md`, section 172.6) and must not be implied by Track A deployments.
- This question is **generated by the archive’s own principles** (“no receipt, no legitimate effect”): do not treat it as absurd; treat it as a bounded research agenda.



## 167.2 Boundaries by track (how to read the archive safely)

### Track A boundaries (deployable core)
Track A must avoid claims that require:
- attested manufacturing/provenance ecosystems (Track C),
- coercion resistance in uncontrolled environments,
- guaranteed endpoint integrity,
- guaranteed availability under state‑level disruption.

### Track B boundaries (research annex)
Track B may propose mechanisms, but must include:
- explicit non‑claims,
- threat model scope,
- what evidence would upgrade the claim,
- red‑team / abuse cases (“how this could go wrong socially”).

### Track C boundaries (North Star)
Track C assumes additional ecosystem properties. Track C must:
- state assumptions explicitly,
- defend against **verification‑ecosystem capture** (endorsement split‑views, selective auditor blindness),
- keep “what would have to be true” as the core deliverable.

## 167.3 A note on “full-stack”
“Full-stack” here means the archive designs and connects the whole election pipeline.
It does **not** mean the archive embeds external corpora.

External sources are referenced by citations and pinned where feasible (`evidence/lock/`).
When this archive disagrees with prevailing expert guidance, it should say so explicitly and explain the reasoning.
