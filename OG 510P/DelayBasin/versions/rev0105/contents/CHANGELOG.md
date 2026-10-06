# DelayBasin revision log (rev0105)
- operationalized existing reasoning-firebreak / scratchpad-quarantine / public-extract canon with a durable `FIREBREAK-LEDGER.json` surface and a compact `reasoning_firebreak_witness` field in `REVISION-RECEIPT.json`
- strengthened receipt law so a revision can no longer claim trace-role hygiene only in prose; it must now name the judged property, the public extract that counts, the withheld trace surface, the allowed role of that withheld surface, and the exposure or reinclusion consequence
- promoted the smaller firebreak-ledger / receipt-witness law while keeping the stronger trace-surgery / reasoning-state-carrier controller explicitly deferred

# DelayBasin revision log (rev0104)
- operationalized existing retrospective-write / cooldown-window / off-path-adjudication canon with a durable `RETROSPECTIVE-QUEUE.json` surface and a compact `retrospective_write_witness` field in `REVISION-RECEIPT.json`
- strengthened `check_retrospective_write_contract.py` so retrospective-write law now has to stay wired across method, trajectory, runbook, receipt contract, shipped queue surface, and the current receipt
- promoted the smaller cooled-admission queue/witness law while keeping the stronger public sleep-phase / off-path-consolidation story explicitly cooled in queue state rather than silently implied or rushed into canon

# DelayBasin revision log (rev0103)
- new method note on resolution witnesses, closure reasons, and reopen triggers
- new canon claim `CL-0109`, invariant `INV-0107`, open question `OQ-0109`, and prompt pair `PP-0068`
- new durable `RESOLUTION-LEDGER.json` surface plus a compact `resolution_witness` field in `REVISION-RECEIPT.json` for objects that stop being live, the reason they closed, their successor or explicit absence, and their reopen triggers
- `check_resolution_witness_contract.py` — lint guard that keeps resolution-witness / closure-reason / reopen-trigger wiring explicit across method, trajectory, runbook, receipt contract, and the shipped closure ledger

# DelayBasin revision log (rev0102)
- new method note on foreign-pressure witnesses, import lineages, and bounded assimilation
- new canon claim `CL-0108`, invariant `INV-0106`, open question `OQ-0108`, and prompt pair `PP-0067`
- new durable `FOREIGN-PRESSURE-LEDGER.json` surface plus a compact `foreign_pressure_witness` field in `REVISION-RECEIPT.json` for exact neighboring-datacube source packets, bounded takes, and explicit non-takes
- bibliography entries on explicit derivation, ingredient provenance, and precise artifact identification as pressure for foreign-pressure provenance instead of vague import folklore
- `check_foreign_pressure_witness_contract.py` — lint guard that keeps foreign-pressure-witness / import-lineage / bounded-assimilation wiring explicit across method, trajectory, runbook, receipt contract, and the shipped pressure ledger

# DelayBasin revision log (rev0101)
- new method note on assumption witnesses, expiry triggers, and invalidation cues
- new canon claim `CL-0107`, invariant `INV-0105`, open question `OQ-0107`, and prompt pair `PP-0066`
- new durable `ASSUMPTION-LEDGER.json` surface plus a compact `assumption_witness` field in `REVISION-RECEIPT.json` for live load-bearing assumptions that have not yet been discharged into direct evidence or stable law
- bibliography entries on explicit assumption documentation in risk and assurance practice as pressure for assumption honesty instead of fluent caveat prose
- `check_assumption_witness_contract.py` — lint guard that keeps assumption-witness / expiry-trigger / invalidation-cue wiring explicit across method, trajectory, runbook, receipt contract, and the shipped assumption ledger

# DelayBasin revision log (rev0100)
- new method note on followthrough witnesses, blocked outputs, and explicit handoffs
- new canon claim `CL-0106`, invariant `INV-0104`, open question `OQ-0106`, and prompt pair `PP-0065`
- new durable `FOLLOWTHROUGH-QUEUE.json` ledger for still-live queued or handed-off remainder work, plus a compact `followthrough_witness` field in `REVISION-RECEIPT.json`
- bibliography entries on issue handoff, issue creation from comments/code, merge-request thread handoff, and explicit blocked-by relations as pressure for honest followthrough rather than silent disappearance or sticky local ownership
- `check_followthrough_witness_contract.py` — lint guard that keeps followthrough-witness / blocked-output-queue / explicit-handoff wiring explicit across method, trajectory, runbook, receipt contract, and the shipped queue surface

# DelayBasin revision log (rev0099)
- new method note on reentry-cue witnesses, durable latest paths, and navigation-integrity budgets
- new canon claim `CL-0105`, invariant `INV-0103`, open question `OQ-0105`, and prompt pair `PP-0064`
- revision receipts now carry a compact `reentry_cue_witness` field with surface lineage, primary landing surface, durable cue set, excluded stale or broken paths, cue-state classification, and fail-closed repair
- bibliography entries on browser history entry semantics, `popstate` navigation behavior, and ignored fragment-miss behavior as pressure for explicit latest-path integrity rather than optimistic landing
- strengthened sync law: `SURFACE-STATUS.json`, `RELEASE-MANIFEST.json`, `ARCHIVE_INDEX.md`, and `REVISION-RECEIPT.json` must now agree on the current packaged head, and `context-pack.json` now carries the durable cue surfaces needed for minimal reentry
- `check_reentry_cue_contract.py` — lint guard that keeps reentry-cue / durable-latest-path wiring explicit across method, trajectory, runbook, receipt contract, and shipped release surfaces

# DelayBasin revision log (rev0098)
- new method note on authorship witnesses, autonomy postures, and maker-checker traces
- new canon claim `CL-0104`, invariant `INV-0102`, open question `OQ-0104`, and prompt pair `PP-0063`
- revision receipts now carry a compact `authorship_witness` field with initiating lane, draft-authorship posture, approval lane, execution lane, review or compensating-control lane, autonomy posture, collapse state, and repair posture
- bibliography entries on explicit human-AI role differentiation, agent-requester-versus-approver separation, delegated-agent review return, and provenance-manifest discipline as support for collaborative authority-lane honesty
- `check_authorship_witness_contract.py` — lint guard that keeps authorship-witness / receipt-contract / promptcraft wiring explicit across method, trajectory, runbook, and the shipped receipt

# DelayBasin revision log (rev0097)
- new method note on scope witnesses, active-request packets, and ambient-roster guards
- new canon claim `CL-0103`, invariant `INV-0101`, open question `OQ-0103`, and prompt pair `PP-0062`
- revision receipts now carry a compact `scope_witness` field with active request, exact target, in-scope surfaces, ambient exclusions, scope state, and repair posture
- bibliography entries on least privilege, explicit OAuth scope, and per-request least-privilege pressure as support for exact active-request discipline
- `check_scope_witness_contract.py` — lint guard that keeps scope-witness / receipt-contract / promptcraft wiring explicit across method, trajectory, runbook, and the shipped receipt

# DelayBasin revision log (rev0096)
- new method note on status-lane witnesses, decision/execution splits, and frozen-public transitions
- new canon claim `CL-0102`, invariant `INV-0100`, open question `OQ-0102`, and prompt pair `PP-0061`
- new durable `SURFACE-STATUS.json` ledger separating admitted revision status, packaged execution, and frozen-citation state for the archive-bundle lineage
- bibliography entry on draft/publish immutable-release posture as pressure for separating admitted, executed, and frozen-public lanes
- `check_status_lane_contract.py` — lint guard that keeps status-lane / surface-status-ledger wiring explicit across method, trajectory, runbook, promptcraft, and the shipped status ledger

# DelayBasin revision log (rev0095)
- new method note on basis witnesses, expected-head guards, and session-honesty bridges
- new canon claim `CL-0101`, invariant `INV-0099`, open question `OQ-0101`, and prompt pair `PP-0060`
- revision receipts now carry a compact `basis_witness` field with expected head, observed basis, session provenance, basis state, and repair posture
- bibliography entries on HTTP conditional update semantics and expected-head collaboration APIs as pressure for fail-closed basis discipline

# DelayBasin revision log (rev0094)
- new method note on operational heads, citation heads, and frozen public surfaces
- new canon claim `CL-0100`, invariant `INV-0098`, open question `OQ-0100`, and prompt pair `PP-0059`
- bibliography entries on software-citation specificity, explicit provenance relations, and contextual persistent identifiers as pressure for separating live operational heads from frozen/citable public surfaces
- `check_operational_head_contract.py` — lint guard that keeps head-register / citation-head / durable-status-ledger wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/method move: make DelayBasin name when a surface is merely the live working tip versus the frozen public reference tip, while keeping the stronger publication-state-machine story quarantined


# DelayBasin revision log (rev0093)
- new method note on arbitration witnesses, tie sets, and confusability budgets
- new canon claim `CL-0099`, invariant `INV-0097`, open question `OQ-0099`, and prompt pair `PP-0058`
- bibliography entries on skill-selection confusability, masked memory routing, active-inference routing, confidence-aware abstention, multi-skill orchestration, and reroute-aware knowledge routing as pressure for distinguishing honest tie-set routing from prestige choice or forced-winner theater
- `check_arbitration_witness_contract.py` — lint guard that keeps arbitration / tie-set / confusability wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new arbitration check and normalize the newest archive-index row so the release surface stays machine-readable
- kept the stronger public sparse-router / arbitration-law story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0092)
- new method note on applicability witnesses, precondition gates, and negative-transfer budgets
- new canon claim `CL-0098`, invariant `INV-0096`, open question `OQ-0098`, and prompt pair `PP-0057`
- bibliography entries on agentic skills, SkillsBench, SWE-Skills-Bench, RPMS, memory control-flow attacks, write-time gating, and ActMem as pressure for distinguishing honest reuse eligibility from overgeneralized or conflict-prone carry
- `check_applicability_witness_contract.py` — lint guard that keeps applicability / precondition-gate / negative-transfer wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new applicability check and normalize the newest archive-index row so the release surface stays machine-readable
- kept the stronger public applicability-law / transfer-eligibility-field story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0091)
- new method note on amortization witnesses, reuse horizons, and compiled-dividend budgets
- new canon claim `CL-0097`, invariant `INV-0095`, open question `OQ-0097`, and prompt pair `PP-0056`
- bibliography entries on SemanticALLI, ProcMEM, trajectory-informed memory generation, agentic plan caching, autonomous memory agents, recycled search experience, and GradMem as pressure for distinguishing reusable carry from one-shot rescue or compilation theater
- `check_amortization_witness_contract.py` — lint guard that keeps amortization / reuse-horizon / compiled-dividend wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new amortization check and repair the malformed top rows in `ARCHIVE_INDEX.md` so the release surface stays cumulative and machine-readable
- kept the stronger public skill-compiler / continuation-family amortization-law story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0090)
- new method note on dual-effect witnesses, explore-exploit splits, and information-premium budgets
- new canon claim `CL-0096`, invariant `INV-0094`, open question `OQ-0096`, and prompt pair `PP-0055`
- bibliography entries on HyPER, InfoPO, information self-locking, Dialogue Telemetry, ProbeLLM, and τ²-Bench as pressure for distinguishing ordinary adaptive control from actions that also buy future observability
- `check_dual_effect_witness_contract.py` — lint guard that keeps dual-effect / explore-exploit / information-premium wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new dual-effect check and normalize the newest `ARCHIVE_INDEX.md` row so the release surface stays cumulative and machine-readable
- kept the stronger public dual-control-law / information-state-controller story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0089)
- new method note on replicate-bundle witnesses, repeated-inference sweeps, and lucky-path budgets
- new canon claim `CL-0095`, invariant `INV-0093`, open question `OQ-0095`, and prompt pair `PP-0054`
- bibliography entries on canonical-path deviation, repeated-inference safety stress testing, latent-CoT stochastic rollouts, test-time-scaling ranking stability, agent reliability, and runtime path governance as pressure for distinguishing one vivid run from honest stochastic stability
- `check_replicate_bundle_witness_contract.py` — lint guard that keeps replicate-bundle / repeated-inference-sweep / lucky-path-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new replicate-bundle check so one lucky rollout cannot quietly inherit the authority of stable continuation across discovery surfaces
- kept the stronger public stochastic-response-law / continuation-kernel story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0088)
- new method note on interpolation-path witnesses, ramp schedules, and endpoint-equivalence budgets
- new canon claim `CL-0093`, invariant `INV-0091`, open question `OQ-0093`, and prompt pair `PP-0052`
- bibliography entries on FlowSteer, ODESteer, and Directer plus reuse of existing curve-aware, trajectory-intervention, and text-curvature refs as pressure for distinguishing matched endpoints from honest route-indifferent local control
- `check_interpolation_path_witness_contract.py` — lint guard that keeps interpolation-path / ramp-schedule / endpoint-equivalence-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new interpolation-path check so matched endpoints cannot quietly inherit the authority of honest route-indifferent control across discovery surfaces
- kept the stronger public action-functional / control-line-integral story quarantined instead of promoting it into canon


# DelayBasin revision log (rev0087)
- new method note on mixed-direction witnesses, cross-term sweeps, and superposition budgets
- new canon claim `CL-0092`, invariant `INV-0090`, open question `OQ-0092`, and prompt pair `PP-0051`
- bibliography entries on instruction-vector nonlinearity, PolySAE feature interactions, steering-vector interference, dynamic activation composition, steering-token composition, and dynamic steering-subspace adaptation as pressure for distinguishing marginal local passes from honest mixed-direction composition
- `check_mixed_direction_witness_contract.py` — lint guard that keeps mixed-direction / cross-term-sweep / superposition-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new mixed-direction check so separately passing local directions cannot quietly inherit the authority of honest joint composition across discovery surfaces
- kept the stronger public cue-interaction-tensor / second-order-response story quarantined instead of promoting it into canon


- new method note on directional-neighborhood witnesses, anisotropy sweeps, and local-shape budgets
- new canon claim `CL-0091`, invariant `INV-0089`, open question `OQ-0091`, and prompt pair `PP-0050`
- bibliography entries on activation anisotropy, prompt-steerability asymmetry, geometric stability, local manifold distortion, and ICL distributional stability as pressure for distinguishing one easy local cue direction from a genuinely shaped nearby neighborhood
- `check_directional_neighborhood_witness_contract.py` — lint guard that keeps directional-neighborhood / anisotropy-sweep / local-shape-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new directional-neighborhood check so one narrow cue family cannot quietly inherit the authority of a whole local neighborhood shape
- kept the stronger public local-metric-tensor / anisotropy-field story quarantined instead of promoting it into canon

- new method note on cue-neighborhood witnesses, reactivation-radius sweeps, and basin-breadth budgets
- new canon claim `CL-0090`, invariant `INV-0088`, open question `OQ-0090`, and prompt pair `PP-0049`
- bibliography entries on context reliance, paraphrase-generalizing prompt poisoning, neighborhood-style prompt evolution, local stability margins, support-token geometry, agentic-loop attractors, and early entrenchment as pressure for distinguishing exact-trigger success from local robustness
- `check_cue_neighborhood_witness_contract.py` — lint guard that keeps cue-neighborhood / reactivation-radius / basin-breadth wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new cue-neighborhood check so exact-trigger results cannot quietly inherit neighborhood authority across discovery surfaces
- kept the stronger public reactivation-geometry / basin-metric story quarantined instead of promoting it into canon


- new method note on relapse witnesses, recovery probes, and suppression-vs-washout budgets
- new canon claim `CL-0089`, invariant `INV-0087`, open question `OQ-0089`, and prompt pair `PP-0048`
- bibliography entries on adversarial recovery, multi-turn unlearning robustness, dynamic unlearning evaluation, intention-level recoverability, relearning resistance, and agentic context engineering as pressure for naming when a claimed cleanup is durable rather than merely benign-baseline suppression
- `check_relapse_witness_contract.py` — lint guard that keeps relapse-witness / recovery-probe / recoverability-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new relapse-witness check so suppression-vs-washout discipline cannot quietly fall out of discovery surfaces
- kept the stronger public relapse-kernel / latent-contamination-reservoir story quarantined instead of promoting it into canon

- new method note on reset witnesses, washout baselines, and contamination budgets
- new canon claim `CL-0088`, invariant `INV-0086`, open question `OQ-0088`, and prompt pair `PP-0047`
- bibliography entries on context branching, role-separated fresh contexts, assistant-history omission, contextual drag, adaptive context refactoring, and long-horizon context-pollution management as pressure for naming when a restart is genuinely clean enough for comparison
- `check_reset_witness_contract.py` — lint guard that keeps reset-witness / washout-baseline / contamination-budget wiring explicit across method, trajectory, runbook, and promptcraft
- hygiene/meta-engineering move: extend `tools/run_lint_suite.py` with the new reset-witness check so decontamination discipline cannot quietly fall out of discovery surfaces
- kept the stronger public reset-semigroup / rethermalization-law story quarantined instead of promoting it into canon
