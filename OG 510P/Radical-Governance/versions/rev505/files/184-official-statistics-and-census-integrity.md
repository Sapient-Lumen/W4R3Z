# Official statistics & census integrity (trustworthy measurement as a constitutional function)

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the official-statistics and census-integrity layer; `03` is the measurement front door; `214` is the institutional evidence-system anchor; `28` handles program commitments; `190` handles experimentation; `202` handles evidence commons and scientific integrity; `142` handles indicator governance; `37` / `51` / `53` are narrower claims/publication components.

**Thesis:** the legitimacy of policy depends on **measurement that is professionally independent, reproducible, and privacy‑preserving**. Without trusted statistics, everything else becomes “rule by story”.

This memo specifies a *minimal* design for an official-statistics system (including census) that can be audited without becoming politicized.

---

## 1) Scope assignment

- **National / regional statistical authority:** produces core economic, demographic, social and environmental statistics; publishes methods; runs major surveys/census.
- **Domain agencies:** produce operational stats, but must conform to the national standards stack (methods, release discipline, confidentiality).
- **Independent oversight:** verifies adherence to standards and investigates interference attempts.

**Interface rule:** if a statistic is used for funding allocation, enforcement, or eligibility, it is “high‑impact” and must satisfy the integrity requirements below.

---

## 2) Non‑negotiables (minimum legitimacy floor)

Anchor principles are the UN Fundamental Principles of Official Statistics (relevance/impartiality/equal access; professional ethics; transparency; prevention of misuse; confidentiality). See UNSD and UNECE summaries.
Refs: UN/UNSD FPOS hub; UNECE FPOS summary.

### A. Professional independence
- Authority over **methods, content, and timing** of releases is insulated from political direction.
- Attempted interference must be loggable and contestable.

(Comparable independence framing: European Statistics Code of Practice, Principle 1.)

### B. Equal access + anti‑leak discipline
- Use a public **advance release calendar** for high-impact series; no selective early release.
- If any pre-release access exists (rare), it must be logged, justified, and time-bounded.

(Release discipline is central in IMF data dissemination standards.)

### C. Methods transparency + reproducibility
For each major series, publish:
- sources + sampling frames
- processing steps
- revisions policy
- quality metrics (coverage, nonresponse, bias checks)
- “limits of inference” (what the series does *not* measure)

### D. Prevention of misuse (with corrective speech)
Statistical authorities have an explicit mandate to **correct misinterpretation** publicly and promptly (without entering partisan debate).
(“Prevention of misuse” is explicitly part of FPOS.)

### E. Confidentiality is constitutional
Microdata collected for official statistics must be protected; re-identification attempts are prohibited and penalized.
(FPOS + confidentiality principle.)

---

## 3) Joinable artifacts (make measurement governable)

Introduce (or map onto existing registers):

- **`STAT-*` Series Card:** definition, scope, steward, methodology version, release cadence.
- **`METH-*` Method Receipt:** versioned method; change justification; backtest results.
- **`REV-*` Revision Receipt:** what changed, why, impact on historical series.
- **`QRY-*` Query Repro Pack:** code/snippets sufficient to reproduce published aggregates from approved pipelines (where feasible).
- **`INT-*` Interference Incident Receipt:** allegation → evidence → outcome (kept nonpartisan; focuses on process violation).

---

## 4) Peer review, capacity, and continuity

- Periodic **peer reviews** of statistical authorities (methods, governance, resourcing).
- Guaranteed baseline funding for core series (avoid “defund to distort”).
- Succession + continuity plans for census/surveys and dissemination infrastructure.

(Eurostat’s Code of Practice includes indicators and peer-review framing.)

---

## 5) Census-specific rails

- Enumerations and imputation rules must be published as part of `METH-*`.
- Non-response follow-up rules must be bounded and rights-respecting.
- Post-enumeration coverage evaluation must be published.

---

## 6) Threat model (failure modes)

- **Politicized series definitions** (quietly redefining unemployment, poverty, inflation baskets).
- **Selective release / suppression** (“no bad news weeks”).
- **Chilling effects** on respondents (privacy doubts, enforcement spillover).
- **Bad confidentiality** (re-identification scandals) causing long-term nonresponse.

Mitigation is not “more messaging”; it is the artifact + independence + confidentiality stack above.

---

## See also

- `03-metrics-and-evidence.md` (indicator design + evidence discipline)
- `31-records-foi-and-government-memory.md` (publication integrity; retention)
- `127-data-governance-and-privacy-interfaces.md` (purpose limitation + access receipts)
- `133-evaluation-and-learning-integrity.md` (anti-gaming measurement)
