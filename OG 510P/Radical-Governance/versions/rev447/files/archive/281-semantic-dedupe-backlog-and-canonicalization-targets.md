# 281 — Semantic Dedupe Backlog and Canonicalization Targets

**Purpose:** record the highest-value remaining overlap clusters so future merge work is deliberate instead of impulsive.

**Standard:** do not collapse a cluster just because cosine similarity is high. Collapse it only when the archive can clearly preserve:
- the best retrieval hook,
- the best implementation hook,
- and the best person-facing explanation.

---

## Tier 1 — ready for controlled canonicalization

### 1. Worked-example architecture duplicates
**Files**
- `276-worked-example-system-consolidated.md`
- `278-worked-example-system-architecture.md`

**Diagnosis**
These had become near-duplicates. In rev445, `276` remains the canonical subsystem architecture, while `278` is narrowed into a map-attachment memo.

**Status**
- resolved enough for now
- do not re-expand `278` into a second architecture memo

---

### 2. Bibliography split
**Files**
- `90-bibliography.md`
- `91-bibliography-extended.md`
- `277-bibliography-canonicalization.md`

**Diagnosis**
This is not a conceptual problem anymore, only a maintenance problem. `91` is the canonical bibliography; `90` should remain a trimmed core set, not regrow into a competing reference corpus.

**Recommended next move**
- keep `90` short and stable
- put new keys in `91` by default

---

## Tier 2 — high overlap, but still distinct enough to preserve

### 3. Justice / grievance / redress cluster
**Files**
- `08-remedy-and-grievance.md`
- `36-appeal-lanes-and-redress-registry.md`
- `76-systemic-redress-and-pattern-remediation.md`
- `195-dispute-resolution-escalation-and-odr-rails.md`

**Why it feels duplicative**
All four live on the same person-path.

**Why it is not yet safe to collapse**
- `08` is the normative and architectural front door
- `36` is the lane/register implementation layer
- `76` handles pattern-level remediation
- `195` handles escalation and ODR routing

**Recommended next move**
Create a short crosswalk or shared glossary, not a destructive merge.

**rev447 action**
- added `283-justice-and-redress-stack-routing-guide.md` as the canonical bridge memo for this cluster
- added stack-relation notes to `08`, `36`, `76`, and `195`

---

### 4. Deliberation / assembly / legitimacy cluster
**Files**
- `88-deliberative-institutions-and-sortition.md`
- `111-deliberation-to-decision-binding.md`
- `143-deliberative-systems-and-citizens-assemblies.md`
- `159-civic-lottery-and-deliberation-infrastructure.md`
- `180-legitimacy-engines-elections-sortition-deliberation-recall.md`
- `224-deliberative-processes-and-citizens-assemblies-rails.md`

**Why it feels duplicative**
All six can surface on the same search query.

**Why it is not yet safe to collapse**
They cover different layers:
- theory of deliberative systems,
- selection infrastructure,
- anti-theater binding rules,
- legitimacy stack,
- and concrete process rails.

**Recommended next move**
One compact “deliberation stack” memo that names the roles of each file without deleting them.

**rev447 action**
- added `284-deliberation-stack-binding-and-legitimacy-guide.md` as the canonical bridge memo for this cluster
- added stack-relation notes to `88`, `111`, `143`, `159`, `180`, and `224`

---

### 5. Emergency / exception cluster
**Files**
- `23-emergency-governance-and-exceptions.md`
- `112-exception-control-and-emergency-powers.md`
- `165-emergency-powers-derogation-sunsets-rails.md`
- `186-emergency-powers-derogations-and-sunset-discipline.md`
- `234-public-health-preparedness-and-response-rails.md`

**Why it feels duplicative**
These all govern exceptional state action.

**Why it is not yet safe to collapse**
- `23` is the broad system frame
- `112` is the generic exception-control kernel
- `165` is the stronger modern emergency-powers rail
- `186` is the narrower discipline companion
- `234` is public-health-specific operating practice

**Recommended next move**
Merge only if a future editor can preserve the general-purpose kernel plus the public-health specialization.

---

### 6. DPI / identity / trust framework cluster
**Files**
- `160-digital-identity-credentials-privacy-utility.md`
- `164-digital-public-infrastructure-governance.md`
- `188-digital-public-infrastructure-governance.md`
- `210-digital-identity-and-credentialing-rails.md`
- `211-privacy-preserving-federation-and-consent-ledgers.md`
- `212-dpi-trust-framework-and-interop-governance.md`
- `213-digital-public-goods-intake-and-certification-rails.md`

**Why it feels duplicative**
Shared language: trust, identity, public infrastructure, interoperability.

**Why it is not yet safe to collapse**
This cluster spans at least four distinct roles:
- public-utility governance,
- identity and personhood utility,
- trust / certification,
- and procurement / intake rules.

**Recommended next move**
A shared glossary and a single “DPI family map” memo would help more than deletion.

---

## Tier 3 — likely cross-system adjacency rather than duplication

### 7. Integrity cluster
**Files**
- `22-public-integrity-and-procurement.md`
- `120-conflicts-of-interest-and-influence-integrity.md`
- `130-audit-and-inspection-integrity.md`
- `181-influence-lobbying-transparency-and-integrity-rails.md`
- `226-public-integrity-system-architecture.md`
- `227-prosecutorial-and-disciplinary-integrity-rails.md`

**Judgment**
These files are close in vocabulary but mostly represent a healthy stack: procurement, COI, inspection, lobbying transparency, system architecture, and enforcement.

**Recommended next move**
Avoid destructive merge. Prefer index improvements.

---

### 8. Constitutional change cluster
**Files**
- `124-constitutional-amendment-and-entrenchment.md`
- `171-constitutional-maintenance-and-amendment-ops.md`
- `205-constitutional-review-observability-and-precedent-ledgers.md`
- `206-constitutional-change-and-amendment-rails.md`

**Judgment**
High adjacency, but distinct roles: entrenchment theory, maintenance cadence, review observability, and change-event rails.

**Recommended next move**
Shared glossary and a sequence note.

---

## Tier 4 — operator hygiene

### 9. README / map / revision-log drift
**Diagnosis**
Several revisions improved the archive substantively without fully refreshing the navigation surface.

**rev445 action**
- fixed README last-updated drift
- surfaced the systems map and attachment guide
- recorded the canonicalization move for `276` / `278`

**Rule going forward**
No deep merge revision is complete until:
1. `00-README.md`,
2. `75-archive-map-and-entry-points.md`,
3. `102-revision-log.md`
all reflect the same reality.

---

## Anti-regret rule

When in doubt:
- narrow a duplicate into a **bridge memo**,
- keep one **canonical anchor**,
- and preserve distinct retrieval hooks until the archive can absorb them cleanly.

That is slower than hard deletion, but it is how this repo avoids semantic amnesia.
