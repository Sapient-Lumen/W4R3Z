# External challenge report (template — bounded)

**Track:** Shared (cross-cutting)

**Purpose:** make it possible for an external reviewer to challenge a **specific** claim, proof obligation, schema, or verifier behavior **without reading the whole archive**.

**Rules (keep it actionable):**
- Aim for **1–2 pages**.
- Include a **minimal reproducer** (packet digest / test vector / code snippet) and the exact tool/version pins.
- If you cannot provide a reproducer, say so explicitly and mark the confidence LOW.

---

## 0) Summary
- **Reporter / org:**
- **Date (UTC):**
- **Surface:** (e.g., PublicNotice; publication compliance; witness governance; offline verifier)
- **Severity guess:** (Critical / High / Medium / Low)

## 1) What is being challenged
Pick one primary target:
- **Claim ID:** (from `docs/166`) ________
- **Non-claim boundary implicated:** (from `docs/167`) ________
- **Proof obligation:** (PO-___ from `docs/159`) ________
- **Hazard:** (HZ-___ from hazard register) ________
- **Schema / kind:** (e.g., `hfv.public_notice.*`) ________
- **Tool / verifier behavior:** (name + path) ________

## 2) The challenge (plain language)
- What you believe is wrong / insufficient:
- What real dispute this could fail to settle:

## 3) Minimal reproducer (preferred)
### Option A — Evidence packet
- **Packet digest (sha256):**
- **Packet contents (paths):**
- **Expected verifier outcome:** (pass / problem codes)
- **Observed verifier outcome:**

### Option B — Test vector
- **Vector file path:**
- **Vector digest (sha256):**
- **Expected vs observed:**

### Option C — Reasoned argument (no reproducer)
- What prevents a reproducer:
- Confidence: (LOW unless independently corroborated)

## 4) Environment pins
- **Archive version:** (e.g., v250)
- **Verifier / tool version(s):**
- **OS / Python / runtime details (if relevant):**

## 5) Proposed fix direction (optional)
- What change you think would close the gap:
- What you think must *not* change (boundaries / non-claims):

## 6) Public response expectations
- Should this be treated as a spec/verifier false-confidence incident? (yes/no)
- If yes: propose the smallest regression vector that would prevent recurrence.

Related:
- Response playbook: `artifacts/playbooks/spec-error-response-playbook.md`
- Response note template: `artifacts/templates/spec-error-response-note.md`
