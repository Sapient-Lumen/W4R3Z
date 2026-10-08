# 218 — Epistemic status tags & confidence rubric (tight, deception-resistant)

**Track:** Shared


Elections disputes fail as often from **interpretation drift** as from missing data.
This doc defines a *small* labeling discipline for statements in claim cards (`217`), PublicNotices (`186`/`195`/`219`),
and verifier reports (`193`) so readers can tell the difference between:

- what was **directly observed / measured**,
- what was **reported by a third party**,
- what is an **inference**,
- and what is still **unknown**.

It intentionally does **not** introduce new schemas or envelope kinds. It is a writing + review convention.


## 218.1 The tag set (use these words; avoid bespoke hedges)

Use one (or more) of the following tags for any *load-bearing* statement in a claim card or public notice:

- **OBSERVED:** first-hand human observation tied to a concrete evidence object (photo/video/log with provenance).
- **MEASURED:** instrumented measurement tied to a concrete evidence object (probe result, parity snapshot, verifier run).
- **ATTESTED:** a signed statement by a role/authority *inside the system* (e.g., poll worker attestation), with keys and envelope.
- **REPORTED:** a statement from an external actor (caller, media, party, social post) treated as an input signal, not a fact.
- **INFERRED:** a conclusion that depends on explicit reasoning from other tagged statements.
- **DISPUTED:** two or more credible accounts conflict; the conflict is part of the claim.
- **UNKNOWN:** the system does not currently know (and should not pretend to know).

**Rule:** if you find yourself writing “appears”, “likely”, “probably”, “we think”, replace it with an explicit tag
plus the minimal evidence pointers that justify it (`163` tokens).


## 218.2 Confidence (use a 3-level scale; define it by evidence, not vibe)

Add a confidence marker for the *claim card’s* main claim statement and for any major inference:

- **HIGH:** the statement is supported by the expected evidence set (or a clearly stated, justified substitute), and the verifier path is straightforward.
- **MEDIUM:** evidence is partially present, or relies on one weak link (single vantage, single witness, missing corroboration); the statement should not be used for final adjudication yet.
- **LOW:** evidence is thin, indirect, or primarily REPORTED; publish only with explicit “what would raise confidence” pointers.

Confidence is about **this packet’s evidence completeness**, not about the author’s authority.


## 218.3 Minimal formatting (keep it small and consistent)

In *human-first* markdown (claim cards, notices), prefix the sentence or bullet with:

- `[OBSERVED|HIGH] ...`
- `[MEASURED|MEDIUM] ...`
- `[REPORTED|LOW] ...`

For multi-step reasoning, keep the chain explicit:

- `[MEASURED|HIGH]` probe cohort shows unreachability from 7/9 vantage points. `EXAMPLE:...`
- `[INFERRED|MEDIUM]` likely localized blocking, not global outage (needs `MEASURED` corroboration). `DOC:...`


## 218.4 Review checklist (what to look for)

When reviewing a claim card (`217`) or a PublicNotice (`186`/`195`):

1. Every “this matters” sentence has a tag.
2. INFERRED statements cite the premises they depend on (by digest or token).
3. REPORTED statements are never promoted to OBSERVED/MEASURED without a new evidence object.
4. UNKNOWN is used where the system truly does not know.
5. Any public-facing conclusion has an explicit “what would change this” sentence when confidence is MEDIUM/LOW.


## 218.5 Where this plugs in (pointers)

- Claim cards: `DOC:docs/217-claim-cards-and-traceability-minspec.md` + `TEMPLATE:artifacts/templates/claim-card.md`
- Incident triage loop: `DOC:docs/216-incident-triage-and-evidence-quickmap.md`
- Publishable verification output: `DOC:docs/193-publishable-verifier-reports.md`
- Comms as evidence: `DOC:docs/186-incident-communications-as-evidence.md` + `DOC:docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
