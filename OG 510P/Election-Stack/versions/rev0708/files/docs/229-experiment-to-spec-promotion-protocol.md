# 229. Experiment → spec promotion protocol (keep research honest, keep Track A clean)

**Track:** Shared

This archive mixes *deployable* controls (Track A) with “hard-mode research” (Track B/C) and a living backlog (`172`).
Without a promotion protocol, research ideas can quietly become “assumed true” and leak into normative surfaces.

This doc is a **tight protocol** for:
- how experiments move from backlog → draft → pilots → Track A candidates, and
- how to keep claims honest while the archive grows.


## 229.1 Core principle

**No promotion without evidence.**
A proposal is not “real” in Track A until it has:
- a bounded definition,
- explicit failure modes / non-claims,
- at least one runnable artifact (example packet / schema / checklist) that makes verification concrete.


## 229.2 Stages (E0–E3)

| Stage | Name | Allowed claims | Minimum artifacts | Where to record |
|---:|---|---|---|---|
| **E0** | Idea | “Could be useful” | 3–7 line problem statement + what evidence would resolve it | add to `172` |
| **E1** | Draft hypothesis | “We think X, if Y holds” | bounded interface sketch + explicit non-claims + threats | new numbered doc *or* small section in existing doc; consider ADR |
| **E2** | Pilotable design | “Testable in a constrained pilot” | at least 1 example packet or schema + a verifier outcome shape (PASS/WARN/FAIL mapping) | numbered doc + example under `artifacts/examples/` (if relevant) |
| **E3** | Track A candidate | “Deployable under explicit assumptions” | operator checklist + failure drill + proof obligations + release-gate coverage | update Track A bundle + `166`/`167` if claims shift; ADR strongly recommended |

Notes:
- **E1/E2 should be Track B/C by default** unless a strong case is made for Track A.
- E3 is not a vibe; it is a **packaged, testable surface**.


## 229.3 The “experiment card” (bounded capture, no prose bloat)

When adding or advancing an experiment, capture *only* the following (inline in the doc or as a short section):

- **Goal:** one sentence.
- **Threat addressed:** 1–2 bullets (link to `01`, `27`, `171` where relevant).
- **Assumptions:** 1–3 bullets (explicit).
- **Non-claims:** 1–3 bullets (link to `167`).
- **Interface sketch:** what artifact(s) would exist? (envelope kind, schema, checklist, tool output).
- **Verifier outcome:** what does PASS/WARN/FAIL mean for this experiment?
- **Evidence needed to advance:** concrete measurements / pilots / exercises.

This keeps the archive honest and prevents “research prose” from inflating into quasi-requirements.


## 229.4 Promotion checklist (minimal)

### E0 → E1
- [ ] Added to `172` with *evidence that would resolve it*.
- [ ] Identified the target track (B/C by default).
- [ ] Added explicit assumptions + non-claims.

### E1 → E2
- [ ] Defined a bounded interface (schema / packet / checklist / tool output).
- [ ] Added at least one runnable artifact (example packet or schema).
- [ ] Added a verifier outcome mapping (PASS/WARN/FAIL semantics).

### E2 → E3 (Track A candidate)
- [ ] Added operator-facing checklist or runbook pointer.
- [ ] Added at least one failure drill (`18` + drill registry) or catastrophe mapping (`171`).
- [ ] Added/updated proof obligations (`159`/`164`) where the control becomes load-bearing.
- [ ] Ensured no Track A doc relies on unpinned external sources (`source:` vs `xref:` policy; see `151`).
- [ ] Ran the full release gate.


## 229.5 Demotion and rollback

If an experiment fails (or is shown unsafe):
- update the doc with a **short “Why it failed / why unsafe”** section,
- ensure Track A does not reference it (or mark references as non-normative),
- record a short ADR if the reversal affects previously-shipped claims.

Demotion is not shameful; it is *evidence of honesty*.


## 229.6 Size discipline

- Prefer **one canonical doc** per experiment family; link out instead of duplicating.
- Prefer **schemas/checklists/examples** over explanatory prose.
- If the archive grows, it should grow in **machine-checkable surfaces** (schemas, registries, examples), not essays.


## 229.7 Premature deployment hazard (political immune system)

The most damaging failure mode is not that Track B/C experiments fail — it is that they are **promoted into Track A under political pressure** before non-claims are resolved.

Therefore, any promotion that introduces **remote ballot return** (or similarly high‑catastrophe surfaces) into a Track A candidate MUST include:

- **Independent security review:** reviewers not funded by the deploying jurisdiction or vendor, with a publishable summary.
- **Adversarial non-claims review:** at least one organization/person with an explicitly skeptical posture reviews the public non‑claims statement for completeness (not endorsement).
- **Rollback plan:** a published, pre-committed plan that specifies conditions and procedure to revert to Track A paper-first workflows.
- **No silent scope creep:** `166`/`167` MUST be updated, and public operator communications MUST repeat the boundary (no “implied safety” via marketing language).

These are not “nice to have.” They exist to keep the archive credible under the pressure that real deployments create.

**Gate:** complete `artifacts/checklists/catastrophe-ordering-review-checklist.md` §1.5, record the three non‑waivable requirements + rollback triggers in an ADR, **and** create/update a bounded row in `artifacts/registries/promotion-events.csv` (pointers to the independent review, adversarial non‑claims review, rollback plan, and the ADR ID).



## 229.8 The political immune system (promotion must resist capture)

Promotion is not only a technical decision. It is a **power decision**: once a mechanism is “in Track A,”
institutions and vendors can cite it as legitimacy.

Minimum immune-system requirements for **E2 → E3**:
- **Adversarial review:** at least one reviewer who is *not* the proposing implementor (preferably from a different stakeholder class).
- **Capture check:** explicitly answer: “How could a vendor or authority satisfy this *in form* while nullifying it in practice?” (MAPT mindset; `187`).
- **Witness posture check:** if the mechanism relies on witness/monitor behavior, state the degraded-mode story when witnesses are monoculture or silent (`135`).
- **Conflict disclosure:** record any funding / implementor entanglements in an ADR when a promoted surface becomes load-bearing (`adr/` + `138`).
- **Rollback plan:** specify a demotion trigger and a public correction path (`234–236`) if a promoted surface proves unsafe.

This is intentionally minimal: it is a guardrail against “promotion by political pressure.”

