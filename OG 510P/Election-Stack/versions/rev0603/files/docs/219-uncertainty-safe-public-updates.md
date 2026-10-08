# 219 — Uncertainty-safe public updates (epistemic tags without schema changes)

**Track:** A (Deployable core)


Elections disputes often degrade because public updates are either:
- **too vague** (creating a rumor vacuum), or
- **too confident** (creating overclaim that later must be retracted).

This doc is a *tight* writing + review convention for publishing updates during incidents or disputes using:
- **PublicNotice** (as evidence) (`186`, `195`, `200`), and
- a signed **Public Statement** template (`artifacts/templates/public-statement-template.md`),

while applying the epistemic discipline in `218` *inside the human text* (no new schemas, no new envelope kinds).

For AI-era impersonation/deepfake response discipline and a measurable time-to-refute budget, see `240-deepfake-frontier-and-time-to-refute.md`.
For interpreting supersession/correction chains into a deterministic “current state”, see `220-publicnotice-graph-resolution-and-effective-state.md`.

If you are shipping a bundle to an external verifier, pair this with a bounded **claim card** (`217`, template: `artifacts/templates/claim-card.md`).

When the update is responding to a **forged “official” statement** or synthetic media incident,
pair this doc with `194.4` (time-to-refute) and drill an authenticity response cell using
`artifacts/checklists/authenticity-response-cell-checklist.md`.

## 219.1 Minimal update contract (what every update should contain)

Each public update SHOULD include, in plain language:

1) **Time** (local + UTC) and **scope**
   - jurisdiction / election_id when applicable
   - what systems or surfaces are in-scope for this update

2) **Status**
   - Intake posture (Normal / Degraded / Frozen)
   - what *changed* since the last update (if this is a follow-up)

3) **What we know** (tagged, confidence-scored)
   - Prefix each load-bearing bullet with the tag set in `218`, e.g.:
     - `[OBSERVED|HIGH] …`
     - `[MEASURED|MEDIUM] …`
     - `[ATTESTED|MEDIUM] …`
     - `[INFERRED|LOW] …`

4) **What we do not know yet** (make missingness explicit)
   - Use `[UNKNOWN|*]` when the unknown is load-bearing (do not hide it in prose)

5) **What we are doing next** (verification plan)
   - name the next evidence object(s) that will be produced or checked (bounded; avoid “we are investigating”)

6) **When we will update again**
   - include an explicit *next update* time when feasible

7) **Reproducibility hooks**
   - include **Notice IDs** (for PublicNotice) and content-addressed pointers (hashes, packet digests) where available
   - prefer digests + references over screenshots (`206`)


## 219.2 Tagging syntax that works in the real world

Use a short prefix convention that can survive copy/paste across channels:

- **Format:** `[<TAG>|<CONF>]` where TAG is from `218` and CONF is HIGH|MEDIUM|LOW.
- Keep tags on **bullets**, not on paragraphs.
- If a statement has multiple parts, split it into multiple bullets.

Examples:

- `[MEASURED|HIGH] Status page requests returned HTTP 200 from 5 vantage regions at 21:14Z.`
- `[OBSERVED|MEDIUM] In-person voting continued at Location X during the outage window.`
- `[REPORTED|LOW] We received reports of ballot-style mismatch in precinct P-014; not yet corroborated.`
- `[UNKNOWN|HIGH] We do not yet know whether the mismatch report is isolated or systematic.`

Avoid bespoke hedges (“seems”, “likely”, “apparently”) as substitutes for tags.


## 219.3 Corrections and reversals (avoid “quiet edits”)

When a previously published statement becomes incorrect:

- Publish a **correction** PublicNotice (see `186` and the PublicNotice correction templates).
- In the corrected notice text:
  - explicitly reference the prior notice_id (and, if helpful, quote the *minimum* necessary clause)
  - replace the prior claim with a tagged correction, e.g.:
    - `[ATTESTED|HIGH] Correction of NOTICE-…: Prior notice stated X. Corrected: Y (reason: …).`

The goal is not to avoid mistakes; it is to make **revisions auditable** and hard to weaponize.


## 219.4 Channel-specific guidance (tight)

- **Status page / website:** publish the full structure in `219.1` and include digest pointers.
- **Social posts:** publish a “digest card” style excerpt (`206`) plus:
  - notice_id
  - next_update time
  - a pointer to the canonical notice feed (`200`) or status page

Do not move primary facts into ephemeral channels without a canonical PublicNotice/statement.


## 219.5 Review gates (fast)

Before publishing, run a 60-second review:

- Use `artifacts/checklists/public-update-epistemic-quickcheck.md`.
- If a statement is likely to be litigated later, ensure it is bounded by a claim card (`217`)
  and that any inferences are tagged (`218`).

