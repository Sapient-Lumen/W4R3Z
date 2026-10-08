# Engineering Backlog

This file tracks high-leverage gaps for building Concord as a deterministic scientific tool.

## Highest Priority

- **[SCREENING CONTRACT + DECLARED PROXY SPEC IMPLEMENTED — UNCERTAINTY-AWARE SCREENING OVERLAY NOW IN PLACE; WORLD SEMANTICS STILL PENDING]** `grlab certify` now emits a schema-typed memory-one result, an explicit anti-vampire `screening_contract`, a `screening_spec_ref` carrying both a human-readable `spec_id` and an immutable `spec_fingerprint_sha256` for the effective normalized screening contract, a declared `stage_game_ref` plus explicit `state_order`, compact uncertainty summaries for the rollout-derived ecology / repair proxy fields, an explicit `uncertainty_contract_ref` for the interval semantics behind those summaries, an explicit `proxy_measurement_contract_ref` for the sign / aggregation / event semantics behind the proxy fields themselves, an explicit `steady_state_contract_ref` for the exact-stationary / Cesàro fallback semantics behind the top-level payoff surface, an explicit `opening_distribution_contract_ref` for the `p0`-to-state product construction behind the declared opening distribution, an explicit `transition_kernel_contract_ref` plus top-level `transition_matrix`, compact `transition_graph_diagnostics` describing communicating classes / closed classes / absorbing states / initial-support reachability, exact basin entry probabilities, and basin-conditioned asymptotic decomposition for the actual 4×4 Markov kernel behind the payoff / recovery / ecology surface, plus a top-level exact `asymptotic_distribution_from_initial_distribution` / asymptotic-payoff surface with a compact `steady_state_distribution_l1_distance_to_asymptotic_distribution` witness so reducible runs can be read as exact long-run mixtures rather than only as finite fallback vectors, exact pre-closure cumulative payoff burden, exact pre-closure state-visit counts, and exact pre-closure transition counts overall and conditional on each recurrent basin so transient path incentives and edge-level mechanism no longer have to be reconstructed from the kernel by hand, and an uncertainty-aware screening overlay (`binding_gate_status`, `gate_stability`, per-check `threshold_decision_state`) so inheritors can distinguish sharp binding decisions from borderline CI-crossing cases without recomputing the gate by hand. The remaining work is to promote the recovery / repair semantics from a schema-backed proxy spec into a genuinely world-declared contract rather than merely a better-declared proxy lane, and to decide whether future gate semantics should adaptively rerun / certify borderline cases rather than only labeling them. See `docs/LIBRARY/topics/anti_vampire_scorecard_spec.md`, `schemas/certify_memory_one_result.schema.json`, `schemas/certify_memory_one_screening_spec.schema.json`, and `examples/certify/canonical_proxy_v1.json`.
- **[CRITICAL]** Do not run search in zero-noise pairwise evaluation. Search must evaluate candidates against a cooperative pool under noise (e.g., 2% implementation noise). See `noisy_ecology_test_reveals_zd_extraction.md` for rationale and results.
- Formalize solver contracts between `gr_engine` artifacts and `grlab certify` outputs.
- Expand control tests for determinism and replay behavior across harness modes.
- Stabilize timing baselines (`goldens/timing_baseline.json`) with real p95 calibration runs.
- Add stricter schema validation coverage for critical artifact types — including the new anti-vampire scorecard fields.

## Near-Term

- Improve search result provenance (search policy config and mutation parameters in outputs).
- Add more holdout suites for out-of-distribution robustness checks.
- Strengthen release posture (`gate-strict`) with installed security tooling in CI.
- Add machine-readable release manifest/checksum command for versioned bundles.
- Promote the new focal leave/rematch proxy into an engine-supported world to test partner-choice as a Golden-Rule stabilizer.
- Do not count `memory_one_exit` in a fixed dyad as “partner choice”; rematching / outside-option mechanics need their own world.
- Keep `mem1_exit_after_break_v1` as a compact rematch-world baseline and canonicalize unreachable post-exit parameters when search lands there.
- Add world-aware genotype-to-phenotype canonicalization before ranking rematch-enabled search results, because the current proxy shrinks 243 raw deterministic exit codes to 63 support-distinct families.
- Treat the current 63-family rematch quotient as a cooperative-pool lower bound; a single suspicious starter reopens it to 87 families, so canonicalization must be recomputed when entrant support changes.
- In the current deterministic no-noise proxy, reuse the rematch canonicalization cache only for entrant additions with C-only initial support; any entrant with initial D support should invalidate and trigger recomputation.
- Treat that start-support gate as zero-noise-only: any nonzero action tremble should invalidate the current cache and force recomputation under the active noise semantics.
- Use a mode-specific rematch cache key rather than one universal one: in the current proxy, opponent/bilateral tremble collapse to one quotient regime, focal tremble collapses to two, and only zero-noise remains heavily signature-sensitive.
- Do not keep the inherited `h=50` support-reachability bound in the current proxy: exact canonicalization saturates by `3/2/2/1` rounds across `{none, opponent, focal, bilateral}` noise modes, so unroll depth should be world-keyed and revalidated when semantics change.
- Compile the current proxy's canonicalization planner instead of keying on full entrant signatures plus `h=50`: the local exact plan shrinks key-depth budget from `12150` slots to `51/2/4/1` across `{none, opponent, focal, bilateral}` noise modes.
- Require rematch-world benchmark artifacts to report occupancy accounting (`matched_round_share`, `dead_round_share`, `in_match_avg_payoff`) alongside aggregate payoff, because the current proxy's delay tax is mostly a loss of time spent in productive matches.
- Do not collapse temporary-partnership persistence and rematch delay into one friction knob; the next endogenous world should expose both match persistence/separation and rematch/search dead-time explicitly.
- Publish `avg_match_length` or an equivalent turnover-rate field in rematch benchmarks; in the current proxy, the same fixed delay imposes a much larger occupancy tax on short temporary partnerships than on long-lived ones.
- In the current zero-noise proxy, replace the bulky `243`-entry `support_signature -> regime` dispatch table with the exact `17`-rule ordered wildcard classifier and regenerate it whenever world semantics change.
- Schema-check and contract-test that ordered classifier before vendoring it into any interim engine metadata.

- Add explicit override / waiver receipts for successor-safe ceremony dispositions so any accepted warning-level residual risk carries a named rationale and review trigger instead of living only in chat history.
- Keep the Rust-blocked workflow first-class: regenerate `docs/RUST_SURFACE_INVENTORY.md`, push Python shadow checks forward, and avoid archive-bloating toolchain workarounds unless they become decision-critical.
- Prefer one canonical blocked-session command surface: `make cloudtainer-shadow-pass` should be the first move in this cloudtainer so future sessions inherit one compact receipt instead of ad hoc command lists.

## Operational Debt

- Generate `flake.lock` on a host where Nix works reliably.
- Add optional signed attestations on top of existing hash-based attest/verify flow.
- Improve docs for adding new probe registries and scorecard suites.
- Keep reading sources citation-first; do not let local PDFs regrow in the long-term archive.

- occupancy-normalized rematch leaderboard contract: publish paired raw/in-match rankings so occupancy artifacts are not misread as strategy-quality changes
- delay-robustness rematch contract: publish a sweep, crossover thresholds, or a robustness interval so single-delay winners are not overstated
- live-contender rematch contract: prune dominated policies and publish leader margins so bulky delay reports track decision-relevant uncertainty rather than every below-top crossover

- winner-certification rematch contract: publish paired-seed top-gap uncertainty or certification flags so tiny leader flips are not archived as stable rank reversals
- budget-aware winner-triage rematch contract: publish approximate additional certification budget for unresolved top panels so near-ties can be deferred or labeled instead of brute-force oversampled
- materiality-gate rematch contract: publish a declared smallest effect of interest plus practical-equivalence status so statistically real but negligible leader gaps are archived as ties
- delta-frontier rematch contract: publish per-panel material/tie delta thresholds so future delta choices can be resolved from a compact artifact instead of ad hoc threshold grids
- delta-budget rematch contract: publish how unresolved panels and additional paired-seed closure cost change across the plausible SESOI band so budget/materiality tradeoffs stay explicit

- delta-hazard rematch contract: publish leader-gap knife-edge bands or a no-knife-edge buffer so SESOI choices near observed top-gap means do not masquerade as ordinary closure-cost points

- delta-admissibility rematch contract: publish budget-admissible SESOI bands plus anchor deltas so declared practical margins do not land in knife-edge closure-cost regions
- delta-topology rematch contract: publish topology-stable delta subbands or stability-first anchors so one admissible parent band cannot hide multiple materially different panel-label summaries

- Add explicit authorization receipts for successor-safe ceremony packages so claim-ready citation carries named basis checks and terms instead of living only in chat history.
- Add compact promotion records for successor-safe ceremony packages so a shift from weak to claim-ready carries prior/current locator references, closed finding codes, and explicit closure basis instead of living only in latest-state snapshots.
- Bind successor-safe ceremony review watches and review verdicts to source- or policy-locator digests so future stewards can reopen on concrete upstream drift rather than only generic trigger labels.
- Add explicit citation advisories for successor-safe ceremony packages so a reopened review verdict can withdraw claim-ready use of an old locator without leaving existing versus new citation handling in chat history.
- Add compact package manifests for successor-safe ceremony receipt packages so current authoritative component membership and file fixity stop living only in filenames and local browsing.
- Add compact package supersession records for successor-safe ceremony receipt packages so refreshed package manifests explicitly name which earlier package root they replaced and which component roles changed.

- Add compact package lineage records for successor-safe ceremony receipt packages so once more than one supersession exists, future stewards can recover the current authoritative package head and ordered replacement chain without walking filenames and timestamps by hand.

- Add compact package-head pointers for successor-safe ceremony receipt packages so once lineage exists, future stewards can discover the live authoritative manifest, status artifacts, and immediate predecessor without opening the whole chain first.

- Add compact package-status cards for successor-safe ceremony receipt package heads so a future steward can answer the live keep-citing question from one machine-checkable object instead of reopening the watch / verdict / advisory trio.
- Add compact package redirects for superseded successor-safe ceremony receipt packages so a future steward who lands on an older package root gets one explicit current-reference target and live-status pointer instead of reconstructing replacement guidance from lineage by hand.
- Bind package-status cards or package catalogs directly to the new package-verification-report surface so future stewards can discover current local verification basis without opening the package head first.


## Additional pass: successor-safe ceremony receipt package claim scopes

- Added one compact downstream-claim discipline for successor-safe ceremony receipt packages so future inheritors can see what the current local verification basis actually supports saying about the live package without overclaiming beyond the blocked Rust lane:
  - `schemas/successor_safe_ceremony_receipt_package_claim_scope.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_claim_scope.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_verification_reports_should_ship_compact_claim_scope_artifacts.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_claim_scope_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `claimscope` subcommand that collapses the current package status card plus verification report into one explicit allowed-versus-restricted claim surface.
- Refreshed the worked package head, redirect, and catalog snapshots so the live package discovery surface now carries the package-claim-scope reference forward.
- Main practical result: the archive now keeps not just what validation ran here, but also one tiny object saying what future stewards may safely claim because of that validation in this cloudtainer.


## Additional pass: successor-safe ceremony receipt package reliance cards

- Added one compact downstream-reliance discipline for successor-safe ceremony receipt packages so future inheritors can recover one explicit live answer to what they may safely rely on from the current package state without reconciling status, verification, and claim-scope artifacts by hand:
  - `schemas/successor_safe_ceremony_receipt_package_reliance_card.schema.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.package_reliance_card.json`
  - `docs/LIBRARY/topics/successor_safe_ceremony_receipt_package_claim_scopes_should_ship_compact_reliance_cards.md`
  - `artifacts/process/successor_safe_ceremony_receipt_package_reliance_card_receipt_20260322.json`
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with a `reliancecard` subcommand that collapses the current package status card, verification report, and claim scope into one explicit downstream reliance surface.
- Refreshed the worked package head / redirect / catalog snapshots so the live package discovery surface now carries the package-reliance-card reference forward.
- Main practical result: the archive now keeps not just whether the live package is citable and what claims remain in scope, but also one tiny object saying what future stewards may safely rely on right now in this Python-pass / Rust-blocked cloudtainer.
