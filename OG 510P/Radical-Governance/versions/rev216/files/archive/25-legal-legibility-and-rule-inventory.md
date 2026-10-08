# Legal Legibility & Rule Inventories (Making “the law” findable and auditable)

**Purpose:** make rules findable, versioned, and contestable so ‘what was in force’ can’t be rewritten after harm occurs.

In multi-level systems, people lose rights *in practice* when they cannot reliably answer:

**What rules apply to me, right now, in this place, from which authority — and how do I challenge them?**

This memo is the **why + boundary conditions**. The **canonical PRR spec** (schema, versioning, as-of queries, machine-readable options) lives in `39-rulebook-and-instruments-registry.md`.

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Rules/instruments registry and version pinning (“as-of” access): `39-...`, `53-...`.
- Person-facing comprehension + contestation paths: `98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`.
- Records custody / FOI and durable “why” memory: `31-...`.
- Interop join keys for rule references across scopes: `70-...`.


## Named tensions (design must surface these)
- **Precision vs understandability:** legal exactness can become unreadability; require usable summaries keyed to `RULE-*`.
- **Stability vs change:** frequent updates can become a compliance trap; preserve “as-of” access and transition notices.
- **Uniformity vs pluralism:** multiple legitimate forms can satisfy the same function; avoid false monoculture.


---

## A. Minimum Viable Legal Legibility (MVLL)
A scope has MVLL if:

1) **Everything enforced is findable**  
If a norm is enforced against people (permits, eligibility, sanctions, tariffs), it MUST be registered with a `RULE` ID, an effective date/window, and an appeal lane.

2) **Decisions cite rules**  
Rights-/resource-affecting decisions publish a `DRR` that cites the specific `RULE` IDs **and versions/as-of date** used (see `31-...` and `70-...`).

3) **Guidance that functions like law is visible**  
If “guidance” is enforced in practice—including **operational manuals, frontline scripts, or software configuration tables**—it MUST appear in the PRR (flagged as such) until clarified, repealed, or converted to a binding instrument (prevents “regulatory dark matter” and policy-by-software).


4) **Findable and understandable for humans**  
PRR entries MUST include a plain-language summary + translations as needed and a usable “how to challenge” path (lane + offline contact). Treat “published but incomprehensible” as legibility theater; test against the `98-persons-path-and-accessibility-invariants.md` persona.


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
