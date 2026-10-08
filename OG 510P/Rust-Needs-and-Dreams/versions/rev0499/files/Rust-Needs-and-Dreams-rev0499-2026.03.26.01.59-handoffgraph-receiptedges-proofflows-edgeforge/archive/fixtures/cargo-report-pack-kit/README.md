# Cargo Report Pack Kit fixtures

This fixture pack freezes a first artifact vocabulary for **Cargo Report Kit** so the seam is not carried only by prose.

The comparison set made this pattern hard to ignore: once a frontier starts carrying many receipts, promotion gates, and warning classes, the archive needs **schemas + examples + named review scenarios** or future revisions quietly blur the boundary back into general explanation.

Artifacts frozen here:
- `cargo-report-pack.schema.json`
- `cargo-report-authority-basis.schema.json`
- `cargo-report-projection-receipt.schema.json`
- `cargo-report-quarantine-receipt.schema.json`
- `cargo-report-currentness.schema.json`
- `cargo-report-import-compat.schema.json`
- `cargo-report-promotion-receipt.schema.json`
- `cargo-report-waiver-ledger.schema.json`
- `cargo-report-execution-receipt.schema.json`
- `cargo-report-lineage-register.schema.json`
- `cargo-report-review-request.schema.json`
- `cargo-report-decision-witness.schema.json`
- `cargo-report-review-separation-receipt.schema.json`

Scenario families:
- `stable_future_incompat_native_replay_preserved/`
- `nightly_build_analysis_support_bundle_projected/`
- `basis_lost_projected_pack_demoted/`
- `quarantined_decoder_unknown_summary_separate/`
- `projected_public_example_active_waiver/`
- `expired_public_example_waiver_demotes/`
- `projected_public_example_review_request_pending/`
- `contradiction_resolved_by_decision_witness/`
- `self_review_without_fallback_holds/`

Review rule:
- if a Cargo Report Kit revision changes claim classes, authority-path classes, projection/quarantine/currentness/compatibility meanings, execution/lineage expectations, or frozen-head promotion rules, update the relevant schema/example/scenario files in this fixture pack before treating the prose revision as complete.


## Taxonomy, scenario index, and review gates
The comparison set made one more thing hard to ignore after the first fixture pass: schemas + examples still leave too much room for semantic drift if every class stays a free-form string.

This fixture pack therefore now carries four machine-readable control surfaces:
- `cargo-report-taxonomy.json` — allowed class values for lanes, claim classes, authority paths, projection/quarantine/currentness/compatibility classes, promotion targets/decisions, and warning classes;
- `cargo-report-scenario-index.json` — which named scenarios cover which classes and which stronger claims they intentionally block;
- `cargo-report-review-gates.json` — the small lifecycle gates that must clear before stronger share/current/frozen-head reuse is honest;
- `cargo-report-hygiene-checks.json` — the declared machine checks, required scenario files, known control surfaces, and example/schema overrides that keep the fixture spine from drifting apart.

Review-completion rule, strengthened:
- if a Cargo Report Kit revision introduces a new class value, warning class, or gate, it is incomplete until the taxonomy, the affected schema enums, the relevant examples, and the scenario index all move together.

Waiver rule, strengthened:
- if stronger share/current/frozen/compatibility reuse depends on an exception, that exception must move through `cargo-report-waiver-ledger` with owner/reviewer identity, expiry, and stale-waiver demotion; prose-only waivers are incomplete.

Execution/lineage rule, strengthened:
- if a projected export, derived summary, quarantined source artifact, or promoted head appears in prose, the fixture pack is incomplete until the matching produced-by receipt and lineage links appear in schemas/examples/scenarios too.

## Contradiction/arbitration coverage
The fixture corpus now also freezes one missing review seam:
same-scope competing artifacts must not silently collapse into one winner.

That means the corpus now includes:
- `cargo-report-contradiction-packet.schema.json`
- taxonomy classes for `conflict_scope_class`, `precedence_rule`, `review_queue_status`, and `head_guard_status`
- a named scenario where same-scope native/derived artifacts compete and stronger current/public/frozen-head reuse stays blocked until the contradiction is resolved

Review-completion rule:
if a revision introduces a new way for same-scope packs, summaries, projections, or heads to compete, it is incomplete until a contradiction/arbitration scenario and the matching review-gate coverage move with it.

## Machine-checked contract hygiene
The comparison set made one further import worth preserving here: once portable meanings live in schemas, example JSON, taxonomy registers, scenario indexes, and review gates, the archive should stop trusting reviewer memory to keep those files aligned.

This fixture pack therefore pairs its control surfaces with:
- `../../tools/check_cargo_report_pack_contract.py` — validates revision stamps, taxonomy usage inside scenario coverage, review-gate artifact refs, scenario-directory presence, and example JSON against the intended schemas;
- `../../tools/hygiene.py` — one entrypoint for archive hygiene.

Practical rule:
- if a Cargo Report Kit revision changes taxonomy/schema/scenario/gate surfaces, it is incomplete until `python tools/hygiene.py` passes.

## Manual-review split truth
The comparison set still left one more seam worth freezing after contradiction packets, waiver ledgers, and execution receipts: **manual review is its own truth, not just a status string**.

This fixture pack therefore now also carries:
- `cargo-report-review-request.schema.json` — the stronger carry being requested, the safe-without-approval sentence, the consulted basis refs, and the gate ids that still block stronger reuse;
- `cargo-report-decision-witness.schema.json` — the resulting reviewer decision, the consulted basis, the blocks cleared versus kept, and any winning artifact ref.

Practical rule:
- if a contradiction, promotion carry, frozen-head carry, currentness carry, compatibility carry, or waiver renewal depends on manual review, the fixture pack is incomplete until the review request and decision witness move as first-class artifacts instead of collapsing into one queue/status label.
- if manual review was scoped to one operational head, the fixture pack is incomplete until the request names `expected_head_ref` + `head_lineage_ref`, the witness names `reviewed_head_ref` + `head_guard_status`, and at least one scenario proves stale-head carries fail closed into rereview/reissue.


## Review-separation / maker-checker coverage
The comparison set still left one more seam worth freezing after review requests, decision witnesses, waivers, and head guards: **who reviewed the stronger carry, and was that review independent enough to count?**

This fixture pack therefore now also carries:
- `cargo-report-review-separation-receipt.schema.json` — proposer / reviewer / executor identity, review-separation class, compensating control, and fallback-review expiry when full independence is weak;
- taxonomy classes for `review_separation_class` and `compensating_control_class`;
- a review gate that blocks stronger carry when self-review or same-team review lacks an explicit fallback control;
- scenario coverage for both an independent-checker path and a self-review hold path.

Practical rule:
- if public-example, frozen-head, contradiction-resolution, rechecked-current, or compatibility carry depends on manual review, the fixture pack is incomplete until the review request and decision witness point at one review-separation receipt saying whether the stronger carry cleared an independent checker or only a compensating fallback lane.
