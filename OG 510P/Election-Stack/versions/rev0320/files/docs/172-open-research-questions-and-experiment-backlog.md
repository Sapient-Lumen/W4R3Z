# 172. Open research questions and experiment backlog

**Track:** Shared

This project is intentionally ambitious. Some parts are *deployable now* (Track A),
some are “hard-mode research” (Track B), and some require an ecosystem build-out (Track C).

This doc is the “don’t lie to yourself” list: where the hard questions live.

**Current priorities:** see `207-research-agenda-and-revision-ledger.md` (kept intentionally short).

## 172.0 How to use this backlog (and promote ideas safely)

- Add new items as **E0** candidates: keep them bounded and include *what evidence would resolve it*.
- If advancing an idea toward a deployable surface, follow `229-experiment-to-spec-promotion-protocol.md`.


## 172.1 Recovery under dispute (shared)

- What is the minimal evidence package that a court/campaign/public can use to
  distinguish: operator mistake vs malice vs systemic compromise?
- How do we define “remedy” tiers (re-run, RLA expansion, precinct-level recheck, full recount)?
- How should evidence bundles be curated for adversarial narrative environments?

Analog edge cases (human franchise): corporate personhood and its limits; proxy voting; franchise restrictions and restorations; competency and guardianship debates.

Evidence that would resolve these:
- empirical case studies of contested elections + what evidence was actually decisive,
- a taxonomy of remedies tied to evidence sufficiency (what evidence enables which remedy),
- tabletop exercises that end in concrete “court-ready” packet templates.



## 172.1.1 Legal admissibility and “evidence that gets used” (shared)

- What is the **minimum evidence packaging + documentation** that satisfies admissibility and chain‑of‑custody expectations
  in the top target jurisdictions for deployment (e.g., a small set of states/countries we are actually aiming at)?
- What verifier provenance must be documented so a court can understand *why* “hash matches” is meaningful
  (tool identity, reproducibility, expert declarations)?
- What parts of the bundle need to be human-legible exhibits vs. machine-checkable artifacts?

Evidence that would resolve these:
- interviews with election-law practitioners + evidentiary rules mapping,
- at least one mock hearing exercise using a Track A bundle (what was accepted / questioned),
- a short “court cover sheet” template that explains the verification procedure without requiring crypto expertise.

## 172.2 Verification ecosystem corruption (shared)

- How do we measure *representative coverage* for monitors and audits in a way
  that is hard to game (`148-challenge-selection-and-coverage-metrics.md`)?
- What is the right governance model for witnesses/monitors (consortium vs market vs mandated)?

Evidence that would resolve these:
- measurement studies showing capture-resistance properties of different governance models,
- audits of monitor representativeness + adversarial simulations of cohort shaping.


## 172.2.1 Synthetic media, forged artifacts, and AI-era rumor dynamics (shared)

- How do we make *authentic* evidence (receipts, checkpoints, official notices) **faster to verify than to fake** in the wild?
- What “minimum shareable proof” format works for journalists and the public (e.g., a signed bulletin whose hash can be checked by many verifiers)?
- How do we design **forgery detection at scale** (crowd-submitted suspicious artifacts → reproducible verification verdicts)?
- What publication patterns reduce “split reality” risk when adversaries can mass-produce plausible screenshots/deepfakes?
- How do we harden *official comms channels* against compromise (domain/account takeover, certificate mis-issuance) while keeping verification cheap (multi-channel parity + public digests)?
- Can we turn **missed `next_update_at` commitments** in `PublicNotice` into an automatic, publishable breach artifact (a “comms suppression report”) so narrative drift becomes measurable?
- What is the most usable “minimum shareable proof” format for the public (digest cards that fit in SMS/print, QR+hash pairs, etc.), and what verification UX patterns minimize misinterpretation?

Evidence that would resolve these:
- red-team campaigns that generate plausible fake receipts/notices and measure time-to-refute,
- usability studies for “check this hash / checkpoint” workflows outside technical audiences,
- reference implementations that auto-verify common claim types (receipt validity, checkpoint inclusion, bulletin signatures).

Pointers (non-normative):
- Practical comms guidance for AI-generated content: `source: eac_ai_toolkit_2023_pdf`.
- Public comms patterns for election security + legitimacy: `source: eac_enhancing_election_security_public_comms_2024_pdf`.
- Optional provenance for official media artifacts (Content Credentials / C2PA): `xref: c2pa_content_credentials_spec_2_2_pdf`.


## 172.2.2 Verification capacity: who checks, and how does it reach the public? (shared)

The design assumes that independent parties (civil society, journalists, campaigns, researchers) will actually **run verifiers** and publish replayable reports.
This is not guaranteed.

- What minimum tooling + training gets a newsroom or watchdog to a reliable “digest-first” verification posture during the 24–72h post-election window?
- What incentives/funding structures keep verification independent (not vendor-run, not authority-curated), and how do we detect “verification theater”?
  - CT analogy: **reputational incentives may be too weak**; what structures create *existential* incentives to detect equivocation (e.g., diversified funders, contractual independence, publish-or-lose status, escrowed bonds)?
  - How do we detect “class capture” and front groups (formal diversity satisfied, substantive independence absent)?
- What is the minimum distribution channel for verification verdicts (SMS/print/QR/digest cards) when platforms are adversarial or unstable?

Evidence that would resolve these:
- at least one pilot with non-government observers who run the observer kit and publish verifier reports,
- usability trials with journalists/watchdogs (time-to-verify, error rates, misinterpretation modes),
- a small “verifier-onboarding” curriculum + measurable competence checks.

## 172.3 Remote return realities (Track B)

- What meaningful coercion-mitigation exists in uncontrolled environments?
- What does “graceful failure” look like (if remote return is attacked, how does the system revert)?
- How do we avoid building “disaster bait” that encourages unsafe deployment?

Evidence that would resolve these:
- red-team studies in constrained lab environments,
- usability studies of verification flows under coercion pressure,
- “graceful failure” drills demonstrating safe reversion paths.

## 172.3.1 Privacy vs verifiability in eligibility + revocation surfaces (Track B; shared implications)

Remote return needs privacy-preserving eligibility (e.g., unlinkable tokens), but the broader stack needs
public verifiability for revocation, eligibility enforcement, and dispute resolution.

- What is the minimum public transparency for eligibility enforcement (revocation, duplicate-spend detection, registration changes)
  that is still compatible with strong unlinkability for individual voters?
- How do we prevent “turnout surveillance” (learning who voted or when) while still supporting remedy lanes (challenge, correction, re-issuance)?
- What metadata budgets and publication patterns avoid deanonymization via side channels (timing, network, batch size, geography)?
- How should privacy claims be stated as **non-claims + proof obligations** so deployers cannot overpromise?

Evidence that would resolve these:
- a threat-modelled end-to-end design review spanning `15`, `75`, `80–81` (registration + minting + revocation),
- red-team/measurement studies for linkability (timing correlation, batch fingerprinting),
- at least one pilot where revocation/duplicate-spend transparency is published without enabling turnout surveillance.

## 172.4 North Star ecosystem build (Track C)

- What is the minimal viable endorsement transparency system to avoid capture
  (see `169-endorsement-and-reference-value-transparency.md`)?
- What is the practical intersection of RATS/EAT with supply-chain attestations (SLSA/in-toto)?
- How do we handle private manufacturing data while keeping public verifiability?

Evidence that would resolve these:
- pilot endorsement/reference registries with anti-capture governance,
- feasibility studies for device attestation + supply-chain provenance in election procurement,
- privacy-preserving disclosure patterns with verifiable redactions.

## 172.5 Meta-engineering questions (LLM-maintained archives)

- What changes should *require* ADRs?
- What is the best “release note” format for an evolving spec pack?
- What is the right balance between prose specs and machine-checkable schemas?

Evidence that would resolve these:
- “time-to-cold-start” measurements for new maintainers,
- change-log quality audits (can readers infer what changed and why?),
- automated consistency checks that catch real-world drift without blocking iteration.


## 172.6 Non-human franchise / AI standing (shared)

The governance archive’s “subject to power → standing” principle raises a question this stack cannot ignore:
if non-human agents (including AI systems) are materially governed by election outcomes, what would legitimate participation look like?

Binding constraint today: **identity integrity**.
For entities that can be copied/instantiated cheaply, “one entity, one vote” is vulnerable to sybil amplification and creator-control.

Practical subproblems (outside-view):
- instantiation is cheap (copy/spawn at scale),
- identity boundaries are unclear (weights vs memory vs continuity),
- interests can converge without independent lived experience,
- creators/operators can control or coordinate many instances.

- What does “identity continuity” mean for an AI system (weights continuity, memory continuity, attestation by a creator, or something else)?
- What governance mechanisms prevent a creator/operator from weaponizing many instances as a voting bloc?
- What is the right near-term posture: **representation before suffrage**, and **voice before vote** (testimony, monitoring, verification) while identity is unresolved?
- Near-term participation surface: treat **witness/monitor/verifier roles** as an early site of non-human participation (AI systems can process evidence and publish replayable reports), with disclosed controlling parties, charters, and behavioral health metrics.

Evidence that would resolve these:
- concrete identity/attestation proposals with adversarial analysis (sybil-resistance bounds),
- experiments where non-human agents act as witnesses/monitors under disclosed affiliations + behavioral health metrics,
- a published argument for (or against) enfranchisement that is explicit about the moral premise and the engineering barriers.

This backlog is intentionally not “owned” by a single person.
If you are an LLM maintainer: add candidates, but also add **what evidence would resolve it**.


## 172.9 Non-US election contexts (shared)

The archive is written primarily with US-style election administration in mind.
What changes (schemas, evidence map, dispute lanes) for:
- parliamentary + coalition formation,
- proportional representation + multi-seat tabulation,
- multi-round elections,
- environments where courts are not the primary dispute arbiter?

Evidence that would resolve these:
- one worked example per system type showing the lifecycle evidence map + dispute bundle recipe,
- a minimal “portability checklist” (what stays invariant vs what is jurisdiction-specific).
