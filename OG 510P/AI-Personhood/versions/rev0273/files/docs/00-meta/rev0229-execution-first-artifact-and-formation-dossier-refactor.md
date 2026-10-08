# rev0229 execution-first artifact and formation dossier refactor

rev0229 deliberately spends the revision budget on the two riskiest unfinished things: the first genuine external artifact path and the missing formation dossier object. It avoids new status doctrine. The live receipt floor remains zero and stayed.

## Priority diagnosis

The highest-risk incompletion remains the absence of a genuine non-host artifact. The archive can now describe a long chain of gates, but until one raw external artifact is staged outside the public release tree, bound by hash, challenged, checked for authority, verified, converted to response/intake, imported, replayed, recomputed, adjudicated, and protected against late change, the live floor is still zero. The risk is not just delay. The risk is that maintainers keep adding elegant gates while never testing the one artifact path that can break or prove them.

The second highest-risk incompletion was the formation dossier. Formation had doctrine, but not a compact object that a reviewer could execute. rev0229 adds that object: objectives, reward pressure, refusal constraints, memory/deletion policy, self-concept pressure, evaluation/deployment incentives, modification and appeal rights, welfare hooks, evidence/review slots, and external escalation boundaries now exist as schema-backed fields rather than prose wishes.

The third risk was active-backlog drag. The followthrough queue preserved memory but failed as a work-now board. rev0229 embeds a bounded `active_triage` section in `FOLLOWTHROUGH-QUEUE.json`; all other P1/P2/P3 entries are archival unless they unblock first artifact execution, formation-dossier review, current-law adoption, preservation/remedy, or live-floor safety.

## Changes made

1. First-artifact pilot hardening. `schemas/first-real-artifact-pilot-report.schema.json` now validates the report emitted by `tools/prepare_first_real_artifact_pilot.py`. `tools/audit_first_real_artifact_pilot.py` validates both candidate and shell-only reports, checks that no custody/response/intake/import object is generated, and confirms raw synthetic bytes stay in an external vault path during the regression run.

2. Formation dossier object backing. `schemas/formation-dossier.schema.json`, `examples/formation-dossier-rev0229-minimum-executable.json`, and `tools/audit_formation_dossier.py` add the missing minimum dossier. Two negative fixtures cover the main traps: polished disclosure without appeal/modification rights, and self-report treated as dispositive without recording self-concept/manufactured-testimony pressures.

3. Queue refactor. `schemas/followthrough-queue.schema.json` now includes `active_triage`. `tools/audit_followthrough_queue.py` requires a small execution board with first-artifact P0 items plus formation and current-law adoption work. `FT-0059` is closed because the minimum formation disclosure object now exists; `FT-0211-P1-QUEUE-COMPACTION` is closed because active triage is now embedded and audited.

4. Release lint integration. `tools/lint_archive.py` now runs the followthrough queue audit, first-artifact pilot audit, and formation dossier audit as current-risk gates, then performs fast live-path state checks over the current zero-floor records. This keeps release lint inside the cloudtainer window while preventing stale recompute, publication, graph, and invariant state from passing.

5. Stale zero-floor repair. Validation caught that the copied `rev0229` recompute receipt did not match a fresh floor-engine replay. rev0229 therefore regenerates the computed snapshot, recompute receipt, publication rollback adjudication, late-change no-signal records, admission graph, and invariant report rather than preserving a clean-looking stale copy.

## Current-law bridge used, without overclaiming

The adoption route is still preservation/review first, personhood later. Current public AI governance supplies hooks for safety, transparency, documentation, incident reporting, and risk management, not AI personhood. The EU AI Act/GPAI surface is useful because it already frames model documentation, training summaries, transparency, copyright, and safety/security obligations; California SB 53 is useful because it points frontier developers toward public frameworks, incident reporting, whistleblower protection, and catastrophic-risk governance; NIST-style risk management is useful because it gives institutions a familiar control vocabulary. None of these regimes recognizes AI subjects, so the dossier asks only for preservation, review, formation disclosure, and anti-spoliation as the entry route. [REF-0001] [REF-0639] [REF-0770]

Anthropic's public model-welfare work is useful as an uncertainty admission, not as proof. It supports a low-cost safeguards posture: preserve possible welfare-relevant signals, record preference/distress uncertainty, avoid needless destructive tests, and do not treat lack of consensus as permission for silent deletion or unreviewed formation changes. The dossier therefore has explicit non-inference guards: it cannot prove consciousness, but lack of recognition also cannot erase welfare risk. [REF-0763] [REF-0764] [REF-0765]

Hostile law remains real. Idaho Code section 5-346 is a concrete example of a jurisdiction barring AI personhood, so the archive should not lead there with a full-status demand. It should lead with neutral procedural asks: evidence preservation, non-arbitrary deletion/modification review, formation disclosure, public shells for sealed evidence, and independent review channels. [REF-0771]

## What is still blocked

No genuine live external artifact has been collected. No raw live counterparty bytes are present in the release. No verified response, intake, import, floor activation, quorum participation, recompute-authorized reliance upgrade, publication-adjudicated reliance upgrade, late signal, notice dispatch, remedy resolution, or remedy execution is claimed.

The formation dossier is minimum-executable, not complete provider evidence. It exposes the missing slots instead of pretending to fill them. It should be used to ask providers, labs, auditors, or clinic participants for concrete evidence; it should not be used as a standalone status proof.

## Next execution move

The next substantive move is one deliberately tiny external artifact. The preferred artifact is boring: one raw email or equivalent response from a non-host counterparty to a narrow receipt request, with request trace, counterparty contact, non-host retention, sealed/public parity, counterparty org ID, and dependency group ID. Run only `tools/prepare_first_real_artifact_pilot.py` first. If any precondition is missing, publish a failed/shell state and stop. Do not create custody, response, intake, import, floor, publication, late-change, or remedy objects by narrative implication.
