# Whistleblowing & Protected Disclosure (Make Reporting Safe and Actionable)

**Merge relation:** canonical implementation-facing whistleblowing memo. `83-whistleblowing-and-protected-disclosures.md` remains the broader moral/organizational frame; this memo is the tighter front door for concrete disclosure lanes, anti-retaliation mechanics, and joinable artifacts.


**Purpose:** convert “reporting wrongdoing” into a **reliable interface**: safe intake, time-bounded handling, anti-retaliation protection, and verifiable closure—without requiring heroic individuals.

**Person served:** the reporting person (and impacted third parties) who needs a trustworthy lane to surface harm, obtain interim protection, and force a real response.

**From-below:** if you speak up, you get (1) a **receipt**, (2) **protection**, (3) **clocked handling**, and (4) a **contestable outcome**—or the system auto-escalates.

## Design primitives (portable)

Treat whistleblowing as a **closed-loop control system** (`104`) with circuit breakers (`105`) and legitimacy receipts (`106`).

### 1) Report Receipt (WRR-*)
Minimum fields:
- `WRR-ID` (stable pointer; can be anonymous/pseudonymous)
- timestamp; channel (internal/external); scope; risk tag (safety, fraud, abuse, harassment, etc.)
- requested confidentiality level; consent for follow-up contact (yes/no)
- **interim-protection trigger** flag (see below)
- evidence pack hash/pointer (can be “none”)

Promise: “a report exists, was received, and will be processed under clocks.”

### 2) Triage & Routing Receipt (WTR-*)
Within a short time budget (`108`), issue:
- jurisdiction/handler assignment (named office, not an individual)
- conflict check outcome (see `120`)
- initial risk assessment + provisional safety actions
- next decision deadline

**Non-reset rule:** transfers must not restart clocks (`109`, `114`).

### 3) Protected Handling (PH-*)
Default protections, tiered by risk:
- confidentiality by default; identity reveal requires documented necessity + approval
- anti-retaliation **presumption**: adverse action after reporting shifts burden to employer/authority (design intent)
- access to support: counsel/union/advocate lane; mental-health referral lane (optional)
- separation of functions: intake ≠ investigation ≠ discipline/HR

Reference baseline principles: ISO whistleblowing management systems guidance, and multi-channel internal/external reporting models. [BIB-ISO-37002] [BIB-OECD-WB-2016] [BIB-COE-WB-2014]

### 4) Interim Protection (IP-*)
If safety/rights risk is plausible, the system must issue **interim protection** quickly:
- stay/hold on adverse actions; temporary accommodations; safe transfer; emergency services referral
- if protection is denied, a **Reason Receipt** must explain why and how to appeal (`106`, `08`)

Circuit-breaker: missed interim-protection deadlines auto-escalate to independent oversight (`105`).

### 5) Outcome & Closure Receipt (WCR-*)
Close with a receipt that includes:
- substantiated / not substantiated / unable to determine (with evidence limits noted)
- actions taken (discipline, policy change, referral to prosecutors/regulators, remediation)
- retaliation monitoring plan + re-contact window
- contest/appeal lane + deadline (`08`, `114`)

Publish aggregate stats (privacy-preserving) via an **Exceptions/Integrity ledger** pattern (`112`, `115`).

## Minimum clocks (time budgets)

- `t0`: WRR issued immediately (or within hours)
- `t1`: WTR triage & routing within days
- `t2`: interim protection decision within days (faster for safety risks)
- `t3`: investigation milestone updates on a schedule
- `t4`: closure with WCR within a bounded maximum unless extended by a documented exception (`112`)

## Failure modes and default fixes

- **“Black hole” intake:** require WRR + public aggregate backlog metrics (`108`, `115`)
- **Retaliation chilling effect:** presumption + monitoring + independent lane (`120`)
- **Conflict capture:** mandatory conflict screening + external routing option (`120`, `114`)
- **Weaponized false reports:** penalties for bad-faith *after* due process; protect the accused with procedural fairness (`06`, `106`)

## Test hooks (plug into `107`)

- **T2.1 Receipt integrity:** every report yields a WRR, and every status change yields a receipt.
- **T2.2 Clock compliance:** deadline-miss triggers escalation/circuit breakers.
- **T2.3 Retaliation monitor:** adverse actions post-report are reviewed and published in aggregate.

## Key references (citation keys)

- [BIB-ISO-37002] ISO 37002:2021 Whistleblowing management systems — Guidelines.
- [BIB-OECD-WB-2016] OECD, *Committing to Effective Whistleblower Protection* (2016).
- [BIB-COE-WB-2014] Council of Europe Recommendation CM/Rec(2014)7.
- [BIB-UNCAC-ART33] UNCAC Article 33 (protection of reporting persons).
- [BIB-UNODC-WB] UNODC thematic page on whistleblower protection.

