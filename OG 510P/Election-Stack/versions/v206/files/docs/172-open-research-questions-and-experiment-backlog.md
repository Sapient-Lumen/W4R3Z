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

Evidence that would resolve these:
- empirical case studies of contested elections + what evidence was actually decisive,
- a taxonomy of remedies tied to evidence sufficiency (what evidence enables which remedy),
- tabletop exercises that end in concrete “court-ready” packet templates.

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

## 172.3 Remote return realities (Track B)

- What meaningful coercion-mitigation exists in uncontrolled environments?
- What does “graceful failure” look like (if remote return is attacked, how does the system revert)?
- How do we avoid building “disaster bait” that encourages unsafe deployment?

Evidence that would resolve these:
- red-team studies in constrained lab environments,
- usability studies of verification flows under coercion pressure,
- “graceful failure” drills demonstrating safe reversion paths.

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

This backlog is intentionally not “owned” by a single person.
If you are an LLM maintainer: add candidates, but also add **what evidence would resolve it**.
