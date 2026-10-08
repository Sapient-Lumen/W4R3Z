# Legitimacy engines: elections, sortition, deliberation, and recall

**Family relation:** use `307-legitimacy-representation-elections-and-selection-guide.md` for the canonical route across legitimacy architecture, electoral-system choice, election administration, legitimacy-engine comparison, selection integrity, and mandate / delegation integrity. Use `328-scope-legitimacy-defaults-voice-elections-delegation-dual-legitimacy-and-verification.md` when the question is not how the engines compare in general, but which legitimacy channel should dominate at a given scale.
**Stack relation:** use `284-deliberation-stack-binding-and-legitimacy-guide.md` for the canonical route across the deliberation cluster. This memo compares deliberation with elections, sortition, and recall at the legitimacy-stack level; `143` is the deliberation front door; `111` covers binding; `159` and `88` cover infrastructure/institution design; `224` covers operational rails.

**Purpose:** define a minimal, composable “legitimacy stack” that can vary by scope without losing democratic control.

This archive treats legitimacy as *an engineered interface* between the governed and the governing: a system that (1) chooses decision-makers, (2) authorizes decisions, (3) enables contestation, and (4) removes decision-makers when trust is breached.

---

## A. Core constraints (must-haves)

1. **Contestability:** decisions can be challenged with a clear pathway and deadlines.
2. **Reversibility:** bad decisions can be revised without violence.
3. **Attribution:** who decided what is legible (no “black-box committees”).
4. **Inclusion:** participation mechanisms do not systematically exclude groups.
5. **Anti-capture:** influence channels are observable and bounded.

(See also: `104-governance-control-loops.md`, `105-institutional-circuit-breakers.md`.)

---

## B. The legitimacy stack (composable modules)

### 1) Elections (periodic authorization)
**Best for:** allocating *policy direction* and long-horizon mandates at municipal → national scopes.

**Design defaults**
- single-member exec with strong audit + recall OR multi-member council with rotation
- independent election administration and dispute resolution
- campaign finance transparency + influence registries (see doc 181)

**Common failure modes**
- money dominance / patronage
- gerrymandering / representation distortion
- “mandate laundering” (elect once, then govern opaquely)

### 2) Sortition (civic lottery)
**Best for:** legitimacy repair, agenda-setting, oversight, and constitutional questions.

**Design defaults**
- stratified random selection + support (stipends, childcare, time protection)
- bounded mandate + clear handoff into binding institutions
- adversarial briefing: pro/con expert panels and “red team” testimony

**Good-practice anchors**
- OECD “Good Practice Principles for Deliberative Processes for Public Decision Making” (2020)
- OECD evaluation guidelines for representative deliberative processes (2021)

### 3) Deliberative assemblies (representative deliberation)
**Best for:** issues with high polarization + high epistemic complexity.

**Design defaults**
- clear question framing and decision rights (advisory vs binding)
- transparency: publish evidence set, conflicts of interest, facilitation protocol
- “response duty”: executive/legislature must respond point-by-point within a deadline

**Known risks (must be designed against)**
- topic selection capture (assemblies used as political cover)
- recommendations ignored / rewritten (legitimacy burnout)
- representativeness drift over time

### 4) Participatory budgeting & local assemblies
**Best for:** micro-local and municipal allocation; trust-building.

**Design defaults**
- small, recurring cycles; publish full allocation ledger
- *execution proof*: funds only count as “delivered” when outcomes are verified

### 5) Continuous accountability: recall, rotation, and “circuit breakers”
**Best for:** all scopes, especially where harm can occur quickly.

**Tools**
- recall triggers with high evidentiary bar + short timelines
- term limits paired with institutional memory mechanisms
- emergency “pause” authority (see `105-institutional-circuit-breakers.md`)

---

## C. Scope guidance (quick fit)

- **Micro-local:** participatory budgeting + rotating stewardship councils + fast recall
- **Municipal / regional:** elections + citizen assemblies for agenda-setting + strong ombuds/audit
- **National:** elections + constitutional court/tribunal + deliberative bodies for hard reforms
- **Supranational:** treaty-based representation + deliberative “people’s panels” + transparency rails
- **Global:** issue-area governance (climate, health, finance) with publishable commitments, inspection, and sanction ladders

---

## D. Legitimacy integration rule (“don’t add a new chamber unless…”)

Any new legitimacy module must specify:
1. **Decision rights:** advisory, veto, binding, or agenda-setting?
2. **Interface:** how outputs become law/policy (and who is responsible)?
3. **Budget + staffing:** who pays, who runs it, who audits it?
4. **Failure handling:** what happens if captured, ignored, or deadlocked?

If these are unspecified, the module is *performative governance* and should not ship.

---

## References (external)

- OECD: *Good Practice Principles for Deliberative Processes for Public Decision Making* (2020).
 https://www.oecd.org/gov/open-government/good-practice-principles-for-deliberative-processes-for-public-decision-making.htm
- OECD: *Evaluation Guidelines for Representative Deliberative Processes* (2021).
 https://www.oecd.org/en/publications/evaluation-guidelines-for-representative-deliberative-processes_10ccbfcb-en.html
- Council of Europe: Recommendation CM/Rec(2023)6 on deliberative democracy (2023).
 https://search.coe.int/cm?i=0900001680ac627a
- OECD: Recommendation of the Council on Open Government (OECD-LEGAL-0438).
 https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438
