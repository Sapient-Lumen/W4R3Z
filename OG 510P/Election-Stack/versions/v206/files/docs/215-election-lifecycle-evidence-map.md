# 215. Election lifecycle evidence map (operator + verifier alignment)

**Track:** A (Deployable core)


This doc is a **compact bridge** between (a) the real-world election lifecycle and (b) the evidence objects,
public surfaces, and operator checklists in this archive.

It is *not* a second operations manual. Its job is to make it easier to answer:

- “What evidence surfaces exist **when**?”
- “What public commitments should already be published **before** Election Day?”
- “If something goes wrong in phase X, what minimal packet(s) make the dispute legible?”

If you only read one section, read **215.2**.

If you are actively triaging an incident and need a compact symptom→packet map, see `216-incident-triage-and-evidence-quickmap.md`.


## 215.1 How to use this map (anti-bloat)

- Treat this as a **checklist of cross-links**, not as a place to expand prose.
- If you add a new evidence kind or a new public surface, update:
  - the relevant numbered spec(s),
  - `docs/PUBLIC_SURFACES.md` (if it’s a stable external surface),
  - the appropriate operator checklist under `artifacts/checklists/`,
  - and **then** update this map with one line.


## 215.2 Phase map (what exists when)

The phases below are intentionally coarse. Jurisdictions vary.
The purpose is to ensure that *high-leverage* evidence surfaces exist early enough that they can’t be “invented later.”

| Phase | Primary dispute / threat themes | “Minimum” evidence surfaces (cross-links) | Operator artifacts (examples) |
|---|---|---|---|
| **P‑0: Program design & procurement** | Vendor capture, opaque updates, non‑reproducible builds | Scope/claims: `154`, `166–167` • Supply chain: `17`, `76`, `97–98`, `170` • Tool maturity & safety: `212` | Procurement language: `artifacts/templates/procurement-language.md` • COI disclosure: `artifacts/checklists/coi-and-funding-disclosure-checklist.md` |
| **P‑1: Pre‑election public comms bootstrapping** | Impersonation, “where do I look?”, split‑reality rumor channels | Official directory: `203` • `.well-known` bootstrap: `204` • Signing key allow‑list: `208` • Cache/freshness posture: `205` • Surface security snapshot: `199` | Official channels hardening: `artifacts/checklists/official-communications-channels-hardening-checklist.md` • Secure time: `artifacts/checklists/secure-time-checklist.md` |
| **P‑2: Registration & eligibility systems** | Registration suppression/disinfo, VRDB integrity, turnout‑oracle leaks | VRDB integrity + availability: `73` • VRDB comms posture: `77` • Cross‑register consistency evidence: `209` | VRDB hardening: `artifacts/checklists/vrdb-hardening-checklist.md` • VRDB disinfo response: `artifacts/checklists/vrdb-disinfo-response-checklist.md` |
| **P‑3: Ballot definition + EMS pipeline** | Targeted ballot manipulation, silent configuration drift | Ballot definition pipeline: `60–61` • CDF mapping: `62`, `70` • Release integrity: `160`, `190` | Ballot definition pipeline checklist: `artifacts/checklists/ballot-definition-pipeline-checklist.md` • Incident response: `artifacts/checklists/ballot-definition-incident-checklist.md` |
| **P‑4: Key ceremonies & parameter publication** | Key compromise, parameter substitution, “late” changes | Key management: `05`, `55–57`, `29` • Publication deadlines: `145`, `181` • Canonical envelopes/signing: `173`, `176` | Key ceremony checklist: `artifacts/checklists/key-ceremony-checklist.md` • Key destruction: `artifacts/checklists/key-destruction-ceremony-checklist.md` |
| **P‑5: Pre‑election testing + public readiness** | “Trust me” testing, contested readiness claims | Assurance posture: `10`, `25` • Public evidence portal: `71` • Exercises: `86`, `90` • Publishable rehearsal outputs: `187` | Exercise planning: `artifacts/checklists/exercise-planning-checklist.md` • Go/No‑Go: `artifacts/checklists/go-no-go.md` |
| **P‑6: Voting period (in‑person / paper‑of‑record)** | Polling place incidents, chain‑of‑custody disputes, selective omission | Precinct closeout evidence: `197–198` • PublicNotice comms lane: `186`, `200` | Precinct closeout capture checklist: `artifacts/checklists/precinct-closeout-evidence-capture-checklist.md` • Incident comms proof: `artifacts/checklists/incident-comms-proof-checklist.md` |
| **P‑7: Voting period (networked evidence surfaces)** | Partition, equivocation, selective censorship, split views | PBB transparency: `04`, `23`, `103` • Public surfaces parity snapshots: `201–202` • Liveness beacons: `210` • Digest cards: `206` | Public surface cache/freshness test plan: `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md` • Unreachability proof: `artifacts/checklists/unreachability-proof-checklist.md` |
| **P‑8: Closeout, tabulation, and ENR** | ENR drift, premature disclosure, altered exports | Results pipeline: `68` • ENR security + drift: `63`, `69` • Results disclosure policy: `64` • Results API contract: `artifacts/templates/results-api-contract.md` | ENR security checklist: `artifacts/checklists/enr-security-checklist.md` • ENR drift monitoring: `artifacts/checklists/enr-drift-monitoring-checklist.md` |
| **P‑9: Audit, recount, certification, and remedies** | “Which remedy is justified?”, missing audit trails | Audit & recovery: `09`, `24`, `36` • Court-ready bundles: `211` • Proof obligations: `159` | After action report: `artifacts/templates/after-action-report.md` • Mass compromise response: `artifacts/checklists/mass-compromise-response-checklist.md` |
| **P‑10: Post‑election retention & transparency** | Evidence decay, selective disclosure, delayed revelations | Retention + secrets policy: `98`, `189` • Publication hygiene: `187`, `tools/public_artifact_lint.py` | Retention incident response: `artifacts/playbooks/retention-incident-response.md` • Public artifact redaction: `artifacts/checklists/public-artifact-redaction-checklist.md` |


## 215.3 The “pre‑commit” set (publish before it matters)

These are the surfaces you want published early enough that they are costly to counterfeit later.
If you publish them only *after* controversy starts, they do less work.

1. **Official channel directory** (`203`) + stable IDs registry (`artifacts/registries/official-channels.csv`).
2. **PublicNotice signing keyset** (`208`) + a key ceremony transcript packet (see key checklists).
3. **`.well-known` discovery pointer** (`204`) that commits to the directory digest(s) and current feed digest(s).
4. **Cache/freshness policy** (`205`) plus a public statement of monitoring posture (how parity/freshness is checked).
5. **Official surface security snapshot** (`199`) repeated on a predictable cadence (pre‑election + election week).


## 215.4 When something goes wrong: minimal packet instincts

This is intentionally heuristic. For concrete kinds and required attachments, see `173`, `176`, and `docs/EVIDENCE_OBJECT_CATALOG.md`.

- If the dispute is **“official comms are forged / inconsistent / buried”**:
  - Publish a `PublicNotice` (`186`) whose subject binds the relevant surface digests.
  - Pair with `PublicSurfaceParitySnapshot` (`201`) and/or `LivenessBeacon` (`210`) rather than shipping screenshots or bodies.
  - If official channels do not converge on the same effective state, assemble a bounded divergence handoff bundle (`222`).
  - Use digest cards (`206`) for low-bandwidth channels.

- If the dispute is **“ENR changed / drifted / is inconsistent across mirrors”**:
  - Publish a `PublicNotice` plus a bounded ENR drift artifact (see `69` + checklists) and (if relevant) a parity snapshot.

- If the dispute is **“a precinct’s closeout evidence is missing or altered”**:
  - Use `197–198` patterns so omission itself is provable (index + chaining), then point the public to the missing entry.

- If the dispute is **“remedy justification”**:
  - Assemble the smallest bundle that satisfies the relevant proof obligations (`159`) using `211` recipes.


## 215.5 Research hooks (keep small)

If you want to extend this map, do it by tightening the cross-links, not by expanding prose.
Candidate additions should land in `207` only if they name:
(a) the claim boundary, (b) the hazard/proof obligation, and (c) an artifact that would count as progress.
