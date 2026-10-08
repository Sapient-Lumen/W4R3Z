# 158. Hazard register (structure + usage)

**Track:** Shared


A hazard register is a **living map of failure modes** with:
- preconditions (what must be true for the hazard to exist),
- triggers/signals (what we can observe),
- impact,
- detection artifacts (what evidence proves it happened),
- and response playbooks.

This is distinct from a generic “risk register” because it is oriented toward **detectability and response**.

## 158.1 Where it lives

- `../artifacts/hazards/hazard-register.csv`

## 158.2 Rules

1. Every high-severity hazard MUST have at least one:
   - detection artifact, and
   - response playbook/checklist.
2. If a hazard is “not detectable”, treat that as a design failure and open an ADR.
3. Tie hazards to claims:
   - if a hazard violates a claim, the claim’s evidence lane MUST mention it.

## 158.3 Minimum fields

See the CSV header for required columns. Recommended additions:
- Severity (S1–S4)
- Likelihood band
- Affected track (A/B/C)
- “Deadline to publish evidence” (if time-bounded accountability applies)

## 158.4 How to use it in reviews

- For any new protocol/scope change:
  - add hazards (or confirm why not)
  - update claim/evidence matrix
  - update drills/checklists if response changes