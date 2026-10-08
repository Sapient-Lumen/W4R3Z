# Freedom of Information & Access to Official Documents Rails (ATI as a person-facing power)

**Cross-stack note:** use `295-public-information-media-and-access-routing-guide.md` for the canonical route across the public-information / media / access cluster. This memo remains the requester-side ATI / FOI lane; `129` is the public-sphere integrity front door; `161` is the media / platform / pluralism specialization; `61` is the official-communication specialization; `77` is the secrecy-boundary neighbor.

**Purpose:** make state power legible by default: people can **ask, receive, reuse, and contest** government-held information without insider status.

**Person served:** a person trying to understand (or challenge) a decision, a journalist/auditor, a community group, or a researcher—especially when government secrecy is convenient.

**Why this is foundational:** access to information (ATI) is widely treated as a core component of freedom of expression and democratic accountability (e.g., UN Human Rights Committee GC34; Council of Europe Tromsø Convention).

---

## Non‑negotiable invariants

1. **No wrong door**: any public body must accept a request and route it, without forcing the requester to “guess the right office.”
2. **Clocked processing**: every request gets a receipt with a deadline and visible state transitions.
3. **Narrow exceptions + reasons**: refusals must be specific, reviewable, and time-bounded; “because security” is not enough.
4. **Partial disclosure default**: redact/withhold only what is necessary; release the rest.
5. **Appealability**: independent review lane with remedy authority and published metrics.
6. **Proactive publication beats requests**: the highest-value datasets and records are published by default.

(These reflect common best-practice expectations in ATI regimes and international guidance.)

---

## Core interface: the FOI / ATI request lane

### 1) Filing (FIR-* — FOI Intake Receipt)
A request produces a **FIR-*** with:
- request text (or assisted‑digital transcription)
- requester contact lane (anonymous/pseudonymous option where lawful)
- scope/body routing target (with auto-routing allowed)
- **deadline** (statutory default) + “complexity extension” rules
- fee estimate (if any) + fee waiver criteria
- a **public tracking token** (privacy-safe) for monitoring status

### 2) Processing states (clocked)
Minimum states:
- **received → validated → searching → reviewing → redacting → releasing → closed**
Each transition is timestamped; any pause needs an explicit reason.

### 3) Exceptions & refusals (FER-* — FOI Exception Receipt)
Any withholding produces a **FER-*** that includes:
- specific exception category invoked (mapped to statute)
- **harm test** and **public interest test** summary
- why partial release is insufficient (if applicable)
- sunset date / declassification review trigger (if the exception is time-bound)
- appeal instructions (where/how/when)

### 4) Release bundle (FRB-* — FOI Release Bundle)
A release includes:
- the disclosed records (or access link)
- redaction log (what categories were withheld and why)
- format + reuse terms (machine-readable when feasible)
- provenance pointer to the **record system** / ledger (joins to `115`)

---

## Proactive publication rails (reduce FOI load; increase trust)

### Publish-by-default registers
Create **publication commitments** with owners and cadences for:
- budgets, contracts, grants, subsidies, procurement change orders (`179`, `138`)
- rules/policies + versions (`118`)
- audits/inspections + follow-through (`130`)
- algorithmic systems registry + monitoring (`191`)
- performance/service SLO dashboards (`189`)
- statistics series metadata (`184`)

Open government guidance typically treats transparency + ATI as core pillars.

### Disclosure clocks + “darkness budgets”
- A body publishes **median/95p time-to-disclose** and backlog size.
- “High-secrecy domains” must publish **aggregate** secrecy metrics (counts, categories, declassification schedules) without exposing protected details.

---

## Appeals, oversight, and anti‑gaming

### Independent review lane (FAR-* — FOI Appeal Receipt)
Appeals must provide:
- deadline to decide
- power to order disclosure and/or impose penalties
- published jurisprudence summaries (legible guidance)
- performance metrics by agency

Global comparative tools (e.g., RTI Rating) can be used as a sanity check for whether a regime’s structure is robust.

### Abuse resistance without chilling access
- Define “vexatious” narrowly; require a **VXR-*** receipt and appeal lane.
- **No retaliation**: requests must not trigger enforcement targeting (join to `121` protected disclosure principles).

---

## Safety, privacy, and open justice tensions

ATI must coexist with:
- privacy and personal safety (redaction + safe withholding receipts) (`127`)
- open justice and court transparency (publication with narrow protective orders) (`130`)
- national security exceptions with independent review and sunsets (`112`, `165`, `186`)

The Tromsø Convention frames a general right with permissible limitations for protected interests, but the limitations must be defined and necessary.

---

## Minimal test hooks (add to `107`)
- **ATI lane exists:** can a person file, track, and appeal within bounded clocks?
- **Narrow exceptions:** does every refusal include a harm/public-interest rationale and sunset?
- **Proactive disclosure:** are core registers published with cadences and owners?
- **Partial disclosure default:** are redaction logs provided and contestable?

---

## References (starting set)
- Council of Europe **Convention on Access to Official Documents (Tromsø Convention)** (entered into force 1 Dec 2020).
- UN Human Rights Committee **General Comment No. 34** (Article 19; access to information held by public bodies).
- OECD **Recommendation on Open Government** (open government principles; transparency/ATI as core).
- **Global RTI Rating** (comparative framework for ATI legal strength).
