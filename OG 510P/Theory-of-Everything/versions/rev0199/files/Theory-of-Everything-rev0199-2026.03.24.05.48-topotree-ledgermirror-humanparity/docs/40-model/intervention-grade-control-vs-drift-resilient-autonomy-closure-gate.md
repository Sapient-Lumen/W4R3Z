# Intervention-grade control versus drift-resilient-autonomy-closure gate

Purpose: split the archive's **witness-package progress** one step further.
A candidate should not earn the same witness credit merely because it can **deliberately write, steer, branch on, stabilize, or erase the same coarse-grained evidential state under public, transportable actuation and feedback rules** and because it can **keep that control loop live through drift, recalibration, relocation, and long-horizon execution without halting the whole program or silently depending on continuous expert babysitting**.
Those are related, but they are not the same achievement.

Read this together with:
- `docs/40-model/empirical-contact-burden-router.md`
- `docs/40-model/witness-closure-gate-family-frame.md`
- `docs/40-model/cross-site-reproducibility-vs-intervention-grade-control-closure-gate.md`
- `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`
- `docs/40-model/completion-bid-cashout-sieve.md`

## Compression verdict

Inside the archive's witness package, once a lane has already moved beyond cross-site reproducibility and has named public actuation and feedback semantics, the current score should now distinguish three nested layers:

1. **intervention-grade control closure** — independently maintained sites or stacks can deliberately write, steer, branch on, stabilize, or erase the same coarse-grained evidential state under public actuation and feedback rules;
2. **drift-resilient autonomy closure** — that same control loop stays live through drift, recalibration, relocation, decoder retuning, or maintenance events across long runtimes without stop-the-world interruption or one silently inherited expert maintenance ecology;
3. **local public witness closure** — a lane can say where the physical records live, what stabilizes them, how they are reread, why they remain public evidence, and why that empirical loop is not mainly outsourced.

A lane may earn real credit on layer 1 while still being weak on layer 2.
That is progress.
It is just not yet drift-resilient autonomy closure, much less full witness closure.

## Why this gate exists

Shared witness-gate scaffolding now lives in `docs/40-model/witness-closure-gate-family-frame.md`. This document only names the pair-specific inflation move below.

**portable actuation being retold as if the whole maintenance ecology needed to keep that actuation live had already been internalized.**

That inflation can happen in at least five ways:
- a control demo can work across several sites only inside one frozen calibration window, after which a human or external scheduler must stop the run and retune the stack;
- actuation semantics can be public while the diagnosis of drift still depends on hand-watched dashboards, tacit heuristics, or manually chosen trigger thresholds;
- a lane can showcase beautiful feedback or branch-conditioned control while every maintenance event still requires stop-the-world recalibration rather than in-run repair;
- a claim of autonomy can attach to one protected subsystem while relocation, patch replacement, decoder adaptation, or control-parameter retuning remain externally borrowed;
- or a lane can demonstrate autonomous protection in one narrow code or hardware lane while the integration burden needed for long-horizon heterogeneous operation remains unpaid.

## The five-step drift-resilient autonomy test

### 1. Drift and uptime target disclosure

Before awarding autonomy credit, the archive should ask what has to remain live, for how long, and against what variation.
At minimum, a lane should disclose:
- which parameters, noise channels, couplers, or timing relationships drift in the claimed regime,
- what uptime or continuity target the claim is supposed to meet,
- what failure budget, breach threshold, or safe operating window defines loss of autonomy,
- and whether the claim concerns one short benchmark episode or a genuinely long-horizon run.

A lane that wins only here earns **intervention-grade control credit**, not yet drift-resilient autonomy closure.

### 2. Online diagnosis and trigger route

A lane earns more than intervention credit only when it can say how degradation is detected during operation.
At minimum, the archive should ask:
- what real-time proxy, syndrome statistic, control residual, or performance estimator is monitored,
- how the lane distinguishes normal fluctuations from meaningful drift,
- what false-positive / false-negative trade-off its trigger logic accepts,
- and which parts of the diagnostic route remain tacitly hand-tuned or operator-dependent.

Without that route, apparent autonomy may still be portable control plus human watchstanding.

### 3. Maintenance action semantics

A lane earns stronger autonomy credit only when it can say what maintenance action occurs once drift is detected.
At minimum, the archive should ask:
- whether the response is recalibration, remapping, decoder retuning, dissipative stabilization, tile replacement, parameter adaptation, or something else,
- how that action preserves or hands off the controlled coarse-grained evidential state,
- what overhead, warm-up cost, or sacrificial routing / reserve capacity the maintenance step consumes,
- and which pieces of the maintenance loop remain provider-specific, manually scripted, or externally supervised.

Without those answers, apparent autonomy may still be a paused experiment with a fast technician.

### 4. Runtime continuity and nearby robustness

A lane earns still stronger autonomy credit only when the maintenance loop keeps the program alive under nearby changes.
At minimum, the archive should ask:
- whether recalibration or repair happens without halting the whole computation or measurement program,
- whether the same continuity story survives nearby changes in hardware family, control electronics, scheduler, or code distance,
- whether the lane can tolerate both slow drift and burst-like anomalies,
- and how much silent reauthoring is needed when the maintenance regime is moved to a nearby stack.

Without that continuity, apparent autonomy may still be intervention-grade control interrupted by maintenance breaks.

### 5. Closure boundary

A lane earns **drift-resilient autonomy closure** credit only when it can say how portable actuation remains live through drift and maintenance without importing a hidden babysitting ecology.
At minimum, it should name:
- the controlled coarse-grained evidential state,
- the online diagnostic or trigger route,
- the maintenance action semantics,
- the runtime continuity / no-stop condition,
- the heterogeneity range across which that loop survives,
- and the remaining debt to full local record-carrier, rereadability, and objectivity closure.

This is still not the same thing as full local witness closure.
A lane may keep control running for a long time while still borrowing the public record carrier, rereadability, or objectivity side from ordinary laboratory witness structure.

## Common failure modes

1. **Frozen-window inflation** — a strong short-run control demo is retold as if long-run autonomy were already solved.
2. **Babysitter laundering** — the loop works only because experts watch, retune, and decide when to intervene.
3. **Stop-the-world maintenance** — recalibration exists, but only by halting the full run and restarting from outside the claimed loop.
4. **Subsystem autonomy overclaim** — one protected state or code patch is stabilized while relocation, decoder, or stack-level maintenance remains external.
5. **Autonomy-to-closure inflation** — drift-resilient autonomy is retold as if local public witness closure were therefore solved too.

## Compact current readout

- **Recent reinforcement-learning QEC control work** makes the stronger burden explicit by arguing that halting computation for recalibration is unsustainable on long runtimes and by turning error-detection events into a continuous learning signal for control-parameter steering.
- **Recent on-FPGA calibration work** shows what partial payment looks like when pulse generation, acquisition, analysis, and feed-forward are co-located strongly enough to support millisecond time-to-decision and many consecutive recalibrations over hours rather than one frozen calibration window.
- **Recent real-time drift-mitigation architecture work** sharpens the runtime-maintenance requirement by using detector-fire-rate histories to predict logical error rates and by remapping logical qubits to fresh tiles while the old ones are recalibrated.
- **Recent scalable dissipative-QEC work** shows why the autonomy rung is real but not trivial: autonomous protection is a genuine alternative to measurement-feedback maintenance, yet scalability and integration burden remain part of the debt rather than a solved afterthought.

That does not refute current observer-relative or bridge-theory programs.
It just means they have not yet paid this stronger maintenance debt.

## Net rule

Within the archive:
- intervention-grade control closure earns real witness-package credit;
- but it does **not** yet count as drift-resilient autonomy closure;
- and neither of those automatically counts as local public witness closure.

Any future completion bid or bridge-family claim that wants stronger witness credit should now say not only how the same evidential state is actively written, steered, branched on, stabilized, or erased, but how that control remains live through drift, recalibration, relocation, and long runtimes without a silently imported maintenance ecology.
