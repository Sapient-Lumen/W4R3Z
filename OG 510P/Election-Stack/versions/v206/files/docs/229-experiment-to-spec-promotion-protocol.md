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
