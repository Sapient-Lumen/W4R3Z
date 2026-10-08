# Microdata access, disclosure avoidance, and trusted research rails

**Problem:** society needs research access to microdata, but disclosure risk can destroy trust and participation.

This memo specifies a **safe access ladder**: open aggregates → safeguarded microdata → protected secure analysis → bounded outputs.

---

## 1) Disclosure avoidance is a system, not a one-off

Before any statistic is published, apply systematic safeguards (“disclosure avoidance” / statistical disclosure control).  
(US Census framing of statistical safeguards.) citeturn1search2

**Minimal rule:** any release that could reasonably enable re-identification requires:
- documented risk assessment
- selected protection method(s)
- output checks + logging

---

## 2) Access ladder (progressive disclosure)

1. **Public aggregates** (default): tables, indicators, reproducible metadata.
2. **Public-use microdata** (rare): heavily transformed/de-identified, strict variables/geo/time suppression.
3. **Licensed microdata**: vetted researchers + project approval + agreements.
4. **Secure environment / TRE**: analysis occurs inside controlled enclave; only vetted outputs leave.
5. **Highly sensitive linkage**: special approval + enhanced monitoring + dual-control output review.

**No enforcement spillover:** microdata collected for statistics must not become a backdoor for law enforcement or immigration enforcement (except where a court compels under extreme, explicit conditions). This is a participation-preserving invariant.

---

## 3) Governance artifacts

- **`MDA-*` Microdata Access Receipt:** applicant, purpose, dataset, legal basis, steward decision, expiry, renewal conditions.
- **`SDL-*` Disclosure Control Plan:** chosen protections (suppression, noise infusion, swapping, top-coding, synthetic data, etc.), plus rationale and evaluation.
- **`OUT-*` Output Check Receipt:** what was reviewed, by whom, what was blocked/modified, and appeal lane.
- **`BREACH-*` Incident Receipt:** disclosure incident, notification, mitigation, and policy change.

---

## 4) Output checking & researcher UX (anti-theater)

- Output checking must be **fast, clocked, and appealable** (avoid “security as censorship”).
- Provide templates and automated checks to reduce arbitrary gatekeeping.
- Publish aggregate metrics: time-to-approve, denial reasons, incident counts (without exposing sensitive detail).

---

## 5) What “good” looks like

- Participation is high because confidentiality is credible.
- Researchers can do real work because access is predictable and not discretionary.
- The public can audit the system because approvals and methods are logged (without exposing private data).

---

## See also

- `184-official-statistics-and-census-integrity.md` (institutional independence + release discipline)
- `127-data-governance-and-privacy-interfaces.md` (purpose limitation + data access receipts)
- `53-publication-integrity-and-tamper-evident-logs.md` (anti-silent-edit)
- `183-governance-observability-and-public-audits.md` (audits + follow-through)
