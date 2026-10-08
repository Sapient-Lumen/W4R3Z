# 150. Maintainer bootstrap and LLM-safe change protocol

**Track:** Shared


This document is written for a future maintainer (human or LLM) who starts “cold” and must make safe changes without relying on memory.

The goal is to make every security-relevant change:

- evidence-backed,
- mechanically reviewable,
- and versioned in a way that prevents silent interoperability or governance breaks.

## 150.1 Non-negotiable invariants

0. **Software independence is the recovery anchor.** If this system is used in binding public elections, a **human-readable ballot of record** (or voter-verifiable paper record) + **risk-limiting audits** remain the legitimacy backstop.

1. **No long-term credential signs ballots.** Citizen credentials (e.g., WebAuthn) may authenticate only to mint **unlinkable eligibility tokens**. Ballots are encrypted/signed only with *ballot-specific* keys and protocols.

2. **No “RECORDED” without proof.** A client MUST NOT display a definitive “RECORDED”/“ACCEPTED” status unless it holds a valid inclusion proof against a quorum-cosigned checkpoint.

3. **EPB is the only “official parameter” object.** Ballot definitions, crypto policies, witness sets, disclosure policy, and deadlines MUST be committed in the ElectionParameterBundle (EPB), included in the log, and quorum-witnessed.

4. **Fail loud on split-world risks.** If witnesses/monitors disagree or checkpoints diverge, the system must emit fork/suppression artifacts, not “best effort” UX.

5. **Evidence is content-addressed.** Public evidence bundles must be immutable, hashed, signed, and (optionally) timestamped/notarized. No silent edits.

## 150.2 Read-this-first map (30-minute cold start)

1. `00–05` (goals, threat model, architecture, protocol, transparency log, key management)
2. `09–10` (audit/recovery, assurance plan)
3. `55` (parameter/key transparency) + `60–62` (ballot definition integrity)
4. `63–72` (public results/ENR, results pipeline, comms)
5. `86–90` (exercises, comms proof, SLOs, scenarios)
6. `91–99` (observer kit, notarization, provenance)
7. `109–116` + `100–103` (availability + gossip / anti split-view)

## 150.3 Mechanical bootstrap steps (before changing anything)

- Validate JSON Schemas: `python3 scripts/validate_schemas.py` (see template)
- Run minimal checkers:
  - `python3 tools/bundle_gossip_checker.py --help`
  - `python3 tools/enr_drift_detector.py --help`
  - `python3 tools/challenge_sampler.py --help`
- Verify artifact index consistency: `python3 scripts/check_index.py` (see template)

If the baseline fails, fix that first. Don’t stack unrelated changes.

## 150.4 Evidence-backed change protocol

Every security-relevant change SHOULD follow this sequence:

1. **Write the question.** What is changing and why? What attacker capability does it address?
2. **Find authoritative sources.** Prefer standards bodies / election authorities / peer-reviewed work.
3. **Pin sources.** Add entries in `evidence/lock/external-sources.toml` with immutable references and sha256.
4. **Update spec text.** Modify the relevant `*.md` specs and/or create an ADR.
5. **Update artifacts.** Add example objects, schemas, test vectors, and/or checklists.
6. **Update detection/evidence lanes.** Ensure there is a way to detect regression (tooling, drills, monitors).
7. **Decide versioning.** If message formats / schemas / policy invariants change, bump the pack version and add a migration note (see `docs/173` versioning rules).
8. **Record the decision.** Add an ADR + update `../artifacts/risks/risk-register.csv` if risk posture changed.

## 150.5 Drift triggers (mandatory periodic review)

When these upstreams change, you MUST re-check the relevant specs and record a decision:

- EAC VVSG/Test Assertions and E2E evaluation process
- NIST Common Data Formats (BD/CVR/ERR/Event logs)
- CISA election guidance updates (ballot return, IR comms, VRDB)
- Relevant IETF RFCs/drafts used here (CT, OHTTP/ODoH, HTTP message signatures, Privacy Pass)

## 150.6 “Ask yourself” prompts

Before you merge anything, answer these in writing (ADR or change note):

- What attacker capability does this change address?
- Which invariant does it rely on?
- What evidence lane detects regression?
- What breaks if an operator deploys this change mid-election?

If you can’t answer these, the change is not ready.