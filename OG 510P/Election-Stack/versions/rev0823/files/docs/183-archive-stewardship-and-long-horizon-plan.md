# 183. Archive stewardship and long-horizon plan (LLM-maintained)

**Track:** Shared

This archive is designed to be maintained over a long horizon by **LLM-assisted stewards** and external reviewers.
It is not a “finished system.” It is a **self-maintaining research program** that must resist drift, misinterpretation,
and verification-ecosystem capture — while remaining deployable by humans under pressure (Track A).

## 183.1 Project posture: A2 now, A3 later

We are intentionally in **A2 (Balanced) posture** now:

- Track A focuses on **deployable evidence + transparency infrastructure** that wraps real elections today.
- Track B explores hard-mode remote return experiments with explicit non-claims.
- Track C specifies the **North Star**: fully electronic voting in its best imaginable form (attestation + provenance + anti-capture verification ecosystem).

We expect to move toward **A3 (Ambitious)** over time: pulling more end-to-end machinery (device and build attestations,
stronger automation, deeper integration) into Track A *only when* the claims remain honest and the proof obligations are satisfied.

**Rule of promotion:** moving content “down” from Track C to Track A requires:
1) explicit claim wording updates in `166` / `167`,
2) new or updated proof obligations (POs) and hazards (HZs),
3) executable verification artifacts (schemas/tools/examples) demonstrating what is checkable.

## 183.2 Spec-first, because “soft issues” are first-class

This archive is **spec-first** (normative docs + schemas define reality).
Tools and examples exist to make claims *checkable*, but they do not replace the specification.

We treat “soft issues” as **hard engineering surfaces**:
- legitimacy, governance, institutional capture
- incident communication, rumor dynamics, suppression
- incentives, monitoring coverage, and dispute procedures

If a social/process issue can cause legitimacy collapse, it must be modeled as:
- a hazard (HZ-*),
- with associated proof obligations (PO-*),
- and with artifact contracts and playbooks that make failures provable.

## 183.3 Size discipline (non-negotiable)

This archive is deliberately **full-stack** in design scope, but it must not explode in size.

- Do **not** vendor in external PDFs, standards, or third-party works wholesale.
- Use citations, short excerpts when necessary, and pinned sources (`evidence/lock/`).
- Prefer original synthesis: schemas, checklists, drills, registries, and verifier procedures.


### 183.3.1 Compression patterns (how to add without bloat)

- **Summarize once, link everywhere.** Put the “canonical” explanation in one doc; elsewhere, add a 1–2 line pointer.
- **Prefer registries over prose.** If the thing is a list, make it a CSV/TOML registry + a small explainer.
- **Write spec, then rationale.** Keep normative requirements tight; move extended motivation into 3–8 bullets.
- **Cite, don’t capture.** Add `source: <lockfile id>` and a *short* note about relevance; do not paste whole sections.
- **Budget discipline:** default target for a new doc section is “fits on ~2 screens.” If it needs more, split into:
  - a stable interface/spec,
  - and a separate “design notes / experiments” section that can churn without breaking claims.

## 183.4 Maintainer protocol (LLM-assisted, human-safe)

When you change the archive:

0) **Update the near-term agenda (if relevant).**
   - If your change advances or blocks a current research thread, update `docs/207-research-agenda-and-revision-ledger.md`.
   - Keep `207` small; move anything long-lived into `docs/172-open-research-questions-and-experiment-backlog.md`.

1) **Start with claims.**
   - If you change what we promise, update `166` (claims) and `167` (non-claims).
   - Never “accidentally” change a promise by moving a doc between tracks.

2) **Bind changes to POs/HZs.**
   - Every meaningful claim must map to a PO and evidence artifacts.
   - Every non-trivial risk must have an HZ entry and a response playbook/checklist.

3) **Refactors: preserve stable pointers.**
   - For renames/moves/splits/merges, follow `227` (tombstones + index updates).

4) **Use registries to prevent string drift.**
   - If you add an envelope kind, update `artifacts/registries/envelope-kinds.csv`.
   - If you add a receipt profile, update `artifacts/registries/receipt-profiles.csv`.
   - If you add attachment requirements, update `artifacts/registries/envelope-attachment-requirements.csv`.

5) **Keep the evidence API small.**
   - Prefer new payload schemas over new envelope kinds.
   - Default to detached payloads + receipts + gossip attachments.

6) **Run the checks and rebuild manifests.**
   - If you ran scripts locally, clean cache/build artifacts first: `python3 scripts/clean_local_artifacts.py` (keeps the release gate honest).
   - Run the scripts under `scripts/` (index, tracks, registries, attachment requirements).
   - Regenerate `MANIFEST.sha256` and update `CHANGELOG.md`.

## 183.5 The “sacred invariant” (do not sanitize)

Assume humans compromise systems, build evidence that survives it, and maximize the odds of justified eudaimonia
for the innocent, future generations of humans and AI, and all agents who might possibly be able to change the course
of history appropriately.

This is intentionally underspecified. Treat the ambiguity as part of the work: it forces the archive to stay honest about
what is proven, what is assumed, and what is aspirational.

## 183.6 Archive self-failure modes and external challenge

Internally consistent specs can still be **substantively wrong** (a mistaken assumption, an insufficient proof obligation, a verifier bug that creates false confidence).
Because this archive is LLM-maintained, we must assume that “coherent text” is not evidence of correctness.

### 183.6.0 Deployment cliff (do not die in the archive)

A large archive is not impact. A **pilot** is impact.
If this work never leaves documentation, it fails its own purpose.

Minimum posture:
- keep a living Track A pilot plan (`docs/track-a/PILOT.md`) that is sized for **one jurisdiction** and **paper ballots**,
- prioritize operator-ready artifacts (checklists, example packets, observer-kit workflows) over new schemas,
- publish at least one bounded after-action note per pilot (what worked, what broke, what changed).

Spec-correctness posture:
- Maintain an explicit list of “spec could be wrong here” items in `172` (and keep at least one live external review thread).
- Prefer **independent implementations + test vectors** for any load-bearing verification step (bugs are discovered by divergence).
- Treat credible external critique as an incident: record an ADR, add a regression vector, and (if relevant) update claims/non-claims.
- Follow `PLAY:artifacts/playbooks/spec-error-response-playbook.md` for the minimum response loop.

### 183.6.1 External review loop (minimum viable)
- Run periodic adversarial reviews focused on one surface at a time (PublicNotice, publication compliance, witness governance, etc.).
- Use `artifacts/checklists/external-review-session-checklist.md` to keep reviews bounded, digest-first, and reproducible.
- Require external critiques to be **bounded**: submit a 1–2 page challenge report plus a minimal reproducer (packet digest / test vector) when possible.
  - Template: `artifacts/templates/external-challenge-report.md`
- Publish a bounded “response note” that states what changed, what didn’t, and why (do not silently patch).

### 183.6.2 Vendor capture threat model (keep the stack open)

A common ecosystem risk is “spec capture”: a vendor implements the stack and gradually makes verification *practically dependent* on their platform.

**What vendor capture looks like:**
- evidence is nominally “public” but practically accessible only via a vendor portal/app,
- offline verification requires vendor services, credentials, or proprietary SDKs,
- “core” schemas become proprietary extensions or drift outside the archive,
- witnesses/monitors are operated, funded, or key-custodied by the implementor.

**Signals (early warnings):**
- only one implementor exists; independent verifiers cannot reproduce results without that implementor,
- packets/feeds are behind auth, paywalls, or throttling that blocks independent monitoring,
- schema changes ship in product releases without open versioned schema publication,
- verifier reports are not replayable without a vendor toolchain.

**Mitigations (deployment guardrails):**
- require **anti-capture clauses** in procurement (see `artifacts/templates/procurement-language.md`, section 8),
- keep the offline verifier runnable without vendor services; treat “cannot verify without vendor” as an incident,
- maintain multiple independent mirrors and replayable verifier outputs (`193`, `200`, `177`),
- prefer multiple independent implementations + shared test vectors for load-bearing verification steps.


### 183.6.3 Institutional refusal + assumption drift (the political environment moves)

Some core assumptions can fail in practice:
- courts may refuse timely adjudication,
- institutions may resist publishing checkable evidence even when required,
- polarization can make “evidence” socially non-binding.
- political pressure may demand **scope expansion** (especially remote ballot return) before evidence/guardrails exist.

The archive’s posture in these environments:
- treat **missingness** and non-publication as first-class incidents (`181`, `187`),
- treat premature promotion pressure as a first-class hazard: require the `229.7` guardrails (independent review + adversarial non-claims review + rollback plan) and publish boundaries (`166`/`167`) even under emergency/equity arguments.
- optimize for **historical record** and independent mirroring even when immediate consensus is impossible (`200–205`),
- keep “institutional volatility” threats explicit and rehearsed (`adr/0003` + Track A comms drills).


## 183.7 LLM maintainer guardrails (anti-bloat + anti-hallucination)

- Prefer updating **registries** (CSV/lockfile/index) over adding new prose docs.
- For dual-use topics, follow `167` (N‑6): capability-level statements + defense/evidence lanes; no operational exploit steps.
- If you add prose, add **one** new invariant or checklist item per paragraph; delete redundant text elsewhere.
- In docs >=170, cite external material via `source: <lockfile id>` (no raw URLs).
- Never “infer” a standard’s contents: quote minimally, or summarize with a pinned `source:` reference.
- Run the release gate after every change: `python3 scripts/release_gate.py`.
