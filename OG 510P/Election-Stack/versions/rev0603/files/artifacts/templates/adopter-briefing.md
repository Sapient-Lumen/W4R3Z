# Adopter briefing (template — 2 pages max)

**Track:** Shared (cross-cutting)


**Purpose:** a fast, honest translation of the Election Stack (Track A) for decision‑makers (election directors, county IT, procurement, legislators, civil society).

**Rules (keep this usable):**
- Max length: ~2 pages.
- Every load‑bearing claim uses epistemic tags (`docs/218`) and points to an evidence artifact (packet digest / public surface / checklist).
- Prefer *what can be proven after a crisis*, not feature lists.

---

## 0) Executive summary (3 sentences)

- [INFERRED|HIGH] **Problem:** Elections fail most often through **legitimacy collapse**: people cannot prove what happened after the fact (under adversarial pressure).
- [ATTESTED|HIGH] **What this gives you:** a **paper‑compatible evidence wrapper** that makes key election facts **portable, independently checkable, and court‑packagable** (Track A).
- [UNKNOWN|LOW] **What it does not do:** it does **not** make internet ballot return safe by default; remote return remains Track B research (see `docs/167`).

## 1) What changes vs. what stays the same

### Stays the same
- Paper ballot of record (or BMD) and existing tabulation/audit/recount procedures.
- Voting system vendor can remain proprietary **(Track A does not require open source)**, but the evidence wrapper is compensating for opacity it cannot remove. The dispute value of the evidence layer **increases** with minimal vendor transparency (config/version IDs, signed change history, hashes when feasible): see `docs/17-supply-chain-and-build-integrity.md`.
### Changes (additive wrappers)
- Official public communications are published as **signed, hash‑bound evidence objects** (`PublicNotice`).
- Public evidence is emitted in **small, verifiable packets** (offline verifier supported).
- “Missing evidence” becomes measurable (suppression / delay reports), rather than rumor.

## 2) What you can prove after a contested election

Pick 3–5, matched to your jurisdiction’s dispute history:

- [MEASURED|MEDIUM] **Who said what, when:** authentic official statements vs forged screenshots (PublicNotice + keyset pins).
- [MEASURED|MEDIUM] **Whether evidence was withheld or delayed:** measurable publication compliance (contracts + trigger events + coverage reports).
- [MEASURED|MEDIUM] **Whether audiences saw different “truths”:** split‑view/parity evidence across public surfaces (parity snapshots + liveness beacons).
- [ATTESTED|MEDIUM] **Court‑ready bundles for specific allegations:** bounded claim‑first evidence packets (`docs/211`).

## 3) Minimal pilot (what “try it once” looks like)

**Scope (recommended first pilot):**
- One county / one election cycle.
- Paper ballots / BMDs.
- Track A evidence wrappers only.

**Deliverables (publishable):**
- PublicNotice feed + signed keyset allow‑list.
- Official channel directory + `.well-known` bootstrap.
- At least 2 public evidence packets (pre-election + election night + post‑election).
- After‑action report (`artifacts/templates/after-action-report.md`).
- Verifier capacity roster published before polls close (kind `hfv.verifier.capacity_roster`; `docs/241-verifier-capacity-and-distribution.md`).

See: `docs/track-a/PILOT.md`.

## 4) Costs and staffing (ballparks + fill-in)

This section exists so adopters do not accidentally treat “evidence wrappers” as “free.”

- [UNKNOWN] Implementation path: (internal build / vendor / partner) ________
- [UNKNOWN] Independent monitoring partners (recommended): ________
- [UNKNOWN] Verifier capacity plan (who will publish replayable reports; where those reports land): ________

**Planning ballparks (replace with local estimate; not based on deployed deployment data):**
- [INFERRED|LOW] **Minimal pilot** (one county; paper ballots; use existing web stack; 1–2 packets + PublicNotice feed):
  - one-time setup: **low five figures → low six figures** (e.g., ~$20k–$150k)
  - per election cycle ops: **low five figures** (e.g., ~$5k–$50k)
- [INFERRED|LOW] **Moderate** (mirrors + newsroom verifier tooling + routine drills + more packets):
  - one-time setup: **low six figures → mid six figures** (e.g., ~$100k–$500k)
  - per cycle ops: **mid five figures → low six figures** (e.g., ~$25k–$150k)
- [INFERRED|LOW] **High** (multi‑county/state; dedicated monitoring cell in the 24–72h window; stronger hardening):
  - one-time setup: **high six figures → low seven figures+** (e.g., ~$500k–$2M+)
  - per cycle ops: **low six figures → seven figures** (e.g., ~$150k–$1M+)

**Staffing implications (typical roles; adjust to your jurisdiction):**
- [INFERRED|LOW] Public communications lead (election window): ~0.1–0.3 FTE
- [INFERRED|LOW] IT/DevOps for public surfaces + mirrors: ~0.1–0.2 FTE (bursty pre-election)
- [INFERRED|LOW] Security/key steward (ceremonies + incident posture): ~0.05–0.1 FTE (bursty)
- [INFERRED|LOW] Legal/public‑records liaison (admissibility + retention): bursty near key dates
- [INFERRED|LOW] Independent monitor liaison (coordination + access): ~0.05–0.1 FTE

Fill in:
- [UNKNOWN] Software/tooling cost line items: ________
- [UNKNOWN] Training + drills: ________
- [UNKNOWN] Monitoring/hosting (if any): ________

## 5) Claims and non‑claims (don’t overpromise)

- Claims contract: `docs/166-scope-and-claims-contract.md`
- Non‑claims / boundaries: `docs/167-non-claims-and-boundaries.md`

## 6) “What happens when something goes wrong?”

- Incident triage quickmap: `docs/216-incident-triage-and-evidence-quickmap.md`
- Court bundle recipes (bounded): `docs/211-court-evidence-bundle-recipes.md`
- Uncertainty‑safe public updates: `docs/219-uncertainty-safe-public-updates.md`

### Legibility-theater guardrails (how to tell this is substantive)

- [MEASURED|MEDIUM] Offline verification works without vendor services (observer kit + packet verifier).
- [MEASURED|MEDIUM] Independent verifier output exists and is replayable (not only official statements).
- [MEASURED|MEDIUM] A pre-election capacity roster exists (who will look + where reports land) and is kept current (kind `hfv.verifier.capacity_roster`; `241`).
- [MEASURED|MEDIUM] Witness/monitor ecosystem shows **dissent + disagreement**, not only cosigns (`hfv.witness.liveness_dissent_report`).
- [MEASURED|MEDIUM] Missed publication deadlines become visible (coverage/suppression reports), rather than “we’ll look into it.”
- [MEASURED|MEDIUM] Publications pass MAPT (minimal adversarial publication test; `docs/187`) so “technically public” does not mean “operationally opaque”.
- [INFERRED|MEDIUM] Multiple implementors/mirrors can verify the same evidence bytes (no single platform chokepoint).

## 7) Next step (decision)

Choose one:
- **Pilot** Track A wrappers (recommended start).
- **Do nothing** (and accept that future disputes may lack portable evidence).
- **Request Track B remote return work** (requires explicit non‑claims and independent review).

---
