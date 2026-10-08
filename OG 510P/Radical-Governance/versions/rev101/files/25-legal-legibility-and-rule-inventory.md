# Legal Legibility & Rule Inventories (Making “the law” findable and auditable)

In multi-level systems, people lose rights *in practice* when they cannot reliably answer:

**What rules apply to me, right now, in this place, from which authority — and how do I challenge them?**

This memo is the **why + boundary conditions**. The **canonical PRR spec** (schema, versioning, as-of queries, machine-readable options) lives in `39-rulebook-and-instruments-registry.md`.

---

## A. Minimum Viable Legal Legibility (MVLL)
A scope has MVLL if:

1) **Everything enforced is findable**  
If a norm is enforced against people (permits, eligibility, sanctions, tariffs), it MUST be registered with a `RULE` ID, an effective date/window, and an appeal lane.

2) **Decisions cite rules**  
Rights-/resource-affecting decisions publish a `DRR` that cites the specific `RULE` IDs **and versions/as-of date** used (see `31-...` and `70-...`).

3) **Guidance that functions like law is visible**  
If “guidance” is enforced in practice—including **operational manuals, frontline scripts, or software configuration tables**—it MUST appear in the PRR (flagged as such) until clarified, repealed, or converted to a binding instrument (prevents “regulatory dark matter” and policy-by-software).

---

## B. Why this matters (failure modes)
- **Retroactive confusion:** people cannot tell which version applied when (breaks review and remedy).
- **Shadow discretion:** frontline scripts or software become de facto law without publication.
- **Forum-shopping:** unclear authority chains encourage arbitrary enforcement and inconsistent outcomes.
- **Boundary collapse:** when multiple scopes overlap, missing rule IDs make interop impossible.

Mitigation is not more text; it’s **joinable inventories** (PRR + competence ledger + appeal lanes) and **decision receipts**.

---

## C. Anti-bloat policy (how to keep PRR sane)
- **Register the enforcement surface first:** permits/eligibility/fines/tariffs.
- Prefer **sunsets + review dates** for low-value or emergency rules.
- Use stable IDs, tombstones, and diff logs; avoid duplicative re-publication.

---

## D. Canonical spec & anchors
- PRR spec: `39-rulebook-and-instruments-registry.md`
- Regulatory policy baseline: [BIB-OECD-RPG-0390]
- Machine-readable legal interchange (optional): [BIB-OASIS-AKN-2018]
