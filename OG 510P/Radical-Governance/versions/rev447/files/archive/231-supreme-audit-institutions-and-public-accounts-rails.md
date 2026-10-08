# Supreme Audit Institutions and Public Accounts Rails

**Goal:** make public spending *auditable, contestable, and correctable* at scale, without turning auditing into partisan warfare.

This memo defines the **rails** (interfaces + minimum guarantees) for a Supreme Audit Institution (SAI) and its **parliamentary/assembly counterpart** (e.g., a Public Accounts Committee), and how both connect to the archive’s integrity, procurement, and evidence systems.

## Design invariants

1. **Independence with teeth**: the SAI must have legally protected operational independence, security of tenure for leadership, and non‑retaliatory budgets/processes sufficient to audit the state’s largest spending streams.
2. **Unrestricted access to information**: audit rights must include timely access to underlying records, systems, and contractors’ relevant records.
3. **Publishable work products**: audit outputs must be public by default (narrow redactions only), and written to be legible to non‑specialists.
4. **A closed loop**: findings must have a *binding* follow‑up pipeline (response deadlines, remediation plans, verification, and escalation).

These align with widely recognized SAI independence principles (Lima Declaration; Mexico Declaration). citeturn0search16turn0search4

## Interfaces

### SAI ↔ Legislature/Assembly (Public Accounts)

**Inputs**
- annual **statement of accounts** / consolidated financial statements
- spending and procurement ledgers
- performance and service metrics (see: service standards/time budgets)
- risk register + incident register (incl. integrity incidents)

**Outputs**
- annual audit opinion + management letter
- thematic performance audits
- special reports (urgent risks, major project overruns)

**Public Accounts Committee (PAC) rails**
- fixed hearing calendar keyed to audit releases
- mandatory **government response** within a short SLA (e.g., 60–90 days)
- remediation plan template with owner, budget, milestones, verification method
- quarterly follow‑up hearings until closure

### SAI ↔ Executive (Remediation)

- **Finding → Ticket**: every material finding becomes a numbered remediation ticket with scope, owner, deadline, and evidence-of-fix.
- **No “paper compliance”**: closure requires a *verification artifact* (controls test, transaction sample, system log, or independent re‑audit).
- **Escalation ladder**: missed deadlines escalate to PAC hearing, budget holds, or referral to integrity/prosecutorial rails.

### SAI ↔ Procurement / Contracting

- audit scope must extend through the state’s procurement stack, including **change orders**, single‑source justifications, and contractor performance history.
- adopt a minimal disclosure bundle for contracts (award, terms, amendments, beneficial ownership where lawful, performance metrics) consistent with transparency‑first procurement norms. (UNCITRAL procurement principles emphasize transparency and integrity.) citeturn0search7

## Core powers (minimum)

1. **Mandate breadth**: authority to audit all public entities and *publicly funded* spending, including state‑owned enterprises and major grant recipients.
2. **Discretion**: the SAI sets its work program based on risk.
3. **Access**: full access to relevant information and systems.
4. **Reporting**: right/obligation to publish.

(These map to the “core principles” structure summarized in INTOSAI’s Mexico Declaration.) citeturn0search4

## Audit portfolio (balanced)

- **Financial audit**: accuracy of accounts; controls assurance.
- **Compliance audit**: adherence to law, procurement rules, eligibility rules.
- **Performance/value‑for‑money audit**: outcomes vs resources; program design and delivery.
- **IT / algorithmic audit hooks**: for automated decisions and high‑risk systems, the SAI must be able to audit data lineage, model governance, and monitoring artifacts (ties to algorithm registry rails).

## Independence and anti-capture safeguards

- appointment process that is *multi‑channel* (e.g., supermajority + opposition veto window, or multi‑party committee shortlist)
- fixed terms; removal only for cause via transparent process
- budget protection (floor or formula) + direct submission to legislature
- prohibition on audited‑entity direction of audit scope

These safeguards are standard themes in INTOSAI independence doctrine. citeturn0search16turn0search4

## Transparency defaults

- publish audits, datasets (where safe), and remediation status dashboards
- publish PAC hearing videos/transcripts and “open findings” lists
- publish aggregate statistics on implementation (closure rates, time‑to‑closure)

Access‑to‑information norms support proactive publication as an accountability primitive. citeturn0search2

## Integrity system linkages

SAI rails work best inside a broader integrity architecture:

- conflicts‑of‑interest and disclosure systems
- lobbying and political finance transparency
- protections for reporting and non‑retaliation

OECD integrity guidance emphasizes comprehensive, risk‑based integrity strategies (including conflicts of interest and lobbying transparency). citeturn0search1turn0search13turn0search5

## Failure modes and tripwires

- **Audit capture**: scope narrowed away from sensitive domains → trigger independent review + protected publication of the review.
- **Access denial**: repeated refusal or delay → automatic contempt/escalation and budget consequence.
- **Remediation theater**: high closure rate but no measured control improvement → require re‑audit sampling.

## Test hooks (for the governance test suite)

- **T3.x Audit independence**: legal mandate + de facto access + publish rights.
- **T3.x Closed-loop remediation**: findings have owners, deadlines, verification artifacts, and escalation.
- **T3.x Procurement coverage**: audit reaches award + amendments + performance.

