
## 2026-03-25 refresh — failure envelopes become the next cross-lane deepening focus

Near-term repo work after this pass should prefer:
1. one shared falsification vocabulary (`failure-envelope.json`, `counterexample-trace.json`, `disproof-summary.md`, `degraded-claim.json`, `withdrawn-guarantee.md`, `repair-hint.json`, `refutation-bridge.json`);
2. one support-envelope lane that can emit a hosted-vs-local or scope-vs-claim counterexample honestly;
3. one front-door lane that can turn that counterexample into a downgraded recommendation or refusal;
4. one continuity bridge that distinguishes challenge, downgrade, refutation, and cleared states.

Do **not** widen this into a generic observability or incident-response platform.

## 2026-03-25 refresh — assurance cases become the next cross-lane deepening focus

Near-term repo work after this pass should prefer:
1. one shared assurance vocabulary (`claim-catalog.json`, `assurance-case.json`, `witness-bundle.json`, `challenge-register.json`, `assurance-summary.md`, `non-claims.md`, `inheritance-bridge.json`);
2. one compact human-facing assurance case for the front door lane;
3. one witness-bundle bridge from the support-envelope ring;
4. one inheritance/supersession bridge from the continuity ring.

Do **not** widen this into a full governance or certification platform.

## 2026-03-25 refresh — delta programs become the next cross-lane deepening focus

Near-term repo work after this pass should prefer:
1. one shared delta vocabulary (`change-intake.json`, `change-classification.json`, `carry-forward-decision.json`, `supersession-diff.json`, `delta-summary.md`, `confidence-reset.json`);
2. one carry-forward doctrine for the continuity ring;
3. one reviewed delta bundle for the front door lane;
4. one basis-delta bridge from the support-envelope ring.

Do **not** widen this into a full workflow or policy engine.

## 2026-03-25 refresh — renewal programs become the next cross-lane deepening focus

Near-term repo work after this pass should prefer:
1. one shared renewal vocabulary (`renewal-program.json`, `freshness-budget.json`, `renewal-ticket.json`, `renewal-ledger.jsonl`, `stewardship-summary.md`, `supersession-record.json`);
2. one cheap-rerun doctrine for the front door lane;
3. one event-trigger map for the continuity ring;
4. one freshness-class bridge from the support-envelope ring.

Do **not** widen this into a workflow engine or org-specific ticketing platform.


## 2026-03-25 (463) — next frontier move is to make the top lanes hand reviewers one durable packet instead of one more report family

Deepen the archive in this order:

1. **P-0509 + P-0536 + minimal P-0535 loop** — define the first review-front-door slice:
   - `review-intake`
   - `review-packet`
   - `signoff-ledger`
   - `override-register`
   - `maintenance-summary`
   - `reapproval-plan`
2. **P-0472 + P-0484** — define the decisive-evidence excerpt layer that makes the packet honest:
   - evidence excerpts
   - matrix/scope summary
   - freshness signal
   - unknown/refused list
3. **P-0431 + P-0496 + P-0125** — define the reapproval / supersession ring:
   - trigger bundle
   - supersession note
   - inherited-vs-fresh guidance
4. **P-0486** — define one narrow debugger review packet with immediate staleness on matrix change
5. **P-0537 / P-0538** — keep hot in research, but require equally clear review packets before practical promotion

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter review packet or supersession contract than `meta/top-lane-review-handoff-plans-2026-03-25.md`.


## 2026-03-25 (461) — next frontier move is to make one leading lane define a reusable evidence-interchange contract

Deepen the archive in this order:

1. **P-0472 + P-0484** — define the first shared interchange contract:
   - `profile-manifest.json`
   - `exchange-bundle.json`
   - `receipt-stream.jsonl`
   - `bundle-verify.json`
   - `bundle-diff.json`
2. **P-0509 + P-0536 + minimal P-0535** — import those bundles into decision packets, basis locks, and handoff summaries
3. **P-0431 + P-0496 + P-0125** — prove the same contract survives mirror, registry, source, and carry-forward changes
4. **P-0486** — borrow the shared profile/verifier doctrine for debugger matrices with explicit degraded and refused states
5. **P-0537 / P-0538** — keep hot, but only promote once the interchange doctrine transfers cleanly

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter interchange contract than `meta/top-lane-interchange-profiles-2026-03-25.md`.


## 2026-03-25 (460) — next frontier move is to make support claims tiered, reviewable, and rerunnable

Deepen the archive in this order:

1. **P-0472 + P-0484** — define the first real conformance kit:
   - stable tier vocabulary
   - stable claim envelope schema
   - raw receipt stream
   - human support summary
   - recheck plan
2. **P-0509 + P-0536 + minimal P-0535** — import those conformance kits into comparison packets, basis locks, and recheck tickets
3. **P-0486** — define a narrow debugger conformance matrix with explicit degraded and refused states
4. **P-0431 + P-0496 + P-0125** — make parity and carry-forward claims explicit and advisory-triggered
5. **P-0537 / P-0538** — keep hot, but only promote once the claim-tier vocabulary actually transfers cleanly

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter conformance-kit plan than `meta/top-lane-conformance-kits-2026-03-25.md`.

## 2026-03-25 (459) — next frontier move is to make one leading lane a real package family instead of a conceptual supercrate

Deepen the archive in this order:

1. **P-0509 + P-0536 + minimal P-0535** — define one real suite topology:
   - `pathfinder-core`
   - `pathfinder-schemas`
   - `cargo-pathfinder`
   - bounded importer boundary
   - bounded corpus boundary
2. **P-0472 + P-0484** — define the support-envelope family with stable packet meaning and isolated docs.rs/target adapters
3. **P-0486** — define a narrow debug-support suite whose probe churn cannot destabilize packet semantics
4. **P-0431 + P-0496 + P-0125** — decide what packet vocabulary is shared and what meanings must remain separate
5. **P-0537 / P-0538** — keep hot, but only promote with equally clear package-family plans

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter package-family plan than `meta/top-lane-suite-topologies-2026-03-25.md`.


## 2026-03-25 (458) — next frontier move is to turn the top lanes into explicit `0.1`→`1.0` product blueprints with acceptance packets

Deepen the archive in this order:

1. **P-0509 + P-0536 + minimal P-0535 loop** — define the first full product blueprint:
   - decision packet
   - review packet
   - basis lock
   - offer summary
   - recheck trigger ticket
   - supersession rule
2. **P-0472 + P-0484** — define the first full support-envelope import blueprint:
   - docs/build parity packet
   - target/toolchain packet
   - support-ceiling note
   - drift trigger vocabulary
3. **P-0486** — define the first narrow debug-support blueprint:
   - debugger matrix packet
   - async-debug ceiling note
   - degraded and refusal outputs
4. **P-0431 + P-0496 (+ P-0125)** — define the first carry-forward blueprint for boundary/source/inventory drift
5. **P-0537 / P-0538** — keep hot in research, but require equally clear release ladders before practical promotion

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter product blueprint or schema family than `meta/top-lane-product-blueprints-2026-03-25.md`.

## 2026-03-25 (457) — next frontier move is to turn the top lanes into one shareable promise bundle another team can adopt

Deepen the archive in this order:

1. **P-0509 + P-0536 + minimal P-0535 loop** — define one receiver-facing offer packet:
   - decision packet
   - frozen witness basis
   - short support summary
   - named recheck triggers
   - one transition route
2. **P-0472 + P-0484** — import the support-envelope truths that make the offer packet honest:
   - hosted/local docs recipe truth
   - target/toolchain/component ceilings
   - explicit “documented vs built vs supported vs unknown” language
3. **P-0486** — only promote once the archive can show:
   - debugger / OS / version matrix packets
   - async debugging claim ceilings
   - refusal behavior and corpus receipts
4. **P-0431 + P-0496 (+ P-0125)** — extend the same promise-bundle discipline to boundary drift, source parity, mirroring, and inventory carry-forward
5. **P-0537 / P-0538** — keep hot in research, but require equally compact support envelopes before practical promotion

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind at least one reusable promise-bundle card and one machine-readable offer packet tighter than `meta/frontier-promise-bundles-2026-03-25.md`.

## 2026-03-25 (456) — next frontier move is to make one top lane runnable end-to-end with an operator, recheck trigger, and scenario corpus

Deepen the archive in this order:

1. **P-0509 + P-0536 + minimal P-0535 loop** — define one end-to-end operating card:
   - named receiver
   - imported surfaces
   - one runner/cadence
   - one frozen basis
   - one reopen/revalidate loop
   - one compact golden corpus
2. **P-0472 + P-0484** — import the reality surfaces that make that operating card honest:
   - hosted/local docs parity
   - build recipe caveats
   - target/toolchain/component support ceilings
3. **P-0486** — only promote once the archive can name:
   - debugger / OS / version corpus
   - async/debugger claim ceilings
   - explicit refusal behavior
4. **P-0431 + P-0496 (+ P-0125)** — extend the same runner/corpus discipline to boundary drift, mirror/source parity, and inventory carry-forward
5. **P-0537 / P-0538** — keep hot in research, but require the same operating-model and corpus discipline before any practical promotion

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind at least one operating-model card and one scenario family tighter than `meta/frontier-operating-surface-2026-03-25.md`.

## 2026-03-25 (455) — next frontier move is to make the front door survive time, drift, and mirror reality

Deepen the archive in this order:

1. **P-0509 + P-0536** — keep the front door and frozen basis pilotable
2. **P-0472 + P-0484** — keep docs/build/target/toolchain reality imports strong
3. **P-0535 + P-0496 + P-0431** — add the continuity ring:
   - `trigger-intake.receipt`
   - `decision-revalidation.report`
   - `transition-plan`
   - `source-parity.report`
   - `mirror-readiness.report`
   - `public-boundary.report`
4. **P-0125** — append SBOM precursor delta/carry-forward where the continuity ring already has frozen inputs
5. **P-0486** — debug/support covenant once the first three layers can explain what changed and what stayed true
6. **P-0537 / P-0538** — keep hot in research and scenarios, but do not overclaim first-wave continuity readiness

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter continuity slice than `meta/frontier-continuity-ring-2026-03-25.md`.

## 2026-03-25 (454) — next frontier move is to make the front door and ground-truth ring pilotable as real `0.1` crates

Deepen the archive in this order:

1. **P-0509 + P-0536** — one pilotable front door:
   - `task-profile`
   - `candidate-import`
   - `decision-pack`
   - `starter-set.lock`
   - `basis-lock`
   - `review-packet`
   - `citation-locator`
   - `build-surface`
2. **P-0472 + P-0484 + P-0535** — one pilotable ground-truth ring:
   - `docsrs-preflight`
   - `hosted-local-diff`
   - `target-support`
   - `component-availability`
   - `trigger-intake`
   - `decision-revalidation`
3. **P-0486** — one pilotable debug-support bundle with explicit debugger/OS/version ceilings
4. **P-0431 + P-0496** — maintenance/distribution ring once the front door and ground-truth imports are stable
5. **P-0537 / P-0538** — keep hot in research and scenario labs, but do not overclaim first-wave product readiness

Guardrail:
do not spend the next pass on another broad frontier narrative unless it leaves behind a tighter MVP slice than `meta/frontier-mvp-stack-2026-03-25.md`.

## 2026-03-25 (453) — next frontier productization proving ground

Deepen the archive in this order:

1. **P-0509** — `task-profile`, `candidate-import`, `decision-pack`, and `starter-set.lock`
2. **P-0536** — `basis-lock`, `review-packet`, `citation-locator`, and `build-surface`
3. **P-0472 + P-0484 + P-0535** — the ground-truth ring: hosted-doc parity, target/toolchain support truth, and lifecycle/recheck packets
4. **P-0486** — debug-support bundle above the frozen ground-truth basis
5. **P-0431 + P-0496** — public-boundary and source-parity maintenance ring
6. **P-0537** — iteration-truth once more Cargo build-analysis substrate is exposed
7. **P-0538** — continue research and comparison bundles without pretending first-wave product readiness

Guardrail:
do not spend the next pass on another territory atlas or another broad sector pitch unless it clearly beats one of these proving grounds.

## Added 2026-03-25 (452) — next repo move is to consolidate the front door, not re-open umbrella sectors

Near-term repo-building order:

1. deepen **P-0509 + P-0536** together so the archive has one obvious decision-plus-memory front door;
2. keep **P-0486** close because debug support remains live ecosystem pain and imports into many later lanes;
3. keep **P-0472 / P-0484** moving because hosted-doc and target/toolchain truth are stable evidence inputs;
4. keep **P-0537 / P-0489** moving because iteration truth and build-dir migration truth are cross-sector reality layers;
5. use **P-0535 / P-0496 / P-0431** as the maintenance / source-parity / public-boundary ring around the front door;
6. mine broad sectors only for sharper seam kits, not for new mega-lanes.

Guardrail:
- after this pass, do not answer a broad territory scan by opening another giant umbrella proposal first;
- answer it by asking which sharper seam beat the existing control-plane frontier.

## Added 2026-03-24 (451) — the next repo move is to make the front door close bounded evidence gaps instead of parking them in prose

Near-term repo-building order:

1. deepen **P-0509** around `evidence-gap.report`, `evidence-campaign.plan`, and `gap-closure.receipt`;
2. keep **P-0536** paired with it so campaign items stay pinned to replayable knowledge packs and basis locks;
3. use minimal **P-0535** posture notes where a gap is not closed but moved to transition/exception/recheck;
4. deepen **P-0486** so conditional debug support exports bounded gaps and closure routes;
5. keep **P-0496 / P-0472 / P-0484** moving because source parity, hosted docs posture, and target truth are exactly the gap sources later stages ask for.

Guardrail:
- after this pass, do not answer “more evidence is needed” with prose alone;
- answer it with a named gap, a bounded campaign plan, and an honest closure receipt first.

## Added 2026-03-24 (450) — the next repo move is to make the front door runnable as a staged program

Near-term repo-building order:

1. deepen **P-0509** around decision-program runbooks and progression reports;
2. keep **P-0536** paired with it so stage progression remains pinned to replayable knowledge packs and basis locks;
3. use minimal **P-0535** posture notes where stage exits become hold / split-boundary / replace-later decisions;
4. deepen **P-0486** so debug support can be assessed per stage rather than once globally;
5. keep **P-0496 / P-0472 / P-0484** moving because offline, hosted, and target truths are exactly the gates later stages ask for.

Guardrail:
- after this pass, do not answer “what should the top crate provide?” with one flat profile result;
- answer it with a named stage, explicit gates, inherited basis, and an honest stage exit first.

## Added 2026-03-24 (449) — the next repo move is to make the front door profile-aware, not broader

Near-term repo-building order:

1. deepen **P-0509** around named policy profiles and profile-satisfaction reports;
2. keep **P-0536** paired with it so profile answers remain pinned to replayable knowledge packs and basis locks;
3. use minimal **P-0535** posture notes where profile floors need lifecycle/transition evidence;
4. deepen **P-0486** so “supported for debugging” becomes profile-aware instead of generic;
5. keep **P-0496 / P-0472 / P-0484** moving because offline, hosted, and target truths are exactly the floors higher-assurance profiles ask for.

Guardrail:
- after this pass, do not answer “what should the top crate provide?” with one flat recommendation surface;
- answer it with a named adopter profile, an evidence floor, and an honest profile-satisfaction report first.

## 2026-03-24 (448) — next roadmap slice

Prefer the next slice in this order:
1. **P-0509 + P-0536 + minimal P-0535 loop** — freeze one comparator packet, one basis lock, one intake receipt, one materialization plan, one adjudication session, one policy-exception receipt, one carry-forward receipt, one expiry ticket, and one recheck ticket
2. **P-0486** — emit one debug support packet that can carry bounded exceptions without losing witness basis
3. **P-0496** — connect restricted-delivery source parity to the same exception/expiry story
4. **P-0472** — keep docs.rs parity bundles aligned with hosted-surface caveats and scoped exception honesty

Guardrail:
- do not add another top-level frontier lane before the archive can show one full compare → freeze → intake → materialize → adjudicate → except → carry-forward → expiry → ticket → revalidate loop.

## 2026-03-24 (447) — next roadmap slice

Prefer the next slice in this order:
1. **P-0509 + P-0536 + minimal P-0535 loop** — freeze one comparator packet, one basis lock, one intake receipt, one materialization plan, one adjudication session, one carry-forward receipt, and one recheck ticket
2. **P-0486** — emit one debug support packet that can be imported into the same adjudication flow later
3. **P-0496** — connect restricted-delivery source parity to the same disagreement/carry-forward story
4. **P-0472** — keep docs.rs parity bundles aligned with hosted-surface caveats and adjudicated support posture

Guardrail:
- do not add another top-level frontier lane before the archive can show one full compare → freeze → intake → materialize → adjudicate → carry-forward → ticket → revalidate loop.

## 2026-03-24 (446) — next roadmap slice

Prefer the next slice in this order:
1. **P-0509 + P-0536 + minimal P-0535 loop** — freeze one comparator packet, one basis lock, one intake receipt, one materialization plan, and one recheck ticket
2. **P-0486** — emit one debug support packet that can be imported by the same intake/materialization discipline later
3. **P-0496** — connect restricted-delivery source parity to the same intake/materialization story
4. **P-0472** — keep docs.rs parity bundles aligned with hosted-surface caveats and materialization ceilings

Guardrail:
- do not add another top-level frontier lane before the archive can show one full compare → freeze → intake → materialize → ticket → revalidate loop.

## 2026-03-23 (445) — next roadmap slice

Prefer the next slice in this order:
1. **P-0509 + P-0536 + minimal P-0535 loop** — freeze one comparator packet, one basis lock, one trigger-intake receipt, and one recheck ticket
2. **P-0486** — emit one comparable debug support packet that can also consume the same recheck/ticket discipline later
3. **P-0496** — connect restricted-delivery source parity to the same trigger and revalidation story
4. **P-0472** — keep docs.rs parity bundles aligned with hosted-surface drift and recheck openings

Guardrail:
- do not add another top-level frontier lane before the archive can show one full compare → freeze → intake → ticket → revalidate loop.

## 2026-03-23 (444) — next roadmap slice

Prefer the next slice in this order:
1. **P-0509 + P-0536** — freeze one comparator packet with one basis lock and one short revalidation report
2. **P-0535** — emit one `transition-review-packet.manifest.json` above the existing lane / seam / anchor receipts
3. **P-0496** — connect restricted-delivery source parity to the same refresh / transition posture
4. **P-0472** — keep docs.rs parity bundles aligned with refresh triggers instead of one-shot issue packets

Guardrail:
- do not add more top-level frontier lanes before the archive can show one full compare → freeze → refresh → transition loop.

## Added 2026-03-24 (443) — the next repo move is to make the first slice emit witness-bearing packets, not just better prose

Near-term repo-building order:

1. deepen **P-0509 + P-0536** around `basis-lock.manifest.json`, release/package/docs witnesses, and one narrow receiver loop;
2. carry the same witness discipline into **P-0486** so debug capability packets can say exactly what session and symbol basis they stand on;
3. continue **P-0496** because source-parity and mirror packets naturally reuse basis-lock thinking;
4. keep **P-0472** and **P-0489** moving because hosted/local drift and build-dir churn remain concrete witness-generating seams;
5. then continue **P-0535 / P-0484 / P-0058** where hard-domain evidence is still thin.

Guardrail:
- after this pass, do not promote a lane as “implementation-ready” until it can say what witness surfaces it captures and what another team receives in `0.1`.

## Added 2026-03-24 (442) — the next repo move is to build the front-door stack and freeze packet discipline

Near-term repo-building order:

1. deepen **P-0509** around receiver-specific decision packets, but only in lockstep with **P-0536** review bundles and pinned support packets;
2. freeze a shared packet-family discipline so receipts, reports, manifests, packs, locks, notes, and imports stop drifting in meaning across the top lanes;
3. deepen **P-0486** so debug capability packets can reuse the same family semantics;
4. keep **P-0496** moving because restricted-delivery claims depend on the same packet discipline and replayability concerns;
5. keep **P-0472** and **P-0489** moving because hosted/local drift and build-dir churn still shape many downstream packet consumers;
6. then continue **P-0535 / P-0484 / P-0058** where hard-domain evidence still thins out.

Guardrail:
- after this pass, do not answer “what next?” with a broader new proposal until you can say what packet family the crate emits, what pinned basis supports it, and how downstream consumers will survive schema evolution.

## Added 2026-03-24 (441) — the next repo move is to turn receiver maps into pilotable `0.1` loops

Near-term repo-building order:

1. deepen **P-0509** around receiver-specific review packets and the highest-value scenario packs;
2. pair it with **P-0536** so those packets stay pinned, cited, and machine-usable;
3. deepen **P-0486** around the same receiver workflows for debugging and incident review;
4. build the first explicit **P-0496** restricted-delivery bundle path so offline/mirror/vendor claims become inspectable;
5. keep **P-0472** and **P-0489** moving because hosted/local drift and build-dir churn still affect many downstream tools;
6. then continue **P-0535 / P-0484 / P-0058** where hard-domain evidence still thins out.

Guardrail:
- after this pass, do not answer “what next?” with broad new crate ideas until you can say which receiver gets which packet in a first adopter program.

## Added 2026-03-24 (440) — the next repo-building move is to make top crates more supportive, not broader

Near-term repo-building order:

1. deepen **P-0509** around receiver-specific review packets and the new hard-domain scenarios;
2. pair that with **P-0536** so those packets have pinned citations, answer boundaries, and machine-usable support surfaces;
3. deepen **P-0486** so debugging packets match those same receiver workflows;
4. keep **P-0472** and **P-0489** moving because hosted/local build truth and consumer transition remain unusually actionable;
5. deepen **P-0535 / P-0484 / P-0058** where the new adoption ladder says offline, native, target, or regulated evidence is still thin;
6. only then promote more sector-specific lanes.

Guardrail:
- after this pass, do not answer “what next?” with a vague new domain idea;
- answer it with a smaller first-release bundle, a supportive surface, or a harder-domain scenario family first.

## Added 2026-03-23 (439) — the next repo-building move is to make pathfinder packets feel real

Near-term repo-building order:

1. deepen **P-0509** around named scenario packs and review packets;
2. connect **P-0536** knowledge-pack work to those same scenario packs so human and machine handoff stay aligned;
3. deepen **P-0486** around evidence packets that match the pathfinder scenarios most likely to need debugging truth;
4. keep **P-0472** and **P-0489** moving because docs/build truth is still unusually actionable today;
5. only then consider promoting a new sector-lab theme, starting with local-first, robotics/digital twins, or geospatial provenance if one of them escapes the control-plane lanes cleanly.

Guardrail:
- after this pass, do not answer “what should we build next?” with another vague sector proposal;
- answer it with a packet, doctor, bundle, or scenario family first.

## 2026-03-23 (438) — next repo-building moves after the scorecard pass

Recommended near-term sequence now:
1. deepen **P-0509** around starter-set decision packs and elimination/re-entry receipts,
2. deepen **P-0486** around debugger/session family fixtures,
3. deepen **P-0472 / P-0489 / P-0046 / P-0058** as the build/docs/native cluster,
4. then begin a real **P-0538** scenario-lab slice using the six proving-ground families in `meta/concurrency-contract-scenario-lab-plan-2026-03-23.md`.

Guardrail:
- do not let a broad concurrency score be mistaken for “ship it before every build-support lane.”
- keep salience and shipability separate.

## 2026-03-23 (437) roadmap refinement

Near-term repo work should now prioritize:

1. pathfinder delivery cards and lane templates,
2. debuggability capability witnesses,
3. docs.rs parity issue bundles,
4. build-dir transition dual-support flows,
5. buildscript UX support bundles,
6. native dependency ABI/provenance receipts,
7. dependency lifecycle and target/toolchain truth where those lanes join regulated, mixed-language, and long-lived adoption.

Do not spend the next pass on a broad new sector batch unless the new work clearly escapes the current control-plane plus native-build support stack.


## 2026-03-23 (436) roadmap refinement

Near-term repo work should prioritize:

1. pathfinder lane templates and candidate-basis rigor,
2. debuggability witness/bundle shape,
3. docs.rs parity issue/review flow,
4. build-dir transition dual-support planning,
5. dependency lifecycle and target/toolchain truth where those flows join safety-critical and regulated adoption.

Do not spend the next pass on a large new sector batch unless a genuinely new horizontal seam appears.

## Added 2026-03-23 (435) — the next roadmap should build lane templates and capability stacks, not just add more ideas

Recommended next-pass order:

1. **P-0509** — productize lane templates, role packs, lane freeze policies, and scope-aware starter-set bundles.
2. **P-0486** — productize the debug capability stack, session-family coverage, inspection/evaluation, async-debug visibility, and packaged handoff truth.
3. **P-0535** — deepen dependency transition work around off-ramp bundles that fit regulated, embedded, and mixed-language environments.
4. **P-0484** — keep target/toolchain/support truth sharp where Wasm, build-std, Rust-for-Linux, or safety-critical support claims would otherwise get blurred.
5. **P-0536** — keep machine-usable crate knowledge aligned with docs.rs and rustdoc JSON realities.
6. **P-0537 / P-0538 / P-0532** — continue deepening the already-strong control-plane lanes when a pass adds a new durable evidence artifact.

Use `meta/control-plane-demand-matrix-2026-03-23.md` as the first filter before adding another sector-specific proposal.

## Added 2026-03-23 (434) — the next roadmap should prioritize the control-plane frontier and use the new bands explicitly

Recommended next-pass order:

1. **P-0537** — push rebuild-basis, rebuild-reason, contention, and action-plan artifacts closer to Cargo build-analysis and build-dir reality.
2. **P-0509** — keep candidate corpus, inclusion/exclusion, re-entry, and review-pack artifacts sharp enough to become real decision infrastructure.
3. **P-0535** — deepen selection anchors, clean-resolve risk, override authority, and off-ramp bundles.
4. **P-0536** — deepen citation / answerability / build-surface / machine-export truth.
5. **P-0538** — continue productizing comparable concurrency semantics with receipts that resist folklore.
6. **P-0486** — productize debug-support posture, symbol-sidecar, debugger-backend, and artifact-completeness receipts.
7. **P-0484** — sharpen target / toolchain / host-target / prerequisite truth for cross-build and support claims.
8. **P-0532** — continue runtime-topology and capability-route truth where async complexity or deployment scrutiny is high.

Keep Band B and Band C work alive, but promote them only when a pass adds a new durable artifact family rather than just more examples or prose.

## Added 2026-03-23 (433) — the next roadmap should stay on the horizontal top frontier

The best next implementation work is not “invent one more proposal.”
It is to keep making the top-ranked lanes more buildable.

Recommended next-pass order:

1. **P-0537** — push toward concrete rebuild-reason / cache-contention / action-plan artifacts aligned with Cargo build-analysis, build-dir layout, relink, and fast-dev-codegen work.
2. **P-0509** — deepen candidate-elimination, re-entry, and decision-timebox artifacts so crate-choice work becomes replayable rather than rhetorical.
3. **P-0535** — deepen clean-resolve risk, selection anchors, source parity, and off-ramp bundles so dependency replacement work becomes operational.
4. **P-0536** — deepen pinned citation locators, item witnesses, target-aware docs surfaces, and answerability/refusal boundaries for human + tool handoff.
5. **P-0011** — deepen maintenance coverage, succession, and routing drift so stewardship posture stops depending on guesswork.

Continue **P-0538**, **P-0532**, **P-0484**, **P-0431**, **P-0125**, **P-0427**, and **P-0433**, but prefer those passes when they add a new durable evidence artifact rather than just more examples or rhetoric.

## Added 2026-03-23 (431) — concurrency-contract passes should now productize late-joiner admission and join-start baseline

- Deepen **P-0538 Concurrency Contract Kit** around `late-joiner-admission.report.json` and `join-start.report.json` before considering any new nearby subscription helper, observer API, or channel-comparison lane.
- Prefer compact scenario bundles proving future-only broadcast subscribe, current-tail resubscribe, current-snapshot watch subscribe, stored-permit late waits, current-waiters-only notify, and fixed-cohort no-late-join surfaces without flattening them together.
- Guardrail: do not broaden into generic stream replay, event-sourcing, or actor/subscriber frameworks unless a pass clearly escapes **P-0538 / P-0529 / P-0532 / debugging lanes**.

## Added 2026-03-23 (429) — concurrency-contract passes should now productize delivery order and gap visibility

- **P-0538 Concurrency Contract Kit** — the next worthwhile implementation slice is `delivery-order.report.json` and `gap-visibility.report.json` above the earlier memory / pressure / audience / claim / acceptance lane.
- Prefer proving grounds where one surface is FIFO to a single receiver, another is FIFO per active receiver with lag counts, another only exposes the latest state, another coalesces repeated wakes, and a selector introduces random ready-operation choice.
- Do not spend the next pass on another queue wrapper, actor helper, or channel comparison matrix unless it can export stronger order and gap receipts than this lane already can.

## Added 2026-03-23 (427) — deepen P-0538 around delivery audience and consumption claim instead of adding another channel helper

Decision: deepen **P-0538 Concurrency Contract Kit** around `delivery-audience.report` and `consumption-claim.report`.

Why:
- the existing lane could now describe reentrancy, fairness, cancellation, recovery, context, locality, liveness, memory, and pressure, but not yet who is actually eligible to observe a delivery unit or what one observer taking it means for others;
- current Tokio / `async-channel` / Flume docs make all-current-waiter notification, all-active-receiver fanout, independent seen-state, single-consumer delivery, and many-receiver-exclusive-claim posture concrete enough for first-class review artifacts;
- the sharper gap is therefore audience/claim honesty, not another wrapper, actor helper, or channel selector.

Consequence: future concurrency-contract passes should prefer audience/claim receipts and doctor rules over more wrapper APIs, comparison blog-post framing, or generic “async messaging” summaries.

## Added 2026-03-23 (425) — compile iteration should now productize coverage scope and claim ceilings

- **P-0537 Compile Iteration Feedback Kit** — the next worthwhile implementation slice is `coverage-scope.receipt.json` and `coverage-ceiling.report.json` above the earlier surface / barrier / activation / generation / drain / outcome lane.
- Prefer proving grounds where support looks broad but is actually bounded: Dioxus three-surface splits, Subsecond tip-crate anchors, Chaud annotation + feature gating, hot-lib-reloader wrapped dylib exports, and Bevy simple subsecond preexisting-route limits.
- Do not spend the next pass on another hot-reload wrapper or benchmark unless it can export stronger coverage receipts than this lane already can.

## Added 2026-03-23 (424) — compile iteration should now productize live-update outcome and degraded mode

- **P-0537 Compile Iteration Feedback Kit** — the next worthwhile implementation slice is `live-update-outcome.report.json` and `degraded-iteration-mode.report.json` above the earlier activation / generation / retirement / drain lane.
- Prefer proving grounds where a patch route remains theoretically valid but the current attempt fails, where warnings imply degraded hot reload rather than healthy hot reload, and where known-danger combinations demand restart-or-disable posture.
- Do not spend the next pass on another dev-loop wrapper, watcher UI, or patch engine unless it can export stronger outcome and degraded-mode receipts than this lane already can.

## Added 2026-03-23 (423) — compile iteration should now productize retirement boundaries and old-generation drain

- **P-0537 Compile Iteration Feedback Kit** — the next worthwhile implementation slice is `retirement-boundary.report.json` and `old-generation-drain.report.json` above the earlier activation / generation lane.
- Prefer proving grounds where one stack rewinds to a clean hot anchor, where old code can survive until an entrypoint is called again, and where reload observer pairs bracket a handoff without proving route drain completeness.
- Do not spend the next pass on another dev-loop wrapper, hot-reload demo, or patch engine unless it can export stronger retirement and drain receipts than this lane already can.


## Added 2026-03-23 (422) — compile iteration should now productize generation witnesses and mixed-generation risk

- **P-0537 Compile Iteration Feedback Kit** — the next worthwhile implementation slice is `generation-witness.report.json` and `mixed-generation-risk.report.json` above the earlier activation/stale-code lane.
- Prefer proving grounds where jump-table latestness, nested call cut points, entrypoint-gated activation, or dylib load counters would otherwise be over-read as whole-process generation truth.
- Do not spend the next pass on another dev-server wrapper, hot-reload demo, or live-coding engine unless it can export stronger code-epoch receipts than this lane already can.

## Added 2026-03-23 (421) — compile iteration should now productize activation boundaries and stale-code risk

- **P-0537 Compile Iteration Feedback Kit** — the next worthwhile implementation slice is `activation-boundary.report.json` and `stale-code-risk.report.json` above the earlier surface / barrier / continuity lane.
- Prefer proving grounds where fresh code only activates at annotated entrypoints, where reload-event pairs require explicit handoff, where stored callbacks can still hit old code, and where identity-sensitive systems need rebinding rather than magical continuity.
- Do not spend the next pass on another watcher wrapper, linker comparison, or generic hot-reload demo unless it can export stronger activation and stale-code receipts than this lane already can.

## Added 2026-03-23 (420) — crate knowledge packs should now productize build surfaces and conditioned availability

- **P-0536 Crate Knowledge Pack Kit** — the next worthwhile implementation slice is `build-surface.receipt.json` and `conditioned-availability.report.json` above the earlier material-basis / citation / item-witness lane.
- Prefer proving grounds where docs.rs metadata defines one hosted surface rather than a universal page set, where `cfg(docsrs)` scope would otherwise be over-read, where scraped examples depend on recipe/dev-dependency posture, and where rustdoc JSON format windows bound machine-surface claims.
- Do not spend the next pass on prompt engineering, ranking, or a crate-chat UI unless it can export stronger build-surface and conditioned-availability receipts than this lane already can.
## Added 2026-03-23 (419) — concurrency-contract passes should now productize mobility/affinity and driver-liveness

- **P-0538 Concurrency Contract Kit** — the next worthwhile implementation slice is `mobility-affinity.report.json` and `driver-liveness.report.json` above the earlier reentrancy / fairness / cancellation / recovery lane.
- Prefer proving grounds where local spawn requires a local context, where a handle exists but does not drive timers or I/O, where a local runtime is thread-bound and not interchangeable with a `LocalSet`, and where a thread-local executor is explicitly driven rather than background-driven.
- Do not spend the next pass on another executor abstraction, spawn helper, or runtime comparison matrix unless it exports stronger locality and liveness receipts than this lane already can.

## Added 2026-03-23 (418) — pathfinder should now productize candidate elimination and re-entry

The next implementation-ready proving ground for **P-0509** is no longer just freeze/replay.
It is the small artifact layer for losers that still matter: why a candidate was out, whether that exclusion is reversible, and what evidence would reopen review without silently replacing the frozen starter set.

Promote next:
- `candidate-elimination.receipt.json`
- `candidate-reentry.policy.json`
- doctor rules for no-silent-resurrection
- bundle inventory that keeps winner, loser, and re-entry conditions separate

## Added 2026-03-23 (416) — dependency lifecycle should now productize selection anchors and clean-resolve risk

- **P-0535 Dependency Lifecycle Transition Kit** — the next worthwhile implementation slice is `selection-anchor.receipt.json` and `reresolution-risk.report.json` above the earlier override/freshness/exception lane.
- Prefer proving grounds where a local-only patch plus current lockfile keeps today green, where a yanked dependency remains locked but no longer safely selectable, and where `rust-version` context changes the selected family.
- Do not spend the next pass on another update-policy engine, vendoring wrapper, or dependency dashboard unless it can export stronger lifecycle anchors and fresh-resolve risk receipts than this lane already can.

## Added 2026-03-23 (415) — pathfinder should now productize freeze timeboxes and as-of replay

- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — the next worthwhile implementation slice is `decision-timebox.receipt.json`, `as-of-replay.report.json`, and portable bundle inventory that keeps freeze-time basis distinct from current-view replay.
- Prefer proving grounds where a fresh release is still inside cooldown, where docs.rs target/default changes alter visibility later, and where current search ordering would otherwise be over-read as historical recommendation authority.
- Do not spend the next pass on another scoring formula, search UI, or “best crates” essay unless it can export stronger timebox/replay receipts than this lane already can.

## Added 2026-03-23 (413) — crate knowledge packs should now productize citation locators and citation-capability ceilings

- **P-0536 Crate Knowledge Pack Kit** — the next worthwhile implementation slice is `citation-locator.receipt.json` and `citation-capability.report.json` above the earlier material-basis / excerpt-lineage / answerability / claim-trace lane.
- Prefer proving grounds where docs.rs `latest` or semver redirects would otherwise be cited as if they were pinned, and where target-sensitive item pages would otherwise be flattened into default-target truth.
- Do not spend the next pass on prompt engineering, ranking, or a crate-chat UI unless it can export stronger locator and citation-capability receipts than this lane already can.

## Added 2026-03-23 (412) — concurrency-contract passes should now productize cancellation classes and recovery posture

- Deepen **P-0538 Concurrency Contract Kit** around richer `wait-cancellation.report.json` fields plus `failure-recovery.report.json` before considering any new nearby lock-wrapper, async-helper, or deadlock-detector lane.
- Prefer compact scenario bundles proving queue withdrawal, true cancel safety, advisory poisoning, no-poisoning posture, and experimental/nightly ceilings without flattening them together.
- Guardrail: do not broaden into generic channel delivery semantics, generic runtime-family choice, or generic verification tooling unless a pass clearly escapes **P-0538 / P-0529 / P-0532 / model-checking lanes**.

## Added 2026-03-23 (410) — concurrency-contract passes should prefer semantic receipts over new primitive wrappers

- Deepen **P-0538 Concurrency Contract Kit** around `reentrancy-scope.report.json`, `progress-fairness.report.json`, `wait-cancellation.report.json`, `execution-context-boundary.report.json`, and `concurrency-support-bundle.manifest.json` before considering any new nearby lock-wrapper, runtime-wrapper, or generic async-helper lane.
- Prefer compact scenario bundles proving Tokio FIFO is not reentrancy, `parking_lot` eventual fairness is not Tokio FIFO, cancellation can lose queue position, and blocking methods can be legal in one context but panic in another.
- Guardrail: do not broaden into generic channel capacity, generic resource budgets, generic runtime-family choice, or generic debugging UX unless a pass clearly escapes **P-0538 / P-0529 / P-0521 / P-0532 / P-0486**.

## 2026-03-23 (409) — next move for P-0051

Advance **P-0051 Rustdoc JSON Support Contract Kit** toward a `0.2` plan built around:

- `source-route.receipt.json`
- `format-window.matrix.json`
- `normalization-loss.report.json`
- `rustdoc-json-support-bundle.manifest.json`

Keep route provenance, supported format windows, and normalization-loss ceilings explicit so later semver/docs/assistant lanes can import this substrate instead of silently reinventing it.

## Added 2026-03-23 (405) — compile-time containment should productize ambient ingress and launcher-route truth before adding more backend breadth

Near-term repo move:

1. deepen **P-0107** around `ambient-input.receipt.json`, `sanitization-mode.receipt.json`, and `launcher-route.receipt.json`;
2. keep current backend examples (`cargo-sandbox`, `cackle`, upstream sandbox experiments) as imported substrate rather than the product itself;
3. resist adding another OS-sandbox wrapper, proc-macro-only helper, or build-security score unless it clearly escapes **P-0107 / P-0508 / P-0519 / P-0040**.

## Added 2026-03-22 (402) — debuggability support capability witnesses

- Deepen **P-0486 Debuggability Support Contract Kit** around `session-scope.receipt`, `capability-witness.report`, and `claim-ceiling.report`.
- Keep live-local, remote, attached, and post-mortem lanes visibly distinct.
- Require task-level evidence before claiming Rust expression evaluation, async inspection, or broad cross-platform debugger support.

## Added 2026-03-23 (401) — cargo publish-receipt joins should now productize registry capability, protection scope, and bundle manifests

- **P-0477 Cargo Publish Receipt Join Kit** — the next worthwhile implementation slice is `registry-capability.receipt.json`, `protection-scope.report.json`, and `publish-join-bundle.manifest.json` above the earlier local-bytes / identity / visibility lane.
- Prefer proving grounds where crates.io-specific enrichments or mitigations would otherwise be over-read as alternate-registry truths.
- Do not spend the next pass on another publish bot, trust score, or registry moderation helper unless it can export stronger joined registry receipts than this lane already can.

## Added 2026-03-23 (400) — workspace-boundary work should now productize ancestor discovery, config layering, and invocation mode

- **P-0506 Cargo Workspace Boundary Doctor Kit** — the next worthwhile implementation slice is `ancestor-discovery.receipt.json`, `config-layering.report.json`, `invocation-mode.report.json`, and `boundary-support-bundle.manifest.json` above the earlier trace / membership / diagnosis lane.
- Prefer proving grounds where parent includes, CLI overrides, `--manifest-path`, manifest-command mode, or single-file package posture would otherwise be flattened into one vague “Cargo discovery issue.”
- Do not spend the next pass on manifest rewriting, config editing, or generic build-failure diagnosis unless it can export stronger boundary receipts than this lane already can.


## Added 2026-03-23 (399) — crate knowledge packs should now productize assistant-context structure, query-support scope, and claim traces

- **P-0536 Crate Knowledge Pack Kit** — the next worthwhile implementation slice is `assistant-context.pack.json`, `query-support.matrix.json`, and `claim-trace.report.json` above the earlier material-basis / export-policy / excerpt-lineage lane.
- Prefer proving grounds where setup/API lookup are supported but performance/security/safety questions must be refused or routed to manual review.
- Do not spend the next pass on prompt engineering, ranking, or a crate-chat UI unless it can export stronger answerability and claim-trace receipts than this lane already can.


## Added 2026-03-23 (397) — safety-contract consumption should now productize authority, coverage, and semantic-lane reports

- **P-0453 Safety Contract Consumer Kit** — the next worthwhile implementation slice is `contract-authority.receipt.json`, `consumer-coverage.matrix.json`, and `semantic-lane.report.json` above the earlier snapshot/diff/runtime/bundle lane.
- Treat this as a receiver-facing honesty layer, not as a new proof engine and not as a universal semantics translator.
- Good first proving grounds are: one std-style contract source plus Kani runtime/proof split, one `verify-rust-std` accepted-tool plurality fixture, and one semantic-lane comparison note for Flux / Creusot / VeriFast.

## Added 2026-03-23 (396) — async runtime assurance should now productize deployment topology and guarded capability matrices

- **P-0532 Async Runtime Assurance Profile Kit** — the next worthwhile implementation slice is `runtime-deployment-topology.receipt.json`, `capability-availability.matrix.json`, and `surface-guard.report.json`.
- Prefer proving grounds where one runtime family spans materially different lanes: Unix Tokio servers vs Windows console control lanes, Embassy host `std` examples vs embedded targets, and mixed host-tooling + target-firmware repositories.
- Do not spend the next pass on another “unified runtime” abstraction or runtime benchmark suite unless it can export stronger deployment and guard receipts than this lane already can.

## Added 2026-03-23 (395) — async runtime assurance should now productize service topology and capability routes

- **P-0532 Async Runtime Assurance Profile Kit** — the next worthwhile implementation slice is `runtime-service-topology.receipt.json`, `capability-route.receipt.json`, and `compatibility-bridge.report.json`.
- Prefer proving grounds where the route is genuinely non-trivial: hand-built Tokio runtimes without default resource drivers, Embassy executor plus HAL time-driver setups, RTIC dispatcher/monotonic lanes, and bridge crates such as `async-compat`.
- Do not spend the next pass on another executor benchmark or another “unified async runtime” abstraction unless it can export stronger receipts than this lane already can.

## Added 2026-03-22 (393) — pathfinder passes now need candidate basis, support visibility, and portable bundles

- Deepen **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** around `candidate-basis.receipt.json`, `support-visibility.report.json`, and `pathfinder-bundle.manifest.json` before considering any new nearby crate-ranking, registry-search, or “blessed starter set” lane.
- Prefer compact scenario bundles proving Cargo package-selection ergonomics are not recommendation authority, public registry/docs surfaces do not settle task fit, and portable bundle inventory keeps basis/visibility/choice separate.
- Guardrail: do not broaden into generic trust scoring, crate-health capture, docs.rs parity, or silent auto-replacement unless a pass clearly escapes **P-0509 / P-0011 / P-0017 / P-0484 / P-0536**.

## Added 2026-03-22 (387) — doctest-support passes now need extraction basis, grouping comparability, and bundle honesty

- Deepen **P-0455 Doctest Extraction & Support Contract Kit** around `extraction-basis.receipt.json`, `grouping-comparison.report.json`, and `doctest-support-bundle.manifest.json` before considering any new nearby docs-example, docs.rs-wrapper, or docs-quality lane.
- Prefer compact scenario bundles proving nightly rustdoc JSON basis vs Markdown fallback, merged-2024 vs standalone comparability drift, and portable bundle inventory.
- Guardrail: do not broaden into generic docs.rs parity, generic runner-profile policy, or generic coverage/debt review unless a pass clearly escapes **P-0455 / P-0481 / P-0472 / P-0476 / P-0451**.

## Added 2026-03-22 (383) — dependency-lifecycle passes now need override authority and freshness honesty

- Deepen **P-0535 Dependency Lifecycle Transition Kit** around `override-authority.receipt.json`, `signal-freshness.report.json`, and `exception-reevaluation.report.json` before considering any new nearby dependency-policy, vendoring, or off-ramp lane.
- Prefer compact scenario bundles proving local config-patch visibility limits, source-replacement versus fork-progress distinction, stale imported signals, expired exceptions, and portable bundle separation.
- Guardrail: do not broaden into generic trust scoring, mirror/source-parity proof, or off-ramp recommendation unless a pass clearly escapes **P-0535 / P-0496 / P-0017 / P-0515 / P-0011**.

## Added 2026-03-22 (382) — trusted-publishing passes now need registry imports, workflow-route receipts, and authorization drift

- Deepen **P-0175 Trusted Publishing Tooling Kit** around `registry-publisher-state.import.json`, `workflow-identity-route.receipt.json`, and `publish-authorization-drift.report.json` before considering any new nearby CI-auth, provenance, or publish-dashboard lane.
- Prefer compact scenario bundles proving imported TP-only state, reusable-workflow route identity, GitLab route drift, and portable bundle inventory.
- Guardrail: do not broaden into generic JWT debugging, registry auth diagnosis, or post-publish provenance unless a pass clearly escapes **P-0175 / P-0492 / P-0477 / P-0015**.

## Added 2026-03-22 (380) — feature-support passes now need observation scope and hosted-doc posture

- Deepen **P-0528 Cargo Feature Surface Contract Kit** around `resolution-scope.receipt.json`, `hosted-feature-profile.receipt.json`, and `feature-support-bundle.manifest.json` before considering any new nearby feature-listing or docs-surface lane.
- Prefer compact scenario bundles proving workspace-wide `--no-default-features` scope drift, docs.rs `all-features` public-doc posture, and portable bundle inventory.
- Guardrail: do not broaden into generic Cargo docs rendering, workspace speedup, or crate-search UX unless a pass clearly escapes **P-0528 / P-0036 / P-0469 / P-0484 / P-0536**.


## Added 2026-03-22 (379) — crate-knowledge exports now need material basis and excerpt lineage

- Deepen **P-0536 Crate Knowledge Pack Kit** around `material-basis.receipt.json`, `export-policy.receipt.json`, and `excerpt-lineage.report.json` before considering any new nearby docs/retrieval/assistant lane.
- Prefer compact scenario bundles proving pinned-vs-floating docs.rs resolution, absent hosted rustdoc JSON, download-archive caveats, and public-support export redaction.
- Guardrail: do not broaden into search ranking, answer generation, or offline docs hosting unless a pass clearly escapes **P-0536 / P-0051 / P-0472 / P-0476 / P-0455**.

## 2026-03-22 — toolchain/target passes should prefer imported authority, public docs surface, and portable bundles

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**

Near-term productization for **P-0484** should keep upstream authority imports, project-local support classes, public docs surface receipts, route/topology receipts, and portable bundle manifests explicit.

## 2026-03-22 — debuggability passes should prefer backend observations, source materials, and portable bundles

After rereading the archive and checking fresh official Rust sources, the sharper near-term move is to deepen **P-0486** around exportable review artifacts rather than opening another debugger-facing lane.

For the next few passes, prefer work that strengthens:

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0121 FFI Boundary & Bindings Conformance Kit**
4. **P-0036 MSRV Workspace Lab**
5. **P-0532 Async Runtime Assurance Profile Kit**

Guardrail: debugger-adjacent proposals should justify why they are not better modeled as **P-0486** plus a narrower crash, source-lookup, visualizer, or runtime lane.


## Added 2026-03-22 (374) — MSRV artifact completeness
- Deepen **P-0036 MSRV Workspace Lab** around `effective-workspace-promise.manifest`, `policy-split-diff.report`, and `msrv-support-bundle.manifest` before considering any new nearby MSRV finder, badge, or CI-matrix lane.

## Added 2026-03-22 (372) — crate-health artifact completeness
- Deepen **P-0011 Crate Health Contract Kit** around `registry-signal.import`, `routing-drift.diff`, and `health-support-bundle.manifest` before considering any new nearby stewardship-scoring or funding lane.

## Added 2026-03-22 (371) — unsafe-contract auditor deepening
- Deepen **P-0120 Unsafe Contract Auditor Kit** around `authority-import.receipt`, `obligation-drift.diff`, `witness-comparison.report`, and callback-boundary scenarios before considering any new nearby unsafe-analysis lane.

## Added 2026-03-22 — Cargo lock-contention witness work now deserves the newer artifact-rich treatment

Near-term preferred sequence now becomes:
1. keep **P-0490**, **P-0484**, **P-0121**, and **P-0469** in the lead cluster for Cargo support-contract work;
2. incubate **P-0490 Cargo Lock Contention Witness Kit** as the core lane for root-authority truth, actor command lanes, and mitigation-cost reporting;
3. reuse rebuild, delegation, and sandbox vocabulary where helpful, but do not collapse waiting/blocking into those adjacent lanes.

- **P-0490 Cargo Lock Contention Witness Kit** — now high priority because current Cargo and rust-analyzer docs already expose enough substrate to support compact receipts for **root authority**, **actor command lanes**, **wait windows**, **blocker-identity exactness**, and **mitigation cost**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `root-authority.receipt.json`, `actor-command-lane.receipt.json`, `wait-window.receipt.json`, and `mitigation-cost.report.json` instead of broadening P-0490 into another generic performance dashboard, process controller, or cache policy essay.

## Added 2026-03-22 — public/private dependency boundaries now deserve a first-class support-contract lane

Near-term preferred sequence now becomes:
1. keep **P-0431**, **P-0484**, and **P-0121** in the lead cluster;
2. incubate **P-0431 Public Dependency Boundary Kit** as the core lane for manifest-intent truth, effective publicness, workspace-gap honesty, and migration bundles;
3. reuse existing public-API / SemVer / external-type tooling as substrate rather than re-describing boundary truth inside those neighboring lanes.

- **P-0431 Public Dependency Boundary Kit** — now high priority because official Rust plans explicitly target stabilization of public/private dependencies while current Cargo and rustdoc-based tooling already expose enough substrate to support compact receipts for **manifest intent**, **boundary verdicts**, **exposure routes**, **evidence provenance**, **workspace gaps**, and **migration posture**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `manifest-intent.receipt.json`, `boundary-verdict.report.json`, `exposure-route.report.json`, `workspace-gap.receipt.json`, and `boundary-migration.plan.json` instead of broadening P-0431 into another public-API diff viewer, lint wrapper, or resolver design essay.

## Added 2026-03-22 — in-place initialization adoption now deserves a first-class lane

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, and **P-0120** in the lead cluster;
2. incubate **P-0447 In-Place Initialization Adoption Kit** as the core lane for placement/address/failure truth;
3. reuse projection, unsafe-field, and FFI vocabulary where helpful, but do not collapse in-place-init review into those adjacent lanes.

- **P-0447 In-Place Initialization Adoption Kit** — now high priority because official Rust planning explicitly centers in-place initialization in the `Beyond the &` agenda while existing crates already provide enough substrate to support compact receipts for **placement topology**, **constructor lanes**, **address commit**, **failure cleanup**, and **drift**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `placement-topology.receipt.json`, `constructor-lane.report.json`, `address-commit.receipt.json`, `failure-cleanup.report.json`, and `init-transition.diff.json` instead of broadening P-0447 into another macro pack, language explainer, or pinning cookbook.

## Added 2026-03-22 — lint-policy evidence now deserves a first-class support-contract lane

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, and **P-0120** in the lead cluster;
2. incubate **P-0459 Clippy Safety Profile & Waiver Kit** as the core lint-policy evidence lane;
3. reuse workspace rollout and future-incompat vocabulary instead of re-describing lint authority and waivers in each adjacent lane.

- **P-0459 Clippy Safety Profile & Waiver Kit** — now high priority because official Rust plans explicitly name safety-critical Clippy work while Cargo and Clippy already expose enough policy/configuration substrate to support compact receipts for **policy authority**, **checked scope**, **diagnostic channels**, **waiver truth**, and **drift**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `policy-authority.receipt.json`, `checked-scope.matrix.json`, `diagnostic-channel.receipt.json`, `waiver-decision.record.json`, and `lint-policy-drift.diff.json` instead of broadening P-0459 into another lint engine, dashboard, or workspace spreadsheet.

## Added 2026-03-22 — unsafe-field invariants now deserve a first-class unsafe-review lane

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, **P-0120**, **P-0036**, and **P-0535** in the lead cluster;
2. incubate **P-0460 Unsafe Field Invariant Ledger Kit** as the core lane for field-authority and mutator-trust truth;
3. reuse broader unsafe-audit, FFI, and verification vocabulary where helpful, but do not collapse field contracts into those adjacent lanes.

- **P-0460 Unsafe Field Invariant Ledger Kit** — now high priority because official Rust work finally makes field-carried invariants, contract imports, and normative unsafe documentation concrete enough to support compact receipts for **field authority**, **mutation lanes**, **trusted constructors**, **witness scope**, and **drift**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `field-authority.receipt.json`, `mutation-lane.report.json`, `trusted-constructor.receipt.json`, `invariant-witness.report.json`, and `field-contract-drift.diff.json` instead of broadening P-0460 into another general unsafe dashboard.

## Added 2026-03-22 — documentation-example support now deserves a first-class docs-facing lane

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, **P-0120**, **P-0036**, and **P-0535** in the lead cluster;
2. incubate **P-0455 Doctest Extraction & Support Contract Kit** as the core lane for documentation-example support truth;
3. reuse runner-profile, docs.rs parity, coverage, and cfg-availability vocabulary instead of re-describing docs support in each adjacent lane.

- **P-0455 Doctest Extraction & Support Contract Kit** — now high priority because Rust docs are still canonical while extraction, runtool, ignore-target, and merged-doctest substrate is finally concrete enough to support compact receipts for **manifest truth**, **rewrite lineage**, **execution mode**, **support class**, and **drift**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `doctest.manifest.json`, `rewrite-lineage.receipt.json`, `execution-mode.receipt.json`, `docs-example-support.report.json`, and `docs-example-drift.diff.json` instead of broadening P-0455 into another docs portal, docs.rs wrapper, or coverage dashboard.

## Added 2026-03-22 — sanitizer workflow evidence now deserves a first-class debugging/safety pass

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, **P-0036**, and **P-0535** in the lead cluster;
2. incubate **P-0434 Sanitizer Profile & Evidence Kit** as the workflow/evidence lane for sanitizer use in practice;
3. reuse target-support and debugger-support vocabulary where helpful, but do not collapse sanitizer evidence into either adjacent lane.

- **P-0434 Sanitizer Profile & Evidence Kit** — now high priority because official Rust goals still include sanitizer stabilization and instrumented standard-library infrastructure, while current sanitizer docs make the operational seams concrete enough to support compact receipts for **instrumentation scope**, **runtime linkage**, **symbolization route**, and **suppression policy**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `instrumentation-scope.receipt.json`, `runtime-linkage.receipt.json`, `symbolization-route.receipt.json`, and `suppression-policy.receipt.json` instead of broadening P-0434 into another runner, verifier, or debugger matrix.


## Added 2026-03-22 — dependency lifecycle now deserves a first-class contract lane

Near-term preferred sequence now becomes:
1. keep **P-0484**, **P-0121**, and **P-0036** in the top cluster;
2. incubate **P-0535 Dependency Lifecycle Transition Kit** as the new lane for criticality placement and seam-backed replacement planning;
3. reuse trust / MSRV / off-ramp vocabulary instead of re-describing dependency lifecycle in each adjacent lane.

- **P-0535 Dependency Lifecycle Transition Kit** — now high priority because official Rust guidance explicitly asks for reusable dependency-lifecycle patterns, while today’s Cargo and crates.io substrate still lacks one portable bundle for **criticality lanes**, **abstraction seams**, **transition posture**, and **lifecycle drift**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `dependency-lane.snapshot.json`, `criticality-boundary.report.json`, `abstraction-seam.receipt.json`, `replacement-readiness.report.json`, `dependency-exception.ledger.json`, and `lifecycle-drift.diff.json` instead of broadening P-0535 into another scanner, ranker, or architecture framework.


## Added 2026-03-22 — immediate next-step guidance

Near-term preferred sequence:
1. finish rounding out **P-0484** with artifact-route and host-target topology receipts;
2. keep **P-0121** and **P-0036** close behind;
3. only then deepen narrower runtime or platform shipkits that can reuse the support-contract vocabulary.

## 2026-03-22 — promote cross-language interop into the top support-contract cluster

After rereading the archive and checking fresh official Rust sources plus current interop substrate, the sharper near-term move is to deepen the strongest support-contract lanes instead of opening another language-specific shipkit.

For the next few passes, prefer work that strengthens:

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0121 FFI Boundary & Bindings Conformance Kit**
3. **P-0036 MSRV Workspace Lab**
4. **P-0532 Async Runtime Assurance Profile Kit**
5. **P-0486 Debuggability Support Contract Kit**

Guardrail: interop-adjacent proposals should justify why they are not better modeled as P-0121 plus a narrower delivery/runtime lane.

## 2026-03-22 — prefer frontier reranking and top-lane deepening over more proposal count

After rereading the archive and checking fresh official Rust sources, the sharper near-term move is to deepen the strongest support-contract lanes instead of opening another narrow crate idea.

For the next few passes, prefer work that strengthens:

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0036 MSRV Workspace Lab**
3. **P-0121 FFI Boundary & Bindings Conformance Kit**
4. **P-0532 Async Runtime Assurance Profile Kit**
5. **P-0486 Debuggability Support Contract Kit**

Guardrail: the archive should stay broad, but new passes should justify why they outrank these before adding another lane.


## Added 2026-03-21 (service readiness / drain contract productization)
- **P-0534 Service Readiness & Drain Contract Kit** — now high priority because Rust service substrate is strong enough that the next missing artifact is no longer “some way to do health checks or graceful shutdown”, but a portable bundle that keeps **activation gates**, **readiness surfaces**, **health channels**, **shutdown triggers**, **drain policy**, and **in-flight fate** honest across Tower/Hyper/Axum/Tonic/Tokio stacks.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `activation-gate.receipt.json`, `readiness-surface.receipt.json`, `health-channel.receipt.json`, `shutdown-trigger.receipt.json`, `drain-policy.receipt.json`, `inflight-fate.report.json`, and `service-transition-bundle.manifest.json` instead of broadening P-0534 into another web framework, probe-endpoint helper, or rollout platform.

## 2026-03-21 refresh — crash support now needs capture / identity / route / replay contracts

This refresh should override stale impressions that the archive mainly needs another crash collector, another hosted dashboard, or another debugger UI.

### Main judgment
- The substrate is now strong enough that **P-0101 Crash Artifact & Symbolication Workbench Kit** should be treated as a build-shaped support-contract lane.
- The missing value is more specific than “crash reporting”: future passes need **capture basis**, **module identity**, **symbol route**, **analysis coverage**, **report determinism**, and **share-safety** to stay separate.
- Capture-side crates, stackwalkers, symbol fetchers, and hosted services all look stronger when they sit below or beside that contract instead of being mistaken for it.

### Best next incubation targets in this stack
1. **P-0101 Crash Artifact & Symbolication Workbench Kit**
2. **P-0256 Evidence Bundle Core Kit**
3. **P-0073 Async Replay Debugger Kit**
4. **P-0083 Debugger UX**

### Working rule
For the next few passes, prefer stabilizing crash-contract receipts and small scenario bundles over adding another upload service wrapper or another one-off crash artifact grammar.

Do **not** let “crash reporting support” collapse capture posture, module identity, symbol route, analysis quality, replayability, and share-safety into one fake green state.

## 2026-03-21 refresh — task supervision now needs topology / reset / timeout contracts

This refresh should override stale impressions that the archive mainly needs another actor framework, another watchdog helper, or another graceful-shutdown wrapper.

### Main judgment
- The substrate is now strong enough that **P-0095 Task Supervision & Restart Kit** should be treated as a build-shaped support-contract lane.
- The missing value is more specific than “supervised tasks”: future passes need **supervision topology**, **restart policy**, **health/readiness basis**, **state reset**, **shutdown escalation**, and **failure bundles** to stay separate.
- Task groups, shutdown helpers, actor supervisors, and restart helpers all look stronger when they sit below or beside that contract instead of being mistaken for it.

### Best next incubation targets in this stack
1. **P-0095 Task Supervision & Restart Kit**
2. **P-0520 Crate Lifecycle Surface Pack Kit**
3. **P-0073 Async Replay Debugger Kit**
4. **P-0532 Async Runtime Assurance Profile Kit**

### Working rule
For the next few passes, prefer stabilizing supervision-contract receipts and small scenario bundles over adding another actor/runtime abstraction or another folklore-heavy restart helper.

Do **not** let “task supervision support” collapse blast radius, restart triggers, state reset, health basis, timeout aftermath, and failure bundles into one fake green state.

## 2026-03-21 refresh — OpenAPI 3.1 support now needs dialect / refs / projection contracts

This refresh should override stale impressions that the archive mainly needs another parser crate or another generator wrapper.

### Main judgment
- The substrate is now strong enough that **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit** should be treated as a build-shaped support-contract lane.
- The missing value is more specific than "OpenAPI 3.1 support": future passes need **dialect identity**, **ref-resolution route**, **bundle/projection policy**, **compatibility profile**, and **semantic-diff authority** to stay separate.
- Parser/model crates, generic JSON Schema validators, code-first emitters, and generators all look stronger when they sit below or beside that contract instead of being mistaken for it.

### Best next incubation targets in this stack
1. **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit**
2. **P-0256 Evidence Bundle Core Kit**
3. **P-0244 SemVer API Diff Evidence Kit**
4. **P-0264 Rust Conformance Harness Toolkit**

### Working rule
For the next few passes, prefer stabilizing OpenAPI/JSON Schema contract receipts and small scenario bundles over adding another framework-specific emitter or generator-first abstraction.

Do **not** let "OpenAPI support" collapse dialect posture, ref policy, projection choice, compatibility profile, and diff verdicts into one fake green state.

## 2026-03-21 refresh — bundle substrate receipts before more bundle count

This refresh should override stale impressions that the archive mainly needs more `*.somethingbundle.zip` proposal count.

### Main judgment
- The archive now has enough bundle-first lanes that **P-0256 Evidence Bundle Core Kit** should again be treated as a portfolio multiplier.
- The missing value is now more specific than “signed and redactable”: future passes need **container basis**, **entry lineage**, **attestation lane**, **publication route**, and **share-safety posture** to stay separate.
- Domain bundle profiles, attestation standards, and publication systems all look stronger when they sit above or beside that substrate instead of re-specifying it.

### Best next incubation targets in this stack
1. **P-0256 Evidence Bundle Core Kit**
2. **P-0503 Assurance Case Workbench Kit**
3. **P-0264 Rust Conformance Harness Toolkit**
4. **P-0485 Verification Campaign Workbench Kit**

### Working rule
For the next few passes, prefer stabilizing bundle-substrate receipts and shared adapter planning over adding another narrow private bundle grammar.

Do **not** let “bundle support” collapse local validity, signatures, publication, and shareability into one fake green state.

## Added 2026-03-21 (trusted publishing productization)
- **P-0175 Trusted Publishing Tooling Kit** — now high priority because the publish-identity substrate is strong enough that the next missing artifact is no longer “some way to use OIDC”, but a portable bundle that keeps **provider scope**, **claim basis**, **trigger policy**, **publish mode**, and **rehearsal result** honest across GitHub Actions, GitLab.com, and mixed migration states.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `provider-capability.matrix.json`, `claim-basis.receipt.json`, `release-trigger.report.json`, `publish-mode.receipt.json`, `publish-rehearsal.report.json`, `provider-drift.diff.json`, and `publish-support-bundle.manifest.json` instead of broadening P-0175 into another publisher, provenance service, or registry-auth debugger.

## Added 2026-03-21 (verification campaign productization)
- **P-0485 Verification Campaign Workbench Kit** — now high priority because the Rust verification substrate is broad enough that the next missing artifact is no longer “some proof tool”, but a portable bundle that keeps **obligation inventory**, **lane semantics**, **trust ledger**, **policy evaluation**, and **comparability** honest across Miri, Kani, Creusot, Prusti, Flux, and Verus.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `campaign-manifest.json`, `obligation-record.json`, `lane-result.json`, `trust-ledger.json`, `policy-evaluation.report.json`, `campaign-diff.report.json`, and `verify-campaign.json` instead of broadening P-0485 into another verifier, proof IDE, or assurance-case editor.


## Added 2026-03-21 (async replay debugger productization)
- **P-0073 Async Replay Debugger Kit** — now high priority because the async-debugging substrate is strong enough that the next missing artifact is no longer “some tracing/debugging tool”, but a portable bundle that keeps **schedule basis**, **time basis**, **instrumentation coverage**, **effect boundaries**, and **replay fidelity** honest across live runtime telemetry, paused-time tests, schedule-control harnesses, and narrow effect cassettes.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `schedule-basis.receipt.json`, `time-basis.receipt.json`, `instrumentation-coverage.report.json`, `effect-boundary.receipt.json`, `replay-fidelity.report.json`, and `async-incident-bundle.manifest.json` instead of broadening P-0073 into another runtime, trace spec, or universal debugger.


## Added 2026-03-21 (stable native plugin host productization)
- **P-0081 Stable Plugin Host Kit** — now high priority because the native-plugin substrate is broad enough that the next missing artifact is no longer “some way to `dlopen` a Rust dylib”, but a portable bundle that keeps **ABI surface**, **capability negotiation**, **lifecycle posture**, and **compatibility witness** truth honest across `abi_stable`, lower-level `libloading`, and serialized fallback boundaries.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `abi-surface.receipt.json`, `capability-negotiation.receipt.json`, `lifecycle-posture.receipt.json`, `compatibility-witness.receipt.json`, and `plugin-bundle.manifest.json` instead of broadening P-0081 into another marketplace, loader framework, or universal stable-ABI fantasy.

## Added 2026-03-21 (Array API productization)
- **P-0003 Array API** — now high priority because the numerics substrate is broad enough that the next missing artifact is no longer “some backend-agnostic trait”, but a portable bundle that keeps **semantic profile**, **layout/view truth**, **device+dtype inspection**, **namespace coverage**, and **interop-route honesty** explicit across dense arrays, linear algebra, tensor backends, and columnar bridges.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `semantic-profile.receipt.json`, `layout-view.receipt.json`, `device-dtype.receipt.json`, `namespace-coverage.receipt.json`, `interop-route.receipt.json`, and `array-bundle.manifest.json` instead of broadening P-0003 into another tensor engine, sparse standard, or Arrow replacement.

## Added 2026-03-21 (Wasm plugin kit productization)
- **P-0002 Wasm Plugin Kit** — now high priority because the component/plugin substrate is strong enough that the next missing artifact is no longer “some way to run Wasm code”, but a portable bundle that keeps **plugin interface**, **capability grants**, **execution budgets**, and **instance lifecycle** honest across Wasmtime components, `cargo component`, and Extism-style plugin systems.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `plugin-interface.receipt.json`, `capability-grant.receipt.json`, `execution-budget.receipt.json`, `instance-lifecycle.receipt.json`, and `plugin-bundle.manifest.json` instead of broadening P-0002 into another runtime, marketplace, or registry client.

## Added 2026-03-21 (test-run artifact standard productization)
- **P-0106 Test Run Artifact Standard Kit** — now high priority because current Rust test substrate is strong enough that the next missing artifact is no longer “some machine-readable output”, but a portable bundle that keeps **run identity**, **selection basis**, **attempt topology**, and **bundle sensitivity** honest across libtest, nextest, and custom harnesses.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `run-identity.receipt.json`, `selection-basis.receipt.json`, `attempt-topology.report.json`, `bundle-sensitivity.receipt.json`, and `testrun-bundle.manifest.json` instead of broadening P-0106 into another test runner or dashboard.

## Added 2026-03-21 (error-surface contract addition)
- **P-0533 Error Surface Contract Kit** — now high priority because the ecosystem has strong error-construction substrate but still lacks one receiver-facing contract for stable error codes, audience-specific surfaces, actionable remediation, and safe-export posture.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `error-identity.receipt.json`, `audience-mode.receipt.json`, `remediation-surface.report.json`, and `sensitivity-posture.receipt.json` instead of broadening P-0533 into another derive, report, or renderer framework.

## Added 2026-03-21 (comptime reflection bridge productization)
- **P-0439 Comptime Reflection Bridge Kit** — now materially more implementation-ready because the next missing artifact is no longer just a generic schema IR; it is a bridge bundle that keeps **schema-source**, **coverage-scope**, **execution-posture**, and **loss-accounting** truth explicit across Bevy registries, Facet shape exports, format-schema projections, and future compile-time reflection adapters.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `schema-source.receipt.json`, `coverage-scope.report.json`, `execution-posture.receipt.json`, and `loss-accounting.report.json` instead of broadening P-0439 into a final reflection standard or a new runtime reflection framework.

## Added 2026-03-21 (async runtime assurance profile addition)
- **P-0532 Async Runtime Assurance Profile Kit** — now high priority because official Rust sources identify both async runtime lock-in and unresolved runtime qualification as live ecosystem problems, while Tokio / Embassy / RTIC docs are now concrete enough to classify into one compact runtime-choice artifact.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `runtime-profile.receipt.json`, `shutdown-behavior.report.json`, and `qualification-basis.receipt.json` instead of broadening P-0532 into a universal async runtime abstraction.

## Added 2026-03-21 (build-dir transition adapter-window deepening)
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — now more implementation-ready because the next missing artifact is no longer just an adapter plan; it is an **adapter-viability report** that keeps version floors, fallback pressure, and dual-support windows honest.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `adapter-viability.report.json` instead of broadening P-0489 into a generic Cargo filesystem API.

## 2026-03-21 refinement — crate health now needs maintenance-coverage truth

This pass did **not** promote another ranking engine, maintainer leaderboard, or funding dashboard.
It sharpened **P-0011 Crate Health Contract Kit** into a more maintenance-aware stewardship contract.

### Main judgment
- Treat `meta/crate-health-maintenance-coverage-2026-03-21.md` as the working sketch for the next serious **P-0011** implementation pass.
- The key new planning detail is that a worthy crate-health crate should publish explicit **maintenance-coverage**, **duty-map-gap**, and **visible-versus-invisible-work** artifacts instead of leaving those truths buried across release cadence, issue traffic, security tabs, and vague maintenance labels.
- `0.1` should stay centered on `capture`, `check`, `diff`, `summary`, and `bundle` workflows above today’s maintainer declarations, registry signals, and repo signals.

### What to keep separate
- Keep **P-0011** separate from **P-0509** pathfinder / crate choice.
- Keep **P-0011** separate from **P-0515** off-ramp / migration support.
- Keep **P-0011** separate from **P-0017** trust/provenance/security posture.
- Keep **P-0011** separate from maintainer-funding or social-scoring schemes.
- Keep **P-0011** separate from generic repository analytics dashboards.

### Preferred proving grounds
- quiet release streams with strong lights-on coverage but weak review bandwidth
- feature-active crates with missing CI/security/docs ownership
- single-maintainer crates that can name a backup but not a duty map
- sunset lanes where maintenance windows exist but duty coverage has already collapsed

## 2026-03-21 refinement — crate resource surfaces now need budget-topology truth

This pass did **not** promote another queue, pool, limiter, or metrics lane.
It sharpened **P-0521 Crate Resource Surface Pack Kit** into a more topology-aware support contract.

### Main judgment
- Treat `meta/crate-resource-surface-budget-topology-2026-03-21.md` as the working sketch for the next serious **P-0521** implementation pass.
- The key new planning detail is that a worthy resource-support crate should publish explicit **budget-topology**, **sharing-behavior**, **multiplication-axis**, and **aggregate-bound-posture** artifacts instead of leaving those truths buried across clone semantics, per-host/per-connection builders, and deployment topology.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s queue/pool/cache/runtime substrate.

### What to keep separate
- Keep **P-0521** separate from **P-0517** performance envelopes.
- Keep **P-0521** separate from **P-0518** observability surfaces.
- Keep **P-0521** separate from **P-0520** lifecycle/drain truth.
- Keep **P-0521** separate from **P-0529** channel semantics.
- Keep **P-0521** separate from new queue/cache/pool implementation substrate.

### Preferred proving grounds
- reqwest client families that share one internal pool but still expose per-host bounds
- sqlx or deadpool clone handles that share one pool state
- Tokio channel senders that multiply handles without multiplying one channel buffer
- tonic per-connection concurrency limits that scale with live connections
- Tower stacks where layer order changes the actual total in-flight budget

## 2026-03-21 refinement — cargo-build-insights now has an implementation-ready `0.1` sketch

This pass did **not** promote another generic Cargo dashboard or another one-run build incident tool.
It sharpened **P-0035 cargo-build-insights** into a more implementation-ready historical-build shape.

### Main judgment
- Treat `meta/cargo-build-insights-product-plan-2026-03-21.md` as the working build sketch for **P-0035**.
- The key new planning detail is that a worthy historical-build crate should publish explicit **comparison-window**, **series-compatibility**, **import/exactness**, and **export-policy** artifacts rather than leaving those truths buried across unstable Cargo reports, local naming conventions, and ad hoc CI screenshots.
- `0.1` should stay centered on `import-session`, `freeze-series`, `compare`, `doctor`, `summary`, `trend-alerts`, and `export` workflows above Cargo's build-analysis/session substrate.

### What to keep separate
- Keep **P-0035** separate from **P-0469** one-run rebuild explanation.
- Keep **P-0035** separate from **P-0468** resolver/graph cause explanation.
- Keep **P-0035** separate from **P-0494** tool-workflow parity.
- Keep **P-0035** separate from **P-0490** lock/contention witnesses.
- Keep **P-0035** separate from hosted dashboards and organization telemetry platforms.

### Preferred proving grounds
- a PR review bundle that compares head against the last green base branch session
- a rolling `main` trend window with redaction but still-useful exported artifacts
- a toolchain bump that requires a series split before any regression claim
- a workspace-scope change that blocks naive comparison

## 2026-03-21 — add CLI surface contract lane

The archive now has adjacent lanes for examples/first-success support, test snapshots, guidance channels, diagnosis bundles, and broader desktop/TUI product engineering. The next ordinary lie was still too cheap: a tool could say “has a CLI / supports JSON / works in CI” and leave downstream teams without one compact answer for **what the stable command surface is, which output mode is for automation, what changes under TTY versus pipe, and what each exit outcome means**.

The sharper move is therefore to add **P-0531 CLI Surface Contract Kit** with first-class review objects for:

- `command-surface.receipt`
- `output-mode.receipt`
- `terminal-mode.receipt`
- `exit-semantics.receipt`

Do not let future passes flatten this lane into another parser helper, another prompt toolkit, or another snapshot-test suite.

## 2026-03-20 — add request-execution policy contract lane

The archive now has adjacent lanes for channel semantics, lifecycle/shutdown truth, resource saturation, observability delivery truth, and capability/support contracts. The next ordinary lie was still too cheap: a crate could say “supports retries / timeout / rate limits / load shedding” and leave downstream teams without one compact answer for **why replay is safe, what the real attempt budget is, where admission waits or rejects, and whether attempts are serial or hedged in parallel**.

The sharper move is therefore to add **P-0530 Request Execution Policy Contract Kit** with first-class review objects for:

- `idempotency-basis.receipt`
- `attempt-budget.receipt`
- `admission-path.receipt`
- `attempt-topology.report`

Do not let future passes flatten this lane into another retry middleware, another resilience-suite survey, or another Tower cookbook.

## 2026-03-20 — add Cargo feature-surface contract lane

The archive now has adjacent lanes for capability contracts, cfg/item availability, Cargo config truth, MSRV policy activation, upgrade support, and resolver explanation. The next ordinary lie was still too cheap: a crate could show a long `[features]` table, pass `--all-features`, and leave downstream teams without one compact answer for which names are public contract, which combinations are really supported, and where unification/default behavior can still surprise them.

The sharper move is therefore to add **P-0528 Cargo Feature Surface Contract Kit** with first-class review objects for:

- `feature-surface.receipt`
- `activation-profile.report`
- `conflict-policy.receipt`
- `unification-risk.report`

Do not let future passes flatten this lane into another feature lister, another combo runner, or another workspace-speed helper.

## 2026-03-20 refinement — crate observability support now includes delivery/completeness truth

This pass revisited **P-0518 Crate Observability Surface Pack Kit** again.

It sharpened **P-0518** around **delivery posture** and **completeness class** so the lane no longer stops at signal existence, activation, and bridge routes.

### What changed

- Treat `meta/crate-observability-surface-product-plan-2026-03-20.md` as the working build sketch for the next implementation-ready pass of **P-0518**.
- The key new planning detail is that a worthy observability-support crate should publish explicit **delivery-posture** and **completeness-class** artifacts rather than letting route truth masquerade as delivery truth.
- Treat `meta/crate-observability-surface-delivery-boundaries-2026-03-20.md` as the lane-boundary note that keeps route existence, loss posture, sampling, periodic aggregation, and exit-sensitive flushing from collapsing into one fake “telemetry support” story.

### Guardrails

- Keep **P-0518** separate from telemetry plumbing: subscribers, appenders, exporters, queues, and collectors are not the same lane as a receiver-facing support contract.
- Keep **P-0518** separate from **P-0520** lifecycle support: shutdown barriers are adjacent, but here the question is only what delivery/completeness claim is honest for a published signal surface.
- Keep **P-0518** separate from performance/memory-profiling lanes: overhead and memory pressure matter, but they are not the same product as delivery/completeness truth.

### Files added for this refinement

- `entries/2026-03-20-307.md` — observability lane sharpened around delivery posture and completeness class
- `meta/crate-observability-surface-product-plan-2026-03-20.md` — current implementation-ready build sketch for the delivery/completeness pass
- `meta/crate-observability-surface-delivery-boundaries-2026-03-20.md` — lane-boundary note for route vs delivery/completeness truth
- `fixtures/crate-observability-surface-pack-kit/delivery-posture.receipt.schema.json` + `completeness-class.report.schema.json` — schemas for honest route interpretation
- three scenario families for lossy nonblocking logs, batch flush dependence, and periodic aggregated metrics

## 2026-03-20 — secrets-kit deepening around revelation path, persistence posture, memory posture, and export posture

- Chose to deepen **P-0037** instead of opening another encrypted-envelope, key-manager, or generic redaction lane.
- Decided that the next implementation pass should elevate **revelation path**, **persistence posture**, **memory posture**, and **export posture** into first-class artifacts.
- Reaffirmed that keyring adapters, zeroize wrappers, protected-memory backends, and secret-at-rest policy are related but not interchangeable with receiver-facing secret-handling contract truth.

## 2026-03-20 — FFI boundary contract deepening

- Chose to deepen **P-0121** instead of opening another packaging, mobile SDK, or generator-wrapper lane.
- Decided that the next implementation pass should elevate **ownership transfer**, **unwind posture**, **callback execution**, and **binding coverage** into first-class artifacts.
- Reaffirmed that whole-program ABI coherence, package/publication truth, bridge-specific generators, and migration/review governance are related but not interchangeable with receiver-facing FFI contract truth.

## 2026-03-20 refinement — crate test-surface lane now also needs isolation-class and reset-capability truth

- Keep **isolation-class truth** explicit alongside fixture catalogs, support levels, topology manifests, environment requirements, and witness lineage: a lane should say whether each helper is fresh per call, fresh per test, process-shared, externally shared, or only safe under a runner-specific isolation model.
- Keep **reset-capability truth** explicit too: OS cleanup, Drop cleanup, explicit reset APIs, best-effort external teardown, and no-reset-support should not collapse into one vague “temporary state” story.
- Prefer tiny receiver-facing artifacts such as `isolation-class.receipt` and `reset-capability.receipt` rather than treating a deterministic seam or a direct test witness as proof that a helper is contamination-safe.

## 2026-03-20 refinement — package review now needs archive-authority and extraction-mutation truth

- Treat `meta/cargo-package-review-product-plan-2026-03-20.md` as the current working sketch for **P-0470**.
- Keep **workspace candidate-set truth**, **packaged-surface truth**, **archive-authority truth**, **extraction-mutation truth**, **manifest-normalization truth**, and **path-explanation truth** explicit.
- Prefer tiny receiver-facing artifacts such as `packaged-surface.receipt`, `archive-authority.report`, and `extraction-mutation.report` rather than another file lister or vague “we reviewed the tarball” claim.


## 2026-03-20 refinement — open table formats now need table-surface, capability, and coupling truth

- Treat `meta/open-table-format-kit-product-plan-2026-03-20.md` as the current working sketch for **P-0028**.
- Keep **table-surface truth**, **capability-profile truth**, **storage/catalog wiring truth**, and **integration-coupling truth** explicit.
- Prefer tiny receiver-facing artifacts such as `table-surface.receipt`, `capability-profile.report`, and `integration-coupling.receipt` rather than another universal trait or vague “supports Iceberg/Delta/Hudi” claim.

## 2026-03-20 refinement — lifecycle support now needs shutdown-phase and timeout-aftermath truth

- Treat `meta/crate-lifecycle-surface-product-plan-2026-03-20.md` as the current working sketch for **P-0520**.
- Keep **activation-boundary truth**, **stop-semantics truth**, **shutdown-barrier truth**, **escape-path truth**, **shutdown-phase truth**, **timeout-aftermath truth**, **blocking-work caveats**, **teardown evidence**, and **drain-recipe truth** explicit.
- Prefer tiny receiver-facing artifacts such as `shutdown-phase.report` and `timeout-aftermath.receipt` rather than another timeout wrapper or vague “graceful timeout” claim.

## 2026-03-20 refinement — lifecycle support now needs shutdown-barrier and escape-path truth

- Treat `meta/crate-lifecycle-surface-product-plan-2026-03-20.md` as the current working sketch for **P-0520**.
- Keep **activation-boundary truth**, **stop-semantics truth**, **shutdown-barrier truth**, **escape-path truth**, **blocking-work caveats**, **teardown evidence**, and **drain-recipe truth** explicit.
- Prefer tiny receiver-facing artifacts such as `shutdown-barrier.report` and `escape-path.receipt` rather than another graceful-shutdown helper crate or vague “server shuts down cleanly” claim.

## 2026-03-20 refinement — text-input now needs edit-path and geometry truth, not just transaction truth

- Treat `meta/text-input-kit-product-plan-2026-03-20.md` as the current working sketch for **P-0027**.
- Keep **IME transaction truth**, **selection-contract truth**, **backend-capability truth**, **web-edit-path truth**, and **selection-geometry truth** explicit.
- Prefer tiny receiver-facing artifacts such as `web-edit-path.receipt` and `selection-geometry.report` rather than another canvas editor demo or vague “WASM text support” claim.

## 2026-03-20 refinement — trust lens now needs identity-risk, assumption, and review-debt truth

- Treat `meta/trust-lens-product-plan-2026-03-20.md` as the current working sketch for **P-0017**.
- Keep **identity-risk truth**, **signal-basis truth**, **assumption-register truth**, **review-debt truth**, and **policy-decision truth** explicit.
- Prefer tiny receiver-facing artifacts such as `identity-risk.report`, `assumption-register.report`, and `policy-decision.report` rather than another score dashboard, crates.io policy wish list, or cargo-vet replacement.

## 2026-03-21 refinement — trust lens now also needs notification-channel coverage

- Treat `meta/trust-lens-product-plan-2026-03-20.md` and `meta/trust-lens-notification-coverage-2026-03-21.md` as the current working sketch for **P-0017**.
- Keep **notification-channel coverage**, **change-class coverage**, and **feed-gap honesty** explicit alongside identity risk, signal provenance, assumptions, review debt, and policy decisions.
- Prefer tiny receiver-facing artifacts such as `notification-channel.report`, `identity-risk.report`, and `policy-decision.report` rather than another score dashboard, feed mirror, or crates.io monitoring wish list.


## 2026-03-20 refinement — crate health now has an implementation-ready `0.1` sketch

This pass did **not** invent another popularity metric or another maintainer leaderboard.
It sharpened **P-0011 Crate Health Contract Kit** into a more implementation-ready shape.

### Main judgment
- Treat `meta/crate-health-contract-product-plan-2026-03-20.md` as the working build sketch for **P-0011**.
- The key new planning detail is that a worthy crate-health crate should publish explicit **maintenance-window**, **succession-map**, **support-intent**, and **health-check** artifacts rather than leaving support truth buried across release dates, README notes, Cargo badges, security tabs, and issue folklore.
- `0.1` should stay centered on `capture`, `check`, `diff`, `summary`, and `bundle` workflows above today’s crates.io / repo / trust / badge substrate.

### What to keep separate
- Keep **P-0011** separate from **P-0509** task-first crate choice.
- Keep **P-0011** separate from **P-0515** off-ramp / successor recipes.
- Keep **P-0011** separate from trust/security scoring lanes.
- Keep **P-0011** separate from repository analytics dashboards.

### Preferred proving grounds
- a quiet release stream that is still honestly reactively maintained
- a frozen-but-supported crate with a visible supported-version horizon
- a crate with one maintainer but an explicit backup or org-owned handoff path
- a sunset-in-progress crate with no successor or support horizon, where failure should stay visible


## Added 2026-03-20 (287): upgrade packs must keep omission truth separate from public completeness

The archive already has publication-surface exactness, redaction receipts, summary-claim traceability, durable cues, and public trace routes. The sharper move now is to keep **omission-register truth** explicit so known-but-not-exported hazards, receipts, or local-only context cannot quietly disappear behind compact public surfaces.

---
## Added 2026-03-20 (286): upgrade packs must keep authorship buckets separate from exact citations

The archive already has source-lineage truth, summary-claim traceability, review provenance, and replay bridges. The sharper move now is to keep **surface-authorship truth** explicit so Cargo-native outputs, maintainer-authored guidance, reviewer-authored decisions, and archive-derived summaries cannot quietly inherit one another's trust surface.

---
## Added 2026-03-20 (285): upgrade packs must keep baseline identity separate from exact command/config truth

The archive already has lane-selection truth, config-basis truth, capture-context truth, and replay bridges. The sharper move now is to keep **baseline-state truth** explicit so a mutable or partially migrated workspace cannot quietly inherit the trust surface of a pinned published release pair.

---
## Added 2026-03-20 (282): upgrade packs must keep replay posture separate from actual replay routes

When future revisions sharpen **P-0514**, do not let the archive collapse these claims into one fake "replayable evidence" story:

1. **the capture says the lane is direct/native/copy/manual posture**,
2. **the pack records one exact rerun or rerender route**,
3. **the evidence only exists as a copied attachment**,
4. **and the remaining comparison must stay manual or unavailable**.

The archive already has capture-context truth and session-honesty truth. The sharper move now is to keep **replay-bridge truth** explicit so native rerender, copied snapshots, and summary-only evidence do not quietly inherit the same trust surface.

---
---
## Added 2026-03-20 (281): upgrade packs must keep session coherence separate from mere evidence presence

When future revisions sharpen **P-0514**, do not let the archive collapse these claims into one fake "all evidence points at the same review moment" story:

1. **which capture or native session produced each receipt**,
2. **which receipts are aligned enough to count as one session family**,
3. **which receipts are being compared across sessions**,
4. **and which public summaries are joining mixed sessions and therefore need disclosure**.

The archive already has capture-context truth and summary-claim traceability. The sharper move now is to keep **session honesty** explicit so public or frozen upgrade packs do not quietly launder cross-session synthesis into fake single-session certainty.

---
## Added 2026-03-20 (280): upgrade packs must keep public-shareable posture separate from silent sanitization

When future revisions sharpen **P-0514**, do not let the archive collapse these claims into one fake “now safe to publish” story:

1. **what private material existed** — local paths, internal package aliases, private registry locators, raw working notes, or similar workspace-private context;
2. **what transformation happened** — dropped, generalized, rewritten, split into private context, or otherwise bounded;
3. **what public surface depends on that transformation** — summary, recipe, manifest, or other exported entry surface;
4. **what review posture justified it** — manual review, dual review, or weaker schema-only posture.

Do not let a public-looking bundle imply that its cleanup is automatically trustworthy just because the exported files look clean.
The archive now has a distinct lane for the receiver-facing upgrade contract, and within that lane it must keep **public cleanliness** and **reviewable sanitization basis** separate.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs durable public cues

- Keep **durable public-cue truth** explicit alongside publication-surface manifests and public trace paths: a pack should say which blocking warnings, supersession states, deviations, freshness states, or manual-review boundaries remain visibly present on exported entry surfaces.
- Prefer one compact `durable-cue.report` rather than assuming warning labels, traceable receipts, or machine-readable registers are enough for a real reader.
- Treat “publicly traceable” and “durably visible” as adjacent but non-identical truths.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs lane-selection origin truth

- Keep **lane-selection truth** explicit alongside package-scope and coverage-matrix truth: a lane should say whether it came from a workspace root, explicit manifest path, ambient `default-members`, explicit `-p`, `--workspace`, or another normalized selection cause.
- Keep **ambient-selection warnings** explicit too: omitted sibling members or gated targets should stay visibly ambient/default-driven when that is the real reason they were not reviewed.
- Prefer one compact `lane-selection.receipt` rather than asking reviewers to infer scope intent from raw command lines and scattered capture receipts.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs public trace paths for exported claims

- Keep **public-trace-path truth** explicit alongside publication-surface exactness and summary-claim traceability: a frozen/public claim should say which exported route a reader can actually follow.
- Keep **typed public-trace misses** explicit too: fragment-missing, target-missing, and private-only failures should stay visibly about the public trace path instead of degrading into generic missing-ref prose.
- Prefer one compact `public-trace-path.report` rather than silently assuming that exported claims and exported files automatically compose into a usable public inspection route.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs exact capture context and sparse coverage matrices

- Keep **capture-context truth** explicit alongside native imports: a `cargo fix`, `cargo metadata`, or SemVer import should not outgrow the exact package/target/feature/toolchain/lockfile context that produced it.
- Keep **coverage-matrix truth** explicit alongside lane fidelity: mentioning touched dimensions is not the same thing as publishing exact observed, unknown, unsupported, or recipe-only cells.
- Prefer tiny receiver-facing artifacts such as `capture-context.receipt` and `coverage-matrix.report` rather than silently borrowing broader lane authority from narrower captures.

## 2026-03-19 refinement target — P-0509 needs freeze readiness, lock-in cost, and scope split before more adjacent discovery lanes

The next meaningful refinement for **P-0509** is not more abstract ranking theory.
It is a productized `0.1` that can emit:

- `starter-set-readiness.report.json`
- `lockin-cost.report.json`
- `scope-split.receipt.json`

and use those artifacts to keep “ranked highly”, “ready to freeze”, and “good for this scope” visibly separate.

## 2026-03-19 refinement — crate guidance-pack lane now has stronger message-stability and guidance-channel review objects

This pass did **not** promote another diagnostic renderer, another proc-macro helper, or another compile-fail harness.
It sharpened **P-0512 Crate Guidance Pack Kit** into a more buildable support-contract shape.

### Main judgment
- Treat `meta/crate-guidance-pack-product-plan-2026-03-19.md` as the working build sketch for **P-0512**.
- The key new planning detail is that a worthy guidance-support crate should publish explicit **message-stability**, **guidance-channel**, and **environment-sensitivity** artifacts rather than leaving those truths buried across compiler diagnostics, compile-fail fixtures, proc-macro helpers, and docs anchors.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s diagnostic namespace, rustdoc `compile_fail`, nightly doctest error-code checks, `trybuild`, `ui_test`, `miette`, and `proc-macro-error2` substrate.

### What to keep separate
- Keep **P-0512** separate from generic diagnostic rendering.
- Keep **P-0512** separate from docs portals and tutorial browsers.
- Keep **P-0512** separate from runtime failure handoff (**P-0513**).
- Keep **P-0512** separate from diagnosis-surface work (**P-0525**).
- Keep **P-0512** separate from test-surface work (**P-0523**): harnesses are substrate, not the whole support contract.

### Preferred proving grounds
- `trybuild` snapshots whose exact rendering changes when `rust-src` is present or absent
- nightly doctest error-code checks that prove a code class without proving exact wording
- proc-macro crates that advertise structured guidance but still panic in one misuse lane
- `miette` URLs that exist before the linked recovery recipe is actually witnessed

- `entries/2026-03-19-265.md` — guidance support deepened around message stability and guidance channels
- `meta/frontier-salience-2026-03-19-85.md` — fresh ranked frontier snapshot for compile-time / early-failure support after the authority pass
- `meta/crate-guidance-pack-product-plan-2026-03-19.md` — refreshed implementation-ready v0.1 sketch for P-0512
- `fixtures/crate-guidance-pack-kit/message-stability.report.schema.json` + `guidance-channel.receipt.schema.json` — schemas for exact-vs-shape stability and receiver-facing guidance transport
- `fixtures/crate-guidance-pack-kit/trybuild_rust_src_changes_rendering_without_changing_core_guidance/` + `nightly_doctest_error_code_is_code_level_not_message_level/` + `proc_macro_panics_bypass_guidance_channel/` + `miette_url_exists_but_recipe_witness_missing/` — scenario families for stderr-render drift, code-level doctest guarantees, proc-macro panic escape, and structured-diagnostic URL vs witnessed recipe boundaries

## 2026-03-19 refinement — crate authority-surface lane now has stronger origin/fallback/refusal review objects

This pass did **not** promote a new lane.
It sharpened **P-0519 Crate Authority Surface Pack Kit** into a more buildable support-contract shape.

### Main judgment
- Treat `meta/crate-authority-surface-product-plan-2026-03-19.md` as the working build sketch for **P-0519**.
- The key new planning detail is that a worthy authority-support crate should publish explicit **authority-origin**, **fallback-chain**, and **refusal-posture** artifacts rather than leaving those truths buried across README prose, capability APIs, and static-scan output.
- `0.1` should stay centered on `capture`, `check`, `doctor`, `diff`, `summary`, and `pack` workflows above today’s `ambient-authority`, `cap-std`, `cap_directories`, `cap-tempfile`, `getrandom`, Cargo env/build-script substrate, and `cargo_capsec` static scanning.

### What to keep separate
- Keep **P-0519** separate from task-first crate choice (**P-0509**).
- Keep **P-0519** separate from configuration/setup scenarios (**P-0516**).
- Keep **P-0519** separate from compile-time sandbox policy.
- Keep **P-0519** separate from capability-oriented runtime substrate and full sandbox platforms.
- Keep **P-0519** separate from generic static authority scanning: scan output is input, not the final product.

### Preferred proving grounds
- explicit tempdir handles that should beat ambient temp discovery
- project-dir denial that silently degrades into tempdir
- cache-root options that lose priority to `$HOME` or project-dir probing
- `getrandom` backend ownership that belongs in the root crate, not an upstream library

- `entries/2026-03-19-264.md` — authority support deepened around origin, fallback order, and refusal posture
- `meta/frontier-salience-2026-03-19-84.md` — fresh ranked frontier snapshot for adoption trust and sandbox-profile truth after the observability/performance passes
- `meta/crate-authority-surface-product-plan-2026-03-19.md` — refreshed implementation-ready v0.1 sketch for P-0519
- `fixtures/crate-authority-surface-pack-kit/authority-origin.receipt.schema.json` + `fallback-chain.report.schema.json` + `refusal-posture.report.schema.json` — schemas for origin truth, fallback-order truth, and denial behavior
- `fixtures/crate-authority-surface-pack-kit/caller_supplied_temp_dir_beats_ambient_temp_root/` + `project_dirs_denied_silently_falls_back_to_tempdir/` + `cache_root_option_loses_priority_to_home_discovery/` + `library_defines_getrandom_backend_instead_of_root_crate/` — scenario families for explicit capability preference, silent denial fallback, priority inversion in cache-root discovery, and root-crate ownership of entropy backends

## 2026-03-19 refinement — crate observability support now has a stronger implementation-ready `0.1` sketch

This pass did **not** promote another subscriber, another exporter, or another backend integration.
It sharpened **P-0518 Crate Observability Surface Pack Kit** around **bridge routes**, **activation truth**, and **sensitivity boundaries**.

### Main judgment
- Treat `meta/crate-observability-surface-product-plan-2026-03-19.md` as the working build sketch for **P-0518**.
- The key new planning detail is that a worthy observability-support crate should publish explicit **signal-stability**, **activation-recipe**, **bridge-route**, **schema-posture**, and **sensitivity-boundary** artifacts rather than leaving route truth buried across subscriber setup, exporter glue, and backend assumptions.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s `tracing`, `tracing-subscriber`, `console-subscriber`, and OpenTelemetry substrate.

### What to keep separate
- Keep **P-0518** separate from telemetry plumbing: subscribers, exporters, and collector setup are not the same lane as a receiver-facing support contract.
- Keep **P-0518** separate from **P-0525** diagnosis support: symptom triage is not the same lane as present-tense signal publication and route truth.
- Keep **P-0518** separate from **P-0517** performance-support contracts: benchmark budgets are not the same thing as emitted-signal promises.
- Keep **P-0518** separate from org/backend governance: platform-wide collector rules are not the same thing as one crate’s support story.

### Preferred proving grounds
- an advertised info-level signal hidden by the documented default filter posture
- a console recipe that requires Tokio `tracing` plus `tokio_unstable`
- an OpenTelemetry route claim where traces/metrics work but logs do not
- a semconv/schema upgrade that changes query expectations
- a payload-derived identifier that must be hashed, dropped, or marked manual-review territory

- `entries/2026-03-19-263.md` — crate observability support sharpened around bridge routes, activation truth, and sensitivity boundaries
- `meta/frontier-salience-2026-03-19-83.md` — fresh ranked frontier snapshot for emitted-signal support after the performance-support pass
- `meta/crate-observability-surface-product-plan-2026-03-19.md` — implementation-ready v0.1 sketch for P-0518
- `fixtures/crate-observability-surface-pack-kit/README.md` — root fixture framing for signal/activation/route/schema/sensitivity truth
- `fixtures/crate-observability-surface-pack-kit/bridge-route.receipt.schema.json` — schema for route truth across fmt/log, console, traces, metrics, and logs
- `fixtures/crate-observability-surface-pack-kit/env_filter_default_hides_advertised_signal/activation-recipe.receipt.example.json` + `console_recipe_requires_runtime_feature/activation-recipe.receipt.example.json` + `semconv_schema_upgrade_changes_query_surface/schema-convention.profile.example.json` — concrete examples for filter posture, runtime-specific activation, and schema/query drift
- `fixtures/crate-observability-surface-pack-kit/otel_bridge_route_drops_logs_without_explicit_appender/` + `untrusted_filter_input_requires_literal_mode_or_manual_review/` + `payload_derived_user_id_requires_hash_or_drop/` — scenario families for route truth, regex/input review boundaries, and sensitive payload posture

## 2026-03-19 refinement — crate performance-envelope lane now has a sharper implementation-ready contract

This pass did not add another benchmark runner or perf dashboard.
It sharpened **P-0517 Crate Performance Envelope Pack Kit** around **execution intent**, **workload lineage**, and **profile identity**.

- Treat `meta/crate-performance-envelope-product-plan-2026-03-19.md` as the working build sketch for **P-0517**.
- The key new planning detail is that a performance-envelope crate should publish explicit **execution-intent reports** and **workload-lineage receipts** alongside metric authority, environment fidelity, and noise classes.
- Keep **P-0517** separate from setup/configuration scenarios (**P-0516**).
- Keep **P-0517** separate from observability surfaces (**P-0518**).
- Keep **P-0517** separate from profiling bundles, benchmark frameworks, and hosted CI perf services.

## 2026-03-19 — persistence support is more useful when it says what path changed and what identity was lost

The latest pass should push **P-0522 Crate Persistence Surface Pack Kit** upward in seriousness.
The reason is not merely that formats and databases are everywhere.
It is that Rust now has enough substrate that the missing value is newly specific: one compact support contract for **publication target**, **identity retention**, **durability boundary**, **compatibility authority**, and **recovery witnesses**.

The sharp idea is **not** another serializer and **not** another “atomic write” helper.
It is one shared layer that can publish what object actually changed and what survived the change.

That makes **P-0522** a stronger Band A support-surface candidate than it looked when it was only a “durability docs would be nice” lane.

## Added 2026-03-19 (257)
- `entries/2026-03-19-257.md`
- `meta/frontier-salience-2026-03-19-77.md`
- `meta/crate-example-surface-product-plan-2026-03-19.md`
- `fixtures/crate-example-surface-pack-kit/README.md`
- `fixtures/crate-example-surface-pack-kit/cli_quickstart/quickstart-path.manifest.example.json`
- `fixtures/crate-example-surface-pack-kit/cli_quickstart/success-witness.receipt.example.json`
- `fixtures/crate-example-surface-pack-kit/async_client_happy_path/adoption-scenario.manifest.example.json`
- `fixtures/crate-example-surface-pack-kit/async_client_happy_path/example-environment.report.example.json`
- `fixtures/crate-example-surface-pack-kit/readme_quickstart_hidden_feature_origin/prerequisite-origin.receipt.example.json`
- `fixtures/crate-example-surface-pack-kit/dynamic_cli_output_normalization/example-normalization.profile.example.json`
- `fixtures/crate-example-surface-pack-kit/guide_book_plus_examples/docs-example-linkage.report.example.json`
- `fixtures/crate-example-surface-pack-kit/proc_macro_getting_started/example-output.report.example.json`
- `fixtures/crate-example-surface-pack-kit/embedded_no_std_demo/example-environment.report.example.json`
- `fixtures/crate-example-surface-pack-kit/credentialed_service_only_path_needs_scenario_honesty/scenario-coverage.report.example.json`
- `fixtures/crate-example-surface-pack-kit/scraped_example_present_but_no_official_success_witness/example-support-check.report.example.json`

It sharpened **P-0524 Crate Example Surface Pack Kit** into a more implementation-ready first-success support product.

Working notes:
- Treat `meta/crate-example-surface-product-plan-2026-03-19.md` as the current build sketch for **P-0524**.
- Keep **P-0524** separate from task-first crate choice (**P-0509**), downstream test surfaces (**P-0523**), tutorial publishing (`mdBook`), transcript tooling (`term_transcript` / `trycmd`), and project templating (`cargo-generate`).
- The center of gravity is now explicit **official quickstarts**, **prerequisite lineage**, **docs/example linkage**, **scenario coverage**, and **witnessed first success**.

## 2026-03-19 refinement — crate diagnosis support now has a fresher implementation-ready `0.1` sketch

This pass did **not** promote another logger, metrics exporter, debugger helper, or hosted support portal.
It sharpened **P-0525 Crate Diagnosis Surface Pack Kit** into a more buildable troubleshooting-support shape.

### Main judgment
- Treat `meta/crate-diagnosis-surface-product-plan-2026-03-19.md` as the working build sketch for **P-0525**.
- The key new planning detail is that a worthy diagnosis-support crate should publish explicit **symptom-taxonomy**, **triage-sequence**, **triage-origin**, **signal-map**, **support-capture / bundle-safety**, and **diagnosis-check / diff** artifacts rather than leaving support truth buried across docs, log filters, and issue folklore.
- `0.1` should stay centered on `init`, `check`, `doctor`, `capture`, `diff`, and `pack` workflows above today’s tracing, Tokio Console, metrics, `miette`, and `tracing-error` substrate.

### What to keep separate
- Keep **P-0525** separate from **P-0518** observability-surface contracts.
- Keep **P-0525** separate from **P-0513** runtime failure handoff bundles.
- Keep **P-0525** separate from **P-0486** debugger/symbol/visualizer posture.
- Keep **P-0525** separate from any hosted incident or support platform.

### Preferred proving grounds
- retry storms whose first-inspection path should split config, auth, and endpoint causes
- queue-growth symptoms that need runtime/metrics honesty rather than vague backlog lore
- local CLI stalls that need bounded, safe support bundles
- console guidance that is documented but not actually supported by the runtime
- capture recipes that would otherwise exfiltrate secret-shaped env/config values

- `entries/2026-03-19-256.md` — crate diagnosis support sharpened around symptom identity, first-inspection order, instrumentation honesty, and safe capture boundaries
- `meta/frontier-salience-2026-03-19-76.md` — fresh ranked frontier snapshot for top-band troubleshooting support
- `meta/crate-diagnosis-surface-product-plan-2026-03-19.md` — implementation-ready v0.1 sketch for P-0525
- `fixtures/crate-diagnosis-surface-pack-kit/retry_storm_client/triage-sequence.manifest.example.json` + `queue_growth_worker/signal-map.report.example.json` + `local_cli_startup_stall/support-capture.report.example.json` + `console_recipe_declared_but_runtime_not_instrumented/diagnosis-check.report.example.json` + `bundle_capture_exports_secret_shaped_env/bundle-safety.report.example.json` — scenario examples for first-inspection order, runtime-signal honesty, safe capture, and bundle safety

## 2026-03-19 refinement — public API readiness now has an implementation-ready `0.1` sketch

This pass did **not** promote another semver checker or another public-API diff engine.
It sharpened **P-0483 Public API Readiness Bundle Kit** into a more buildable release-review shape.

### Main judgment
- Treat `meta/public-api-readiness-product-plan-2026-03-19.md` as the working build sketch for **P-0483**.
- The key new planning detail is that a worthy public-release crate should publish explicit **public-surface**, **semver-verdict**, **public-dependency-boundary**, **docs-readiness**, **waiver-ledger**, and **release-readiness** artifacts rather than leaving public-contract truth buried across separate analyzer outputs and release PR discussion.
- `0.1` should stay centered on `capture`, `diff`, `gate`, `explain`, and `pack` workflows above today’s `cargo-public-api`, `cargo-semver-checks`, Cargo public-dependency work, rustc lints, and rustdoc JSON/coverage substrate.

### What to keep separate
- Keep **P-0483** separate from **P-0244** semver-break evidence and witness tooling.
- Keep **P-0483** separate from **P-0431** public/private dependency boundary classification and migration.
- Keep **P-0483** separate from **P-0451** item-level cfg/availability truth.
- Keep **P-0483** separate from generic docs dashboards or changelog automation.

### Preferred proving grounds
- a patch release that accidentally widens the public dependency boundary
- a minor release that adds public API but regresses public docs/examples
- an intended major break whose waiver/intent record has gone stale
- a crate where analyzer outputs conflict and `manual_review_required` is the only honest verdict

- `entries/2026-03-19-255.md` — public API readiness deepened around public-surface truth, boundary drift, docs readiness, and waiver posture
- `meta/frontier-salience-2026-03-19-75.md` — fresh ranked frontier snapshot for joined public-release review after the MCP/desktop/off-ramp passes
- `meta/public-api-readiness-product-plan-2026-03-19.md` — implementation-ready v0.1 sketch for P-0483
- `meta/public-api-readiness-lanes-2026-03-19.md` — amnesia-resistor note keeping semver evidence, public-dependency boundary work, item-level availability truth, and joined release readiness separate
- `fixtures/public-api-readiness-bundle-kit/public-surface.snapshot.schema.json` + `semver-verdict.report.schema.json` + `public-dependency-boundary.report.schema.json` + `docs-readiness.report.schema.json` + `waiver-ledger.receipt.schema.json` + `release-readiness.verdict.schema.json` — schemas for joined public-release review
- `fixtures/public-api-readiness-bundle-kit/scenarios/patch_release_accidental_public_dependency_leak/` + `minor_release_public_docs_regression/` + `intended_major_break_with_stale_waiver/` — scenario families for quiet public-boundary growth, docs-surface regression, and stale intent/waiver posture

## 2026-03-19 refinement — crate off-ramp now has an implementation-ready `0.1` sketch

This pass did **not** invent another advisory scanner or another maintenance-score dashboard.
It sharpened **P-0515 Crate Off-Ramp Pack Kit** into a more implementation-ready shape.

### Main shift

- The missing value for **P-0515** is no longer just “better deprecation messaging”.
- The sharper missing value is a receiver-facing contract that keeps **successor intent**, **stopgap horizons**, and **checked exit recipes** distinct.
- Real Rust substrate now exists below that layer: rustc deprecation signals, Cargo yank/update behavior, crates.io Security tabs, RustSec advisories, and visible docs.rs redirect-crate patterns.

### Immediate implications

- Keep **P-0515** separate from **P-0011 Crate Health**: broad governance posture is not the same lane as a checked exit path.
- Keep **P-0515** separate from advisory/outdated tooling: detectors are not successor plans.
- Keep **P-0515** separate from **P-0514**: leaving a crate is not the same as moving to the next release of the same crate.
- Treat renamed crates, advisory-driven stopgaps, successor splits, and no-successor retirements as the core proving grounds.

### What to watch next

Future passes in this area should ask whether the missing value is really about:

- successor-intent maps,
- stopgap-horizon receipts,
- checked exit recipes,
- crate health / governance,
- or advisory and outdated detection.

Do not let these drift back into one vague “maintenance support” bucket.

---
## 2026-03-19 refinement — text-input-kit now has an implementation-ready `0.1` sketch

This pass did **not** promote another layout engine or another generic GUI harness.
It sharpened **P-0027 text-input-kit** into a more buildable transaction/selection-support shape.

### Main judgment
- Treat `meta/text-input-kit-product-plan-2026-03-19.md` as the working build sketch for **P-0027**.
- The key new planning detail is that a worthy text-input crate should publish explicit **IME-transaction**, **selection-contract**, and **backend-capability** artifacts rather than leaving text-entry truth buried across toolkit code, platform quirks, and issue threads.
- `0.1` should stay centered on `replay`, `doctor`, `diff`, and `bundle` workflows above today’s `winit`, hidden-input web fallback, layout/editing substrate, and AccessKit text vocabulary.

### What to keep separate
- Keep **P-0027** separate from **P-0197** text layout/shaping correctness work.
- Keep **P-0027** separate from **P-0087** accessibility doctoring and release gating.
- Keep **P-0027** separate from **P-0202** platform capture/interop bundles.
- Keep **P-0027** separate from another full widget toolkit or editor framework.

### Preferred proving grounds
- a Windows preedit flow where plain key events leak and require explicit dedup logic
- a Web/WASM hidden-input flow where candidate anchoring or fullscreen behavior is approximate rather than native
- an emoji/ZWJ delete flow where scalar deletion corrupts a user-visible grapheme cluster
- a custom text widget that still needs honest value/selection export into accessibility layers

- `entries/2026-03-19-250.md` — text-input-kit deepened around IME transactions, selection truth, and backend capability receipts
- `meta/frontier-salience-2026-03-19-70.md` — fresh ranked frontier snapshot for text-input/product-engineering work after the accessibility-doctor pass
- `meta/text-input-kit-product-plan-2026-03-19.md` — implementation-ready v0.1 sketch for P-0027
- `meta/text-input-stack-boundaries-2026-03-19.md` — amnesia-resistor note keeping event ingress, transaction semantics, layout, accessibility export, and regression tooling separate
- `fixtures/text-input-kit/ime-transaction.report.schema.json` + `selection-contract.report.schema.json` + `backend-capability.receipt.schema.json` — schemas for transaction truth, selection truth, and adapter-capability honesty
- `fixtures/text-input-kit/scenarios/windows_preedit_keyboardinput_overlap_requires_dedup/` + `web_hidden_input_fullscreen_breaks_candidate_anchor/` + `emoji_zwj_backspace_breaks_grapheme_cluster_selection/` — scenario families for native overlap bugs, web fallback honesty, and grapheme-safe deletion

## 2026-03-19 refinement — UI Accessibility Doctor now has an implementation-ready `0.1` sketch

This pass did **not** promote another GUI framework or another generic testing harness.
It sharpened **P-0087 UI Accessibility Doctor Kit** into a more buildable support-contract shape.

### Main judgment
- Treat `meta/ui-accessibility-doctor-product-plan-2026-03-19.md` as the working build sketch for **P-0087**.
- The key new planning detail is that an accessibility doctor crate should publish explicit **semantic-contract**, **rule-authority**, and **baseline-drift** artifacts rather than leaving semantic truth buried across toolkit code, screenshots, and ad hoc manual review.
- `0.1` should stay centered on `inspect`, `doctor`, `diff`, `gate`, and `bundle` workflows above today’s AccessKit, `accesskit_winit`, toolkit integrations, and AccessKit-powered testing substrate.

### What to keep separate
- Keep **P-0087** separate from **P-0202** accessibility capture/interop bundles.
- Keep **P-0087** separate from another GUI framework or platform adapter.
- Keep **P-0087** separate from legal/compliance claims that the crate cannot honestly automate.
- Keep **P-0087** separate from lower-level text-input substrate work.

### Preferred proving grounds
- a dialog action that loses its accessible name
- a virtualized list whose node ids churn enough to invalidate clean diffs
- a custom/canvas text field that focuses correctly but still lacks value/selection semantics
- an icon-only control where tooltip-derived naming should stay manual-review territory

- `entries/2026-03-19-249.md` — UI Accessibility Doctor deepened around semantic contracts, rule authority, and baseline drift
- `meta/frontier-salience-2026-03-19-69.md` — fresh ranked frontier snapshot for end-user product engineering, accessibility supportiveness, and portfolio rebalance
- `meta/ui-accessibility-doctor-product-plan-2026-03-19.md` — implementation-ready v0.1 sketch for P-0087
- `fixtures/ui-accessibility-kit/semantic-contract.report.schema.json` + `rule-authority.policy.schema.json` + `baseline-drift.report.schema.json` — schemas for authoring-side semantic truth, explicit rule authority, and reviewable baseline drift
- `fixtures/ui-accessibility-kit/scenarios/virtualized_list_recycles_node_identity_and_breaks_diff/` + `icon_only_button_name_comes_from_tooltip_requires_manual_review/` + `canvas_textbox_reports_focus_but_not_value_or_selection/` — scenario families for identity churn, fragile name derivation, and text-input semantic underreporting

## 2026-03-18 refinement — Node-API package contract now has an implementation-ready `0.1` sketch

This pass did **not** promote a new generic JavaScript/FFI lane.
It sharpened **P-0498 Node-API Package & Prebuild Contract Kit** into a more buildable shipping-contract shape.

### Main judgment
- Treat `meta/node-api-package-prebuild-contract-product-plan-2026-03-18.md` as the working build sketch for **P-0498**.
- The key new planning detail is that a Node-API shipping crate should publish explicit **prebuild coverage**, **loader route**, and **publish identity** artifacts rather than leaving npm-native support truth buried across CI YAML, generated loaders, and package settings.
- `0.1` should stay centered on `inspect`, `matrix`, `check`, `diff`, and `bundle` workflows above today’s Node-API, `napi-rs`, package exports, and npm trusted-publishing substrate.

### What to keep separate
- Keep **P-0498** separate from another binding generator or package template.
- Keep **P-0498** separate from generic npm publishing bots or provenance verifiers.
- Keep **P-0498** separate from consumer-side doctoring (**P-0487**).
- Keep **P-0498** separate from cross-ecosystem foreign-package generalization.

### Preferred proving grounds
- a clean Node-only native prebuild matrix
- a musl tuple hidden behind local-build fallback
- a package using `node-addons` for native loading and `default` for WASM fallback
- a trusted-publisher release where strong provenance still does not settle Bun/Deno claims

- `entries/2026-03-18-242.md` — Node-API package contract deepened around prebuild coverage, loader routes, and publish identity
- `meta/frontier-salience-2026-03-18-62.md` — fresh ranked frontier snapshot for npm-native support truth above prebuild, loader, and publish-identity drift
- `meta/node-api-package-prebuild-contract-product-plan-2026-03-18.md` — implementation-ready v0.1 sketch for P-0498
- `fixtures/node-api-package-prebuild-contract-kit/prebuild-coverage.report.schema.json` + `loader-route.receipt.schema.json` + `publish-identity.report.schema.json` — schemas for shipped-tuple truth, actual loader routing, and trusted-publisher/provenance posture
- `fixtures/node-api-package-prebuild-contract-kit/scenarios/musl_gap_hidden_by_local_build_fallback/` + `node_addons_native_path_with_default_wasm_fallback/` + `trusted_publisher_provenance_present_but_manual_runtime_claims_still_need_review/` — scenario families for honest non-prebuilt gaps, explicit native/universal route splits, and release-identity-vs-runtime-claim boundaries

## 2026-03-18 refinement — Wasm component shipkit now has an implementation-ready `0.1` sketch

This pass did **not** promote a new broad Wasm lane.
It sharpened **P-0206 Wasm Component Contract & Conformance ShipKit** into a more buildable shipping-kit shape.

### Main judgment
- Treat `meta/wasm-component-artifact-conformance-product-plan-2026-03-18.md` as the working build sketch for **P-0206**.
- The key new planning detail is that a component shipping crate should publish explicit **tooling-lineage**, **world-lock**, and **composition-closure** artifacts rather than leaving component truth buried across target selection, WIT files, composition commands, and runtime folklore.
- `0.1` should stay centered on `inspect`, `lock`, `check`, `exercise`, `diff`, and `pack` workflows above today’s native targets, `cargo-component`, WAC, and Wasmtime substrate.

### What to keep separate
- Keep **P-0206** separate from a full Wasm runtime.
- Keep **P-0206** separate from a full registry/distribution platform.
- Keep **P-0206** separate from target/toolchain support contracts (**P-0484**).
- Keep **P-0206** separate from general Wasm portability/performance workbenches when the sharper need is still contract truth.

### Preferred proving grounds
- native `wasm32-wasip2` command components
- transitional `cargo-component` projects that still need explicit lineage honesty
- composition cases where package-version inference breaks interface matches
- components that build but still require host-supplied imports

- `entries/2026-03-18-241.md` — Wasm component shipkit deepened around tooling lineage, world locks, and composition closure
- `meta/frontier-salience-2026-03-18-61.md` — fresh ranked frontier snapshot for Wasm component contract truth above shifting tooling paths
- `meta/wasm-component-artifact-conformance-product-plan-2026-03-18.md` — implementation-ready v0.1 sketch for P-0206
- `fixtures/wasm-component-artifact-conformance-kit/tooling-lineage.report.schema.json` + `world-lock.report.schema.json` + `composition-closure.report.schema.json` — schemas for build/composition lineage, versioned world truth, and closure/runnability classification
- `fixtures/wasm-component-artifact-conformance-kit/scenarios/cargo_component_transitional_build_repacked_with_wac/` + `package_version_inference_breaks_interface_match/` + `native_wasip2_component_still_requires_host_supplied_imports/` — scenario families for transitional build honesty, version-shape mismatch, and “built but still open” closure truth

## 2026-03-18 refinement — Rust Android Mobile Kit now has an implementation-ready `0.1` sketch

This pass did **not** promote a new broad foreign-package lane.
It sharpened **P-0168 Rust Android Mobile Kit** into a more buildable shipping-kit shape.

### Main judgment
- Treat `meta/rust-android-mobile-kit-product-plan-2026-03-18.md` as the working build sketch for **P-0168**.
- The key new planning detail is that an Android shipping crate should publish explicit **ABI coverage**, **load-doctor policy**, and **page-size compatibility** artifacts rather than leaving Android readiness buried across NDK env setup, packaging scripts, and app-integration folklore.
- `0.1` should stay centered on `init`, `build`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s `cargo-ndk`, UniFFI, AAR, and JNI substrate.

### What to keep separate
- Keep **P-0168** separate from a full Android UI/app framework.
- Keep **P-0168** separate from generic project generation or full mobile-stack replacement.
- Keep **P-0168** separate from whole-project Rust toolchain support (**P-0484**).
- Keep **P-0168** separate from generic foreign-package contract vocabulary across every ecosystem.

### Preferred proving grounds
- JNI library copied into `jniLibs/` for a normal Android app
- UniFFI-generated Kotlin bindings that still need honest packaging status
- AAR-shipped Rust library with native-library collision risk
- a release gate where 16 KB page-size readiness is visible and diffable

- `entries/2026-03-18-238.md` — crate ecosystem pathfinder deepening around evidence origin, freshness windows, and starter-set scope
- `meta/frontier-salience-2026-03-18-58.md` — fresh ranked frontier snapshot for provenance-aware, freshness-aware, scope-aware crate choice
- `meta/epic-crate-portfolio-2026-03-18.md` — portfolio map for what should count as worthy or epic crate work across the archive
- `fixtures/crate-ecosystem-pathfinder-kit/evidence-origin.report.schema.json` + `freshness-window.policy.schema.json` + `starter-set-scope.report.schema.json` — schemas for recommendation provenance, freshness gating, and starter-set scope truth
- `fixtures/crate-ecosystem-pathfinder-kit/pubtime_cooldown_prevents_fresh_release_overpromotion/` + `docsrs_default_target_shift_changes_visible_support_story/` + `trusted_publishing_and_security_tab_do_not_equal_task_fit/` — new fixture families for publish-cooldown honesty, docs-visibility drift, and trust-signal-vs-fit boundaries

## 2026-03-18 refinement — crate ecosystem pathfinder lane now has stronger provenance / freshness / scope review objects

This pass did **not** promote a new lane.
It sharpened **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** into a more reviewable shape.

### Main judgment
- Treat `meta/crate-ecosystem-pathfinder-product-plan-2026-03-19.md` as the working build sketch for **P-0509**.
- The key new planning detail is that a pathfinder crate should now publish explicit **evidence-origin reports**, **freshness-window policies**, and **starter-set-scope reports** rather than leaving authority, recency, and audience half-implied across crates.io metadata, docs.rs visibility, registry security signals, and maintainer folklore.
- `0.1` should stay centered on `init`, `import`, `explain`, `freeze`, `diff`, and `bundle` workflows above today’s registry/docs/trust/health substrate.

### What to keep separate
- Keep **P-0509** separate from **P-0011 Crate Health**.
- Keep **P-0509** separate from **P-0017 Trust Lens**.
- Keep **P-0509** separate from docs.rs parity or toolchain-target support contracts.
- Keep **P-0509** separate from global ranking or official-blessing debates.

### Preferred proving grounds
- recently published crates that look promising but are still inside a review window
- lanes where docs.rs visible support changed because target defaults changed
- lanes where stronger supply-chain posture still does not settle role coverage or interop fit
- teams that need separate teaching, production, and org-policy starter-set answers

- `entries/2026-03-17-236.md` — crate persistence-surface deepening sharpened around compatibility authority, atomicity scope, and recovery witnesses
- `meta/frontier-salience-2026-03-17-56.md` — fresh ranked frontier snapshot for trusted compatibility meaning, exact atomicity scope, and recovery-witness truth
- `fixtures/crate-persistence-surface-pack-kit/compatibility-authority.policy.schema.json` + `atomicity-scope.report.schema.json` + `recovery-witness.receipt.schema.json` — schemas for compatibility-authority meaning, atomicity-scope truth, and declared-versus-witnessed recovery evidence
- `fixtures/crate-persistence-surface-pack-kit/atomic_no_intermediate_state_mistaken_for_power_loss_durability/` + `postcard_stable_wire_claim_vs_serde_shape_guard/` + `repair_path_documented_but_unwitnessed_for_current_surface/` — new fixture families for atomicity-vs-durability drift, stable-wire-authority honesty, and recovery-witness gaps

## 2026-03-17 refinement — crate persistence-surface lane now has stronger compatibility-authority / atomicity-scope / recovery-witness review objects

This pass did **not** promote a new lane.
It sharpened **P-0522 Crate Persistence Surface Pack Kit** into a more reviewable shape.

### Main judgment
- Treat `meta/crate-persistence-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0522**.
- The key new planning detail is that a persistence-surface crate should now publish explicit **compatibility-authority policies**, **atomicity-scope reports**, and **recovery-witness receipts** rather than leaving durable-byte truth half-implied across file helpers, serializer lore, engine docs, and maintainer memory.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s file, serializer, format, and storage-engine substrate.

### What to keep separate
- Keep **P-0522** separate from serializer/storage-engine substrate.
- Keep **P-0522** separate from upgrade packs (**P-0514**).
- Keep **P-0522** separate from lifecycle/resource/authority surfaces (**P-0520** / **P-0521** / **P-0519**).
- Keep **P-0522** separate from async file wrappers or convenience I/O layers.

### Preferred proving grounds
- config-file crates that mix Serde compatibility knobs with stronger or weaker format promises
- durable local-state crates using temp-file replacement or journal/transaction paths
- SDK/client crates that cache credentials, cursors, or snapshots across releases
- embedded-store adapters whose recovery story differs between crash recovery and external corruption/repair


- `entries/2026-03-17-234.md` — crate example-surface planning sharpened around prerequisite provenance, success witnesses, and scenario coverage
- `meta/frontier-salience-2026-03-17-54.md` — fresh ranked frontier snapshot for first-success contracts, prerequisite truth, and witnessed quickstarts
- `fixtures/crate-example-surface-pack-kit/prerequisite-origin.receipt.schema.json` + `success-witness.receipt.schema.json` + `scenario-coverage.report.schema.json` — schemas for prerequisite provenance, witnessed quickstart success, and scenario-by-scenario coverage honesty
- `fixtures/crate-example-surface-pack-kit/readme_quickstart_hidden_feature_origin/` + `scraped_example_present_but_no_official_success_witness/` + `credentialed_service_only_path_needs_scenario_honesty/` — new fixture families for hidden prerequisite origins, scraped-example-vs-official-start drift, and honest scenario gaps

## 2026-03-17 refinement — crate example-surface lane now has stronger first-success review objects

This pass did **not** promote a new lane.
It sharpened **P-0524 Crate Example Surface Pack Kit** into a more reviewable shape.

### Main judgment
- Treat `meta/crate-example-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0524**.
- The key new planning detail is that an example-surface crate should publish explicit **prerequisite-origin receipts**, **success-witness receipts**, and **scenario-coverage reports** rather than leaving first-success truth buried across README prose, docs.rs metadata, examples folders, or “works for me” maintainer memory.
- `0.1` should now stay centered on `init`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s README/rustdoc/examples/docs.rs/test substrate.

### What to keep separate
- Keep **P-0524** separate from project templating (`cargo-generate`).
- Keep **P-0524** separate from tutorial publishing (`mdBook`).
- Keep **P-0524** separate from transcript or snapshot tooling (`trycmd`, `term-transcript`, `skeptic`).
- Keep **P-0524** separate from docs.rs hosting/parity work (**P-0472**).

### Preferred proving grounds
- CLI crates with README command snippets and normalized success witnesses
- SDK/client crates where local/loopback starts differ from real credentialed paths
- embedded or `no_std` crates that may need explicit scenario-gap honesty
- guide-heavy crates whose README/rustdoc/book/examples surfaces can drift apart


- `entries/2026-03-17-232.md` — crate guidance-pack planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-guidance-pack-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0512
- `meta/frontier-salience-2026-03-17-52.md` — fresh ranked frontier snapshot for guidance authority, recovery provenance, and checked recipe fidelity
- `fixtures/crate-guidance-pack-kit/guidance-authority.policy.schema.json` + `recovery-origin.receipt.schema.json` + `recipe-fidelity.report.schema.json` — schemas for exact-vs-advisory guidance meaning, recovery-hint provenance, and recipe fidelity
- `fixtures/crate-guidance-pack-kit/compile_fail_doctest_catches_failure_but_not_message_drift/` + `do_not_recommend_hides_blanket_impl_but_recipe_missing/` + `proc_macro_diagnostic_url_points_to_stale_syntax/` — new fixture families for failure-only docs checks, suppressed-bad-hint without smallest path, and proc-macro anchor drift

## 2026-03-17 refinement — crate guidance-pack lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0512 Crate Guidance Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-guidance-pack-product-plan-2026-03-17.md` as the working build sketch for **P-0512**.
- The key new planning detail is that a guidance-pack crate should publish explicit **guidance-authority policy**, **recovery-origin receipts**, and **recipe-fidelity reports** rather than leaving compile-time help buried across diagnostic attributes, compile-fail fixtures, docs examples, and maintainer memory.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s compiler-diagnostic, rustdoc, and compile-fail harness substrate.

### What to keep separate
- Keep **P-0512** separate from generic diagnostic rendering.
- Keep **P-0512** separate from docs portals and tutorial browsers.
- Keep **P-0512** separate from runtime failure handoff (**P-0513**).
- Keep **P-0512** separate from pathfinder / crate-choice work (**P-0509**).

### Preferred proving grounds
- trait-heavy libraries
- proc-macro crates
- feature-rich async/framework crates
- target/cfg-limited crates
- docs-heavy crates whose compile-fail examples and recipes can drift apart


- `entries/2026-03-17-231.md` — crate runtime-handoff planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-runtime-handoff-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0513
- `fixtures/crate-runtime-handoff-pack-kit/capture-exactness.policy.schema.json` + `share-safety.receipt.schema.json` + `handoff-fidelity.report.schema.json` — schemas for runtime-capture exactness, safe-to-share classification, and post-failure bundle fidelity
- `fixtures/crate-runtime-handoff-pack-kit/error_stack_attachment_secret_needs_hash_redaction/` + `spantrace_declared_but_error_layer_missing/` + `panic_hook_present_but_report_bundle_path_missing/` — new fixture families for attachment redaction, unsupported async-context drift, and panic-hook artifact-path honesty

## 2026-03-17 refinement — crate runtime-handoff lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0513 Crate Runtime Handoff Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-runtime-handoff-product-plan-2026-03-17.md` as the working build sketch for **P-0513**.
- The key new planning detail is that a runtime-handoff crate should publish explicit **capture-exactness policy**, **share-safety receipts**, and **handoff-fidelity reports** rather than leaving post-failure truth buried across panic hooks, ad hoc log dumps, report files, and issue-template prose.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s error, panic, attachment, and span-context substrate.

### What to keep separate
- Keep **P-0513** separate from compile-time guidance (**P-0512**).
- Keep **P-0513** separate from generic report rendering.
- Keep **P-0513** separate from tracing / observability platforms.
- Keep **P-0513** separate from hosted crash collectors or domain-specific incident bundles.

### Preferred proving grounds
- CLI tools with custom panic hooks or user-submittable report files
- async services where span traces matter more than raw executor stacks
- library crates using attachment-heavy runtime errors
- privacy-sensitive applications where config/env/user identifiers must not leak into public support bundles
- framework crates whose runtime support story still lives mostly in issue comments


- `entries/2026-03-17-227.md` — crate configuration-scenario planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-configuration-scenario-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0516
- `fixtures/crate-configuration-scenario-pack-kit/scenario-class.policy.schema.json` + `config-origin.receipt.schema.json` + `matrix-fidelity.report.schema.json` — schemas for scenario-class meaning, setup-fact provenance, and claimed-matrix fidelity
- `fixtures/crate-configuration-scenario-pack-kit/docsrs_all_features_vs_minimal_default/` + `tls_backends_compile_together_but_policy_picks_one/` + `no_std_builds_but_examples_need_std/` — new fixture families for docs.rs/default drift, backend-choice policy, and `no_std`-versus-example honesty

## 2026-03-17 refinement — crate configuration-scenario lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0516 Crate Configuration Scenario Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-configuration-scenario-product-plan-2026-03-17.md` as the working build sketch for **P-0516**.
- The key new planning detail is that a configuration-scenario crate should publish explicit **scenario-class policy**, **config-origin receipts**, and **matrix-fidelity reports** rather than leaving setup truth buried across features, docs.rs metadata, examples, and README prose.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s Cargo/docs.rs feature and metadata substrate.

### What to keep separate
- Keep **P-0516** separate from task-first crate choice (**P-0509**).
- Keep **P-0516** separate from docs.rs parity / hosting work (**P-0472**).
- Keep **P-0516** separate from feature-doc renderers and powerset executors.
- Keep **P-0516** separate from generic Cargo config-precedence explanation.

### Preferred proving grounds
- crates with runtime or TLS backend choices
- crates with `no_std` / `alloc` lanes whose examples or docs skew toward `std`
- crates whose docs.rs configuration materially widens the docs surface
- workspaces where official setup depends on `required-features`-gated examples or bins


- `entries/2026-03-17-226.md` — memory-observability planning sharpened into an implementation-ready v0.1 shape
- `meta/memory-observability-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0084
- `fixtures/memory-observability-kit/capture-scope.policy.schema.json` + `symbolization-fidelity.report.schema.json` + `regression-gate.policy.schema.json` — schemas for capture boundaries, symbolization trust, and release-gate posture
- `fixtures/memory-observability-kit/alloc_count_flat_but_peak_rss_regresses/` + `dhat_scope_guard_ends_before_background_phase/` + `jemalloc_stats_present_but_callsite_attribution_missing/` — new fixture families for RSS-vs-count drift, scope-boundary blind spots, and backend-capability honesty

## 2026-03-17 refinement — memory-observability lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0084 Memory Observability Kit** into a more buildable shape.

### Main judgment
- Treat `meta/memory-observability-product-plan-2026-03-17.md` as the working build sketch for **P-0084**.
- The key new planning detail is that a memory-observability crate should publish explicit **capture-scope policy**, **symbolization-fidelity reports**, and **regression-gate policy** artifacts rather than leaving memory evidence buried across profiler invocations, heap dumps, and screenshots.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s allocator-tracing, scoped heap-profiling, and allocator-introspection substrate.

### What to keep separate
- Keep **P-0084** separate from crate-authored resource-surface contracts (**P-0521**).
- Keep **P-0084** separate from workload/metric authority packs (**P-0517**).
- Keep **P-0084** separate from generic observability-surface contracts (**P-0518**).
- Keep **P-0084** separate from hosted profiler platforms and allocator-selection crates.

### Preferred proving grounds
- services with RSS regressions but stable alloc-count totals
- async systems whose interesting memory phase starts after the obvious request scope
- jemalloc-based systems with stats visibility but weak attribution
- redaction-sensitive incident handoff where raw paths or symbols cannot leave the box


- `entries/2026-03-17-225.md` — crate authority-surface planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-authority-surface-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0519
- `fixtures/crate-authority-surface-pack-kit/authority-budget.policy.schema.json` + `injection-boundary.receipt.schema.json` + `profile-witness.report.schema.json` — schemas for authority-budget meaning, injection-boundary truth, and restricted-profile witnesses
- `fixtures/crate-authority-surface-pack-kit/env_or_home_cache_fallback_breaks_offline_profile/` + `seeded_rng_but_system_clock_still_leaks_nondeterminism/` + `cap_std_dir_profile_blocks_absolute_path_escape/` — new fixture families for env/home fallback drift, clock-leak nondeterminism, and capability-profile absolute-path escapes

## 2026-03-17 refinement — crate authority-surface lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0519 Crate Authority Surface Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-authority-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0519**.
- The key new planning detail is that an authority-surface crate should publish explicit **authority-budget policy**, **injection-boundary receipts**, and **profile-witness reports** rather than leaving ambient-power and determinism posture buried across READMEs, code examples, and crate docs.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s capability, sandbox, and explicit-handle substrate.

### What to keep separate
- Keep **P-0519** separate from task-first crate choice (**P-0509**).
- Keep **P-0519** separate from configuration/setup scenarios (**P-0516**).
- Keep **P-0519** separate from compile-time sandbox policy.
- Keep **P-0519** separate from capability-oriented runtime substrate and full sandbox platforms.

### Preferred proving grounds
- parser/config crates with env or `$HOME` fallback behavior
- SDK/client crates claiming offline or deterministic modes
- plugin/runtime helpers with host-supplied capability handles
- WASI/capability-oriented crates with absolute-path escape risk
- regulated or safety-sensitive components where authority drift matters


- `entries/2026-03-17-224.md` — crate ecosystem pathfinder planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-ecosystem-pathfinder-product-plan-2026-03-19.md` — concrete command/artifact/adoption plan for P-0509
- `fixtures/crate-ecosystem-pathfinder-kit/evidence-weight.policy.schema.json` + `role-coverage.report.schema.json` + `decision-axis.report.schema.json` — schemas for weight/veto policy, task-role coverage, and separated decision axes
- `fixtures/crate-ecosystem-pathfinder-kit/async_http_service_tokio_lockin_tradeoff/` + `cli_baseline_newcomer_vs_power_stack/` + `embedded_no_std_alloc_split/` + `manual_review_required_conflicting_signals/` — new fixture families for runtime lock-in tradeoffs, onboarding-vs-power defaults, embedded constraint splits, and honest ambiguity

## 2026-03-17 refinement — crate ecosystem pathfinder lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** into a more implementation-ready `0.1` shape.

Treat `meta/crate-ecosystem-pathfinder-product-plan-2026-03-19.md` as the working build sketch for **P-0509**.
Use it when future passes need to decide what the crate should actually do before drifting back into vague “better discoverability” language.

- `entries/2026-03-17-223.md` — crate performance-envelope planning sharpened into an implementation-ready v0.1 shape
- `entries/2026-03-19-262.md` — crate performance support sharpened around execution intent, workload lineage, and profile identity
- `meta/crate-performance-envelope-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0517
- `fixtures/crate-performance-envelope-pack-kit/metric-authority.policy.schema.json` + `environment-fidelity.receipt.schema.json` + `noise-class.report.schema.json` — schemas for metric authority, environment fidelity, and confidence/noise posture
- `fixtures/crate-performance-envelope-pack-kit/release_claim_measured_with_bench_profile/` + `instruction_count_ci_authoritative_not_walltime/` + `compat_layer_skips_local_benchmark_semantics/` — new fixture families for profile-fidelity drift, CI instruction authority, and compatibility-layer semantic gaps

## 2026-03-17 refinement — crate performance-envelope lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0517 Crate Performance Envelope Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-performance-envelope-product-plan-2026-03-17.md` as the working build sketch for **P-0517**.
- The key new planning detail is that a performance-envelope crate should publish explicit **metric-authority policy**, **environment-fidelity receipts**, and **noise-class reports** rather than leaving benchmark honesty buried across profile defaults, runner quirks, CI imports, and chart screenshots.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s Cargo / Criterion / Iai / Divan / CodSpeed substrate.

### What to keep separate
- Keep **P-0517** separate from setup/configuration scenarios (**P-0516**).
- Keep **P-0517** separate from observability surfaces (**P-0518**).
- Keep **P-0517** separate from profiling bundles and generic benchmark frameworks.
- Keep **P-0517** separate from hosted CI perf services.

### Preferred proving grounds
- CLI crates with cold-start and binary-size posture
- parser/serializer crates with small-input latency versus throughput tradeoffs
- crates using Iai-Callgrind for CI-stable instruction budgets
- crates layering CodSpeed on top of Criterion or Divan benches
- frameworks whose default profile or adapter choice changes what users should trust


- `entries/2026-03-17-221.md` — crate lifecycle-surface planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-lifecycle-surface-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0520
- `fixtures/crate-lifecycle-surface-pack-kit/activation-boundary.policy.schema.json` + `stop-semantics.receipt.schema.json` + `teardown-evidence.report.schema.json` — schemas for activation meaning, stop-behavior truth, and cleanup evidence
- `fixtures/crate-lifecycle-surface-pack-kit/lazy_background_worker_starts_on_first_request/` + `join_handle_drop_detaches_background_task/` + `protocol_writer_requires_shutdown_not_drop/` — new fixture families for lazy start boundaries, detach-on-drop truth, and protocol shutdown evidence

## 2026-03-17 refinement — crate lifecycle-surface lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0520 Crate Lifecycle Surface Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-lifecycle-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0520**.
- The key new planning detail is that a lifecycle-surface crate should publish explicit **activation-boundary policy**, **stop-semantics receipts**, and **teardown-evidence reports** rather than leaving startup/stop truth buried across Tokio docs, examples, and issue threads.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s async shutdown substrate.

### What to keep separate
- Keep **P-0520** separate from runtime failure handoff (**P-0513**).
- Keep **P-0520** separate from observability contracts (**P-0518**).
- Keep **P-0520** separate from authority posture (**P-0519**).
- Keep **P-0520** separate from graceful-shutdown frameworks and structured-concurrency substrate.

### Preferred proving grounds
- client crates with lazy reconnect or subscription workers
- stream / protocol crates with `flush` / `shutdown` obligations
- watcher crates with drop-versus-detach ambiguity
- blocking bridge crates where async abort is not enough
- service crates using `CancellationToken` + `TaskTracker` to prove drain completion


- `entries/2026-03-17-220.md` — cfg availability-ledger planning sharpened into an implementation-ready v0.1 shape
- `meta/cfg-availability-ledger-product-plan-2026-03-17.md` — concrete command/artifact/fidelity plan for P-0451
- `fixtures/cfg-availability-ledger-kit/availability-class.policy.schema.json` + `availability-origin.receipt.schema.json` + `matrix-fidelity.report.schema.json` — schemas for availability-class meaning, origin receipts, and matrix fidelity
- `fixtures/cfg-availability-ledger-kit/cfg_doc_visible_but_doctest_and_downstream_use_fail/` + `docsrs_custom_cfg_exposes_docs_only_api_slice/` + `minor_release_moves_public_item_behind_feature/` — new fixture families for docs-only visibility, docs.rs-only slices, and semver-sensitive feature drift

## 2026-03-17 refinement — cfg availability ledger lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0451 Cfg Availability Ledger Kit** into a more buildable shape.

### Main judgment
- Treat `meta/cfg-availability-ledger-product-plan-2026-03-17.md` as the working build sketch for **P-0451**.
- The key new planning detail is that an availability-ledger crate should publish explicit **availability-class policy**, **origin receipts**, and **matrix-fidelity reports** rather than leaving conditional API truth buried across source `cfg`s, rustdoc markers, docs.rs metadata, and feature tables.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s rustdoc / docs.rs / Cargo substrate.

### What to keep separate
- Keep **P-0451** separate from whole-project support contracts (**P-0484**).
- Keep **P-0451** separate from docs.rs parity / replay bundles (**P-0472**).
- Keep **P-0451** separate from producer-side capability summaries (**P-0510**).
- Keep **P-0451** separate from generic public-API / SemVer slice tools and raw rustdoc-JSON helpers.

### Preferred proving grounds
- feature-heavy crates with optional-dependency indirection
- platform-heavy crates with `unix` / `windows` / `wasm32` surfaces
- crates using `#[cfg(doc)]` or `#[cfg(docsrs)]` to improve docs discoverability
- docs.rs metadata profiles with custom features or rustc cfgs
- releases where public items quietly move behind features


- `entries/2026-03-17-219.md` — crate observability-surface planning sharpened into an implementation-ready v0.1 shape
- `meta/crate-observability-surface-product-plan-2026-03-17.md` — concrete command/artifact/adoption plan for P-0518
- `fixtures/crate-observability-surface-pack-kit/signal-stability.policy.schema.json` + `activation-recipe.receipt.schema.json` + `schema-convention.profile.schema.json` — schemas for stability meaning, actual activation requirements, and semantic-convention/schema posture
- `fixtures/crate-observability-surface-pack-kit/env_filter_default_hides_advertised_signal/` + `console_recipe_requires_runtime_feature/` + `semconv_schema_upgrade_changes_query_surface/` — new fixture families for filter-gated visibility, runtime-specific console recipes, and query-surface drift under schema changes

## 2026-03-17 refinement — crate persistence-surface lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0522 Crate Persistence Surface Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-persistence-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0522**.
- The key new planning detail is that a persistence-surface crate should publish explicit **contract-level policy**, **write-path receipts**, and **failure-model profiles** rather than leaving durable-byte promises buried across README prose, file helpers, serializer knobs, and storage-engine docs.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s serde / file / storage substrate.

### What to keep separate
- Keep **P-0522** separate from release-to-release upgrade packs (**P-0514**).
- Keep **P-0522** separate from setup/configuration scenario packs (**P-0516**).
- Keep **P-0522** separate from lifecycle/resource/authority surface packs (**P-0520** / **P-0521** / **P-0519**).
- Keep **P-0522** separate from serializers, embedded stores, migration frameworks, and domain-specific schema workbenches.

### Preferred proving grounds
- Serde-backed config crates with renamed/defaulted/unknown-field evolution.
- Temp-file replacement saves where replacement semantics and durability guarantees differ.
- Embedded stores with automatic unclean-shutdown recovery but weaker external-corruption guarantees.
- Stable wire/export formats with explicit compatibility windows.
- Rebuildable caches that must be demoted from public-contract status.

## 2026-03-17 refinement — toolchain/target support lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0484 Toolchain & Target Support Contract Kit** into a more buildable shape.

### Main judgment
- Treat `meta/toolchain-target-support-product-plan-2026-03-17.md` as the working build sketch for **P-0484**.
- The key new planning detail is that a toolchain-support crate should publish explicit **support-class policy**, **support-evidence provenance**, and **external-prerequisite manifests** rather than leaving “supported target” claims buried across files and folklore.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s rustup / Cargo / docs.rs substrate.

### What to keep separate
- Keep **P-0484** separate from docs.rs parity replay and issue bundles (**P-0472**).
- Keep **P-0484** separate from item-level cfg/API availability truth (**P-0451**).
- Keep **P-0484** separate from linker-lane diagnosis and native-build doctor crates.
- Keep **P-0484** separate from MSRV-only tools and from generic CI orchestration.

### Preferred proving grounds
- Cross-platform libraries with implicit docs.rs target posture.
- Cross-compiled apps where the Rust target is installed but the linker/SDK is still missing.
- Virtual workspaces with `resolver = "3"` and mixed `rust-version` policies.
- Embedded/device-aware crates with runner or board-only truth.
- Path-toolchain projects where `components`, `targets`, and `profile` in the file do **not** actually apply.

## 2026-03-17 refinement — toolchain/target support deepened with override lineage, component availability, and exercise scope

This pass did **not** promote a new lane.
It sharpened **P-0484 Toolchain & Target Support Contract Kit** further.

### Main judgment
- Keep **override-lineage receipts**, **component-availability reports**, and **exercise-scope reports** separate from the earlier support-class, evidence, and prerequisite artifacts.
- Requested toolchains, effective toolchains, requested components, available components, and exercised scopes should not collapse into one fake support verdict.
- `0.1` should keep compile/docs/run/test/bench and host-helper lanes separately reviewable rather than quietly upgrading compile success into full target support.

### What to keep separate
- Keep **P-0484** separate from docs.rs parity replay and issue bundles (**P-0472**).
- Keep **P-0484** separate from item-level cfg/API availability truth (**P-0451**).
- Keep **P-0484** separate from linker-lane diagnosis and native-build doctor crates.
- Keep **P-0484** separate from MSRV-only tools and from generic CI orchestration.

### Preferred proving grounds
- contributor shells that export `RUSTUP_TOOLCHAIN` and silently mask repository pins
- nightly-based projects that depend on components with uneven availability
- cross-target builds that compile but cannot run tests without a runner
- builds where `--target` splits host build-script / proc-macro scope from target-lane flags
- path-toolchain projects where `components`, `targets`, and `profile` in the file do **not** actually apply

## 2026-03-17 refinement — crate diagnosis-surface lane now has sharper support-surface boundaries

This pass did **not** promote a new lane.
It sharpened **P-0525 Crate Diagnosis Surface Pack Kit** by separating class meaning, triage provenance, and bundle safety more explicitly.

### Main judgment
- Treat `meta/crate-support-surface-boundaries-2026-03-17.md` as the amnesia resistor for the adjacent support-surface cluster.
- Treat `symptom-class.policy`, `triage-origin.receipt`, and `bundle-safety.report` as the new diagnosis-specific review objects that keep troubleshooting support conservative.
- Keep diagnosis support centered on symptoms, first-inspection order, and safe bundle posture rather than magical auto-root-cause claims.

### What to keep separate
- Keep **P-0525** separate from **P-0512** compile-time recovery recipes.
- Keep **P-0525** separate from **P-0513** runtime failure handoff bundles.
- Keep **P-0525** separate from **P-0518** emitted-signal contracts.
- Keep **P-0525** separate from **P-0524** first-success example paths.

### Preferred proving grounds
- tokio-console guidance that exists in docs but not in real runtime instrumentation
- timeout buckets that should split into separate symptom classes
- support-bundle recipes that still leak secret-shaped values

## 2026-03-17 refinement — crate diagnosis-surface lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0525 Crate Diagnosis Surface Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-diagnosis-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0525**.
- The key new planning detail is that a diagnosis-surface crate should publish explicit **symptom-taxonomy**, **triage-sequence**, and **capture-policy** artifacts rather than leaving troubleshooting support buried in prose.
- `0.1` should stay centered on `init`, `check`, `triage`, `summary`, `diff`, and conservative `bundle` workflows above today’s diagnostics substrate.

### What to keep separate
- Keep **P-0525** separate from generic tracing / metrics plumbing.
- Keep **P-0525** separate from debugger or tokio-console-specific tooling.
- Keep **P-0525** separate from pretty diagnostic renderers like `miette` and error-context helpers like `tracing-error`.
- Keep **P-0525** separate from hosted incident or support platforms.

### Preferred proving grounds
- Async client crates with `request_hang` versus `retry_storm` ambiguity.
- Queue / worker crates with `queue_growth` versus starvation distinctions.
- CLI crates with bounded dry-run and config-sanity checks.
- SDK crates with auth-drift versus endpoint-mismatch boundaries.
- Embedded / device-aware crates with explicit board-only capture honesty.

## 2026-03-17 refinement — crate example-surface lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0524 Crate Example Surface Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-example-surface-product-plan-2026-03-17.md` as the working build sketch for **P-0524**.
- The key new planning detail is that an example-surface crate should publish **normalization profiles** for dynamic output rather than quietly burying unstable quickstarts in snapshot magic.
- `0.1` should stay centered on `init`, `check`, `summary`, `diff`, and `pack` workflows above existing docs/example/test substrate.

### What to keep separate
- Keep **P-0524** separate from project templating (`cargo-generate`).
- Keep **P-0524** separate from tutorial publishing (`mdBook`).
- Keep **P-0524** separate from transcript or snapshot tooling (`trycmd`, `term-transcript`, `skeptic`).
- Keep **P-0524** separate from docs.rs hosting/parity work (**P-0472**).

### Preferred proving grounds
- CLI crates with dynamic output that needs reviewable normalization.
- Guide-heavy crates with README + mdBook + `examples/` drift risk.
- Async SDKs with local versus credentialed starts.
- Embedded / `no_std` crates with board-only honesty.
- Proc-macro crates with compile-success plus compile-fail pairing.

## Update 2026-03-17 (211) — crate diagnosis-surface lane

- Treat **P-0525 Crate Diagnosis Surface Pack Kit** as the current sharpest missing receiver-facing troubleshooting-support lane above diagnostics substrate and below full support platforms.
- Prefer tiny receiver-facing artifacts: `diagnosis-surface-pack.toml`, `symptom-catalog.receipt.json`, `self-check.manifest.json`, `signal-map.report.json`, `remediation-playbook.manifest.json`, `support-capture.report.json`, and `diagnosis-surface-diff.report.json`.
- Keep the boundary sharp between failure-path guidance, runtime handoff, observability contracts, debugger posture, downstream test support, and diagnosis-surface contracts.
- Favor conservative capture policy, redaction posture, and manual-review markers over magical host scraping or speculative auto-diagnosis.

## 2026-03-17 refresh — crate persistence-surface lane joins the ecosystem-supportiveness frontier

This pass added **P-0522 Crate Persistence Surface Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

Primary lane judgment:
- Treat **P-0522** as the next missing layer inside the broader crate-supportiveness frontier.
- The archive now has stronger answers for choosing crates, understanding support claims, fitting interop profiles, configuring crates, surviving failures, upgrading releases, leaving crates, reviewing observability/authority/lifecycle/resource posture, and reasoning about performance.
- It still needed a receiver-facing artifact for persisted bytes/state: what is public contract versus internal-only, what compatibility window is promised, what durability boundary exists, and how recovery or migration works.

Why it now looks especially strong:
- Official Rust messaging now explicitly recommends more **supportive interfaces from crates**.
- Docs and source still dominate the learning surface, which makes persisted-state support artifacts more valuable.
- The standard library already exposes durability-relevant nuance (`sync_data` vs `sync_all`).
- Serde already encodes many compatibility decisions in code.
- The ecosystem already has stable wire-format, format-reflection, revision-history, and crash-recovery substrate.

What to keep separate:
- Keep **P-0522** separate from **P-0514**: upgrade packs explain code/release migration, persistence packs explain persisted-state migration and compatibility.
- Keep **P-0522** separate from **P-0516**: setup recipes are not the same thing as durable-bytes promises.
- Keep **P-0522** separate from **P-0519**, **P-0520**, and **P-0521**: ambient powers, shutdown behavior, and resource posture are not the same thing as format stability and recovery semantics.
- Keep **P-0522** separate from serializer/storage-engine substrate and from domain schema workbenches.

Preferred artifacts:
- `persistence-pack`
- `persistence-surface.receipt`
- `format-compat.report`
- `durability-boundary.report`
- `recovery-posture.report`
- `migration-recipe.manifest`
- `compatibility-window.report`
- `persistence-diff.report`

## 2026-03-17 refresh — crate lifecycle-surface lane joins the ecosystem-supportiveness frontier

This pass added **P-0520 Crate Lifecycle Surface Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The archive now has **twelve** distinct ecosystem-supportiveness lanes:
  - **P-0509** task-first crate choice,
  - **P-0516** present-tense configuration/setup scenario support,
  - **P-0517** performance-envelope support,
  - **P-0518** observability-surface support,
  - **P-0519** authority-surface / ambient-dependency support,
  - **P-0520** lifecycle-surface / background-work support,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0520** is not generic shutdown orchestration and not structured concurrency by itself. It is the boring workflow that turns a crate’s steady-state and stop-path behavior into **lifecycle packs, background-work receipts, cancel-safety reports, shutdown-obligation reports, drain recipes, and lifecycle diffs**.

### Working rule
- Keep **P-0520** separate from **P-0513**: runtime failure handoff is not the same lane as steady-state lifecycle truth.
- Keep **P-0520** separate from graceful-shutdown frameworks: orchestration helpers are not the same thing as a per-crate contract.
- Keep **P-0520** separate from structured-concurrency substrate: task-group semantics are building blocks, not the support artifact.
- Keep **P-0520** separate from **P-0518** and **P-0519**: emitted telemetry and ambient powers are not the same thing as cancel / drop / drain behavior.
- Keep **P-0520** separate from **P-0516**: setup recipes are not the same thing as shutdown and cleanup obligations.

## 2026-03-17 refresh — crate authority-surface lane joins the ecosystem-supportiveness frontier

This pass added **P-0519 Crate Authority Surface Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The archive now has **eleven** distinct ecosystem-supportiveness lanes:
  - **P-0509** task-first crate choice,
  - **P-0516** present-tense configuration/setup scenario support,
  - **P-0517** performance-envelope support,
  - **P-0518** observability-surface support,
  - **P-0519** authority-surface / ambient-dependency support,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0519** is not generic sandboxing and not static authority scanning by itself. It is the boring workflow that turns a crate’s host-touching posture into **authority packs, determinism reports, capability-injection reports, checked sandbox recipes, and authority diffs**.

### Working rule
- Keep **P-0519** separate from compile-time sandbox policy: build-script permissions are not the same lane as a library’s receiver-facing authority surface.
- Keep **P-0519** separate from capability-oriented runtime substrate: `cap-std`-style APIs are building blocks, not the contract.
- Keep **P-0519** separate from **P-0516**: setup recipes are not the same thing as ambient authority posture.
- Keep **P-0519** separate from **P-0518**: emitted telemetry is not the same thing as what the crate may touch or assume.
- Keep **P-0519** separate from generic static scans: import heuristics are not the same thing as a maintainer-authored profile with verification recipes.

## 2026-03-17 refresh — crate observability-surface lane joins the ecosystem-supportiveness frontier

This pass added **P-0518 Crate Observability Surface Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The archive now has **ten** distinct ecosystem-supportiveness lanes:
  - **P-0509** task-first crate choice,
  - **P-0516** present-tense configuration/setup scenario support,
  - **P-0517** performance-envelope support,
  - **P-0518** observability-surface support,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0518** is not generic tracing/OTel setup and not semantic-convention linting by itself. It is the boring workflow that turns a crate’s intended emitted telemetry into **observability packs, signal-catalog receipts, cost/redaction reports, checked recipes, and surface diffs**.

### Working rule
- Keep **P-0518** separate from telemetry plumbing: wiring a subscriber or exporter is not the same lane as publishing a stable signal catalog.
- Keep **P-0518** separate from schema linting: naming rules are not the same thing as a receiver-facing surface contract.
- Keep **P-0518** separate from redaction tooling: generic scrubbing is not the same thing as declaring one crate’s sensitivity boundaries.
- Keep **P-0518** separate from **P-0513**: runtime-failure handoff is not the same lane as present-tense observability support.
- Keep **P-0518** separate from **P-0517**: performance posture is not the same thing as emitted signal posture.

## 2026-03-16 refresh — crate configuration-scenario lane joins the ecosystem-supportiveness frontier

This pass added **P-0516 Crate Configuration Scenario Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main shift

The archive now has eight distinct ecosystem-supportiveness lanes:

  - **P-0509** task-first crate choice,
  - **P-0516** present-tense configuration/setup scenario support,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0516** is not generic Cargo config provenance and not feature-combination testing by itself. It is the boring workflow that turns a crate’s intended setup story into **scenario packs, config-surface receipts, named recipes, checked matrices, conflict reports, and scenario diffs**.

### Immediate implications

- Keep **P-0516** separate from **P-0509**: choosing a crate is not the same lane as configuring the chosen crate.
- Keep **P-0516** separate from generic Cargo config tools: explaining precedence is not the same thing as naming intended scenarios.
- Keep **P-0516** separate from feature-doc or powerset tools: rendering or testing flags is not the same thing as publishing a receiver-facing scenario contract.
- Treat crates with real runtime/backend, `std`/`no_std`, docs.rs, or integration-lane choices as high-value proving grounds for the fixture vocabulary.

### What to watch next

Future passes in this area should ask whether the missing value is really about:

- crate-authored configuration scenario packs,
- raw support/interop claims,
- feature-matrix testing,
- generic Cargo config provenance,
- or compile/runtime supportiveness once the crate is already running.

Do not let these drift back into one vague “better setup docs” bucket.

---
## 2026-03-16 refresh — crate off-ramp lane joins the ecosystem-supportiveness frontier

This pass added **P-0515 Crate Off-Ramp Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main shift

The archive now has seven distinct ecosystem-supportiveness lanes:

  - **P-0509** task-first crate choice,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0515** successor / deprecation / off-ramp support,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0515** is not advisory detection and not broad maintenance scoring. It is the boring workflow that turns a crate sunset into **off-ramp packs, successor maps, checked exit recipes, compatibility reports, and sunset diffs**.

### Immediate implications

- Keep **P-0515** separate from **P-0011 Crate Health**: one is receiver-facing exit planning, the other is broad maintenance/governance metadata.
- Keep **P-0515** separate from **P-0514**: moving to the next version of the same crate is not the same lane as leaving the crate.
- Keep **P-0515** separate from advisory/outdated tooling: detection is not the same thing as a checked successor plan.
- Treat crates with real rename/supersession/sunset stories as high-value proving grounds for the fixture vocabulary.

### What to watch next

Future passes in this area should ask whether the missing value is really about:

- crate-authored off-ramp packs,
- crate health / governance posture,
- advisory or ban detection,
- or release-to-release upgrades.

Do not let these drift back into one vague “maintenance metadata” bucket.

---
## 2026-03-16 refresh — crate ecosystem frontier gains an upgrade-pack lane

This pass added **P-0514 Crate Upgrade Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The crate frontier now has **six** distinct cross-cutting ecosystem lanes:
  - **P-0509** task-first crate choice,
  - **P-0514** release-to-release upgrade support,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0514** is not semver verdict polish and not release automation. It is the boring workflow that turns one crate release transition into **upgrade packs, hazard reports, fixup receipts, checked migration recipes, and upgrade diffs**.
- Future crate-ecosystem passes should now ask not only “which crate?”, “what does it support?”, “how does it guide people when they fail?”, and “what does it hand off at runtime?”, but also “what exactly does it hand people when they upgrade?”

### Working rule
When touching supportiveness work, do **not** collapse:

- crate choice,
- support claims,
- shared profile contracts,
- crate-authored compile-time guidance,
- crate-authored runtime handoff,
- release-to-release upgrade packs,
- SemVer/public-API evidence,
- and release automation / changelog tooling

into one vague “ecosystem DX” story.

## 2026-03-16 refresh — crate ecosystem frontier gains a runtime handoff lane

This pass added **P-0513 Crate Runtime Handoff Pack Kit** and should further change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The crate frontier now has **five** distinct cross-cutting ecosystem lanes:
  - **P-0509** task-first crate choice,
  - **P-0512** compile-time / early-failure guidance,
  - **P-0513** runtime failure handoff,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0513** is not renderer polish and not a whole observability stack. It is the boring workflow that turns runtime failures into **redacted handoff packs, runtime receipts, panic receipts, and failure-shape diffs**.
- Future crate-ecosystem passes should now ask not only “which crate?”, “what does it support?”, and “how well does it guide people before it runs?”, but also “what exactly does it hand off after runtime failure?”

### Working rule
When touching supportiveness work, do **not** collapse:

- crate choice,
- support claims,
- shared profile contracts,
- crate-authored compile-time guidance,
- crate-authored runtime handoff,
- generic error rendering,
- and tracing / domain-specific incident tooling

into one vague “ecosystem DX” story.

## 2026-03-16 refresh — crate ecosystem frontier gains a receiver-facing guidance lane

This pass added **P-0512 Crate Guidance Pack Kit** and should change how the repo thinks about “ecosystem supportiveness”.

### Main judgment
- The crate frontier now has **four** distinct cross-cutting ecosystem lanes:
  - **P-0509** task-first crate choice,
  - **P-0512** receiver-facing crate guidance,
  - **P-0510** producer-side capability contracts,
  - **P-0511** shared ecosystem interop profiles.
- The missing value for **P-0512** is not renderer polish or more metadata. It is the boring workflow that turns common failure paths into **guidance packs, recipe manifests, fixture checks, and support-surface diffs**.
- Future crate-ecosystem passes should now ask not only “which crate?” and “what does it support?”, but also “how well does it help people recover when they fail?”

### Working rule
When touching supportiveness work, do **not** collapse:

- crate choice,
- support claims,
- shared profile contracts,
- crate-authored failure guidance,
- and generic diagnostic rendering

into one vague “ecosystem DX” story.

## 2026-03-21 refresh — local-first sync deepened for presence truth and history-retention honesty

This pass again did **not** add a new proposal.

Instead, it sharpened **P-0076 Local-first Sync Kit** around two collaboration truths that current substrate now makes impossible to ignore:

- **presence / awareness** is often session-level, best-effort, and not durable identity,
- **history retention** can diverge from current-state sync after compaction, export, or shallow snapshots.

### Main judgment
- **P-0076** should now be read as: **repo contract → sync-state receipt → transport session receipt → membership ledger → presence-surface receipt → history-retention receipt → divergence triage → portable sync bundle**.
- The missing value is still not another CRDT engine. It is the coordination artifact that keeps durable document state, ephemeral collaboration state, and history/branch claims separately reviewable.
- The next serious implementation move should stabilize `presence-surface.receipt.json` and `history-retention.receipt.json` rather than broadening the lane into a whole collaboration framework.

### Working rule
When touching local-first work, do **not** collapse:

- durable sync state,
- ephemeral presence/awareness state,
- history/branch retention posture,
- transport/bootstrap/session truth,
- and membership/key-epoch truth

into one vague “sync support” story.

## 2026-03-09 refresh — local-first fixtures restored and transport truth sharpened

This pass again did **not** add a new proposal.

Instead, it repaired an archive-memory mismatch around **P-0076 Local-first Sync Kit** and tightened the proposal’s transport/bootstrap semantics.

### Main judgment
- **P-0076** should now be read as: **repo contract → sync-state receipt → transport session receipt → membership ledger → divergence triage → portable sync bundle**.
- The crate should record **bootstrap method**, **direct vs relay path**, and **relay class** explicitly; those are operational facts, not implementation trivia.
- Bootstrap handles such as tickets should be treated as **convenience material** and normally **redacted** from support bundles, not promoted into durable identity or authorization truth.

### Working rule
When touching local-first work, do **not** collapse:

- document sync semantics,
- transport guarantees and relay behavior,
- bootstrap convenience tokens,
- durable replica identity,
- and membership / revocation truth

into one vague "peer connected" story.

## 2026-03-09 refresh — accessibility frontier splits into doctor/gating and capture/interop

This pass again did **not** add a new proposal.

Instead, it upgraded two overlapping proposals — **P-0087** and **P-0202** — by separating them into cleaner stack layers and adding fixture-first artifacts.

### Main judgment
- **P-0087** should now be read as: **semantic contract → doctor findings → baseline diff → release/CI gate result**.
- **P-0202** should now be read as: **platform capture → normalized tree/event model → semantic diff → redacted repro bundle → capability/caveat report**.
- The missing value is no longer “Rust accessibility infrastructure” in the abstract; it is the boring workflow layer above AccessKit and platform APIs.

### Working rule
When touching accessibility work, do **not** collapse:

- emitted widget semantics,
- release/CI gating,
- platform/backend translation,
- observer-side capture bundles,
- and compliance language

into one vague “a11y crate” claim.

## 2026-03-09 refresh — accessibility interop lab becomes lane-explicit

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0202 Cross-Platform Accessibility Interop & Conformance Kit** and clarified its boundary with **P-0087 UI Accessibility Kit**.

### Main judgment
- **P-0202** should now be read as: **capture profile → normalized tree → event stream → conformance result → interop diff → portable a11ybundle**.
- The missing value is not another toolkit abstraction or another raw platform binding; it is the receiver-facing lab artifact above authoring substrate and below organization-specific accessibility review workflow.
- This is timely because AccessKit plus desktop adapters now give Rust meaningful authoring/exposure substrate, while teams still lack redacted cross-platform repro bundles and honest comparability rules.

### Working rule
When touching accessibility work, do **not** collapse:

- toolkit authoring semantics,
- platform exposure capture,
- standards-informed policy packs,
- and support/repro bundle design

into one vague “a11y crate” claim.

## 2026-03-09 refresh — local-first sync becomes lane-explicit

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0076 Local-first Sync Kit** from a worthy but still essay-like product bet into a much more implementable artifact-first plan.

### Main judgment
- **P-0076** should now be read as: **repo contract → sync-state receipt → transport receipt → membership/key-epoch receipt → divergence triage → portable sync bundle**.
- The missing value is not another CRDT engine; it is the compact receiver-facing coordination artifact above already-meaningful Rust substrate.
- This is timely because Rust now has real local-first pieces in Automerge, Loro, Yrs, peer-sync substrate, and MLS/OpenMLS, while ordinary teams still lack a boring default product kit.

### Working rule
When touching local-first work, do **not** collapse:

- CRDT engine choice,
- durable store semantics,
- transport guarantees,
- membership / revocation semantics,
- and support-bundle design

into one vague “sync layer” claim.

## 2026-03-09 refresh — assurance case workbench becomes fixture-first

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0503 Assurance Case Workbench Kit** from a strong upper-layer idea into a much tighter artifact-first plan.

### Main judgment
- **P-0503** should now be read as: **evidence import → claim graph → conservative status → assurance diff → optional GSN/SACM export**.
- The missing value is not another editor; it is the compact receiver-facing review contract above bundle-first and verification/conformance evidence producers.
- This is timely because Rust’s safety-critical direction is becoming more explicit while GSN/SACM and existing assurance-case tools already provide export substrate rather than something Rust must invent from scratch.

### Working rule
When touching assurance-case work, do **not** collapse:

- evidence producers,
- bundle/profile substrate,
- assurance-case assembly and review,
- standards-shaped exports,
- and organization-specific certification workflows

into one vague “safety certification platform”.

## 2026-03-09 refresh — evidence bundle core boundaries

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0256 Evidence Bundle Core Kit** from a strong substrate hunch into a tighter fixture-first plan.

### Main judgment
- **P-0256** should now be read as: **bundle substrate → attestation lane → profile contract → optional publication lane**.
- The missing value is not another signature or transparency primitive; it is the compact receiver-facing bundle contract above them.
- This is timely because the surrounding ecosystem now has clearer layering in in-toto, Sigstore, and SCITT while Rust already has usable ZIP/COSE/Sigstore/JCS substrate.

### Working rule
When touching bundle-first proposals, do **not** collapse:

- deterministic local bundle rules,
- DSSE / COSE / Sigstore material,
- domain-specific report contracts,
- and OCI / SCITT / external publication lanes

into one vague “signed bundle” claim.

## 2026-03-09 refresh — reproducibility evidence as a layered stack

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0242 Reproducible Build Evidence Kit** from a good ecosystem essay into a tighter artifact-first plan.

### Main judgment
- **P-0242** should now be read as a layered review contract: **build recipe → rebuild verdict → diff triage → optional publication/attestation**.
- The missing value is not “Rust wrapper for diffoscope”; it is the compact receiver-facing bundle above existing reproducibility substrate.
- This is timely because reproducibility work is becoming more operational and more publishable across ecosystems, while ordinary Rust teams still lack a small local result contract.

### Working rule
When touching reproducibility proposals, do **not** collapse:

- official build recipe,
- third-party rebuild result,
- deep diff output,
- and public attestation/publication

into one vague success/failure blob.

## 2026-03-09 refresh — conformance to assurance stack

This refresh should override stale impressions that Rust testing/conformance/certification needs one giant umbrella crate.

### Main judgment
- Rust now has meaningful harness substrate, but it still lacks a boring **suite/case/result contract** above Cargo + nextest + `libtest-mimic` style plumbing.
- The sharp stack here is increasingly **P-0264 → P-0256 → P-0503** rather than another bespoke protocol harness or premature “certification platform”.
- A good next pass should prefer stable case IDs, environment receipts, comparison findings, and import-ready bundles over another generic testing DSL.

### Best next incubation targets in this stack
1. **P-0264 Rust Conformance Harness Toolkit**
2. **P-0256 Evidence Bundle Core Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0485 Verification Campaign Workbench Kit**

### Working rule
For the next few passes, prefer suite schemas, verdict vocabulary, compact failing-case bundles, and conservative assurance imports over adding more domain-specific harness count.

Do **not** let “needs certification support” get rewritten into “one crate should own execution, evidence packing, and assurance argument editing.”

## 2026-03-09 refresh — correctness labs above moving substrate

This refresh should override stale impressions that the strongest remaining non-Cargo work is just “another engine” or “another SDK”.

### Main judgment
- Rust now has meaningful substrate in both **text layout/i18n** and **passkeys/WebAuthn**, but it still lacks the shared **correctness-lab** layer above that substrate.
- Active backend/runner churn is evidence that comparison bundles, scenario DSLs, and conformance corpora are more valuable than prematurely blessing one backend as “the answer”.
- **P-0197** and **P-0200** look much stronger when read as artifact-first labs rather than as broad framework proposals.

### Best next incubation targets in this stack
1. **P-0197 Text Layout & Shaping Conformance Kit**
2. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
3. **P-0264 Rust Conformance Harness Toolkit**
4. **P-0256 Evidence Bundle Core Kit**

### Working rule
For the next few passes, prefer scenario models, fixture schemas, normalized outputs, and bug-bundle surfaces over adding one more backend or SDK in these domains.

Do **not** let active backend choice get misread as proof that the missing crate must be another backend.

## 2026-03-09 refresh — text layout stack boundaries and fixture depth

This refresh should override any stale impression that **P-0197** is already handoff-ready just because the repo mentioned text correctness earlier.

### Main judgment
- Rust now has meaningful text substrate in **Parley**, **COSMIC Text**, **HarfRust/rustybuzz**, and **ICU4X**, but the archive still needed a sharper boundary between Unicode data, shaping, layout policy, fallback, and repro-bundle work.
- **P-0197** looks stronger when read as a **case / corpus / receipt / diff / diagnosis** kit above those layers, not as a stealth attempt to become another layout engine.
- The missing value is increasingly the boring artifact contract that other teams can attach to bugs, upgrades, and backend migrations.

### Best next incubation targets in this stack
1. **P-0197 Text Layout & Shaping Conformance Kit**
2. **P-0264 Rust Conformance Harness Toolkit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**

### Working rule
For future passes, prefer pinned corpus provenance, backend capability receipts, semantic layout IR, and diagnosis bundles over adding one more backend-shaped proposal.

Do **not** let text work drift back into “Rust just needs another renderer”.

## 2026-03-09 refresh — text layout profile contracts and decision origins

This refresh sharpens the receiver-facing contract for **P-0197**.

### Main judgment
- The repo should now treat `layout-profile` as a first-class artifact, not a comment embedded inside the case.
- The repo should now expect `decision-origin` and `font-resolution` receipts whenever policy, backend discretion, or runtime font discovery can move the result.
- The missing value is the boring review artifact that makes policy-vs-backend-vs-font-universe drift legible to another maintainer.

### Best next incubation targets in this stack
1. **P-0197 Text Layout & Shaping Conformance Kit**
2. **P-0264 Rust Conformance Harness Toolkit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0503 Assurance Case Workbench Kit**

### Working rule
For future passes, prefer profile contracts, decision-origin receipts, and runtime font-resolution truth over adding another backend-shaped text proposal.

## 2026-03-09 refresh — bundle substrate and assurance stack

This refresh should override stale bundle-first readings elsewhere in this file.

### Main judgment
- The archive now has enough `*.Xbundle.zip` proposals that **bundle fragmentation** is a bigger risk than lack of ideas.
- **P-0256 Evidence Bundle Core Kit** should now be treated as likely shared substrate for many later bundle-first crates.
- **P-0485** and **P-0503** look stronger when read as higher-layer import/review crates above that substrate, not as private packaging grammars.

### Best next incubation targets in this stack
1. **P-0256 Evidence Bundle Core Kit**
2. **P-0485 Verification Campaign Workbench Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0264 Rust Conformance Harness Toolkit**

### Working rule
For the next few passes, prefer shared bundle/profile vocabulary, adapter planning, and stack clarity over adding more narrow bundle-first proposal count.

Do **not** let every bundle-first proposal invent a private container contract unless the proposal can justify why reuse would fail.

## 2026-03-09 refresh — broad portfolio balance

This refresh should override overly narrow readings elsewhere in this file.

### Main judgment
- The archive’s sharpest current sub-frontier is still Cargo explainability, but the repo as a whole now needs a **broad portfolio lens** as well.
- The strongest “epic crate” bets are increasingly crates that create a **shared coordination artifact** above existing substrate: bundles, receipts, ledgers, conformance suites, and support packs.

### Broad top tier right now
1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0242 Reproducible Build Evidence Kit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0485 Verification Campaign Workbench Kit**
5. **P-0264 Rust Conformance Harness Toolkit**
6. **P-0076 Local-first Sync Kit**
7. **P-0197 Text Layout & Shaping Conformance Kit**
8. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
9. **P-0503 Assurance Case Workbench Kit**
10. **P-0469 Cargo Rebuild Explanation Kit**

### Working rule
For the next few passes, prefer strengthening portfolio-multiplier crates before adding more narrow proposal count.

Do **not** let the repo’s ranking surface collapse into one family only.

## 2026-03-08 refresh — Cargo resolver workspace-inheritance layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- manifest origin truth for `[workspace.dependencies]` versus member manifests,
- inherited `default-features` policy (disabled, neutralized, or re-enabled),
- target-specific inherited dependency scope,
- and conservative reporting when current docs and observed behavior do not line up cleanly.

Why this matters now:

- Cargo workspace docs say workspace-dependency features are additive.
- Dependency-spec docs still say inherited dependencies cannot use keys like `default-features`.
- A current documentation issue says the resulting semantics are easy to misread.
- Issue history shows both neutralized `default-features = false` and member-side re-enabling behavior.
- Target-specific inherited dependency behavior still has enough bug history to justify manual-review boundaries.

So the missing value is a **dependency-origin / inherited-policy why-bundle**, not another generic feature matrix.

For the next few passes, prefer:

- stabilizing `dependency-origin.report`,
- tiny workspace-inheritance scenarios,
- and explicit manifest-origin capture for **P-0468**.

Do **not** drift into:

- another generic workspace-deps wrapper,
- a false claim that the member manifest alone authored the effective policy,
- or a host/target/config story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver feature-intent layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- positive feature requests versus negative feature intent,
- explanation subject scope (`--bin`, `-p`, workspace root, or equivalent),
- explicit reporting when another package kept a feature active anyway,
- and conservative reporting when investigative surfaces blur the requested subject.

Why this matters now:

- Cargo features docs explicitly warn that `default-features = false` may still fail to keep defaults off.
- The same docs say `--no-default-features` only disables defaults for the selected packages.
- Resolver docs still say multiple selected workspace packages unify dependency features.
- The feature-unification tracking issue is still open.
- Open issues still show subject-selection-dependent outcomes for `--bin`, `-p`, and workspace builds.

So the missing value is a **feature-intent and suppression why-bundle**, not another generic graph browser.

For the next few passes, prefer:

- stabilizing `feature-intent.report`,
- tiny positive/negative intent scenarios,
- and explicit subject-scope capture for **P-0468**.

Do **not** drift into:

- another generic feature-matrix runner,
- a false claim that raw tree output already preserves who asked for what,
- or a workflow/IDE story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver unification-scope layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- feature-unification policy (`selected`, `workspace`, `package`),
- selected-package scope versus participating-package scope,
- explicit `feature_unification_policy_changed` diffs,
- and conservative reporting when investigative surfaces do not preserve package-mode truth exactly.

Why this matters now:

- unstable Cargo docs now define the three unification modes explicitly,
- the resolver docs still say multiple selected workspace packages unify dependency features,
- the tracking issue still has unresolved representation questions for package mode,
- and the long-running package-set-sensitivity issue is still open.

So the missing value is a **policy-and-participant why-bundle**, not another generic graph export.

For the next few passes, prefer:

- stabilizing `unification-scope.report`,
- tiny selected/workspace/package policy scenarios,
- and explicit participant-set capture for **P-0468**.

Do **not** drift into:

- another generic graph browser,
- a false claim that `cargo tree` already preserves package-mode truth,
- or a compile-time-deps/editor-parity story that forgets this is still resolver explanation work.

## 2026-03-08 refresh — Cargo resolver lane + platform coverage layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundaries:

- dependency-kind lane partition,
- platform-coverage truth for target-specific clauses,
- explicit `--filter-platform` / selected-target capture,
- and stronger manual-review markers when human-facing views merge lanes.

Why this matters now:

- Cargo’s resolver and features docs both make lane splits explicit for target-specific, build/proc-macro, and dev cases.
- `cargo tree` still says its feature view is only close to what Cargo will build.
- `cargo metadata` still includes all targets unless the capture narrows platform scope.
- `--unit-graph` remains the richer internal-graph substrate, but it is still unstable.
- current issue reports still show normal/dev and proc-macro/build cases where exactness must stay conservative.

So the missing value is a **lane-aware why-bundle**, not another generic graph API.

For the next few passes, prefer:

- stabilizing `lane-partition.report` and `platform-coverage.report`,
- tiny lane/target scenarios,
- and stronger exactness markers for **P-0468**.

Do **not** drift into:

- another generic graph query crate,
- a false claim that `cargo tree` or all-target metadata already gives exact build truth,
- or a mega Cargo doctor that absorbs host/target, linker, and editor-parity stories.

## 2026-03-08 refresh — Cargo resolver exactness + MSRV layer

This pass again did **not** add a new proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the missing receiver-facing boundaries:

- `resolve-why.lock` as a capture-scope spine,
- mixed-MSRV version-choice receipts,
- selection-sensitive scenario bundles,
- and exact/manual-review vocabulary in the receipt itself.

Why this matters now:

- Cargo’s resolver docs now make mixed-workspace MSRV heuristics explicit.
- The same docs make the two-pass feature story explicit.
- `cargo tree` says its view is only close to what Cargo will build, not exact.
- the Cargo plumbing goal still says `cargo metadata` excludes feature resolution.
- `--unit-graph` remains useful but unstable.

So the missing value is a **why-bundle with boundary metadata**, not another graph API.

For the next few passes, prefer:

- stabilizing `resolve-why.lock`,
- tiny MSRV and selection-sensitive scenarios,
- and stronger exactness markers for **P-0468**.

Do **not** drift into:

- another generic graph query crate,
- another mega Cargo doctor,
- or a tool that silently treats `cargo tree` output as exact build truth.

## 2026-03-08 refresh — host/target scope implementation layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0505 Cargo Host/Target Scope Contract Kit** — now strong enough that the best next work is schema freeze and tiny scenario validation, not more broad ideation.

### Immediate follow-ons
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should keep tool-only build-surface parity separate from scope drift.
- **P-0504 Linker Lane Contract & Diagnosis Kit** — should keep linker-lane choice separate from config-scope behavior.
- **P-0484 Toolchain & Target Support Contract Kit** — should keep broader support posture separate from host/target config facts.

### Working planning rule
For the next few passes, prefer `scope-observation.receipt`, `scope-diff.report`, same-triple mixed-build fixtures, and adapter planning for **P-0505** instead of adding another generic cross-build or Cargo doctor proposal.

### Added implementation rule
Treat stable Cargo config docs, unstable host-config surfaces, and docs.rs-style rustdoc quirks as substrate. The crate value begins at the **portable policy / observation / diagnosis / diff bundle** above them.

## 2026-03-08 refresh — rebuild explanation implementation layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0469 Cargo Rebuild Explanation Kit** — now strongest not just because the pain is real, but because Cargo’s official build-analysis/report substrate is finally strong enough that the missing value is clearly the stable receipt layer above it.

### Immediate follow-ons
- **P-0468 Cargo Resolver Explanation Kit** — should keep sharing receipt vocabulary while staying graph-cause focused.
- **P-0035 cargo-build-insights** — should remain the imported-session warehouse / regression layer rather than absorbing the per-run support story.
- **P-0490 Cargo Lock Contention Witness Kit** — should remain the specialized live-blocking witness and be importable context for rebuild bundles.

### Working planning rule
For the next few passes, prefer:
- `fingerprint-delta` and `cache-conflict` schemas,
- tiny `check_then_build`, `wrapper_rustflags_drift`, and `shared_target_lock_hint` scenarios,
- and explicit evidence-lane boundaries for **P-0469**,

instead of adding another generic Cargo performance proposal.

### Added implementation rule
Treat `cargo report sessions/rebuilds/timings`, timing HTML, build/fingerprint logs, and wrapper/env capture as substrate.
The crate value begins at the **stable support receipt / diff / redaction bundle** above them.

## 2026-03-08 refresh — host/target config scope layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0505 Cargo Host/Target Scope Contract Kit** — now newly justified because Cargo’s official config docs, unstable host-config surfaces, and real issue reports make the missing value clearly the scope contract / observation / doctor layer above them.

### Immediate follow-ons
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should keep tool-only / editor-oriented build-surface parity separate from host/target scope diagnosis.
- **P-0504 Linker Lane Contract & Diagnosis Kit** — should keep linker-lane choice and switch-risk distinct from config-scope behavior.
- **P-0484 Toolchain & Target Support Contract Kit** — should keep broader target/toolchain posture separate from mixed-build scope facts.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny mixed-build scenario bundles, and adapter planning for **P-0505** instead of adding another generic cross-build or “Cargo doctor” proposal.

### Added implementation rule
Treat `build.rustflags`, `build.rustdocflags`, `target.*`, `[host]`, `target-applies-to-host`, `--target`, and docs-builder/rustdoc quirks as substrate. The crate value begins at the **scope contract / observation receipt / diagnosis / diff bundle** above those surfaces.

## 2026-03-08 refresh — linker lane contract layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0504 Linker Lane Contract & Diagnosis Kit** — now newly justified because the official Rust/Cargo substrate and the ecosystem’s real lane-specific tools make the missing value clearly the contract/receipt/doctor layer above them.

### Immediate follow-ons
- **P-0484 Toolchain & Target Support Contract Kit** — should keep broader target/toolchain posture separate from linker-lane drift.
- **P-0058 native-deps-kit** — should keep native probing/fallback behavior separate from linker-lane diagnosis.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — should keep hardware-support promises separate from linker-lane support promises.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny link-lane scenario bundles, and adapter planning for **P-0504** instead of adding another generic cross-compilation or linker-wrapper proposal.

### Added implementation rule
Treat Cargo linker config, `rustc` linker knobs, rustup cross-compilation docs, and existing tools like `cargo-zigbuild`, `cargo-xwin`, `xwin`, and `cross` as substrate. The crate value begins at the **lane contract / diagnosis / diff bundle** above those surfaces.

## 2026-03-08 refresh — safety-critical assurance layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0503 Assurance Case Workbench Kit** — now newly justified because Rust’s safety-critical direction is increasingly explicit about evidence, while the repo already contains enough lower-layer evidence producers to make an argument-assembly layer practical.

### Immediate follow-ons
- **P-0433 MC/DC Coverage Workbench Kit** — should keep producing qualification-friendly coverage evidence.
- **P-0453 Safety Contract Consumer Kit** — should keep exposing contract surfaces and consumption receipts.
- **P-0459 Clippy Safety Profile & Waiver Kit** — should keep machine-readable policy and waiver records importable by assurance packs.
- **P-0465 BorrowSanitizer Workflow & Evidence Kit** — should keep feeding unsafe/aliasing evidence into higher-level review packs.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny mixed-evidence fixtures, and adapter planning for **P-0503** instead of adding another generic regulated-industry proposal.

### Added implementation rule
Treat standards like GSN and SACM as export and interchange surfaces. The Rust-native value begins at the **boring, diffable claim/evidence pack** above Rust tooling outputs.

## 2026-03-08 refresh — Cargo build-dir consumer transition implementation layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — now substantially more implementation-ready because the official Cargo substrate is explicit enough that the missing value is clearly the migration receipt, not proof that layout drift exists.

### Immediate follow-ons
- **P-0490 Cargo Lock Contention Witness Kit** — should stay focused on live waits rather than drifting into migration planning.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should stay focused on tool-build parity / fallback while sharing provenance vocabulary.
- **P-0471 Cargo Artifact Handoff Kit** — should be treated as a destination adapter for consumers that never needed intermediate-layout scraping in the first place.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny scenario bundles, and proposal-file upgrades for **P-0489** instead of adding another generic Cargo output / migration proposal.

### Added implementation rule
Treat `build.build-dir`, release-note warnings, `build-script-executed` JSON, `OUT_DIR`, and `CARGO_BIN_EXE_<name>` as substrate. The crate value begins at the **consumer inventory / path contract / transition receipt** layered above them.

## 2026-03-08 refresh — Cargo resolver explanation implementation layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0468 Cargo Resolver Explanation Kit** — now substantially more implementation-ready because Cargo’s official surfaces and ecosystem prior art make the missing value clearly the explanation receipt, not raw graph access.

### Immediate follow-ons
- **P-0469 Cargo Rebuild Explanation Kit** — should keep sharing receipt vocabulary with P-0468 while staying focused on run-delta causes.
- **P-0035 cargo-build-insights** — should remain the historical warehouse / regression layer above imported sessions and explanation bundles, not a replacement for them.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should stay focused on tool-workflow parity while reusing the same observed-fact / conservative-inference vocabulary.

### Working planning rule
For the next few passes, prefer schema stabilization, tiny scenario bundles, and proposal-file upgrades for **P-0468** instead of adding another generic Cargo graph or feature-management proposal.

### Added implementation rule
Treat `cargo tree`, `cargo metadata`, `--unit-graph`, and `guppy`/`hakari` as substrate and prior art. The crate value begins at the **portable explanation receipt** above them.

## 2026-03-08 refresh — Cargo build-analysis adoption layer

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0469 Cargo Rebuild Explanation Kit** — now stronger because it can layer on top of Cargo's evolving `-Zbuild-analysis` / `cargo report` substrate instead of inventing a recorder from scratch.

### Immediate follow-ons
- **P-0468 Cargo Resolver Explanation Kit** — should reuse the same session / baseline / receipt vocabulary when comparing graph choices across runs.
- **P-0035 cargo-build-insights** — should be treated as the historical warehouse / regression-adjudication layer above imported Cargo sessions, not as a competitor to P-0469.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should reuse the same receipt vocabulary when a tool-only run is compared against a fuller build.

### Working planning rule
For the next few passes, prefer build-analysis import schemas, tiny example bundles, and proposal-file upgrades for P-0469 / P-0035 / P-0468 / P-0494 instead of adding another generic Cargo performance proposal.

### Added implementation rule
Treat `cargo report` HTML replay as a human attachment, not the machine contract. Freeze imported session/report data into smaller stable bundles.


## 2026-03-08 refresh — native build / buildscript stack

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target in this frontier
- **P-0046 buildscript-ux-kit** — best first move because it helps every build-script user immediately and creates shared report vocabulary for the rest of the stack.

### Immediate follow-ons
- **P-0059 buildscript-testkit** — should share normalized directive/report vocabulary with P-0046 and focus on fake-tool fixture scenarios first.
- **P-0058 native-deps-kit** — should reuse report/test vocabulary from P-0046/P-0059 and stay focused on declarative contracts plus a doctor UX.

### Added implementation refresh
- **P-0046** should now be read as a crate that layers on Cargo JSON where available, labels capture origin explicitly (`live_capture` vs `cargo_json_cached`), and distinguishes warnings that were hidden by default from those shown to the user.

### Working planning rule
For the next few passes, prefer schemas, fixture corpora, and planning notes for P-0046 / P-0059 / P-0058 instead of adding more native-build-adjacent proposal count.

### Added implementation rule
When touching this frontier again, prefer example bundles and crate-split/API notes over adding more native-build proposal count.


## 2026-03-08 refresh — Cargo explainability stack

This refresh should override stale impressions elsewhere in this file.

### Best next incubation target
- **P-0469 Cargo Rebuild Explanation Kit** — strongest 0.1 candidate because the user story is concrete, the pain is current, and the artifact is easy to explain and review.

### Immediate follow-ons
- **P-0468 Cargo Resolver Explanation Kit** — should share receipt vocabulary and fixture style with P-0469.
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should be treated as the tool-invocation parity layer above the same stack.

### Working planning rule
For the next few passes, prefer adding schemas, fixture corpora, and incubation notes to these three proposals instead of adding more proposal count.

# Roadmap

## 2026-03-23 (403)
- Deepen **P-0515 Crate Off-Ramp Pack Kit** around `successor-authority.receipt`, `stopgap-horizon.report`, `recipe-witness.report`, and `offramp-support-bundle.manifest`.
- Guardrail: do not flatten compiler deprecation notes, advisory stopgaps, maintainer-authored successor declarations, and recipe witnesses into one fake “migration supported” claim.

## Added 2026-03-21 (318) — workspace tool dependencies now need install-root and route-authority truth

- Treat `meta/cargo-workspace-toolchain-manifest-product-plan-2026-03-21.md` as the current working sketch for **P-0055**.
- Keep **manifest intent**, **install-root posture**, **tool-route authority**, **toolchain context**, and **shadowing visibility** explicit.
- Prefer tiny receiver-facing artifacts such as `install-root.receipt` and `tool-route.receipt` rather than another installer wrapper or vague “repo pins its tools” claim.
 (incubation picks)

This file is intentionally opinionated. Update it when new evidence changes the landscape.

## Candidate top 3 to incubate
1) **P-0001 Cargo Snapshot** — huge pain + clear MVP; aligns with enterprise needs.
2) **P-0016 Audit Lens** — rides strong research signal; composes with cargo-vet.
3) **P-0015 Cargo Attest** — matches ecosystem direction (Trusted Publishing); hard but high leverage.

## Why these
- Strong external evidence that the pain is real and recurring.
- Clear “library core + cargo plugin” architecture.
- Can ship an MVP without compiler changes.

## Next concrete actions (2-week spikes)
- P-0001: prototype `cargo snapshot create` that emits a tarball + manifest for a single workspace.
- P-0016: implement schema + diff tool with one Cargo Scan fixture.
- P-0015: implement statement + provenance JSON emission for `cargo package` output.


## Watchlist (high leverage, later)
- **P-0019 Cargo Transparency Bundle** — likely best as an integration layer that plugs into cargo-dist.
- **P-0020 embedded-hal TCK** — strong ecosystem multiplier after embedded-hal 1.0 stability.
- **P-0021 mpi-typed** — niche but high impact in HPC communities.

## Watchlist (new: 2026-03-04)
- **Local-first Sync Kit** — big upside if it nails secure-by-default + deterministic repro artifacts; needs tight scope to avoid “platform” creep.
- **Verification Workbench Kit** — can dramatically lower adoption friction for Kani/Creusot/Prusti/Miri by standardizing workflows and artifacts.
- **OTA Update Kit** — security-critical, repetitive work; good candidate for a conformance-first MVP.
- **WASI Conformance Kit** — interop multiplier for the Component Model era; pairs well with plugin kits.

## Watchlist additions (new evidence)
- **P-0023 vet-workbench** — cargo-vet adoption/UX blocker; could be a standalone accelerator for supply-chain hygiene.
- **P-0024 data-contract-kit** — “schema evolution” is universal in distributed systems; Rust still lacks a default, integrated kit.
- **P-0025 chaos-lab** — deterministic chaos testing is emerging; a unified reproducible-harness could make it mainstream.
- **P-0022 privacy-metrics-kit** — recurring “no telemetry” debates point to a missing reusable privacy/consent framework.

Last updated: 2026-03-04

## Next wave candidates
- **P-0026 cargo-tuf-mirror** — aligns with ecosystem direction (TUF adoption) and complements offline/mirror work.
- **P-0027 text-input-kit** — high-leverage for every GUI toolkit; IME and selection bugs are chronic and costly.
- **P-0028 open-table-format-kit** — strategic for Rust-in-data; avoids each engine reimplementing format glue.
- **P-0029 audio-graph-kit** — consolidates fragmented real-time audio plumbing into reusable primitives.


## New candidates (2026-03-01)
- **P-0030 cargo-build-jail** — strong supply-chain leverage; can ship as external tool before upstream changes.
- **P-0033 cargo-capabilities** — makes sandboxing/policy scalable by reducing “ad-hoc allowlist” pain.
- **P-0031 isolate-kit** — reusable substrate; also a dependency for P-0030 and plugin sandboxes.
- **P-0032 inference-kit** — valuable, but should incubate only with a committed adopter (avoid “abstraction-only” trap).

- **P-0038 cargo-repro-pack** — improves verifiability and supply-chain posture by making `.crate` artifacts deterministic (prototype for upstream).
- **P-0039 i18n-icu-kit** — a pragmatic i18n foundation: typed tokens + ICU-backed formatting without framework lock-in.
- **P-0040 proc-macro-sandbox-kit** — accelerates migration to sandboxed proc macros by giving authors a compatibility harness.
- **P-0041 cargo-prebuilt-artifacts** — supply-chain-aware prebuilt dep packs; potentially huge CI speedups if trust model is right.


## New candidates (2026-03-01-08)
- **P-0042 cargo-event-stream** — unblock IDE/CI tooling by making Cargo output machine-readable and robust to proc-macro noise.
- **P-0043 winit-web-ime-kit** — unlock serious WASM GUI text input (global IME) with a shared, tested bridge.
- **P-0044 ebpf-shipkit** — reduce bespoke packaging/testing burden for Rust eBPF apps; likely to accelerate adoption.

## Recent candidates
- **P-0042 cargo-event-stream** — unlocks IDE/CI tooling; pairs with build-analysis reporting.
- **P-0045 cargo-input-manifest** — build signatures for caching/repro; shares primitives with reproducible packaging.
- **P-0046 buildscript-ux-kit** — reduces “build.rs noise” and enables CI policies without upstream changes.

## New candidates (install trust & sandboxing)
- **P-0047 cargo-binary-trust** — verification/policy layer for fast binary installs (composes with cargo-binstall/cargo-dist); responds to rising demand for “fast installs” plus trust concerns.
- **P-0048 install-script-jail** — sandbox runner for third-party installer scripts (curl|sh) with auditable reports; extends build-sandbox ideas to the broader devtool ecosystem.
## New candidates (native deps + codegen + robotics)
- **P-0058 native-deps-kit** — unify system dependency workflows across pkg-config/vcpkg/vendoring with a “doctor” UX; reduces ubiquitous -sys pain.
- **P-0059 buildscript-testkit** — make build.rs testable; raises reliability for FFI and native builds without upstream changes.
- **P-0060 openapi-sdk-kit** — reduce fragmentation by standardizing an OpenAPI IR + conformance fixtures; make codegen outputs trustworthy and upgrade-friendly.
- **P-0061 rclrs-extras-kit** — fill ROS 2 Rust gaps (actions/executors/launch ergonomics) with conformance fixtures; improves “Rust robotics” viability.

Last updated: 2026-03-01

## New candidates (2026-03-01-16)
- **P-0062 Durable Workflow Kit** — high leverage if kept library-first; prioritize replay + local UX over platform ambitions.
- **P-0063 Passkey Stack Kit** — adoption multiplier: wrap existing protocol crates with secure defaults + framework adapters.
- **P-0064 BLE Conformance Kit** — avoid “yet another BLE crate”; focus on capability model + test harness + compatibility matrix.
- **P-0065 HTTP Cassette Kit** — unify fragmented VCR crates with a shared cassette format + redaction + adapters.

## Watchlist additions
- P-0066 Determinism Sim Kit
- P-0067 Kube Integration Testkit
- P-0068 Markdown Safe Kit

## Watchlist (new additions)

- **P-0069 mail-transport-security-kit** — operational “doctor” + evaluation engine for MTA-STS/TLS-RPT/DANE.
- **P-0070 saml-stack-kit** — secure XML signature substrate + SAML SP building blocks + conformance fixtures.
- **P-0071 MCP Guard Kit** — transport exposure, auth boundaries, operation guards, and review bundles for MCP deployments (built atop SDKs).
- **P-0072 pdf-safe-kit** — safe-by-default parsing/extraction limits + fuzz/conformance scaffolding.


## Frontier bets (2026-03-04)
- P-0073 Async Replay Debugger Kit
- P-0074 Capability Sandbox Kit
- P-0075 Cargo Provenance Suite
- P-0076 Local-first Sync Kit


# Roadmap (incubation picks)

This file is intentionally opinionated. Update it when new evidence changes the landscape.

## Candidate top 3 to incubate
1) **P-0001 Cargo Snapshot** — huge pain + clear MVP; aligns with enterprise needs.
2) **P-0016 Audit Lens** — rides strong research signal; composes with cargo-vet.
3) **P-0015 Cargo Attest** — matches ecosystem direction (Trusted Publishing); hard but high leverage.

## Why these
- Strong external evidence that the pain is real and recurring.
- Clear “library core + cargo plugin” architecture.
- Can ship an MVP without compiler changes.

## Next concrete actions (2-week spikes)
- P-0001: prototype `cargo snapshot create` that emits a tarball + manifest for a single workspace.
- P-0016: implement schema + diff tool with one Cargo Scan fixture.
- P-0015: implement statement + provenance JSON emission for `cargo package` output.


## Watchlist (high leverage, later)
- **P-0019 Cargo Transparency Bundle** — likely best as an integration layer that plugs into cargo-dist.
- **P-0020 embedded-hal TCK** — strong ecosystem multiplier after embedded-hal 1.0 stability.
- **P-0021 mpi-typed** — niche but high impact in HPC communities.

## Watchlist (new: 2026-03-04)
- **Local-first Sync Kit** — big upside if it nails secure-by-default + deterministic repro artifacts; needs tight scope to avoid “platform” creep.
- **Verification Workbench Kit** — can dramatically lower adoption friction for Kani/Creusot/Prusti/Miri by standardizing workflows and artifacts.
- **OTA Update Kit** — security-critical, repetitive work; good candidate for a conformance-first MVP.
- **WASI Conformance Kit** — interop multiplier for the Component Model era; pairs well with plugin kits.

## Watchlist additions (new evidence)
- **P-0023 vet-workbench** — cargo-vet adoption/UX blocker; could be a standalone accelerator for supply-chain hygiene.
- **P-0024 data-contract-kit** — “schema evolution” is universal in distributed systems; Rust still lacks a default, integrated kit.
- **P-0025 chaos-lab** — deterministic chaos testing is emerging; a unified reproducible-harness could make it mainstream.
- **P-0022 privacy-metrics-kit** — recurring “no telemetry” debates point to a missing reusable privacy/consent framework.

Last updated: 2026-03-04

## Next wave candidates
- **P-0026 cargo-tuf-mirror** — aligns with ecosystem direction (TUF adoption) and complements offline/mirror work.
- **P-0027 text-input-kit** — high-leverage for every GUI toolkit; IME and selection bugs are chronic and costly.
- **P-0028 open-table-format-kit** — strategic for Rust-in-data; avoids each engine reimplementing format glue.
- **P-0029 audio-graph-kit** — consolidates fragmented real-time audio plumbing into reusable primitives.


## New candidates (2026-03-01)
- **P-0030 cargo-build-jail** — strong supply-chain leverage; can ship as external tool before upstream changes.
- **P-0033 cargo-capabilities** — makes sandboxing/policy scalable by reducing “ad-hoc allowlist” pain.
- **P-0031 isolate-kit** — reusable substrate; also a dependency for P-0030 and plugin sandboxes.
- **P-0032 inference-kit** — valuable, but should incubate only with a committed adopter (avoid “abstraction-only” trap).

- **P-0038 cargo-repro-pack** — improves verifiability and supply-chain posture by making `.crate` artifacts deterministic (prototype for upstream).
- **P-0039 i18n-icu-kit** — a pragmatic i18n foundation: typed tokens + ICU-backed formatting without framework lock-in.
- **P-0040 proc-macro-sandbox-kit** — accelerates migration to sandboxed proc macros by giving authors a compatibility harness.
- **P-0041 cargo-prebuilt-artifacts** — supply-chain-aware prebuilt dep packs; potentially huge CI speedups if trust model is right.


## New candidates (2026-03-01-08)
- **P-0042 cargo-event-stream** — unblock IDE/CI tooling by making Cargo output machine-readable and robust to proc-macro noise.
- **P-0043 winit-web-ime-kit** — unlock serious WASM GUI text input (global IME) with a shared, tested bridge.
- **P-0044 ebpf-shipkit** — reduce bespoke packaging/testing burden for Rust eBPF apps; likely to accelerate adoption.

## Recent candidates
- **P-0042 cargo-event-stream** — unlocks IDE/CI tooling; pairs with build-analysis reporting.
- **P-0045 cargo-input-manifest** — build signatures for caching/repro; shares primitives with reproducible packaging.
- **P-0046 buildscript-ux-kit** — reduces “build.rs noise” and enables CI policies without upstream changes.

## New candidates (install trust & sandboxing)
- **P-0047 cargo-binary-trust** — verification/policy layer for fast binary installs (composes with cargo-binstall/cargo-dist); responds to rising demand for “fast installs” plus trust concerns.
- **P-0048 install-script-jail** — sandbox runner for third-party installer scripts (curl|sh) with auditable reports; extends build-sandbox ideas to the broader devtool ecosystem.
## New candidates (native deps + codegen + robotics)
- **P-0058 native-deps-kit** — unify system dependency workflows across pkg-config/vcpkg/vendoring with a “doctor” UX; reduces ubiquitous -sys pain.
- **P-0059 buildscript-testkit** — make build.rs testable; raises reliability for FFI and native builds without upstream changes.
- **P-0060 openapi-sdk-kit** — reduce fragmentation by standardizing an OpenAPI IR + conformance fixtures; make codegen outputs trustworthy and upgrade-friendly.
- **P-0061 rclrs-extras-kit** — fill ROS 2 Rust gaps (actions/executors/launch ergonomics) with conformance fixtures; improves “Rust robotics” viability.

Last updated: 2026-03-01

## New candidates (2026-03-01-16)
- **P-0062 Durable Workflow Kit** — high leverage if kept library-first; prioritize replay + local UX over platform ambitions.
- **P-0063 Passkey Stack Kit** — adoption multiplier: wrap existing protocol crates with secure defaults + framework adapters.
- **P-0064 BLE Conformance Kit** — avoid “yet another BLE crate”; focus on capability model + test harness + compatibility matrix.
- **P-0065 HTTP Cassette Kit** — unify fragmented VCR crates with a shared cassette format + redaction + adapters.

## Watchlist additions
- P-0066 Determinism Sim Kit
- P-0067 Kube Integration Testkit
- P-0068 Markdown Safe Kit

## Watchlist (new additions)

- **P-0069 mail-transport-security-kit** — operational “doctor” + evaluation engine for MTA-STS/TLS-RPT/DANE.
- **P-0070 saml-stack-kit** — secure XML signature substrate + SAML SP building blocks + conformance fixtures.
- **P-0071 MCP Guard Kit** — transport exposure, auth boundaries, operation guards, and review bundles for MCP deployments (built atop SDKs).
- **P-0072 pdf-safe-kit** — safe-by-default parsing/extraction limits + fuzz/conformance scaffolding.


## Frontier bets (2026-03-04)
- P-0073 Async Replay Debugger Kit
- P-0074 Capability Sandbox Kit
- P-0075 Cargo Provenance Suite
- P-0076 Local-first Sync Kit


## New candidates (2026-03-05)
- P-0283 TLS 1.3 + X.509 Path Validation Interop & Evidence Kit (tlsbundle)
- P-0284 IEC 60870-5-104 Interop & Evidence Kit (iec104bundle)
- P-0285 HL7 v2 + MLLP Interop & Evidence Kit (hl7bundle)

- P-0271 WebGPU CTS triage & evidence kit
- P-0272 Apache Arrow Flight/Flight SQL interop & evidence kit
- P-0273 gNMI interop & evidence kit

- **P-0197 Text Layout & Shaping Conformance Kit** — high leverage for every Rust GUI toolkit; keeps scope to deterministic layout outputs + fixtures.
- **P-0198 Network Cassette & Impairment Kit** — makes network failures reproducible and shareable (redaction-first), with capture→replay→diff workflows.
- **P-0199 MessageFormat 2 Localization Kit** — positions Rust for MF2 adoption; conformance-first implementation that composes with ICU4X.
- **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — turns passkeys into a testable integration surface with scenario DSL + portable evidence bundles.
- **P-0201 Secure Email Interop ShipKit** — cohesive MIME/S/MIME/OpenPGP + auth verification with deterministic normalization and shareable diagnostics.

Last updated: 2026-03-05
## New candidates (2026-03-05)

- **P-0286 SNMPv3 Interop & Evidence Kit** — canonical/redactable USM transcripts + capability matrices + replay/diff.
- **P-0287 RADIUS + EAP Interop & Evidence Kit** — registry-pinned decoding + exchange bundles + replay/diff for AAA flows.
- **P-0288 CAN + ISO-TP + UDS Interop & Evidence Kit** — canonical CAN/UDS traces + timing/state checks + reproducible diagnostic bundles.
- **P-0289 DNP3 Secure Authentication Interop & Evidence Kit** — canonical SA transcripts + capability matrices + replay/diff.
- **P-0290 OpenID Federation 1.0 Interop & Evidence Kit** — trust-chain resolution + policy diffs + reproducible federation bundles.
- **P-0291 JPEG XL Conformance & Evidence Kit** — golden tests + fuzz corpus bundles + reproducible divergence triage.

Last updated: 2026-03-05


## New candidates (2026-03-06)
- **P-0292 OpenRTB 2.6 + AdCOM Interop & Evidence Kit** — high-leverage for adtech compatibility; profile-as-code plus redactable trace bundles.
- **P-0293 MAVLink Microservices Interop & Evidence Kit** — strong robotics/drone multiplier; mission/parameter/file/signing scenarios with replay.
- **P-0294 AS2 + MDN Interop & Evidence ShipKit** — gives Rust a credible B2B transport story without promising a full EDI suite.
- **P-0295 ORC Interop & Canonicalization Kit** — lakehouse/data infra helper around `orc-rust`; semantic diffs + bug bundles.
- **P-0296 BPMN 2.0 + DMN Conformance Workbench Kit** — process/rules assets under CI with portable traces and FEEL corpora.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (69)

1. **FIX + Orchestra** — strongest case for a profile-as-code + replay + certification workbench around multiple existing Rust engines.
2. **XBRL + iXBRL** — prioritize conformance-runner + canonical-fact diff MVP, ideally side-by-side with Arelle outputs.
3. **SECS/GEM** — prototype transcript IR + GEM state-trace model before broadening into vendor-specific flows.
4. **IPP Everywhere** — keep scope anchored to capability inspection, job replay, and certification-style bundles.
5. **EBICS** — validate whether a neutral simulated-bank suite can cover enough onboarding pain to justify a full workbench.


## Frontier queue — 2026-03-06 (70)

1. **FHIR + SMART** — strongest cross-cutting case for IG lockfiles, validator adapters, and PHI-safe evidence bundles.
2. **OCPP** — certification/test-case momentum plus active field pain makes profile-aware replay unusually actionable.
3. **RDAP + EPP** — compelling because Rust already has credible RDAP substrate and ICANN-adjacent operational context.
4. **OpenADR** — now that Rust VEN/VTN implementations exist, scenario/evidence layers could materially accelerate adoption.
5. **IFC / BIM** — conformance-first workbench looks more promising than trying to outbuild mature authoring tools.


## Frontier queue — 2026-03-06 (71)

1. **EPCIS + CBV** — strongest cross-industry case in this pass; traceability, lineage, and recall evidence have broad adoption surface and clear standards gravity.
2. **SIP + SDP + RTP** — active Rust substrate plus never-ending interop pain make a replay/evidence layer unusually credible.
3. **AS4 + Peppol eDelivery** — strong B2B/e-government leverage if kept discovery/trust/evidence-first rather than platform-ambitious.
4. **ONVIF + RTSP** — practical value for security/video stacks; profile-aware camera bundles could materially reduce field debugging time.
5. **DLMS/COSEM** — high infrastructure relevance, but success depends on keeping scope to utility-profile evidence rather than full smart-meter platforms.


## Frontier queue — 2026-03-06 (72)

1. **DCSA eBL + PINT** — recent production interoperability milestones make portable dispute/onboarding bundles more timely than they looked even a year ago.
2. **OPC UA PubSub + UAFX** — strongest industrial bet if scoped to timing/metadata/profile evidence instead of generic OPC UA breadth.
3. **GTFS + GTFS Realtime** — high public utility and unusually clear leverage from schedule-aware semantic validation.
4. **OGC API Features + CQL2** — GeoRust substrate is finally good enough that conformance/query lockfiles might stick.
5. **STIX 2.1 + TAXII 2.1** — strong security standards case; worth watching for maintainer-energy and policy-scope risk.

Last updated: 2026-03-06



## Frontier queue — 2026-03-06 (74)

1. **UBL + EN16931 + Peppol/PINT** — strongest mix of adoption surface, active release cadence, and missing profile/evidence tooling.
2. **AMWA NMOS** — compelling because official testing already exists but topology/activation evidence is still messy in practice.
3. **SDMX 3.0** — unusually good “machine-readable standards + public API + early Rust substrate” setup for a conformance workbench.
4. **LTI 1.3 + Advantage** — strong certification/replay case now that Rust has credible LTI libraries.
5. **3MF** — conformance-suite momentum and packaging semantics make this more valuable than yet another raw parser.

Last updated: 2026-03-06



## Frontier queue — 2026-03-06 (75)

1. **Crossref 5.4.0 + JATS 1.4** — strongest case in this pass because the transformation/validation seam is active, standards-driven, and now close enough to fresh Rust substrate.
2. **OpenDRIVE + OpenSCENARIO** — official checker infrastructure raises the value of a neutral replay/diff crate above one more parser.
3. **DDEX ERN + MEAD** — compelling because partner onboarding pain is real and Rust is finally getting plausible parser/builder substrate.
4. **OCFL + BagIt Profiles** — preservation workflows would benefit from a boring artifact for transfer/storage bugs, but the maintainer pool is narrower than for publishing or automotive ecosystems.
5. **CCSDS CFDP** — high-value niche where a small, careful replay/evidence layer could materially improve mission integration debugging.

Last updated: 2026-03-06



## Added 2026-03-06 (76)
- **P-0332 (Medium-High)** EPUB 3.3 + EPUBCheck + OPDS 2.0 Interop & Evidence Kit — strong publishing/library value; the sharp idea is validator normalization plus publication/catalog seam debugging.
- **P-0333 (High)** BIDS + NIfTI Conformance & Dataset Evidence Kit — unusually leverageable for research-data QA because the official validator exists but replayable, redactable Rust evidence does not.
- **P-0334 (Medium-High)** STAC 1.1 + STAC API Validation & Replay Kit — real Rust substrate and large ecosystem; replayable query behavior is the differentiator.
- **P-0335 (Medium-High)** LAS 1.4/1.5 + LAZ 1.4 + COPC Interop & Evidence Kit — strong geospatial delivery/QA value if kept on metadata/package semantics rather than analysis.
- **P-0336 (Medium)** MARC 21 + BIBFRAME Conversion Workbench Kit — strategically important migration seam, though probably a narrower maintainer pool than publishing/geospatial data proposals.


## Watchlist additions (2026-03-06-77)
- **P-0337 GA4GH htsget + refget + Crypt4GH Interop & Evidence Kit** — strongest of this pass; unusually good fit for compliance + reference-integrity + redactable evidence.
- **P-0338 xAPI 2.0 + cmi5 Conformance & Replay Kit** — good “profile lockfile + replay” candidate with active Rust substrate.
- **P-0339 NETCONF + YANG + RESTCONF Conformance & Evidence Kit** — promising if kept controller-neutral and capability-lock focused.

## New candidates (2026-03-06, pass 78)
- **P-0342 OpenUSD Core Spec 1.0 + USDZ Conformance & Evidence Kit** — validator-aware scene/package replay and portable bug bundles.
- **P-0343 CityGML 3.0 + CityJSON 2.0 Conformance & Conversion Workbench Kit** — subset-aware validation, conversion-loss reports, and procurement-friendly evidence.
- **P-0344 netCDF + CF Conventions + OPeNDAP Interop & Evidence Kit** — CF-aware validation, subset replay, and semantic dataset diffs.
- **P-0345 CAP 1.2 + IPAWS Interop & Evidence Kit** — profile-pinned emergency-alert validation and redactable exchange bundles.
- **P-0346 MusicXML 4.0 + MEI Interop & Evidence Kit** — notation conversion-loss reporting, semantic diffs, and score bug bundles.


## Frontier queue — 2026-03-06 (79)

1. **WARC + CDXJ + WACZ** — strongest fit for the archive’s missing-middle thesis because the cross-layer preservation/replay seam is clear and Rust substrate now exists.
2. **glTF 2.0 + KTX 2.0** — official validator plus current crate momentum makes a profile/evidence workbench newly plausible.
3. **MCAP + rosbag2** — excellent operational multiplier for robotics teams if kept focused on schema/channel/clock evidence.
4. **miniSEED 3 + StationXML + SeedLink** — very neglected and important, but probably best started with a tight interchange/replay core.
5. **MPEG-DASH + DASH-IF** — useful conformance-wrapper candidate, especially if profile packs stay narrow and validator-first.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (80)

1. **ISO 20022 + CBPR+ / HVPS+ / SEPA** — strongest mix of economic surface, current migration pressure, and missing profile/evidence tooling.
2. **LSP + DAP + LSIF** — unusually high Rust-ecosystem leverage because protocol crates exist but portable interop testing is still weak.
3. **OME-Zarr / NGFF** — official validator + fresh Rust metadata/Zarr substrate makes a conformance-first workbench newly realistic.
4. **WMO GRIB2 + BUFR** — table/version pinning and ecCodes normalization could save real operational pain across weather-data stacks.
5. **FITS + WCS + VOTable** — strong archive/science value if scope stays coordinate- and export-seam focused rather than trying to absorb the whole VO ecosystem.

Last updated: 2026-03-06

## Frontier queue — 2026-03-06 (81)

1. **Apache Iceberg REST Catalog + Delta Kernel / UniForm** — strongest near-term multiplier because open lakehouse adoption is high and the missing value is squarely in the metadata/interop seam.
2. **RDF 1.2 + SPARQL 1.2 + SHACL 1.2** — broad standards surface with real Rust substrate and a very crisp canonicalization/evidence gap.
3. **VCF 4.5 + BCF 2.2 + CSI/Tabix** — especially strong because Rust already has excellent low-level format support, making the missing workbench layer newly plausible.
4. **OData 4.01/4.02 + CSDL** — large practical API surface, but best started with a careful metadata/query core before vendor overlays proliferate.
5. **Amazon Ion + PartiQL** — narrower adopter base, but unusually differentiated and a good fit for a semantic replay workbench.

Last updated: 2026-03-06


## Frontier queue — 2026-03-06 (82)

1. **ONNX + ONNX Runtime + Backend Test** — strongest fit for the archive’s current thesis because the missing value is clearly in model/opset/backend replay rather than raw model loading.
2. **HL7 v2.x + MLLP + Message Profiles** — broad operational footprint and clear need for redacted, replayable evidence in hospital integrations.
3. **OSCAL 1.1.x cross-model workbench** — compelling because Rust now has substrate, but package linkage and validation evidence are still underbuilt.
4. **OMA LwM2M 1.2 + OMNA registry** — high-value IoT/fleet seam if kept object-version and registration-focused.
5. **UN/EDIFACT syntax + directories** — neglected but important partner-onboarding/debugging seam; best started with a tight release/profile core.

Last updated: 2026-03-06


## Frontier queue — 2026-03-07 (95)

1. **Promoted on 2026-03-16 to P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — keep future work focused on task-first decision packs above today's generic search substrate, and keep it visibly distinct from crate health, trust scoring, façade crates, and blessing/stdlib debates.
2. **Edition-drift witness kit** — adjacent to P-0427 and potentially strong if it stays focused on edition deltas and migration receipts rather than general linting.
3. **Cargo explanation receipts for cache/build decisions** — adjacent to P-0428; only worthwhile if it sharpens “why did Cargo do this?” rather than duplicating existing build-insight proposals.
4. **Public syntax / macro expansion evidence kits** — promising only if they sit cleanly between current rustc_public work and existing rustdoc/build proposals.
5. **Unsafe-contract witness corpora** — likely high value, but should be checked against existing unsafe/audit proposals before promotion.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (96)

1. **Cargo test harness/reporting interop kit** — only worthwhile if it sharpens the handoff between libtest/custom harnesses/Cargo reporting instead of duplicating the archive’s existing run-record and test-artifact proposals.
2. **Public-API/boundary release gate kit** — promising as a follow-on above P-0431 if it stays focused on release-review receipts rather than generic linting.
3. **Toolchain profile lock / hardening profile pack** — adjacent to P-0430 and possibly strong if it remains a policy/receipt layer rather than a new distribution channel.
4. **Cargo resolver explanation receipts** — adjacent to P-0432 and only worth adding if it can explain feature-resolution surprises without collapsing back into generic metadata tooling.
5. **Safety-case evidence glue for Rust toolchains** — adjacent to P-0433, but must avoid overpromising certification and instead stay narrowly evidence-oriented.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (97)

1. **Exploit-mitigation profile pack** — adjacent to P-0434/P-0430 and only worth adding if it sharpens hardening-profile receipts instead of duplicating sanitizer/sysroot work.
2. **Single-file package publication handoff kit** — adjacent to P-0435 and promising only if it stays focused on repro/tutorial/archive handoff rather than becoming a new package manager.
3. **Cargo cache contention explainer** — adjacent to P-0436 and worthwhile only if it sharpens “why are these processes blocking?” without scraping too much unstable internals.
4. **Backend bug minimization corpus kit** — adjacent to P-0437 and only strong if it stays repro-oriented rather than trying to benchmark everything.
5. **Reflection/comptime migration receipts** — still promising, but should be revisited only if the language experiment matures enough that a workflow layer is clearer.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (98)

1. **Ergonomic ref-counting workflow receipts** — promising if it focuses on migration/explainability for `.use` / share-style ergonomics rather than becoming a broad smart-pointer framework.
2. **In-place initialization evidence/workbench kit** — newly sharper after this pass, but should avoid duplicating P-0440 and instead focus on constructor/pinning/address-stability receipts.
3. **Cargo rebuild-explainer receipts** — adjacent to P-0438 and only worth adding if it can explain actual Cargo rebuild choices without overclaiming knowledge of unstable internals.
4. **Reflection/comptime adapter packs** — follow-on work above P-0439 if specific downstream categories (schema/CLI/editor/config) prove they need richer annotations.
5. **C++ exception/panic boundary policy kit** — adjacent to P-0441 and only worthwhile if it stays narrowly about boundary policy/evidence instead of generic FFI advice.

Last updated: 2026-03-07


## Frontier queue — 2026-03-07 (99)

1. **Polonius / borrowck transition witness kit** — promising if it stays clearly distinct from P-0442 and focuses on borrow-check outcome drift rather than generic compile-fail workflows.
2. **Namespace release-gate receipts** — adjacent to P-0443 and only worthwhile if it sharpens actual rollout/release review instead of duplicating the planner.
3. **Kernel subsystem waiver matrix kit** — adjacent to P-0444 and only strong if it stays narrowly about waiver policy/evidence and not full build orchestration.
4. **Const docs/report adapters** — adjacent to P-0445 and valuable only if downstream docs/release-note workflows prove they need first-class rendering.
5. **Externally-implementable-items migration kit** — promising if it stays focused on transition planning and capability ledgers rather than broad trait-system theory.

Last updated: 2026-03-07



## Frontier queue — 2026-03-07 (100)

1. **Crate slicing soundness/adoption kit** — newly stronger now that official 2026 goal text and a `cargo-slicer` prototype exist; future work should stay focused on receipts, waivers, and fallback-to-full-crate behavior rather than trying to own slicing end-to-end.
2. **Namespace release-gate receipts** — still adjacent to P-0443 and only worth adding if it sharpens rollout review instead of duplicating the planner.
3. **Pinned-drop / pin-ergonomics casebook kit** — adjacent to P-0447 and only strong if it stays tightly on design feedback receipts rather than generic pin helpers.
4. **Share-trait docs/report adapters** — adjacent to P-0448 and worthwhile only if real teams need first-class rendering or release-note artifacts.
5. **Trait-evolution codemod assists** — adjacent to P-0449 and only worth promoting if a clearly conservative, semver-aware subset emerges.

Last updated: 2026-03-07


## Watchlist additions (2026-03-07-101)
- **P-0451 Cfg Availability Ledger Kit** — broad maintainer leverage if kept ledger-first; avoid drifting into “build a better rustdoc”.
- **P-0450 Parallel Front-End Parity Lab Kit** — strong while stabilization work is active; keep scope on parity receipts and reduced repros, not generic benchmarking.
- **P-0452 Externally Implementable Item Adoption Kit** — promising if it stays semver/migration/diagnostics-focused rather than becoming DI or linker abstraction.
- **P-0453 Safety Contract Consumer Kit** — strategically important, but should prove its value with extraction/diff/runtime receipts before ambitious multi-tool translation.



## Watchlist additions (2026-03-07-102)
- **P-0454 ABI Coherence Profile Kit** — strongest if it stays on whole-program flag contracts, exemption ledgers, and sysroot receipts rather than becoming a generic compiler-flags helper.
- **P-0455 Doctest Extraction & Pipeline Kit** — promising while rustdoc extraction and grouping work are moving; keep scope on manifests, rewrites, and runner receipts instead of rebuilding rustdoc.
- **P-0456 Formality Counterexample Bridge Kit** — strategically important, but should prove value with minimized divergence bundles before ambitious multi-engine orchestration.
- **P-0457 External Toolchain Handshake Kit** — worth pursuing if it remains a contract artifact for non-Cargo orchestrators rather than drifting into “replace Cargo” ambition.



## Watchlist additions (2026-03-07-103)
- **P-0458 Async Dyn Transition Kit** — strong while async dyn support is still converging; keep scope on recipe comparison and migration receipts rather than broad async refactoring.
- **P-0459 Clippy Safety Profile & Waiver Kit** — high practical leverage if it stays artifact-first and does not overclaim certification or official policy status.
- **P-0460 Unsafe Field Invariant Ledger Kit** — strategically novel, but should prove value with a tiny vocabulary and conservative mutation witnesses before deeper analysis.
- **P-0461 Edition Drift Witness Kit** — broadly adoptable if it remains a rehearsal/evidence layer above `cargo fix --edition` instead of becoming a generic codemod engine.



## Frontier queue — 2026-03-07 (104)

1. **Invocation-reuse compatibility kit** — newly stronger now that “Incremental Systems Rethought” is a 2026 goal; only worth adding if it sharpens `check`/`build`/`clippy` compatibility receipts instead of duplicating shared-cache and build-analysis proposals.
2. **Edition-scoped API surface planner** — promising after the new standard-library-across-editions goal, but only if it stays on migration/review artifacts rather than generic docs rendering.
3. **Open-enum ABI readiness kit** — potentially strong if it remains narrowly about extension/ABI receipts for separately compiled boundaries rather than becoming another broad enum helper crate.
4. **BorrowSanitizer suppression / expectation pack** — adjacent to P-0465 and only worthwhile if real teams need structured expectation files beyond evidence bundles.
5. **Sized-hierarchy docs/report adapters** — adjacent to P-0464 and worth revisiting only if release-note or rustdoc workflows prove they need first-class rendering.

Last updated: 2026-03-07


## Watchlist additions (2026-03-07-104)
- **P-0462 Crate Slicing Soundness & Adoption Kit** — strongest if it stays on candidate/fallback/benefit receipts rather than turning into a new slicer.
- **P-0463 Libtest JSON Interop Kit** — broad leverage if it remains schema-lock and interop focused instead of becoming a runner replacement.
- **P-0464 Sized Hierarchy & Extern-Type Readiness Kit** — strategically useful if it stays audit-first and does not overclaim final language semantics.
- **P-0465 BorrowSanitizer Workflow & Evidence Kit** — high-value if it remains finding-bundle oriented and does not pretend a clean run proves safety.

## Frontier queue — 2026-03-07 (105)

1. **Python wheel ABI / free-threading shipkit** — newly strong because PyO3/maturin/Python docs now make the compatibility seam explicit; future work should stay on wheel-policy and release receipts rather than becoming a general Python packaging tool.
2. **Apple XCFramework / SwiftPM shipkit** — newly strong because Swift bindings and XCFramework helpers already exist; the sharper missing layer is slice/checksum/privacy/origin receipts above them.
3. **Cargo rebuild/cache explanation receipts** — still promising because the survey keeps pointing at build/storage pain, but only worthwhile if it sharpens reviewable decisions instead of duplicating existing build-insight proposals.
4. **Sanitizer expectation/suppression packs** — adjacent to P-0434/P-0465 and only worth promoting if teams clearly need structured expectation layers beyond evidence bundles.
5. **Python/Apple release-drift diffing** — promising follow-on work only after P-0466/P-0467 stabilize their core receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-105)
- **P-0466 Python Wheel ABI & Free-Threading ShipKit** — strongest if it remains policy/matrix/receipt-first and does not drift into a new upload tool.
- **P-0467 Apple XCFramework & SwiftPM ShipKit** — strongest if it remains slice/checksum/privacy/origin-first and does not become a full Xcode generator.


## Frontier queue — 2026-03-07 (106)

1. **Cargo resolver explanation receipts** — promoted to **P-0468** because Cargo's resolver/tree/plumbing surfaces are now strong enough that the sharper missing layer is a feature/version/duplicate-build why-bundle, not another metadata dump.
2. **Cargo rebuild explanation receipts** — promoted to **P-0469** because survey/build-dir/relink evidence now makes a compact per-run rebuild witness sharper than generic performance dashboards.
3. **Cargo cache contention explainer** — still promising, but only if later work stays narrowly on blocking/lease facts instead of duplicating P-0469's broader rebuild story.
4. **Public-API/boundary release gate kit** — still promising as a follow-on above P-0431 and P-0438 if it remains release-review-first.
5. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-106)
- **P-0468 Cargo Resolver Explanation Kit** — strongest if it remains cause-chain / duplicate-build / diff-first and does not collapse back into raw graph export.
- **P-0469 Cargo Rebuild Explanation Kit** — strongest if it remains a per-run why-bundle and does not turn into a full analytics warehouse.


## Frontier queue — 2026-03-07 (107)

1. **Cargo artifact handoff kit** — promoted to **P-0471** because Cargo’s produced-artifact JSON, unstable `artifact-dir`, and output-tracking work now make a downstream handoff manifest sharper than another bespoke release script.
2. **Cargo package review kit** — promoted to **P-0470** because packaging docs still imply manual inspection and `.crate` drift review; the missing layer is a publish-readiness receipt.
3. **Cargo lints adoption receipts** — still promising if it stays on profile inheritance / waiver / workspace receipt workflows rather than becoming a lint runner.
4. **Artifact-sidecar contract kit** — adjacent to P-0471 and only worth adding if SBOM or similar sidecars converge enough to justify a smaller standardized vocabulary.
5. **Publish-surface / provenance join layer** — promising follow-on work only after P-0470 and P-0015 have stable core artifacts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-107)
- **P-0470 Cargo Package Review Kit** — strongest if it remains review/diff/policy-first and does not become a new publish orchestrator.
- **P-0471 Cargo Artifact Handoff Kit** — strongest if it remains manifest/receipt-first and does not drift into a full release platform.


## Frontier queue — 2026-03-07 (108)

1. **Docs.rs build parity / issue bundles** — promoted to **P-0472** because docs.rs now exposes enough documented environment and metadata surface that the sharper missing layer is a preflight/diff/limit receipt, not another docs runner.
2. **Cargo lints adoption receipts** — promoted to **P-0473** because stable `workspace.lints` and emerging Cargo-lint surfaces now make inheritance / waiver / rollout artifacts sharper than another lint wrapper.
3. **Artifact-sidecar contract kit** — still promising, but only if SBOM or related sidecars converge enough to justify a compact common vocabulary above P-0471.
4. **Publish-surface / provenance join layer** — still promising once P-0470 and P-0015 have stable core receipts.
5. **Docs coverage review bundles** — promising follow-on work only if rustdoc coverage JSON and docs maintenance workflows converge enough to justify a separate receipt layer from P-0472.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-108)
- **P-0472 Docs.rs Build Parity & Evidence Kit** — strongest if it remains receipt/diff/limit-first and does not become a new docs host or full builder emulator.
- Treat **P-0472** as the current center of gravity for docs.rs parity work: deepen fidelity classes, hosted-build imports, and conservative drift-cause reports before inventing another neighboring docs-support crate.
- **P-0473 Cargo Lints Adoption Receipt Kit** — strongest if it remains inheritance/waiver/rollout-first and does not become a generic lint runner.


## Frontier queue — 2026-03-07 (109)

1. **Cargo config-layer receipts** — promoted to **P-0474** because Cargo now has enough config substrate that the sharper missing layer is an effective-config / origin-trace / redacted support bundle, not another parser.
2. **Rustdoc mergeable-info handoff** — promoted to **P-0475** because `doc.parts` / merge / finalize substrate now exists, but ordinary maintainers still lack a manifest / compatibility / finalize receipt workflow.
3. **Docs coverage review bundles** — still promising, but only if rustdoc coverage and docs maintenance workflows converge enough to justify a layer distinct from P-0472 and P-0475.
4. **Publish-surface / provenance join layer** — still promising once P-0470 and P-0015 have stable core receipts.
5. **Artifact-sidecar contract kit** — still promising only if SBOM or adjacent sidecars converge enough to justify a compact vocabulary above P-0471.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-109)
- **P-0474 Cargo Config Layer Receipt Kit** — strongest if it remains origin/redaction/diff-first and does not become a generic config framework.
- **P-0475 Rustdoc Mergeable Info Handoff Kit** — strongest if it remains manifest/compatibility/finalize-first and does not become a new docs host or UI.


## Frontier queue — 2026-03-07 (110)

1. **Docs coverage review bundles** — promoted to **P-0476** because rustdoc coverage JSON and rustdoc JSON now make a review bundle sharper than another docs scorecard.
2. **Publish-surface / provenance join layer** — promoted to **P-0477** because package review, registry checksums, and trusted-publishing facts now make a post-publish receipt sharper than another CI publisher.
3. **Artifact-sidecar contract kit** — still promising only if SBOM or adjacent sidecars converge enough to justify a compact vocabulary above P-0471.
4. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than broad rebuild analytics.
5. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-110)
- **P-0476 Rustdoc Coverage Review Bundle Kit** — strongest if it remains API-aware docs review and does not become a generic dashboard.
- **P-0477 Cargo Publish Receipt Join Kit** — strongest if it remains checksum/identity/join-first and does not become another publish platform.



## Frontier queue — 2026-03-07 (111)

1. **Cargo future-incompat triage** — promoted to **P-0478** because Cargo already has display/report substrate; the sharper missing layer is a durable owner/waiver/remediation bundle.
2. **Artifact-sidecar contract kit** — promoted to **P-0479** because sidecar conventions are now emerging enough that a narrow attachment/schema contract is sharper than another general artifact exporter.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than broad rebuild analytics.
4. **Python/Apple release-drift diffing** — still promising follow-on work once P-0466 and P-0467 have stable receipt vocabularies.
5. **Public-API release gate kit** — still promising as a follow-on above P-0431 and P-0438 if it remains release-review-first.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-111)
- **P-0478 Cargo Future-Incompat Triage Kit** — strongest if it remains owner/waiver/remediation-first and does not become another generic diagnostics viewer.
- **P-0479 Cargo Artifact Sidecar Contract Kit** — strongest if it remains attachment/schema/diff-first and does not turn into a second general artifact manifest layer.


## Watchlist additions (2026-03-07-112)
- **P-0480 Cargo Global Cache Policy & GC Receipt Kit** — promising if it stays on Cargo-home inventory, dry-run policy, and cleanup receipts instead of drifting into a general-purpose disk janitor.
- **P-0481 Doctest Runtool Profile Kit** — promising if it stays on runner profiles, target matrices, and ignore audits instead of becoming a broad cross-device test framework.


## Frontier queue — 2026-03-07 (113)

1. **Python/Apple release-promise drifting** — promoted to **P-0482** because foreign-language shipping substrate is now real enough that the sharper missing layer is a consumer-promise diff/impact artifact, not another builder.
2. **Public-API release readiness bundles** — promoted to **P-0483** because semver checks, public-API diffing, public-dependency work, and docs-surface metrics now make a joined release-review artifact sharper than another individual analyzer.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger support-pack refresh** — still promising only if it becomes a compact compatibility/receipt workflow above P-0083 rather than another general debugger wishlist.
5. **Foreign-SDK consumer doctor** — still promising follow-on work once P-0482 stabilizes its promise vocabulary and receipts.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-113)
- **P-0482 SDK Release Promise Drift Kit** — strongest if it remains consumer-promise/diff/impact-first and does not become a second build-and-upload tool.
- **P-0483 Public API Readiness Bundle Kit** — strongest if it remains joined public-contract review and does not collapse back into a generic compatibility platform.


## Added 2026-03-07 (114)
- **P-0484 Toolchain & Target Support Contract Kit** — strong day-to-day maintainer value because it joins support intent, observed environment, docs posture, and drift into one contributor/reviewer artifact.
- **P-0485 Verification Campaign Workbench Kit** — strategic assurance value because it gives Rust’s growing verification ecosystem one honest obligation/trust/policy/evidence bundle instead of more scattered logs and notes.


## Frontier queue — 2026-03-07 (115)

1. **Debuggability support contracts** — promoted to **P-0486** because Rust already has meaningful debugging substrate, and the sharper missing layer is now a support-posture/symbol-receipt workflow rather than another debugger wishlist.
2. **Foreign-SDK consumer doctor** — promoted to **P-0487** because P-0482 covered producer-side release promises, but downstream adoption diagnosis is still its own unserved seam.
3. **Cargo cache contention explainer** — still promising if it stays narrowly on blocking/lease facts rather than duplicating P-0469 or P-0480.
4. **Debugger formatter/conformance refresh** — still promising only if it becomes a clean follow-on above P-0083 and P-0486 instead of a broad debugger platform.
5. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-115)
- **P-0486 Debuggability Support Contract Kit** — strongest if it remains support-posture/symbol-layout/diff-first and does not become a new debugger UI or crash backend.
- **P-0487 Foreign SDK Consumer Doctor Kit** — strongest if it remains consumer-diagnosis-first and does not collapse back into a second shipkit or release bot.


## Added 2026-03-07 (116)
- **P-0488 Cargo Minimal-Version Witness Kit** — strong day-to-day crate-maintainer value because it turns lower-bound checking into one honest proof/blame/waiver artifact instead of a flaky nightly CI job and scattered notes.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — strategically useful for Cargo-adjacent tooling because it gives scripts and helpers a migration path away from internal build-dir scraping as Cargo’s layout evolves.


## Frontier queue — 2026-03-07 (116)

1. **Lower-bound dependency witnesses** — promoted to **P-0488** because Cargo’s lower-bound substrate and new minimum-version lint now make a reviewable witness sharper than a generic dependency updater or compatibility platform.
2. **Build-dir consumer transitions** — promoted to **P-0489** because Cargo’s evolving build-dir story now clearly creates a tooling-migration seam distinct from cache policy or final-artifact handoff.
3. **Debugger formatter/conformance refresh** — still promising only if it becomes a clean follow-on above P-0083 and P-0486 instead of a broad debugger platform.
4. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
5. **Cargo cache contention explainer** — still promising if it stays narrowly on live blocking facts rather than duplicating P-0436, P-0480, or P-0489.

Last updated: 2026-03-07

## Watchlist additions (2026-03-07-116)
- **P-0488 Cargo Minimal-Version Witness Kit** — strongest if it remains lower-bound-proof/blame/waiver-first and does not turn into a generic dependency updater.
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — strongest if it remains audit/path-contract/transition-first and does not collapse into another cache manager or profiler.


## Added 2026-03-07 (117)
- **P-0490 Cargo Lock Contention Witness Kit** — high practical value because it gives teams one honest artifact for IDE/manual/CI lock waits instead of scattered anecdotes and workaround folklore.
- **P-0491 Debugger Visualizer Compatibility Kit** — useful narrower follow-on because embedded visualizer assets are now a real stable surface, but their backend compatibility is still not boring to review.


## Frontier queue — 2026-03-07 (117)

1. **Cargo lock-contention witnesses** — promoted to **P-0490** because Cargo and rust-analyzer now document enough blocking substrate that the sharper missing layer is a live wait/collision/mitigation artifact.
2. **Debugger visualizer compatibility receipts** — promoted to **P-0491** because stable embedded NatVis/GDB support now makes a narrow backend-matrix follow-on sharper than another broad debugger toolkit.
3. **Other foreign package ecosystems** — still promising only after the Python/Apple consumer-diagnosis vocabulary proves stable enough to generalize.
4. **Cargo compile-time-deps workflow receipts** — still promising if it stays narrowly on tool-only build surfaces and does not collapse back into generic editor/Cargo performance tooling.
5. **Build-std adoption receipts** — still promising if the unstable substrate sharpens enough that a new workflow layer would not duplicate P-0116 or related build-std ideas.

## Watchlist additions (2026-03-07-117)
- **P-0490 Cargo Lock Contention Witness Kit** — strongest if it remains live-blocking/wait/mitigation-first and does not become another profiler, scheduler, or cache manager.
- **P-0491 Debugger Visualizer Compatibility Kit** — strongest if it remains asset/back-end matrix first and does not collapse into P-0083’s formatter-pack ambition or P-0486’s broader support contract.


## Added 2026-03-07 (119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — high practical leverage because Cargo now has a documented tool-only compile surface, but maintainers still lack one honest artifact for what editor/wrapper workflows actually built and when they must fall back to a real build.
- **P-0495 Cargo Artifact Dependency Adoption Kit** — strong targeted leverage because Cargo artifact dependencies are real enough to justify a contract/env-var/fallback layer, but still too unstable and niche for a simple “just use it” answer.


## Frontier queue — 2026-03-07 (119)

1. **Compile-time-deps workflow receipts** — promoted to **P-0494** because Cargo now explicitly documents a tool-only compile surface intended for tools, while the `cargo check` policy boundary keeps the missing layer firmly in parity/fallback artifacts rather than build correctness claims.
2. **Artifact-dependency adoption receipts** — promoted to **P-0495** because Cargo’s artifact-dependency substrate plus RFC 3028 / RFC 3176 now make a contract/target/env-var/fallback layer sharper than another generic build helper.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-119)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — strongest if it remains tool-surface/parity/fallback-first and does not turn into a rust-analyzer fork, a new checker, or a false equivalence layer between `cargo check` and `cargo build`.
- **P-0495 Cargo Artifact Dependency Adoption Kit** — strongest if it remains contract/target/env-var/fallback-first and does not collapse into another final-artifact exporter, package manager, or Cargo syntax proposal.


## Added 2026-03-07 (120)
- **P-0496 Cargo Vendor & Source Parity Kit** — high practical leverage because vendored and source-replaced dependency workflows are common, yet maintainers still lack one honest artifact for where resolution actually came from and whether offline claims are true.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — valuable cross-domain leverage because Rust already has real CPU-feature substrate, but maintainers still lack one compact release artifact for hardware-support promises and fallback posture.


## Frontier queue — 2026-03-07 (120)

1. **Vendor/source-parity receipts** — promoted to **P-0496** because Cargo now has serious source-management substrate, while the sharper missing layer is a source-origin and offline-honesty artifact rather than another mirror or registry.
2. **CPU baseline/runtime-dispatch contracts** — promoted to **P-0497** because Rust already has codegen knobs and runtime detection, while the sharper missing layer is a downstream hardware-support promise rather than another SIMD abstraction.
3. **Other foreign package ecosystems** — still promising once the Python/Apple and generic foreign-consumer vocabulary proves stable enough to generalize to Node/npm, NuGet, or similar ecosystems.
4. **Invocation-reuse compatibility kit** — still promising if the 2026 incremental-systems work sharpens a clean check/build/clippy reuse receipt distinct from P-0490 and P-0494.
5. **Build-std adoption receipts** — still promising only if a new workflow layer would sharpen support/adoption facts without duplicating P-0430 or related sanitizer/toolchain proposals.

## Watchlist additions (2026-03-07-120)
- **P-0496 Cargo Vendor & Source Parity Kit** — strongest if it remains source-origin/parity/offline-honesty-first and does not collapse into another mirror, registry, or package-review system.
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** — strongest if it remains hardware-support/dispatch/fallback-first and does not turn into another SIMD abstraction, benchmark harness, or compiler-wrapper fantasy.


## Added 2026-03-08 (122)
- **P-0500 JAR/JNI Native ShipKit** — promoted because the JVM now looks like the next clean foreign-package sibling: real JNI/Maven substrate exists, but maintainers still lack an honest classifier/load/native-access contract.

## Frontier queue — 2026-03-08 (122)

1. **JAR/JNI ship contracts** — promoted to **P-0500** because the package/runtime contract has become sharper than generic Rust/Java interop framing.
2. **Cross-ecosystem support-contract generalization** — still promising once enough producer-side package-contract vocabularies stabilize.
3. **Invocation-reuse compatibility kit** — still promising if incremental-systems work creates a distinct check/build/clippy reuse receipt.
4. **Build-std adoption receipts** — still promising only when it can stay adoption-first rather than duplicating existing sysroot evidence work.


## Added 2026-03-08 (123)
- Promote **P-0501 RubyGems Native Extension ShipKit** as the next concrete foreign-package ecosystem seam.
- Use `meta/foreign-package-contract-vocabulary.md` before any future attempt to generalize Python/Apple/Node/NuGet/JVM/Ruby shipping contracts.
- Keep future foreign-package work biased toward **review artifacts** (artifact matrices, loader receipts, support-risk bundles) rather than raw binding/framework substrate.

## Frontier queue — 2026-03-08 (123)
1. Cross-ecosystem support-contract vocabulary and schemas
2. RubyGems fat-gem/package-contract fixtures
3. Invocation-reuse compatibility receipts
4. Build-std adoption/support receipts



## Debug support stack refresh — 2026-03-08 (126)

1. **P-0486 Debuggability Support Contract Kit** — promoted as the strongest next non-Cargo incubation target because debugging remains a top ecosystem pain while Rust already has enough substrate that the missing layer is now a support-posture / symbol-layout / drift bundle rather than another debugger wishlist.
2. **P-0493 Source Path Hygiene & Debug Source Kit** — strengthened because path trimming/remapping and `rust-src` / `rustc-dev` lookup now clearly form their own support seam instead of a footnote inside broad debuggability.
3. **P-0491 Debugger Visualizer Compatibility Kit** — remains real but narrower; strongest once it reuses broader support vocabulary instead of acting like a universal debugger platform.

### Watchlist additions (2026-03-08-126)
- **P-0486 Debuggability Support Contract Kit** — strongest if it remains support-posture / symbol-layout / diff-first and does not become a new debugger UI, crash backend, or giant IDE integration.
- **P-0493 Source Path Hygiene & Debug Source Kit** — strongest if it remains remap/trim-path/source-component diagnosis first and does not collapse into P-0486 or a full source-packaging system.
- **P-0491 Debugger Visualizer Compatibility Kit** — strongest if it remains asset/backend-matrix-first and does not silently absorb broader symbol/source support posture.

## Update 2026-03-08 (137) — debuggability support implementation refresh

- Treat **P-0486** as the current center of gravity for the debug-support stack.
- Prefer a tiny receiver-facing bundle: `debuggability.receipt`, `symbol-layout.manifest`, `visualizer.manifest`, `support-posture.report`, and optional `debuggability-drift.diff`.
- Keep the distinction sharp between **broad support posture** (P-0486), **source lookup / path hygiene** (P-0493), and **visualizer conformance** (P-0491).


## Update 2026-03-17 (215) — debuggability support productization pass

- Treat **P-0486 Debuggability Support Contract Kit** as the current center of gravity for the debug-support stack.
- Prefer a tiny receiver-facing bundle: `debuggability.receipt`, `symbol-layout.manifest`, `visualizer.manifest`, `support-posture.report`, `support-class.policy`, `artifact-handoff.manifest`, `source-lookup-impact.report`, and optional `debuggability-drift.diff`.
- Keep the distinction sharp between **broad support posture** (P-0486), **source lookup / path hygiene diagnosis** (P-0493), **visualizer compatibility** (P-0491), and **runtime symptom/triage support** (P-0525).
- Best next passes should add scenario bundles, conservative evidence classes, and small adoption paths for P-0486 instead of inventing another generic debugger-support crate.

## 2026-03-08 refresh — native build upstream fit

### Best next archive move in this frontier
- Add example bundles and fixture notes that prove the stack layers on **real Cargo surfaces** (`--message-format=json`, `links` overrides, manifest metadata) rather than inventing a parallel universe.

### Planning rule
- Prefer upgrades that make P-0046 / P-0059 / P-0058 easier to align with upstream Cargo evolution (metabuild, multiple-build-scripts, reduced build-script reliance) over adding another native-build proposal.


## Update 2026-03-08 (132) — cargo tool-workflow stack

- Treat **P-0494**, **P-0490**, and **P-0489** as one adjacent stack rather than three blurry editor/tooling ideas.
- Prefer fixture/schema work and shared vocabulary for `workflow_role`, `target_dir_policy`, and `manual_review_required`.
- Incubation order for this stack should currently lean **P-0494 → P-0490 → P-0489**.


## Update 2026-03-08 (134) — cargo lock contention implementation refresh

- Treat **P-0490 Cargo Lock Contention Witness Kit** as the next tool-workflow-adjacent proposal that most benefits from fixture/schema work rather than another proposal-count increase.
- Prefer a tiny receiver-facing bundle: `cache-root.manifest`, `lock-wait.receipt`, `collision-diagnosis.report`, and `mitigation.plan`.
- Keep the distinction sharp between **what tool workflow was used** (P-0494), **who blocked whom** (P-0490), and **which consumers scrape Cargo internals** (P-0489).
- Best next passes should add scenario bundles, redaction rules, and conservative diff vocabularies for P-0490 instead of inventing another generic Cargo IDE-friction proposal.


## Update 2026-03-08 (138) — debugger visualizer implementation refresh

- Treat **P-0491** as the narrow visualizer-conformance layer inside the debug-support stack, not as a universal debugger product.
- Prefer a tiny receiver-facing bundle: `visualizer-policy`, `visualizer-assets.manifest`, `backend-matrix.receipt`, `render-golden.report`, `embed-vs-external.report`, and optional `visualizer-drift.diff`.
- Keep the distinction sharp between **broad support posture** (P-0486), **source lookup / path hygiene** (P-0493), and **visualizer compatibility** (P-0491).
- Best next passes should add scenario bundles and conservative verdict vocabulary for NatVis target limits, GDB safe-path refusal, and explicit external/manual backend lanes instead of inventing another generic debugger proposal.


## Update 2026-03-08 (139) — visualizer activation/external-lane refresh

- Keep **P-0491** explicitly split across asset discovery, activation/trust, and backend support verdicts.
- Treat LLDB-family support as an explicit external/manual formatter lane unless stronger Rust-side embedding evidence exists.
- Prefer conservative receipts over fake backend parity claims.


## Update 2026-03-08 (146) — native-deps mode/policy refresh

- Treat **P-0058 native-deps-kit** as a sharper implementation target again, but only if it stays focused on **contract + mode lock + policy report + doctor receipt**.
- Prefer tiny receiver-facing artifacts: `native-contract`, `resolution-mode.lock`, `vendoring-policy.report`, `backend-attempts.receipt`, and `consumer-doctor`.
- Keep the distinction sharp between **buildscript UX** (P-0046), **buildscript testability** (P-0059), and **native mode/policy truth** (P-0058).
- Best next passes should add scenario bundles and conservative vocabulary for additive vendoring, explicit env-forced internal builds, and override handoff rather than inventing another generic cross-platform native-build proposal.

## Update 2026-03-08 (147) — source-parity implementation refresh

- Treat **P-0496 Cargo Vendor & Source Parity Kit** as a sharper implementation target again, but only if it stays focused on **source identity + coverage truth + conservative parity verdicts**.
- Prefer tiny receiver-facing artifacts: `source-contract.toml`, `source-origin.receipt.json`, `source-parity.lock`, `source-coverage.report.json`, and `vendor-parity.report.json`.
- Keep the distinction sharp between **mirror/air-gap transfer tooling** (P-0001 / P-0018), **package/publish review** (P-0038 / P-0470), and **vendored/source parity review** (P-0496).
- Best next passes should add scenario bundles and conservative vocabulary for logical-source alias splits, git-history requirements, and path-dependency spillover rather than inventing another generic offline Cargo proposal.



## Update 2026-03-08 (148) — cargo lock contention topology note

- **P-0490 Cargo Lock Contention Witness Kit** rose because the official substrate is now explicit enough that the next repo work should freeze **root-sharing topology** and **wrapper-context** artifacts, not just generic wait receipts.
- Keep the distinction sharp between **shared roots** (target-dir, build-dir, package-cache), **live waits**, and **wrapper/cache-mode drift**.
- Best next passes should add real tiny witness bundles for one mixed-tool workspace before inventing any scheduler, daemon, or broader Cargo performance umbrella.


- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should now freeze comparison baselines and override-command provenance explicitly so label-scoped runs, paired build-script overrides, and relative wrappers stay reviewable instead of being normalized away.


## Added 2026-03-08 (150)
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — should now freeze selection coverage and workspace invocation topology explicitly so `allTargets`, `check.workspace`, startup leakage, and linked-project once-mode runs do not get normalized away as generic editor noise.


## Update 2026-03-08 (155) — resolver feature-origin refresh

- **P-0468 Cargo Resolver Explanation Kit** rose again because the next high-value artifact is now a compact **feature-origin report**.
- Keep the distinction sharp between **feature causes**, **feature intent**, **manifest origin**, and **feature authoring origin / activation preconditions**.
- Best next passes should add tiny scenario bundles and conservative vocabulary for hidden optional aliases, weak forwarding, and misleading feature-like cfg names instead of inventing another generic Cargo feature browser.


## Update 2026-03-08 (156) — resolver dependency-identity refresh

- **P-0468 Cargo Resolver Explanation Kit** rose again because the next high-value artifact is now a compact **dependency-identity report**.
- Keep the distinction sharp between **local dependency key**, **original package name**, **feature-reference token**, and **metadata / index / publish-surface field mapping**.
- Best next passes should add tiny scenario bundles and conservative vocabulary for renamed optional dependencies, unsupported inherited renames, and registry-surface mismatches instead of inventing another generic Cargo feature browser or manifest linter.


## Addendum (2026-03-09): async determinism stack
- **P-0104 Deterministic Simulation Kit** now looks more credible as a cross-backend artifact/adaptor layer: simulation profile, backend capability receipt, fault plan, transcript, and replay/minimization bundle.
- Keep it distinct from **P-0114 Distributed Systems Hardship Harness Kit**, which should own curated hardship/profile suites rather than the general bundle/receipt substrate.
- Keep it distinct from **P-0073 Async Replay Debugger Kit** and **P-0066 Determinism Sim Kit**, which target different truth surfaces.

## 2026-03-09 refresh — passkey lab capability receipts and comparability truth

### Main judgment
- The best next move for **P-0200** is not more protocol breadth; it is stronger artifact contracts for scenario truth, runner capability truth, and comparability truth.
- A Chromium-class virtual-authenticator lane looks like the right first automation baseline.
- Firefox/geckodriver should currently be treated as an explicitly cautionary lane rather than silently promoted into broad browser-parity claims.

### Immediate follow-ons
1. Freeze `scenario-profile`, `runner-capability.receipt`, and `compatibility-matrix.report` before expanding to more overlays.
2. Keep SPC and similar payment/auth overlays explicit.
3. Add manual-device and certification-import lanes only after the core bundle contract is stable.


## Update 2026-03-16 (172) — async transition and BorrowSanitizer evidence refresh

- Treat **P-0458 Async Dyn Transition Kit** as a stronger cross-ecosystem transition workbench now that the official 2026 async story explicitly includes `async fn in dyn trait`.
- Treat **P-0465 BorrowSanitizer Workflow & Evidence Kit** as a sharper lane inside the broader sanitizer/debugging frontier, not as a generic sanitizer wrapper.
- Prefer tiny receiver-facing bundles in both cases: recipe/allocation/migration receipts for P-0458, and profile/boundary/finding/reduction receipts for P-0465.
- Keep the distinction sharp between **language-transition artifacts**, **general sanitizer workflows**, **debug-support contracts**, and **higher-level verification imports**.

## Update 2026-03-16 (196) — crate capability contract lane

- Treat **P-0510 Crate Capability Contract & Interop Profile Kit** as a top-tier follow-on to **P-0509**: task-first crate choice still lacks a good producer-side fact surface.
- Prefer tiny receiver-facing artifacts: `capability-contract`, `observed-capabilities.receipt`, `interop-exports.report`, `profile-conformance.report`, and `capability-diff.report`.
- Keep the distinction sharp between **producer-side capability contracts** (P-0510), **task-first decision packs** (P-0509), **item-level availability truth** (P-0451), **whole-project support contracts** (P-0484), and **slice tools** like MSRV/API/semver/security analysis.


## Update 2026-03-16 (197) — shared ecosystem interop profile lane

- Treat **P-0511 Crate Interop Profile Pack Kit** as the missing shared-contract layer next to **P-0509** and **P-0510**: task-first choice and producer-side support truth still do not define a reusable ecosystem boundary by themselves.
- Prefer tiny receiver-facing artifacts: `interop-profile-pack`, `static-conformance.receipt`, `behavioral-probe.report`, `pair-compatibility.report`, and `migration-hazards.report`.
- Keep the distinction sharp between **shared ecosystem interop profiles** (P-0511), **producer-side capability contracts** (P-0510), **task-first decision packs** (P-0509), **trait-evolution / EII migration planners** (P-0449 / P-0452), and **public-API / semver slice tools** like `cargo-semver-checks`.


## Update 2026-03-16 (200) — crate upgrade-pack lane

- Treat **P-0514 Crate Upgrade Pack Kit** as a top-tier follow-on to the broader crate-supportiveness frontier: semver/public-API evidence and release automation still do not tell downstream users how to move between crate releases.
- Prefer tiny receiver-facing artifacts: `upgrade-pack`, `upgrade-hazards.report`, `fixup-hints.receipt`, `migration-recipe.manifest`, and `upgrade-diff.report`.
- Keep the distinction sharp between **release-to-release upgrade packs** (P-0514), **SemVer/public-API evidence** (P-0244 / P-0483), **compile-time guidance** (P-0512), **runtime handoff** (P-0513), and **release automation/changelog tooling**.


## Update 2026-03-17 (203) — crate performance-envelope lane

- Treat **P-0517 Crate Performance Envelope Pack Kit** as the next missing layer inside the broader crate-supportiveness frontier: setup scenarios and benchmark tools still do not tell downstream users which performance tradeoff they are actually buying.
- Prefer tiny receiver-facing artifacts: `perf-pack`, `perf-surface.receipt`, `perf-scenario.report`, `perf-recipe.manifest`, `perf-budget.report`, and `perf-diff.report`.
- Keep the distinction sharp between **configuration scenarios** (P-0516), **performance envelopes** (P-0517), **generic benchmark/profiling substrate**, and **hosted CI perf services**.



## Update 2026-03-17 (207) — crate resource-surface lane

- Treat **P-0521 Crate Resource Surface Pack Kit** as the next missing layer inside the broader crate-supportiveness frontier: performance envelopes, observability, authority posture, and lifecycle truth still do not tell downstream users what queues, buffers, pools, caches, workers, and bursts they are actually buying.
- Prefer tiny receiver-facing artifacts: `resource-pack`, `resource-surface.receipt`, `capacity-profile.manifest`, `saturation-behavior.report`, `resource-budget.report`, and `resource-diff.report`.
- Keep the distinction sharp between **configuration scenarios** (P-0516), **performance envelopes** (P-0517), **observability surfaces** (P-0518), **authority surfaces** (P-0519), **lifecycle surfaces** (P-0520), and **resource surfaces** (P-0521).


## Update 2026-03-17 (210) — crate example-surface lane

- Treat **P-0524 Crate Example Surface Pack Kit** as the next missing layer inside the broader crate-supportiveness frontier: task-first crate choice, failure-path guidance, setup scenarios, and downstream test support still do not tell downstream users what the smallest officially supported starting point actually is.
- Prefer tiny receiver-facing artifacts: `example-surface-pack`, `example-catalog.receipt`, `quickstart-path.manifest`, `adoption-scenario.manifest`, `example-environment.report`, `docs-example-linkage.report`, and `example-surface-diff.report`.
- Keep the distinction sharp between **task-first crate choice** (P-0509), **failure-path guidance** (P-0512), **configuration scenarios** (P-0516), **downstream test surfaces** (P-0523), **docs rendering / docs.rs parity / hosting**, and **receiver-facing example-surface contracts** (P-0524).

## Update 2026-03-17 (209) — crate test-surface lane

- Treat **P-0523 Crate Test Surface Pack Kit** as the next missing layer inside the broader crate-supportiveness frontier: setup scenarios, authority posture, lifecycle truth, and persistence/resource lanes still do not tell downstream users how a crate expects their tests to be written.
- Prefer tiny receiver-facing artifacts: `test-surface-pack`, `fixture-catalog.receipt`, `fake-backend.report`, `scenario-corpus.manifest`, `deterministic-seam.report`, and `test-surface-diff.report`.
- Keep the distinction sharp between **generic testing substrate**, **runtime/setup support surfaces**, **domain-specific conformance labs**, and **receiver-facing test-surface contracts**.


## Update 2026-03-17 (218) — crate test-surface product plan

- Treat **P-0523 Crate Test Surface Pack Kit** as a real `0.1` candidate now that the archive has explicit artifacts for support levels, environment requirements, and scenario witnesses.
- Keep the distinction sharp between **generic testing substrate**, **runtime/setup support surfaces**, **domain-specific conformance labs**, and **receiver-facing test-surface contracts**.
- The missing value for **P-0523** is not another mock crate or test runner; it is the boring workflow that turns fixtures, fakes, deterministic seams, topologies, and named scenarios into a compact downstream-testing contract.
- Prefer a small cargo subcommand plus library with `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` over a giant hosted or execution-heavy test platform.


## Update 2026-03-17 (222) — crate resource-surface product plan

- Treat **P-0521 Crate Resource Surface Pack Kit** as a real `0.1` candidate now that the archive has explicit artifacts for boundedness meaning, pressure-signal guidance, and observed saturation truth.
- Keep the distinction sharp between **configuration scenarios** (P-0516), **performance envelopes** (P-0517), **observability contracts** (P-0518), **lifecycle truth** (P-0520), and **receiver-facing resource-surface contracts** (P-0521).
- The missing value for **P-0521** is not another queue/cache/limiter/runtime-metrics stack; it is the boring workflow that turns resource classes, bounds, saturation semantics, and pressure signals into a compact downstream-support contract.
- Prefer a small cargo subcommand plus library with `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` over a giant instrumentation or profiling platform.
- Treat **P-0521** as sharper now that admission order, backlog ownership, capacity shrink, and acquire fate are first-class review objects rather than vague operator folklore.
- Keep the distinction sharp between “there is a limit”, “the crate owns the waiting room”, and “callers know what happens when the limit is hit”.


## 2026-03-17 refinement — crate upgrade-pack lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0514 Crate Upgrade Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-upgrade-pack-product-plan-2026-03-17.md` as the working build sketch for **P-0514**.
- The key new planning detail is that an upgrade-support crate should elevate **hazard classes**, **fixup-capability receipts**, and **migration-lane fidelity** into first-class artifacts rather than leaving them implicit across changelogs, SemVer reports, `cargo fix` runs, and support threads.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s SemVer/public-API/fix-suggestion/release-automation substrate.

### What to keep separate
- Keep **P-0514** separate from SemVer/public-API evidence (**P-0244** / **P-0483**).
- Keep **P-0514** separate from compile-time guidance (**P-0512**) and runtime handoff (**P-0513**).
- Keep **P-0514** separate from release automation / changelog tooling.
- Keep **P-0514** separate from domain-specific migration workbenches.

### Preferred proving grounds
- crates with renamed APIs where source fixes exist but manifest/config/docs edits remain
- crates whose default feature or backend policy changes without a clean source rewrite
- minor releases that keep API shape compatible but shift behavior enough to require validation
- workspaces where only a library lane or default-feature lane was really checked


## 2026-03-17 refinement — crate capability-contract lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0510 Crate Capability Contract & Interop Profile Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-capability-contract-product-plan-2026-03-17.md` as the working build sketch for **P-0510**.
- The key new planning detail is that a capability-contract crate should elevate **claim-class policy**, **support-obligation receipts**, and **profile-fidelity reports** into first-class artifacts rather than leaving them implicit across manifests, docs.rs settings, rustdoc JSON, and README prose.
- `0.1` should stay centered on `init`, `observe`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s Cargo/docs.rs/rustdoc substrate.

### What to keep separate
- Keep **P-0510** separate from task-first decision packs (**P-0509**).
- Keep **P-0510** separate from shared ecosystem interop profiles (**P-0511**).
- Keep **P-0510** separate from item-level availability ledgers (**P-0451**).
- Keep **P-0510** separate from whole-project toolchain/target support (**P-0484**).
- Keep **P-0510** separate from slice tools for MSRV/API/semver/security analysis.

### Preferred proving grounds
- async crates that use Tokio internally but expose mostly runtime-neutral public APIs
- crates claiming `no_std` / `alloc` support while docs.rs or examples still lean on `std` overlays
- crates with `build.rs`, `links`, or proc macros that materially change downstream adoption cost
- crates whose support story draws from both package metadata and docs.rs target overlays

## 2026-03-17 refinement — crate interop-profile lane now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0511 Crate Interop Profile Pack Kit** into a more buildable shape.

### Main judgment
- Treat `meta/crate-interop-profile-product-plan-2026-03-17.md` as the working build sketch for **P-0511**.
- The key new planning detail is that an interop-profile crate should elevate **profile-class policy**, **boundary-obligation receipts**, and **pair-fidelity reports** into first-class artifacts rather than leaving them implicit across docs, trait names, adapter crates, and issue-thread lore.
- `0.1` should stay centered on `init`, `observe`, `check`, `pair`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s `http` / `tower-service` / `futures-core` / Serde substrate.

### What to keep separate
- Keep **P-0511** separate from task-first decision packs (**P-0509**).
- Keep **P-0511** separate from producer-side capability contracts (**P-0510**).
- Keep **P-0511** separate from trait-evolution / customization-point planners (**P-0449** / **P-0452**).
- Keep **P-0511** separate from SemVer/public-API slice tools.
- Keep **P-0511** separate from domain-specific conformance kits.

### Preferred proving grounds
- async libraries that use Tokio internally but want runtime-neutral public APIs
- middleware ecosystems built around `tower-service` + `http`
- framework families that rely on shared middleware reuse across crates
- Serde model crates that want to stay format-neutral rather than silently becoming transport-specific
- releases that look semver-compatible while quietly tightening ecosystem lock-in


## 2026-03-17 refinement — cfg availability deepened with slice witness, gate normalization, and re-export lineage

This pass did **not** promote a new lane.
It sharpened **P-0451 Cfg Availability Ledger Kit** further.

### Main judgment
- Treat `meta/cfg-availability-ledger-lanes-2026-03-17.md` as the boundary note for **P-0451**.
- The key new planning detail is that an availability-ledger crate must keep **slice-witness receipts**, **gate-normalization reports**, and **re-export-lineage reports** separate from its earlier availability-class, origin, and fidelity artifacts.
- `0.1` should not let a hosted docs.rs slice, a shortened `doc(auto_cfg)` badge, or an ergonomic re-export silently stand in for full downstream-use truth.

### What to keep separate
- Keep **P-0451** separate from whole-project support contracts (**P-0484**).
- Keep **P-0451** separate from docs.rs parity / replay bundles (**P-0472**).
- Keep **P-0451** separate from producer-side capability summaries (**P-0510**).
- Keep **P-0451** separate from generic public-API / SemVer slice tools and raw rustdoc-JSON libraries.

### Preferred proving grounds
- crates using `#[doc(auto_cfg(hide(...)))]` or `#[doc(cfg(...))]` to simplify visible gates
- docs.rs metadata profiles that add custom `rustc` cfgs or features
- workspaces where `cfg(docsrs)` affects the final crate but not dependencies
- public ergonomic re-exports whose real target gate lives deeper in the module graph


## Update 2026-03-18 (240) — Python wheel/free-threading shipkit product plan

- Treat **P-0466 Python Extension Compatibility Contract ShipKit** as a real `0.1` candidate now that the archive has sharper review objects for ABI target class, thread-support declarations, and variant horizon.
- Keep the distinction sharp between **binding generators**, **build backends/upload tooling**, **free-threading porting guidance**, **Python package-index evolution**, and a **reviewable Rust-backed extension release contract**.
- The missing value for **P-0466** is not another uploader or backend; it is the boring workflow that turns PyO3 features, wheel tags, repair steps, `gil_used` posture, and `abi3t` / wheel-variant planning into one compact support artifact.
- Prefer a small cargo subcommand plus library with `inspect`, `matrix`, `check`, `diff`, and `bundle` over a giant hosted release platform.

## 2026-03-18 refinement — Apple XCFramework shipkit now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0467 Apple XCFramework & SwiftPM ShipKit** into a more buildable shape.

### Main judgment
- Treat `meta/apple-xcframework-swiftpm-shipkit-product-plan-2026-03-18.md` as the working build sketch for **P-0467**.
- The key new planning detail is that an Apple shipkit should elevate **slice coverage**, **package alignment**, and **trust posture** into first-class artifacts rather than leaving them implicit across XCFramework contents, wrapper packages, checksums, signatures, and privacy manifests.
- `0.1` should stay centered on `inspect`, `check`, `diff`, and `bundle` workflows above today’s UniFFI / `cargo swift` / `xcframework` / SwiftPM / Xcode substrate.

### What to keep separate
- Keep **P-0467** separate from binding generators and full project generators.
- Keep **P-0467** separate from consumer-side foreign SDK doctoring (**P-0487**).
- Keep **P-0467** separate from cross-ecosystem release-promise drift work (**P-0482**).
- Keep **P-0467** separate from generic codesign/notarization automation.

### Preferred proving grounds
- Rust SDKs distributing remote SwiftPM binary targets around XCFramework zips
- releases where device support exists but simulator or macOS slices drift
- releases where the wrapper/checksum/module identity lags behind a rebuilt binary bundle
- signed SDK bundles whose privacy-manifest posture still needs explicit review


## 2026-03-18 refinement — NuGet native interop shipkit now has an implementation-ready `0.1` sketch

This pass did **not** promote a new lane.
It sharpened **P-0499 NuGet Native Interop ShipKit** into a more buildable shape.

### Main judgment
- Treat `meta/nuget-native-interop-shipkit-product-plan-2026-03-18.md` as the working build sketch for **P-0499**.
- The key new planning detail is that a NuGet shipkit should elevate **RID coverage**, **loader route**, and **deployment posture** into first-class artifacts rather than leaving them implicit across `.nupkg` contents, generated bindings, runtime probing, and special publish modes.
- `0.1` should stay centered on `inspect`, `check`, `diff`, and `bundle` workflows above today’s NuGet native-asset rules, RID guidance, `csbindgen`, P/Invoke / `LibraryImport`, and .NET loading substrate.

### What to keep separate
- Keep **P-0499** separate from binding generators and source generators.
- Keep **P-0499** separate from consumer-side foreign SDK doctoring (**P-0487**).
- Keep **P-0499** separate from cross-ecosystem release-promise drift work (**P-0482**).
- Keep **P-0499** separate from full NuGet/MSBuild publishing automation.

### Preferred proving grounds
- Rust-backed NuGet packages shipping multi-RID native assets with generated C# bindings
- releases where the managed wrapper claims a broader RID family than the packaged assets really cover
- plugin-host scenarios requiring `AssemblyDependencyResolver` or explicit unmanaged-library resolvers
- releases that work in ordinary runtime but overclaim single-file or Native AOT support

## Added 2026-03-18 (245): Hex native NIF shipping contract deepening

The next worthy BEAM-facing move was **not** another NIF wrapper.
It was to sharpen **P-0502 Hex Native NIF ShipKit** around the three review objects the current substrate now makes unavoidable:

1. **checksum residency** — not just whether a checksum file exists in CI or git, but whether it is actually present in the published Hex tarball;
2. **NIF-version window** — not just “supports OTP X+”, but what minimum NIF ABI/version the release is actually configured to target;
3. **fallback trigger** — not just “source build exists”, but when uncovered targets or prerelease flows actually force users into a local Rust build.

Read **P-0502** as: **Hex tarball receipt → checksum-residency report → NIF-version-window report → fallback-trigger report → loader receipt → support bundle**.

## 2026-03-18 — JAR/JNI shipkit deepening

The next move here was not to add another Java bridge.
It was to sharpen **P-0500 JAR/JNI Native ShipKit** around the three review objects the current substrate now makes unavoidable:

- classifier dialect
- native-access posture
- loader residency

Read **P-0500** as: **native matrix → classifier-dialect report → loader-residency report → native-access report → symbol contract → Central/Maven publish receipt → support bundle**.

The intended `0.1` remains a small read-mostly cargo subcommand and library above Maven/Central publication, JDK native-access policy, `os-maven-plugin` classifier conventions, and `jni-rs` authoring substrate.


## 2026-03-18 — R package native shipkit deepening

The next move here was not to add another Rust↔R binding layer.
It was to sharpen **P-0526 R Package Native ShipKit** around the three review objects the current substrate now makes unavoidable:

- registration posture
- DLL load contract
- install posture

Read **P-0526** as: **package metadata + wrapper/entrypoint import → registration-posture report → DLL-load-contract report → install-posture report → build-toolchain receipt → support bundle**.

The intended `0.1` remains a small read-mostly cargo subcommand and library above `extendr` / `rextendr`, base-R loading/registration rules, and CRAN binary/source realities.


## 2026-03-18 — RubyGems native shipkit deepening

The next move here was not to add another Rust↔Ruby binding layer.
It was to sharpen **P-0501 RubyGems Native Extension ShipKit** around the three review objects the current substrate now makes unavoidable:

- platform coverage
- resolver route
- extension residency

Read **P-0501** as: **gemspec + artifact inventory + lockfile/Bundler import → platform-coverage report → resolver-route report → extension-residency report → publish/rebuild receipts → support bundle**.

The intended `0.1` remains a small read-mostly cargo subcommand and library above Bundler, RubyGems, `rb-sys`, `magnus`, and fat-gem deployment substrate.


## Added 2026-03-19 (251) — embedded filesystem / LittleFS adoption
- **P-0527 LittleFS Native Adoption Kit** — sharpened because the ecosystem now has both a mainstream FFI-backed littlefs path and a fresh pure-Rust port, but still lacks one boring adoption layer for storage-adapter receipts, compatibility witnesses, power-cut evidence, and image/support bundles.


## Added 2026-03-19 (252) — desktop shipping / release contract
- **P-0012 Desktop ShipKit** — sharpened because the ecosystem now has real desktop release substrate (`dist`, cargo-packager, Tauri distribution/updater docs), but still lacks one boring contract for release identity, update-channel topology, and crash-symbol handoff across Rust desktop app pipelines.


## 2026-03-19 refinement — crate lifecycle-surface lane now has a concrete review-object pass

This pass did **not** promote a new lane.
It sharpened **P-0520 Crate Lifecycle Surface Pack Kit** into a more reviewable shape.

### Main judgment
- Treat `meta/crate-lifecycle-surface-product-plan-2026-03-19.md` as the working refinement note for **P-0520**.
- The key new planning detail is that a lifecycle-support crate should elevate **activation boundaries**, **stop semantics**, **blocking-work caveats**, **teardown evidence**, and **drain recipes** into first-class artifacts rather than leaving them implicit across docs, examples, issue threads, and runtime helpers.
- `0.1` should stay centered on `init`, `capture`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today’s Tokio / tokio-util / async-shutdown / structured-concurrency substrate.

### What to keep separate
- Keep **P-0520** separate from runtime failure handoff (**P-0513**).
- Keep **P-0520** separate from observability contracts (**P-0518**).
- Keep **P-0520** separate from authority posture (**P-0519**).
- Keep **P-0520** separate from resource surfaces (**P-0521**).
- Keep **P-0520** separate from graceful-shutdown frameworks and structured-concurrency substrate.

### Preferred proving grounds
- handles whose `drop` detaches work rather than stopping it
- lazy-start clients that only spawn background tasks on first use
- protocol writers whose supported clean stop is `flush` + `shutdown`, not drop
- blocking-pool tasks whose abort semantics are weaker than ordinary async tasks
- task groups whose drop/detach/shutdown paths are meaningfully different


## Update 2026-03-19 (261) — crate test-surface deepening

- Revisit **P-0523 Crate Test Surface Pack Kit** now that nextest record/replay, portable recordings, compile-fail harnesses, and richer snapshot-normalization substrate make the lane more concrete.
- Keep the distinction sharp between **generic testing substrate**, **receiver-facing test support**, **example/first-success support**, and **diagnosis/troubleshooting support**.
- Promote **support level**, **topology honesty**, **witness lineage**, and **normalization boundary** into first-class review objects.
- Prefer compact artifacts such as `support-level.policy`, `test-environment.requirements`, `scenario-witness.receipt`, `witness-lineage.receipt`, and `snapshot-normalization.report` over vague “tested in CI” prose.

## 2026-03-19 refinement — crate upgrade-pack lane now centers hazard authority and workspace/package scope

This pass did not add a new lane.
It deepened **P-0514 Crate Upgrade Pack Kit** again because the surrounding release substrate is stronger but the downstream lane contract is still weak.

- Treat `meta/crate-upgrade-pack-product-plan-2026-03-19.md` as the current working sketch for **P-0514**.
- Keep **hazard authority**, **package-scope truth**, and **follow-through coverage** explicit.
- Do not let release automation, changelog prose, SemVer-green verdicts, or `cargo fix` success get rephrased as whole-lane migration proof.


## 2026-03-20 refinement — crate upgrade-pack lane now centers source lineage, hazard arbitration, and active follow-through state

- Treat `meta/crate-upgrade-pack-product-plan-2026-03-20.md` as the current working sketch for **P-0514**.
- Keep **source-lineage truth**, **hazard arbitration**, and **active follow-through state** explicit alongside the earlier authority/scope/follow-through artifacts.
- Prefer tiny receiver-facing artifacts: `source-lineage.receipt`, `hazard-arbitration.report`, and `followthrough-state.report` rather than another release bot, changelog improver, or codemod ambition jump.


## 2026-03-20 refinement — crate upgrade-pack lane now also needs deviation ledgers and warning registers

- Keep **deviation-ledger truth** explicit alongside readiness and export posture: if a team intentionally proceeds under a freeze/export/consistency override, that decision should become a numbered, expiring record with owner, authority, and public-summary status.
- Keep **warning-register truth** explicit alongside publication-surface labels: one compact register should say which warnings are active, blocking, public, and temporarily carried by a deviation.
- Prefer tiny receiver-facing artifacts such as `deviation-ledger.receipt` and `warning-register.report` rather than silently carrying exceptions in prose or scattering warning meaning across many files.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs export posture and exact public surface

- Keep **export-posture truth** explicit alongside pack readiness: a lane can be migration-ready yet still remain private because paths, package aliases, or working notes need redaction.
- Keep **publication-surface truth** explicit alongside the exported summary: the public contract should say exactly which files/receipts are on-surface and which remain internal, floating, or off-surface.
- Prefer tiny receiver-facing artifacts such as `export-posture.report` and `publication-surface.manifest` rather than treating the whole working tree as the public contract.

## 2026-03-20 refinement — crate upgrade-pack lane now centers source heads and pack readiness

- Keep **source-head truth** explicit alongside `source-lineage.receipt`: the latest useful operational guide is not automatically the citation-ready frozen head.
- Keep **pack-readiness truth** explicit alongside the constituent receipts: `hold`, `candidate`, and `freeze_ready` are reviewable states, not moods.
- Prefer tiny receiver-facing artifacts such as `source-heads.report` and `pack-readiness.report` rather than inventing another release pipeline or pretending that bundle completeness equals freeze readiness.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs explicit review queues and cross-register consistency

- Keep **review-queue truth** explicit alongside `pack-readiness.report`: remaining source pinning, arbitration, scope, follow-through, and approval work should be queued, not buried in prose.
- Keep **cross-register consistency truth** explicit alongside the constituent receipts: a pack must fail loudly when readiness, source heads, package scope, follow-through, and posture surfaces disagree.
- Prefer tiny receiver-facing artifacts such as `review-queue.report` and `cross-register-consistency.report` rather than polishing a contradictory bundle into a fake freeze-ready contract.


## Added 2026-03-20 (281)
- For `crate-upgrade-pack-kit`, freeze/public posture should now carry explicit maker/checker review provenance so independently checked public contracts stop collapsing into polished self-review.


## 2026-03-20 refinement — crate upgrade-pack lane now also needs config-basis truth

- Treat `meta/crate-upgrade-pack-product-plan-2026-03-20.md` as the current working sketch for **P-0514**.
- Keep hidden Cargo config hierarchy, `--config`, environment overrides, and `[patch]` / source-replacement surfaces explicit so the lane cannot read as the default reviewed baseline when it was actually shaped by a narrower or less portable override basis.


## 2026-03-20 — pathfinder next implementation step: decision aging

The archive’s next worthy **P-0509** implementation step is no longer more raw candidate import.
It is one compact watch layer above frozen starter-set locks:

- `revisit-trigger.policy.json`
- `freeze-horizon.policy.json`
- `decision-watch.report.json`

The product question is not “can we rank again?” but “can a frozen decision age honestly without silently turning into stale folklore or an auto-replacement engine?”


## 2026-03-20 refinement — spiffe-identity-kit now centers identity-source truth, trust-domain scope, peer handoff, and rotation state

- Treat `meta/spiffe-identity-kit-product-plan-2026-03-20.md` as the current working sketch for **P-0134**.
- Keep **identity-source truth**, **trust-domain-policy truth**, **peer-identity handoff**, and **rotation/failure posture** explicit.
- Prefer tiny receiver-facing artifacts such as `identity-source.receipt`, `trust-domain-policy.receipt`, `peer-identity.receipt`, and `rotation-state.report` rather than another mesh layer, auth framework, or TLS reimplementation.


## 2026-03-20 addendum — cfg availability needs audience-specific usability truth

- `meta/cfg-availability-ledger-usability-boundaries-2026-03-20.md` — keeps docs-visible, same-crate-compilable, doctest-usable, downstream-usable, and hosted default-surface drift from collapsing into one fake availability verdict.
- `fixtures/cfg-availability-ledger-kit/usability-witness.receipt.schema.json` + `default-surface-drift.report.schema.json` — schemas for audience-specific usability and hosted default-surface drift.
- `fixtures/cfg-availability-ledger-kit/cfg_doc_visible_item_needs_separate_doctest_and_downstream_usability_witness/` + `docsrs_default_target_shift_changes_default_docs_surface_without_new_support/` — new fixture families for docs-visible-only slices and hosted default-target drift.

## 2026-03-20 addendum — MSRV now looks more epic when it distinguishes support policy from update-path reality

**P-0036 MSRV Workspace Lab** looks stronger after this refinement because Cargo now has real policy and lockfile substrate, but still lacks a small reviewable layer for **policy activation**, **command-family floors**, and **lockfile-authoring truth**. The sharper idea is not another minimum-version finder. It is one shared layer that can tell another team whether the intended resolver policy is actually active and whether ongoing update/package work still fits the claimed support floor.


## 2026-03-20 refinement — publish-receipt lane now has a sharper implementation-ready contract

This pass did not add another publisher, provenance system, or docs hosting lane.
It sharpened **P-0477 Cargo Publish Receipt Join Kit** around **capture basis**, **receipt authority**, and **publication visibility**.

- Treat `meta/cargo-publish-receipt-join-product-plan-2026-03-20.md` as the working build sketch for **P-0477**.
- The key new planning detail is that a publish-receipt crate should publish explicit **capture-basis receipts** and **publication-visibility reports** alongside local package, index, and identity receipts.
- Keep **P-0477** separate from trusted-publishing rehearsal (**P-0175**).
- Keep **P-0477** separate from docs.rs parity / hosted build diagnosis (**P-0472**).
- Keep **P-0477** separate from provenance attestations (**P-0015**).


## 2026-03-20 refinement — cargo future-incompat lane now also needs visibility and suppression truth

- Keep **finding-visibility truth** explicit alongside capture locks, owner maps, waiver ledgers, and evidence-source receipts: a lane should say whether a finding was terminal-visible, only visible in a full or recalled report, suppressed-but-recorded, or hidden by a narrowed recall surface.
- Keep **suppression-basis truth** explicit too: `#[allow]`, `--cap-lints`, Cargo notification-frequency settings, and package-filtered recalls should not collapse into one vague “warning was hidden” story.
- Prefer tiny receiver-facing artifacts such as `finding-visibility.report` and `suppression-basis.receipt` rather than treating terminal cleanliness as proof that no future-incompat debt exists.

## 2026-03-20 refinement — i18n-icu-kit now centers message schema, data profile, formatter coverage, and fallback witnesses

- Treat `meta/i18n-icu-kit-product-plan-2026-03-20.md` as the current working sketch for **P-0039**.
- Keep **message-argument schema truth**, **locale-data profile truth**, **formatter-coverage truth**, and **fallback-witness truth** explicit.
- Prefer tiny receiver-facing artifacts such as `message-arg-schema.receipt`, `data-profile.receipt`, `formatter-coverage.report`, and `fallback-witness.report` rather than another syntax war, pipeline suite, or all-in-one localization framework.

## 2026-03-20 refinement — schema-compatibility lane now needs basis/profile/strength/policy truth

- Keep **comparison-basis truth** explicit alongside diff results: old/new identity, normalization, generated-vs-authored basis, and latest-only versus transitive history should stay visible.
- Keep **compatibility-profile truth** explicit too: Buf category, OpenAPI severity threshold, registry mode, or validation-only posture should not be inferred from green output alone.
- Keep **finding-strength truth** explicit: definite, potential, validation-only, and witness-backed results are not one certainty class.
- Keep **policy-decision truth** explicit: ignore files, waivers, thresholds, and manual-review boundaries should remain inspectable.



## Added 2026-03-20 (125)
- Deepen **P-0474 Cargo Config Layer Receipt Kit** around `invocation-basis.receipt` and `replayability.report` before inventing another neighboring config or support crate.
- Keep effective-config capture, invocation basis, redaction safety, and replayability as separate truths.


## 2026-03-20 refinement — channel semantics need capacity, overflow, delivery, and drain truth

- Treat `meta/channel-surface-contract-product-plan-2026-03-20.md` as the current working sketch for **P-0529**.
- Keep **capacity-posture truth**, **overflow-policy truth**, **delivery-obligation truth**, and **shutdown/drain truth** explicit.
- Prefer tiny receiver-facing artifacts such as `capacity-posture.receipt`, `overflow-policy.receipt`, `delivery-obligation.report`, and `shutdown-drain.receipt` rather than another channel implementation, benchmark suite, or actor stack.


## Update 2026-03-21 (314) — debuggability support backend-coverage pass

- Treat **P-0486 Debuggability Support Contract Kit** as the current center of gravity for the debug-support stack.
- Prefer a tiny receiver-facing bundle: `debuggability.receipt`, `symbol-layout.manifest`, `visualizer.manifest`, `support-posture.report`, `support-class.policy`, `artifact-handoff.manifest`, `debugger-backend-coverage.report`, `source-lookup-impact.report`, and optional `debuggability-drift.diff`.
- Keep the distinction sharp between **broad support posture** (P-0486), **visualizer compatibility** (P-0491), **source lookup / path hygiene diagnosis** (P-0493), and **runtime symptom / first-diagnosis support** (P-0525).
- Best next passes should keep backend-family coverage, capability ceilings, and portable-claim ceilings explicit instead of letting `pdb` / `dSYM` / NatVis / GDB-script presence masquerade as broad debugger support.


## 2026-03-21 refinement — Cargo cache policy now needs recovery obligation and cache-surface truth

- Treat `meta/cargo-global-cache-policy-product-plan-2026-03-21.md` and `meta/cargo-global-cache-recovery-boundaries-2026-03-21.md` as the current working sketch for **P-0480**.
- Keep **inventory-basis truth**, **cache-surface truth**, **recovery-obligation truth**, **offline-cost honesty**, and **mixed-toolchain compatibility truth** explicit.
- Prefer tiny receiver-facing artifacts such as `cache-surface.receipt`, `recovery-obligation.report`, and `gc.receipt` rather than another disk cleaner, `target/` janitor, or remote-cache server.

- 2026-03-21: productized **P-0458 Async Dyn Transition Kit** with a `0.1` build sketch centered on recipe identity, tooling interop, and native-readiness posture instead of another bridge macro.


## Added 2026-03-21 (337)
- Deepened **P-0503 Assurance Case Workbench Kit** around **claim-library basis**, **import policy**, **assumption ledgers**, **review gates**, and **export projection**.
- Treat `meta/assurance-case-workbench-product-plan-2026-03-21.md` as the current working build sketch for **P-0503**.
- Keep **P-0503** separate from **P-0485** verification campaigns, **P-0256** generic evidence bundles, standards-native editor suites, and full certification-workflow ownership.

## 2026-03-22 refinement — crate health now needs work-routing and continuity-backstop truth

This pass sharpened **P-0011 Crate Health Contract Kit** again.
It turned the lane from broad stewardship posture into a more operational routing contract.

Immediate working notes:
- Treat `meta/crate-health-routing-continuity-plan-2026-03-22.md` as the build sketch for the next serious **P-0011** implementation pass.
- Keep `work-routing.report`, `response-channel.receipt`, and `continuity-backstop.report` separate from broad maintenance coverage.
- Prefer importers for CODEOWNERS / issue forms / private vulnerability reporting / registry signals only when the final artifacts stay explicit about `maintainer_declared` versus `repo_import` versus `manual_review_required`.

Guardrails:
- Keep **P-0011** separate from **P-0017** trust/security posture.
- Keep **P-0011** separate from maintainer-funding dashboards and sponsorship tooling.
- Keep **P-0011** separate from **P-0515** off-ramp / successor planning.
- Keep **P-0011** separate from host-platform mechanics like GitHub workflow policy; the crate owns the normalized contract above them.


## 2026-03-22 refinement — crate health now needs imported-signal, routing-drift, and support-bundle truth

This pass sharpened **P-0011 Crate Health Contract Kit** again.
It turned the lane from routing/continuity prose into a more artifact-complete stewardship contract.

Immediate working notes:
- Treat `meta/crate-health-artifact-completeness-plan-2026-03-22.md` as the current build sketch for the next serious **P-0011** implementation pass.
- Keep `registry-signal.import`, `routing-drift.diff`, and `health-support-bundle.manifest` separate from both broad health profile and host-platform trust/security lanes.
- Prefer importers for crates.io and GitHub substrate only when the final artifacts stay explicit about `maintainer_declared` versus `repo_import` versus `manual_review_required`.

Guardrails:
- Keep **P-0011** separate from **P-0017** trust/security posture.
- Keep **P-0011** separate from funding/sponsorship tooling.
- Keep **P-0011** separate from repository analytics dashboards.
- Keep **P-0011** separate from host-platform settings UIs; the crate owns the portable contract above them.

## Added 2026-03-22 — unsafe contract auditing roadmap

Near-term repo move:

1. deepen **P-0120** around authority-source imports and diffable unsafe-site inventory;
2. later connect P-0120 bundles to P-0485 verification-campaign bundles;
3. resist opening another unsafe-review proposal unless it clearly cannot be synthesized into P-0120 + an adjacent lane.

## 2026-03-22 — next concrete move for delegated build-time work

After this pass, the next highest-leverage implementation move in the build-time frontier is to prototype `cargo build-delegate snapshot` against one multi-script fixture and one `links`-override fixture.
The success condition is not automation breadth; it is whether one support bundle can answer:

1. what units existed,
2. which output lane each unit owned,
3. whether live execution or override authority won,
4. and what changed between two captures.


## Added 2026-03-22 (350): compile-time sandbox policy needs authority, scope, and mode receipts before another backend

The archive already had build-time sandbox ideas, proc-macro readiness work, and runtime authority surfaces.
What was still too cheap was the claim “we sandbox compile-time code” without answering:

- which policy source was authoritative,
- which actor got which powers,
- whether the run was observe, audit, or enforce,
- what break-glass exceptions existed,
- and what changed across releases.

So the missing value for **P-0107** is not another OS isolation layer and not another static scanner.
It is the boring workflow that turns current runner behavior into **policy-authority receipts, actor-capability matrices, enforcement-mode receipts, exception-ack records, and sandbox-policy drifts**.


## Added 2026-03-22 (351): rebuild explanation should productize baseline authority before adding more analytics

Near-term repo move:

1. deepen **P-0469** around baseline-authority and reverse-impact artifacts;
2. keep **P-0035** as the many-session warehouse above those bundles;
3. resist adding another generic Cargo performance crate unless it clearly cannot be synthesized into P-0469 + an adjacent lane.


## 2026-03-22 implementation addendum — P-0442 trait-solver drift witness kit

The key new planning detail is that a worthy solver-drift crate should publish explicit **comparison-lane**, **corpus-authority**, **obligation-class**, **diagnostic-normalization**, **minimization-lineage**, and **solver-drift** artifacts instead of burying all meaning inside stderr diffs.

## 2026-03-22 — P-0433 MC/DC Coverage Workbench Kit — artifact-rich deepening

Promote P-0433 from a rough evidence-bundle idea into a first-class support-contract lane.

Near-term work:
1. freeze `decision-authority.receipt.json`, `construct-support.matrix.json`, and `caveat-basis.receipt.json`;
2. prove independence-pair and lineage artifacts on tiny scenarios;
3. keep branch-only, MC/DC-preview, and manual-review-required states sharply distinct.


## 2026-03-22 — next concrete move for Cargo script / single-file-package work

After this pass, the next highest-leverage implementation move in the single-file-package frontier is to prototype `cargo script-workbench capture` against one embedded-frontmatter fixture and one manifest-command fixture.
The success condition is not launcher breadth; it is whether one support bundle can answer:

1. what was explicit versus inferred,
2. what discovery rules applied,
3. what invocation semantics Cargo used,
4. where cache and lock state lived,
5. and what a safe export path looks like.

## Added 2026-03-22 — broad frontier rerank implementation addendum

Near-term preferred portfolio:
1. keep P-0484, P-0011, P-0535, and P-0120 in the lead structural cluster;
2. treat P-0486, P-0490, and P-0469 as the universal productivity/support cluster;
3. incubate P-0536 as the docs/search/assistant handoff lane instead of opening another docs portal or rustdoc wrapper.

## 2026-03-22 — next concrete move for crate knowledge pack work

Prototype `cargo crate-knowledge pack` on:
1. one crate with docs.rs metadata and target/feature gating;
2. one crate with rich README/examples/doctests;
3. one crate with obvious docs.rs-hosted divergence.

Success condition: one bundle can answer canonical API/docs/example provenance, visibility gates, hosted docs presence, and support/search slice boundaries.



## 2026-03-22 refinement — crate knowledge pack now needs artifact and slice policy before any retrieval UX

This pass sharpened **P-0536 Crate Knowledge Pack Kit** from a justified lane into a more implementation-ready support contract.

Immediate working notes:
- Treat `meta/crate-knowledge-pack-product-plan-2026-03-22.md` as the build sketch for the next serious **P-0536** implementation pass.
- Keep `api-surface.receipt`, `docs-source.manifest`, `example-lineage.report`, `docsrs-presence.import`, and `knowledge-slice.manifest` separate.
- Prefer tiny receiver-facing bundles and slice profiles over a portal, index UI, or assistant-specific product.

Guardrails:
- Keep **P-0536** separate from **P-0051** rustdoc JSON normalization.
- Keep **P-0536** separate from **P-0472** docs.rs parity evidence.
- Keep **P-0536** separate from **P-0476** docs coverage review.
- Keep **P-0536** separate from **P-0455** doctest extraction / support truth.
- Keep **P-0536** separate from search ranking or assistant product logic; the crate owns the normalized handoff contract above them.

## 2026-03-22 — next concrete move for crate knowledge pack work

After this pass, the next highest-leverage implementation move in the docs/search/support frontier is to prototype `cargo crate-knowledge pack` against:
1. one crate with docs.rs metadata, README content, and feature-gated APIs;
2. one crate with an `examples/` tree plus doctest-heavy docs;
3. one release pair that exercises API/example/docs.rs drift.

The success condition is not retrieval quality or chatbot polish.
It is whether one support bundle can answer:

1. what public API is authoritative,
2. what docs sources are canonical versus imported,
3. which examples are official versus illustrative,
4. what docs.rs actually hosted,
5. and what a safe slice/export path looks like for support/search/assistant consumers.


## 2026-03-22 (370) — next worthiest repo move after crate-knowledge deepening

Prefer productizing **P-0535 Dependency Lifecycle Transition Kit** before adding more adjacent supply-chain proposals.

### Why
- the lane is now top-tier and cross-sector,
- the artifact family was still missing transition-plan / exception-ledger / imported-context objects,
- and the fixture family needed real scenario coverage to resist future overlap with trust-scoring, off-ramp, and source-parity work.

### Concretely finished in this pass
- promoted `transition-plan.manifest.json`, `dependency-exception.ledger.json`, and `imported-signal.receipt.json` into first-class review objects,
- added mixed-criticality, seam-proof, owned-fork/exception, and direct-leak drift scenarios,
- and tightened the boundary against **P-0496 Cargo Vendor & Source Parity Kit**.

### Preferred next move after this
Either:
1. bring **P-0532 Async Runtime Assurance Profile Kit** up to similar schema/scenario readiness, or
2. deepen **P-0011** / **P-0484** only if a pass can add missing first-class artifacts rather than more prose.


## Added 2026-03-22 (async runtime assurance artifact completeness)
- **P-0532 Async Runtime Assurance Profile Kit** — now needs one more productization pass centered on `qualification-basis.receipt.json`, `runtime-profile-diff.report.json`, and `runtime-assurance-bundle.manifest.json`.
- The right near-term goal is not more runtime sectors; it is making host-vs-target lane separation and evidence-class honesty executable in the fixtures.

## 2026-03-22 roadmap addendum (377)

Deepen **P-0469** toward a buildable MVP in this order:

1. session import/freeze,
2. baseline-authority receipt,
3. comparison-scope receipt,
4. unit rebuild classification,
5. artifact-route drift report,
6. reverse-impact report,
7. portable rebuild-support bundle.

Do not spend the next pass on another Cargo timings UI unless it clearly escapes this support-contract lane.

## 2026-03-22 roadmap addendum (378)

Deepen **P-0490** toward a buildable MVP in this order:

1. root-authority receipt,
2. actor-command-lane receipt,
3. wait-window receipt,
4. package-cache lock-mode receipt,
5. residual-contention report,
6. mitigation-outcome diff,
7. portable contention-support bundle.

Do not spend the next pass on a scheduler, cache arbitrator, or generic wrapper unless it clearly escapes this incident-witness lane.

## 2026-03-22 roadmap addendum (381)

Deepen **P-0121** toward a buildable MVP in this order:

1. interface-authority import capture,
2. ownership/unwind normalization,
3. callback execution capture,
4. callback-lifecycle receipt,
5. binding/layout/error normalization,
6. diff report for authority/lifecycle drift,
7. portable FFI support bundle.

Do not spend the next pass on another generator wrapper, package shipkit, or FFI score unless it clearly escapes this boundary-contract lane.


## 2026-03-22 roadmap addendum (384)

Deepen **P-0121** toward a buildable MVP in this order:

1. interface-authority import capture,
2. projection-basis receipt,
3. derivative-parity report,
4. ownership/unwind/callback normalization,
5. coverage/layout/error normalization,
6. projection-drift report,
7. portable FFI support bundle.

Do not spend the next pass on another generator wrapper, package shipkit, or generic FFI score unless it clearly escapes this boundary-contract lane.

## 2026-03-22 roadmap addendum (385)

Deepen **P-0433** toward a buildable MVP in this order:

1. decision authority,
2. construct support,
3. campaign-scope receipt,
4. independence-pair evidence,
5. caveat basis,
6. comparison-basis receipt,
7. qualification-basis receipt,
8. evidence lineage,
9. portable MC/DC support bundle.

Do not spend the next pass on another coverage dashboard, wrapper, or trend view unless it clearly escapes this support-contract lane.



## Update 2026-03-22 (386) — visualizer activation/origin refresh

- Treat **P-0491** as the lane that should keep asset presence, activation route, formatter origin, and backend verdict separate.
- Prefer a tiny receiver-facing bundle: `visualizer-policy`, `visualizer-assets.manifest`, `activation-route.receipt`, `formatter-origin.receipt`, `backend-matrix.receipt`, and `visualizer-support-bundle.manifest`.
- Keep the distinction sharp between **broad support posture** (P-0486), **source lookup / path hygiene** (P-0493), and **visualizer compatibility** (P-0491).
- Best next passes should add backend-version drift, launcher provenance, and conservative bundle diffing instead of inventing another debugger platform crate.

## 2026-03-22 roadmap addendum (388)

Deepen **P-0481** toward a buildable MVP in this order:

1. runner-profile policy,
2. runner-route receipt,
3. execution-basis receipt,
4. target matrix,
5. ignore audit,
6. route/basis drift,
7. portable runtool-support bundle.

Do not spend the next pass on another emulator wrapper, docs portal, or generic cross-device test framework unless it clearly escapes this support-contract lane.


## 2026-03-22 roadmap addendum (389)

- Treat **P-0491** as the lane that should keep asset presence, activation route, formatter origin, probe surface, comparison basis, and backend verdict separate.
- Do not let future passes flatten `lldb`, `lldb-dap`, CDB/WinDbg/Visual Studio, or embedded-`.pdb` NatVis delivery into one fake “visualizer support” story.


## 2026-03-22 (390) — deepen P-0433 around profile compatibility, campaign policy, and manual-review debt

Next step after scope/comparison/qualification honesty: make **P-0433** explicit about retained input durability and unresolved review obligations.

Promote these artifacts into the lane:
1. `profile-compatibility.receipt.json`
2. `campaign-policy.receipt.json`
3. `manual-review-debt.report.json`

This should keep MC/DC bundles from being treated as durable trend inputs or release-ready evidence simply because a runner succeeded.

## 2026-03-22 roadmap addendum (391)

Deepen **P-0537** toward a buildable MVP in this order:

1. iteration profile,
2. edit-event receipt,
3. patch-eligibility report,
4. linker-route receipt,
5. state-continuity contract,
6. restart-fallback plan,
7. latency-budget report,
8. portable iteration-support bundle.

Do not spend the next pass on another watcher wrapper, linker benchmark, or framework-local hot reload helper unless it clearly escapes this support-contract lane.


## Added 2026-03-22 (392): cargo-event-stream deepening
- **P-0042 cargo-event-stream** — build the stable event-handoff layer above evolving Cargo structured logging and `--message-format=json`; focus on event envelopes, foreign-output containment, rendering-policy receipts, session manifests, and portable redacted bundles.


## 2026-03-23 roadmap addendum (394)

Deepen **P-0440** toward a buildable MVP in this order:

1. projection-authority receipt,
2. borrow-semantics matrix,
3. semantics-witness report,
4. projection-drift diff,
5. portable projection-support bundle.

Do not spend the next pass on another pinning macro, generalized-reference helper, or language-design explainer unless it clearly escapes this semantics-support lane.

## Added 2026-03-23 (398) — example-surface deepening around official-start authority, entrypoint viability, and hosted visibility
- **High**: P-0524 Crate Example Surface Pack Kit

Rationale: current Rust, Cargo, rustdoc, and docs.rs sources now make the sharper missing layer more specific than “examples are present” or “quickstarts have witnesses.” The sharp gap is whether one path is actually blessed as the receiver-facing start, whether README/rustdoc/example/guide entrypoints are viable in the same lane, and whether hosted visibility is being mistaken for local runnable proof. The sharper missing crate is therefore a reviewable contract for **official-start authority**, **entrypoint viability**, **hosted visibility**, and **portable first-success bundles**.


## Added 2026-03-23 (build-dir transition need / authority / rehearsal deepening)
- **P-0489 Cargo Build-Dir Consumer Transition Kit** — now more implementation-ready because the next missing artifact is no longer just an adapter plan or viability note; it is a **consumer-need report**, **adapter-authority receipt**, **windowed-viability matrix**, and **rehearsal-support bundle**.
- For the next few passes, prefer schema stabilization and tiny scenario bundles around `consumer-need.report.json`, `adapter-authority.receipt.json`, `windowed-viability.matrix.json`, and `rehearsal-support-bundle.manifest.json` instead of broadening P-0489 into a generic Cargo filesystem API.


## 2026-03-23 (406) — next callback-support proving ground for P-0121

Deepen **P-0121** next around mixed callback-family bundles that keep:
1. callback authority,
2. callback execution,
3. callback lifecycle,
4. callback completion,
5. callback-adjacent error posture
separate across UniFFI, Diplomat, CXX, and WIT-facing surfaces.

## 2026-03-23 roadmap addendum (407)

Deepen **P-0125** toward a buildable next slice in this order:

1. capture-route receipt,
2. artifact-coverage report,
3. coverage-ceiling report,
4. bundle manifest,
5. route/coverage diffs,
6. transform/format adapters only after those are stable.

Do not spend the next pass on another CycloneDX/SPDX emitter, attestation stack, or generic provenance portal unless it clearly escapes this Cargo-native precursor-support lane.

## 2026-03-23 (408)
- Deepen **P-0055 Cargo Workspace Toolchain Manifest Kit** around `command-authority.receipt`, `component-availability.report`, `fallback-ceiling.report`, and `tool-support-bundle.manifest`.
- Guardrail: do not flatten rustup proxy/component lanes, Cargo external-subcommand lanes, workspace-managed binaries, and PATH fallback lanes into one fake “the tool ran” claim.


## 2026-03-23 (411) — next compile-iteration proving ground

Deepen **P-0537** next in this order:

1. `reload-surface.report.json`
2. `fallback-restart.plan.json`
3. `latency-budget.report.json`
4. Dioxus / Tauri / Trunk-cargo-leptos scenario packets
5. bundle-level diffs only after those are stable

Guardrail:
do not flatten UI-only reload, asset-visible update, frontend devserver HMR, Rust hotpatch, and rebuild/restart into one fake “fast dev loop” verdict.


## 2026-03-23 (414) — next crate-knowledge proving ground

Deepen **P-0536** next in this order:

1. `item-witness.manifest.json`
2. `identity-fidelity.report.json`
3. doctor rules for cross-blob opaque-ID misuse
4. version-bump / target-sensitive scenario packets
5. bundle-level diffing only after those are stable

Guardrail:
do not flatten raw rustdoc JSON item IDs, docs.rs page locators, source spans, and “same conceptual item” into one fake stable-identity verdict.

## 2026-03-23 (417) — next compile-iteration proving ground, part two

Deepen **P-0537** next in this order:

1. `edit-scope.receipt.json`
2. `fast-path-barrier.report.json`
3. tip-crate / layout / workspace-cascade scenario packets
4. bundle-level diffing for widened vs narrowed fast paths
5. framework adapters only after those are stable

Guardrail:
do not flatten edit scope, interface impact, barrier cause, fallback class, and readiness class into one fake “the edit stayed fast” verdict.

## 2026-03-23 (426) — next concurrency-contract proving ground

Deepen **P-0538** next in this order:

1. `delivery-memory.report.json`
2. `backlog-pressure.report.json`
3. coalesced-wake / latest-value / bounded-history / rendezvous scenario packets
4. doctor rules for fake “channel-like” equivalence
5. bundle-level diffs only after those are stable

Guardrail:
do not flatten coalesced wake memory, latest-value state, FIFO queued work, per-receiver bounded broadcast history, unbounded growth risk, and zero-capacity rendezvous into one fake “message passing” verdict.


## 2026-03-23 (428) — next concurrency proving ground

Deepen **P-0538** next in this order:

1. `delivery-acceptance.report.json`
2. `observation-evidence.report.json`
3. sender-success / count-hint / close-signal scenario packets
4. doctor rules for fake receipt claims
5. bundle-level diffing only after those are stable

Guardrail:
do not flatten queue admission, latest-state replacement, receiver-count hints, close notifications, and actual downstream observation into one fake “send succeeded” verdict.


## 2026-03-23 (430) — next concurrency proving ground

Deepen **P-0538** next in this order:

1. `closure-finality.report.json`
2. `post-close-availability.report.json`
3. drain-tail / reopenable-close / one-shot-race scenario packets
4. doctor rules for fake “closed means empty” claims
5. bundle-level diffs only after those are stable

Guardrail:
do not flatten closed, drained, terminal, reopenable, and empty into one fake “channel lifecycle” verdict.


## 2026-03-23 (432) — next concurrency proving ground

Deepen **P-0538** next in this order:

1. `observer-cursor.report.json`
2. `observer-progress-isolation.report.json`
3. independent-cursor / self-lag-rebase / shared-work-pool scenario packets
4. doctor rules for fake multi-observer equivalence
5. bundle-level diffing only after those are stable

Guardrail:
do not flatten delivery audience, single-delivery claim, order/gaps, join posture, and observer-local progress into one fake “multi-receiver semantics” verdict.


## Added 2026-03-25 (462) — policy-pack layer

Next deepening sequence after this pass:
1. force **P-0509 + P-0536 + minimal P-0535** through a real `policy-pack.json` + `verdict-report.json` + `override-ticket.json` design;
2. tighten how **P-0472 + P-0484** export policy-ready evidence and conformance inputs;
3. make **P-0431 + P-0496 + P-0125** explicit recheck-trigger suppliers for policy reruns;
4. only then let debugger / iteration / concurrency lanes specialize verdict doctrine.
