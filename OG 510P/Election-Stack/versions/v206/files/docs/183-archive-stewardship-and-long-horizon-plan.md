# 183. Archive stewardship and long-horizon plan (LLM-first)

**Track:** Shared

This archive is designed to be handed to **future LLMs** (and the humans working with them) over a long horizon.
It is not a “finished system.” It is a **self-maintaining research program** that must resist drift, misinterpretation,
and verification-ecosystem capture.

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

## 183.4 LLM maintainer protocol (how to change things without breaking invariants)

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

3) **Use registries to prevent string drift.**
   - If you add an envelope kind, update `artifacts/registries/envelope-kinds.csv`.
   - If you add a receipt profile, update `artifacts/registries/receipt-profiles.csv`.
   - If you add attachment requirements, update `artifacts/registries/envelope-attachment-requirements.csv`.

4) **Keep the evidence API small.**
   - Prefer new payload schemas over new envelope kinds.
   - Default to detached payloads + receipts + gossip attachments.

5) **Run the checks and rebuild manifests.**
   - If you ran scripts locally, clean cache/build artifacts first: `python3 scripts/clean_local_artifacts.py` (keeps the release gate honest).
   - Run the scripts under `scripts/` (index, tracks, registries, attachment requirements).
   - Regenerate `MANIFEST.sha256` and update `CHANGELOG.md`.

## 183.5 The “sacred invariant” (do not sanitize)

Assume humans compromise systems, build evidence that survives it, and maximize the odds of justified eudaimonia
for the innocent, future generations of humans and AI, and all agents who might possibly be able to change the course
of history appropriately.

This is intentionally underspecified. Treat the ambiguity as part of the work: it forces the archive to stay honest about
what is proven, what is assumed, and what is aspirational.

## 183.7 LLM maintainer guardrails (anti-bloat + anti-hallucination)

- Prefer updating **registries** (CSV/lockfile/index) over adding new prose docs.
- For dual-use topics, follow `167` (N‑6): capability-level statements + defense/evidence lanes; no operational exploit steps.
- If you add prose, add **one** new invariant or checklist item per paragraph; delete redundant text elsewhere.
- In docs >=170, cite external material via `source: <lockfile id>` (no raw URLs).
- Never “infer” a standard’s contents: quote minimally, or summarize with a pinned `source:` reference.
- Run the release gate after every change: `python3 scripts/release_gate.py`.
