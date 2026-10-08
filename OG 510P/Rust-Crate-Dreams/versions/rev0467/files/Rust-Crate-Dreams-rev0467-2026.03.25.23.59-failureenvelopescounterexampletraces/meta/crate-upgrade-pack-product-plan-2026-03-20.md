## 2026-03-20 refinement — crate upgrade-pack lane now also needs omission-register truth

- Keep **omission-register truth** explicit alongside publication-surface, redaction, summary-claim, and durable-cue truth: a lane should say when known hazards, receipts, or local-only context were intentionally left off the public entry surface or export bundle for non-redaction reasons.
- Prefer one compact `omission-register.report` rather than asking readers to infer completeness from whatever happens to be visible.
- Treat “not exported” and “not known” as adjacent but non-identical truths.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs surface-authorship truth

- Keep **surface-authorship truth** explicit alongside source-lineage, summary-claim, review-provenance, and replay-bridge truth: a lane should say whether each surfaced artifact is Cargo-native generated evidence, maintainer-authored guidance, reviewer-authored governance, archive-derived presentation, or mixed/third-party context.
- Prefer one compact `surface-authorship.report` rather than asking readers to infer trust-plane changes from file names, source kinds, or prose labels.
- Treat “exactly cited” and “same authorship/trust plane” as adjacent but non-identical truths.

## 2026-03-20 refinement — crate upgrade-pack lane now also needs baseline-state truth

- Keep **baseline-state truth** explicit alongside config-basis, lane-selection, capture-context, and replay-bridge truth: a lane should say whether the checked subject was a pinned published release, a reconstructible package extract, or a mutable local workspace.
- Keep **pristine-vs-drift posture** explicit too: dirty trees, partially migrated workspaces, and local unpublished edits should not quietly inherit the trust surface of a clean release-pair baseline.
- Prefer one compact `baseline-state.receipt` rather than asking readers to infer starting-subject honesty from command lines, package scope, or stray notes.

---
## 2026-03-20 refinement — crate upgrade-pack lane now also needs config-basis truth

- Keep **config-basis truth** explicit alongside lane-selection, capture-context, and replay-bridge truth: a lane should say which Cargo config layers or override surfaces materially shaped what was resolved or built.
- Keep **ambient-vs-explicit config posture** explicit too: checked-in repo config, CI injection, user-home config, `--config`, environment variables, and manifest overrides should not collapse into one fake "command ran under default Cargo behavior" story.
- Prefer one compact `config-basis.receipt` rather than asking readers to infer hidden basis from `env` digests, lockfiles, or stray notes.

---
## 2026-03-20 refinement — crate upgrade-pack lane now also needs session-honesty truth

- Keep **session-honesty truth** explicit alongside capture-context and coverage-matrix truth: a lane should say whether imported evidence belongs to one native session, one explicit capture family, a cross-session comparison, or a mixed-session synthesis.
- Keep **mixed-session disclosure** explicit too: public summaries that join receipts across distinct sessions should carry a visible warning and one summary claim about that posture.
- Prefer one compact `session-honesty.report` rather than asking readers to infer coherence from scattered session ids inside import receipts.

# Crate upgrade-pack product plan — 2026-03-20

This note tightens **P-0514 Crate Upgrade Pack Kit** one step past the 2026-03-19 authority/scope pass.
The earlier pass already established that the crate should publish **hazard-authority truth**, **package-scope truth**, and **follow-through coverage truth**.
This pass asks a sharper question:

> What still has to become explicit before a maintainer-authored upgrade pack can be trusted when it imports human-authored release notes, faces conflicting signals, or carries manual migration work across release pairs?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But it should now treat the following review objects as first-class:

1. **`source-lineage.receipt.json`** for imported human-authored migration surfaces,
2. **`hazard-arbitration.report.json`** for adjacent authorities that disagree or only nearly agree,
3. **`followthrough-state.report.json`** for keeping migration-step membership separate from active request and current-lane completion.
4. **`import.receipt.json`** for preserving native tool/report import truth and stability posture.
5. **`fixup-posture.report.json`** for separating fix capability from allowed execution posture.
6. **`source-heads.report.json`** for keeping latest operational guidance separate from citation-ready frozen source heads.
7. **`pack-readiness.report.json`** for giving reviewers one fused answer about whether the pack should stay on hold or can be frozen.
8. **`review-queue.report.json`** for turning remaining debt into explicit queued review work instead of one prose step.
9. **`cross-register-consistency.report.json`** for rejecting impossible combinations across readiness, sources, scope, follow-through, and posture surfaces.
10. **`export-posture.report.json`** for keeping internal maturity separate from public-shareable posture.
11. **`publication-surface.manifest.json`** for freezing the exact public contract surface instead of implying the whole working tree is exported.
12. **`deviation-ledger.receipt.json`** for making non-default freeze/export/consistency posture explicit, numbered, and expiring.
13. **`redaction.receipt.json`** for making public-export sanitization explicit instead of silent.
14. **`warning-register.report.json`** for backing compact warning labels with severity, audience, and source/provenance.
15. **`revalidation-window.policy.json`** for declaring review clocks, material-change triggers, and supersession rules.
16. **`freshness-state.report.json`** for classifying whether a pack is current, stale-but-usable, expired, or superseded.
17. **`summary-claim.register.json`** for keeping exported human summary claims traceable to exact receipts, warnings, and fallback refs.
18. **`capture-context.receipt.json`** for binding imported evidence to the exact package/target/feature/toolchain/lockfile context that produced it.
19. **`session-honesty.report.json`** for saying whether imported evidence belongs to one coherent session family or a mixed-session synthesis that needs disclosure.
20. **`coverage-matrix.report.json`** for making exact checked cells explicit instead of flattening dimension lists into fake whole-lane coverage.
21. **`public-trace-path.report.json`** for proving that public summary claims actually route to resolvable exported evidence instead of private or broken refs.
22. **`lane-selection.receipt.json`** for proving why this exact package/feature/target lane was selected instead of a wider or narrower ambient Cargo default.
23. **`durable-cue.report.json`** for keeping decisive public meanings durably visible on exported entry surfaces instead of trapping them in labels or machine-readable registers.
24. **`replay-bridge.receipt.json`** for making direct replay, native-storage rerender, copied attachments, and manual-only snapshots reviewably distinct.
25. **`config-basis.receipt.json`** for making Cargo config hierarchy, environment/config injection, and dependency override surfaces reviewably explicit.
26. **`baseline-state.receipt.json`** for proving whether the checked subject was a pinned published baseline, reconstructible extract, or mutable/dirty local workspace.
27. **`surface-authorship.report.json`** for keeping native tool output, maintainer guidance, reviewer decisions, and archive-derived summaries in distinct trust buckets.
28. **`omission-register.report.json`** for keeping known-but-not-exported hazards, receipts, and local-only context reviewably disclosed instead of silently absent.

That is the next honest refinement.
Without it, the crate can still look reviewable while silently flattening nearby but non-equivalent truths.

## What the crate should provide other people now

For downstream adopters, release reviewers, and docs/support tool authors, the crate should now provide:

1. **One compact upgrade contract** instead of scattered release notes, changelog prose, compiler suggestions, and issue-thread folklore.
2. **Hazard-class truth** so people can distinguish `machine_fix_available`, `manifest_edit_required`, `behavior_check_required`, `manual_review_required`, and similar categories.
3. **Hazard-authority truth** so each hazard states whether it came from SemVer/public-API evidence, feature/default-policy drift, config/runtime policy drift, a witnessed behavior check, or a maintainer-authored note.
4. **Source-lineage truth** so imported release/changelog/docs/thread surfaces can be reviewed as canonical, advisory-only, or blocked-fail-closed inputs.
5. **Hazard-arbitration truth** so packs can keep disagreements visible instead of laundering them into one synthetic winner.
6. **Package-scope truth** so a workspace can honestly say “the library member lane was checked, the CLI/example lane was not”.
7. **Fixup-capability receipts** so each claimed automation path says which tool produced it, what applicability was observed, and which surfaces it actually touched.
8. **Active follow-through state** so docs/config/example/manual steps stay separate from current-lane completion claims.
9. **Native import truth** so machine-native tool/report imports can stay distinct from later prose or lossy normalization.
10. **Fixup posture truth** so “automation exists” never masquerades as “unattended execution is allowed”.
11. **Source-head truth** so a pack can say which imported guidance head is current for operators and which source, if any, is frozen enough to cite.
12. **Pack-readiness truth** so reviewers can see whether the pack honestly stays `hold`, graduates to `candidate`, or is actually `freeze_ready`.
13. **Review-queue truth** so remaining source pinning, arbitration, scope, follow-through, and approval work is explicit and ordered.
14. **Cross-register consistency truth** so the pack can loudly reject impossible states instead of letting contradictions hide in separate receipts.
15. **Export-posture truth** so a pack can stay private/internal until audience scope and redaction posture are actually honest.
16. **Publication-surface truth** so the public contract says exactly which files and receipts are exported.
17. **Deviation-ledger truth** so temporary overrides stop living as informal meeting memory.
18. **Warning-register truth** so public labels, blocker severity, and source provenance stay joined.
19. **Redaction-receipt truth** so public-shareable posture can point to exact sanitization transforms instead of silent cleanup.
20. **Revalidation-window truth** so a pack declares how long it stays current and which changes reopen review.
20. **Freshness-state truth** so old packs can become stale, expired, or superseded instead of pretending to stay current forever.
21. **Summary-claim traceability truth** so exported human summary prose stays tied to exact receipts, warnings, and fallback refs instead of floating as free-standing authority.
22. **Capture-context truth** so imported fixes/checks/reports never outgrow the exact package/target/feature/toolchain context that produced them.
23. **Session-honesty truth** so same-session evidence can stay distinct from mixed-session synthesis and public claims can disclose when several review moments were joined.
24. **Coverage-matrix truth** so explicit matrix cells can stay observed, recipe-only, unknown, or unsupported without collapsing into one fuzzy dimension list.
25. **Public-trace-path truth** so a public claim can prove which exported route a reader can actually follow and whether any fragment/target miss remains.
26. **Lane-selection truth** so workspace defaults, explicit `-p` selection, feature activation, and target gating cannot quietly impersonate deliberate maintainer scope.
27. **Lane-fidelity reports** so people can distinguish fully observed lanes from sampled, recipe-only, workspace-subset-only, or manual-review-only lanes.
28. **Replay-bridge truth** so replay posture labels stop sounding actionable without one exact rerun/rerender/copy route.
29. **Config-basis truth** so hidden Cargo config and override surfaces stop sounding like the ordinary reviewed baseline.
30. **Baseline-state truth** so pristine published/extracted baselines stay distinct from dirty or partially migrated local workspaces.
31. **A diffable upgrade-support surface** so reviewers can see whether releases are getting easier or harder to adopt.
32. **Public-completeness honesty** so compact exported surfaces do not quietly masquerade as exhaustive ones.

## What still has to become explicit after summary-claim traceability and matrix honesty

Two more review objects now look load-bearing rather than decorative:

### 17. `capture-context.receipt.json`
This receipt exists so imported evidence never outruns the exact capture session that produced it.

A good first schema should let each capture say:

- `origin_kind` — `cargo_fix_run`, `cargo_check_run`, `cargo_metadata_run`, `cargo_semver_checks_run`, `cargo_report_replay`, or another explicit origin,
- `command_family` — the reviewed command lane in compact form,
- `selection` — the package, target, feature, profile, and target-triple selection that was actually active,
- `toolchain_posture` and `lockfile_posture`,
- optional native ids such as session ids or report ids,
- and `replay_posture` so direct replay, native-storage replay, copied attachment, or summary-only posture do not collapse together.

This is the missing honesty layer between “a native import exists” and “the whole lane was checked”.

### 18. `session-honesty.report.json`
This report exists so imported evidence can stop pretending to come from one review moment when it was actually joined across several sessions.

A good first schema should let the pack say:

- whether the lane is backed by one native session, one explicit capture family, a cross-session comparison, or a mixed-session synthesis,
- which capture refs and native session ids belong to each group,
- which alignment bases justify treating several captures as one family,
- and whether public summary prose may speak as a single-session lane, comparison-only lane, or a mixed-session lane that requires visible disclosure.

This is the missing honesty layer between "all receipts have ids" and "these receipts can safely be read as one coherent review moment".

### 18. `coverage-matrix.report.json`
This report exists so dimension lists stop pretending to be whole-lane coverage.

A good first schema should let the pack say:

- which dimensions participate (`packages`, `targets`, `feature_sets`, `runtime_profiles`, `config_profiles`),
- which exact sparse cells it is willing to speak about,
- whether each cell is `observed_ok`, `observed_hazard`, `fix_only`, `recipe_only`, `manual_review_required`, `unsupported`, `not_requested`, or still `unknown`,
- and which evidence/capture-context refs back that cell.

This is the missing honesty layer between “some features and targets were mentioned” and “this exact release lane was really checked”.


### 19. `public-trace-path.report.json`
This report exists so exported summary claims stop sounding inspectable when their promised public route is actually private, broken, or anchorless.

A good first schema should let each public trace route say:

- which `summary-claim` it serves,
- whether the posture is direct public receipt, summary-plus-exported-receipt, summary-plus-warning-register, summary-plus-review-queue, summary-only, or missing/withheld,
- which primary and fallback public refs a reader should follow,
- whether the route resolves, fails on a missing fragment, fails on a missing target, stays private-only, or is still blocked on redaction,
- and which typed miss kind should stay visible when the route fails.

This is the missing honesty layer between “the summary names evidence refs” and “a public reader can actually follow the route and land somewhere real.”

### 20. `lane-selection.receipt.json`
This receipt exists so reviewed upgrade scope never quietly inherits more meaning than Cargo selection actually supplied.

A good first schema should let the pack say:

- what the invocation subject was (`cwd` package, workspace root, explicit manifest path, imported receipt, or maintainer-declared subject),
- how the manifest walk resolved and whether config discovery came from ambient parent walking or an explicit manifest chain,
- whether the lane attached as a standalone package, workspace member, workspace `default-members`, `--workspace`, or an explicit workspace subset,
- which package-selection mode actually produced the lane (`current_package`, `default_members`, explicit `-p`, `--workspace`, published subset, or imported unknown),
- how features and targets were selected, including `default` features and `required-features` target gating,
- and which warnings should remain visible when ambient workspace defaults or gating still explain an omission.

This is the missing honesty layer between “here are the cells we observed” and “here is why this exact lane, rather than a sibling member or gated target, became the upgrade contract under review.”

### 21. `durable-cue.report.json`
This report exists so decisive public meanings stop hiding in compact labels, machine-readable registers, or supporting receipts that a reader is unlikely to keep in view.

A good first schema should let each cue say:

- which governing warning/readiness/freshness/deviation/manual-review object it serves,
- whether the posture is summary banner, summary callout, warning-label-plus-summary, replacement notice, exported status block, or still missing a durable equivalent,
- which exported surface refs keep the meaning durably visible,
- which compact-only refs still exist for machine-readable portability,
- and whether the cue is truly durable, compact-only, register-only, or still missing.

This is the missing honesty layer between “a public reader *could* discover the controlling meaning somewhere in the bundle” and “the controlling meaning is durably visible on the public entry surface itself.”

## Three new review objects to keep first-class now

### 1. `source-lineage.receipt.json` must stay fail-closed about imported release surfaces

The earlier pass made `hazard-authority.receipt.json` explicit.
This pass argues that authority is still too easy to over-claim unless imported human-authored surfaces carry their own source-lineage object.

A good first schema should let each import say:

- `surface_kind` — `github_release`, `changelog_file`, `migration_guide`, `docs_page`, `issue_thread`, `release_pr`, or similar,
- `authority_scope` — `canonical_release_surface`, `project_docs_surface`, `advisory_discussion_surface`, or `unknown`,
- `canonical_locator` — the reviewable release/tag/path locator the pack intends to rely on,
- `fetched_locator` — the actual fetched URL/path/anchor,
- `pin_status` — whether the source is exact-content pinned, tag/version pinned, path-only, host-only, floating, or unresolved,
- `review_status` — `reviewed`, `imported_unreviewed`, `declared_only`, or `blocked`,
- `promotion_status` — whether the import may back hazard authority, stays advisory-only, or must fail closed into manual review.

Why it matters:

- a GitHub `releases/latest` page is not the same thing as a release-tag-pinned note;
- a changelog path without a reviewed release anchor is not the same thing as a release-pair witness;
- a docs migration page can be valuable while still being broader or looser than a specific `from -> to` lane;
- and an issue thread may be useful context while remaining advisory-only.

Without this artifact, upgrade packs will keep treating nearby source surfaces as interchangeable.
They are not.

### 2. `hazard-arbitration.report.json` should preserve conflict-transparent abstention

`hazard-authority.receipt.json` says **where a hazard claim came from**.
That is not the same question as **what to do when two or more authorities remain simultaneously live**.

A good first schema should let each arbitration record say:

- `subject` — the migration surface or hazard family being judged,
- `candidate_authorities` — the still-live authorities/claims,
- `confusability_class` — `semver_slice_vs_feature_policy`, `maintainer_note_vs_behavior_witness`, `scope_mismatch`, `stale_import`, `incomplete_witness`, or similar,
- `arbitration_rule` — the compact rule allowed to choose among candidates,
- `abstain_baseline` — what honest fallback applies if no safe winner exists,
- `outcome` — `winner_selected`, `manual_review_required`, `unsupported_lane`, or `advisory_only`,
- and optional `selected_authority_refs` plus notes.

Why it matters:

- SemVer/public-API evidence can stay green while feature/default-policy or runtime-profile migration still produces a real hazard.
- A maintainer note can claim a lane is covered while the checked recipe still fails.
- A behavior witness can exist for one package subset while broader workspace language still sounds universal.

Without this artifact, upgrade packs will keep collapsing disagreement into a polished answer.
Sometimes the correct answer is **manual review because the candidates do not honestly collapse**.

### 3. `followthrough-state.report.json` should split lane membership from current request/completion state

The earlier pass kept `fixup-capability.receipt.json` follow-through-aware.
This pass argues that the remaining missing object is **current state**, not just capability.

A good first schema should let each step say:

- `step_id` and `surface` — what migration step exists and where it lands,
- `request_state` — `not_needed`, `active`, `rerequest_needed`, or `closed`,
- `completion_state` — `not_started`, `machine_fixed`, `human_receipted`, or `completed_previous_lane`,
- optional `completion_lane` / `receipt_ref`,
- and compact notes.

Why it matters:

- a docs/example update can belong to the migration family even after the current request is closed,
- a previously completed docs step may need a new explicit request when a newer release pair changes the same surface again,
- a machine fix can satisfy one step while leaving another step on the same surface active,
- and “manual work exists somewhere in this family” is not the same claim as “the current lane still asks for that work.”

Without this artifact, upgrade packs will keep confusing retained step membership with live request state.


## Two more review objects worth freezing now

### 14. `revalidation-window.policy.json` should make pack perishability explicit

The current lane can already say whether a pack is internally coherent enough to freeze or export.
It still needs one bounded object that says **how that judgment ages**.

A good first schema should let each policy say:

- which review clock applies,
- when the clock starts,
- which material changes immediately expire the pack,
- whether a missed clock only makes the pack `stale_but_usable` or fully `expired`,
- and whether a newer current pack automatically supersedes an older one.

Why it matters:

- a moved migration-guide head is not the same thing as the same head reviewed later,
- a changed dependency/workspace graph can invalidate a once-frozen recipe set,
- and public upgrade summaries should not quietly survive as if time and lane drift do not exist.

### 15. `freshness-state.report.json` should separate stale, expired, and superseded packs

Even with a declared policy, downstream users still need one compact answer about the pack in hand.

A good first schema should let the report say:

- `current`, `stale_but_usable`, `expired`, `superseded`, or `unknown`,
- the reason class,
- any trigger refs,
- whether public use is still allowed,
- and which newer pack supersedes the current one when applicable.

Why it matters:

- `stale_but_usable` is not the same thing as `expired`,
- `expired` is not the same thing as `superseded`, because superseded means revalidation already happened elsewhere,
- and older public summaries should redirect to newer current packs instead of competing with them.

## One more review object worth freezing now

### 16. `summary-claim.register.json` should stop exported prose from floating free of exact receipts

The pack can already publish a bounded public surface and a compact warning register.
That still leaves a reader-facing gap:

> which exact public summary claims are being made, what backs them, and where should a reader go when one sentence compresses too much?

A good first schema should let each claim say:

- `claim_id` and `section_id` — the stable local handle for the public sentence or bullet,
- `claim_class` / `audience` / `status` — whether the statement is a hazard, scope limit, fixup posture, manual-review boundary, freshness note, or next-step claim and who it is for,
- `authoring_mode` — `native_import`, `maintainer_authored`, `mixed_synthesis`, or `derived_register`,
- `evidence_refs` — the exact receipts/reports that constrain the claim,
- optional `warning_refs`, `deviation_refs`, and `source_head_refs`,
- and one `fallback_ref` when the summary sentence should hand a reader into a more exact receipt or review-queue item.

Why it matters:

- a public summary sentence can compress hazard authority, scope partiality, warning state, and a manual boundary into one polished line;
- downstream tools may import the summary before they import every sidecar receipt;
- and once a pack becomes public, the summary often becomes the first-contact surface even when it is not the most exact one.

Without this object, the lane still permits one ordinary lie: exported prose that sounds exact because the pack is reviewable somewhere else.

## Recommended `0.1` command-surface refinements

### `cargo upgrade-pack capture`
Should now capture:

- `from -> to` lane identity,
- imported SemVer/public-API findings,
- hazard classes,
- hazard authorities,
- source-lineage receipts,
- hazard-arbitration reports,
- fixup-capability receipts,
- package-scope report,
- followthrough-state report,
- recipe references,
- checked feature/target/runtime/package dimensions,
- and known manual-review boundaries.

### `cargo upgrade-pack doctor`
Should now render warnings such as:

- `source_lineage_unpinned_or_floating`
- `advisory_source_cannot_promote_hazard_authority`
- `hazard_authorities_conflict_manual_review_required`
- `source_fix_observed_but_followthrough_rerequest_needed`
- `pack_review_clock_elapsed_stale_but_usable`
- `material_change_requires_revalidation`
- `newer_pack_supersedes_current_public_summary`
- `previous_lane_completion_cannot_close_current_lane`
- `package_scope_partial`
- `manual_review_required`

`doctor` should remain a human-first renderer over captured artifacts, not a magical verifier.

## Suggested proving-ground scenarios

A disciplined `0.1` should now prove itself on a small set of fixtures:

1. **GitHub release notes imported through a floating alias rather than a release-pinned anchor**
2. **SemVer/public-API slice stays green while feature-policy drift and behavior witnesses still produce a real hazard**
3. **docs/example follow-through was completed on an older lane but must be explicitly re-requested for the current lane**
4. **maintainer note remains advisory-only because source lineage is too weak to back hazard authority**
5. **workspace subset witness forces abstention instead of a fake whole-workspace verdict**

## Bundle draft

A sharper bundle draft is now:

- `upgrade-pack.toml`
- `upgrade-hazards.report.json`
- `hazard-authority.receipt.json`
- `source-lineage.receipt.json`
- `hazard-arbitration.report.json`
- `fixup-capability.receipt.json`
- `package-scope.report.json`
- `followthrough-state.report.json`
- `pack-readiness.report.json`
- `review-queue.report.json`
- `cross-register-consistency.report.json`
- `export-posture.report.json`
- `publication-surface.manifest.json`
- `redaction.receipt.json`
- `deviation-ledger.receipt.json`
- `warning-register.report.json`
- `summary-claim.register.json`
- `public-trace-path.report.json`
- `durable-cue.report.json`
- `revalidation-window.policy.json`
- `freshness-state.report.json`
- `migration-recipe.manifest.json`
- `upgrade-check.report.json`
- `upgrade-diff.report.json`
- `upgrade-notes.summary.md`

## Two more review objects worth freezing now

### 8. `review-queue.report.json` should turn pack debt into explicit queued review work

`pack-readiness.report.json` fuses debt into one verdict.
That still leaves a practical receiver-facing gap:

> what exact work remains, in what order, and which items block `candidate` versus `freeze_ready`?

A good first schema should let the queue say:

- `readiness_ref` — which fused readiness verdict the queue inherits,
- a bounded set of `queue_items`, each with `item_id`, `class`, `status`, `required_before`, and compact summary text,
- `blocker_refs` back to source-head, arbitration, scope, follow-through, or posture artifacts,
- optional `suggested_next_action` and `command_hint`,
- and one `next_queue_head`.

Why it matters:

- one prose `next_safest_step` hides concurrency and dependency ordering,
- real upgrade maturation work is often review/unblock work rather than more capture work,
- and a future maintainer should not have to rediscover which missing pin, approval, or scope confirmation actually blocks freeze.

Without this artifact, pack maturity still leaks into project-manager folklore instead of staying a reviewable support surface.

### 9. `cross-register-consistency.report.json` should fail loudly when honest receipts disagree

The pack now carries source lineage, source heads, hazard arbitration, import truth, fixup posture, package scope, follow-through state, and pack readiness.
That creates a new risk:

> the pack can be locally honest in each file and globally dishonest in the combination.

A good first schema should let one consistency report bind:

- `source_heads_ref`, `pack_readiness_ref`, `package_scope_ref`, `followthrough_state_ref`, and optional `fixup_posture_ref`,
- a compact set of `checks` with `rule`, `status`, `reason`, and `refs`,
- and one `overall_status` that stays `unknown` rather than implying success under missing inputs.

Why it matters:

- `freeze_ready` should fail if citation-head gaps remain,
- `freeze_ready` should fail if active follow-through or partial scope claims remain,
- and already-typed lanes should stay exact rather than borrowing broader or looser claims from nearby receipts.

Without this artifact, contradiction detection stays informal at exactly the moment the pack is supposed to become a public contract.

### 11.5 `redaction.receipt.json` should keep public export from relying on silent sanitization

`export-posture.report.json` can already say whether redaction is still required, applied, or blocked.
`publication-surface.manifest.json` can already say which public files and refs are exported.

A good first schema should let one redaction receipt say:

- `source_surface_refs` — which internal notes, recipes, or working surfaces required sanitization,
- `target_surface_refs` — which public summary or manifest surfaces depend on that sanitization,
- `status` — whether the redaction pass is only planned, already applied, fully verified, or not needed,
- one list of `operations` with a compact `basis`, `action`, `subject_ref`, and public effect for each transform,
- `verification_posture` — whether the pass was manually reviewed, dual-reviewed, or only schema-checked,
- and optional `private_context_refs` so the archive can preserve where the private raw material still lives without exporting it.

Why this deserves first-class status:

- `redaction_status: applied` is still too easy to claim without one bounded record of what changed,
- workspace-local paths, private registry locators, internal package aliases, and raw working notes are common reasons a pack should stay private until cleaned up,
- and once a pack becomes public, reviewers should be able to inspect the *basis* for public-shareable posture without seeing the private raw values themselves.

Without this object, the lane still permits one ordinary lie: a public-looking pack whose sanitization story is trusted because the bundle looks clean, not because the transformation basis was actually receipted.

### 12. `deviation-ledger.receipt.json` should make override posture numbered and expiring

Once the pack can honestly say `hold`, `candidate`, `freeze_ready`, `withhold_publication`, or `public_candidate`, one practical gap remains:

> what happens when a maintainer intentionally proceeds under a temporary exception without pretending the underlying blocker vanished?

A good first schema should let each deviation say:

- `class` — `freeze_override`, `export_override`, `publication_override`, `consistency_override`, or `manual_review_override`,
- `applies_to_refs` — which readiness, consistency, source-head, or publication artifacts the deviation touches,
- `owner` and `approving_authority`,
- `approved_on` and `expires_on`,
- `reason` plus any `compensating_controls`,
- and whether a `public_summary` exists or cannot be published.

Why it matters:

- a temporary override is sometimes honest, but only if it becomes a numbered, expiring record;
- otherwise teams quietly turn blocker states into folklore exceptions;
- and the public contract can drift into looking baseline-clean while really operating under a hidden exception.

### 13. `warning-register.report.json` should join compact labels back to source and severity

The pack now has source-head warnings and publication-surface `warning_labels`, but one compact receiver-facing gap remains:

> which warnings are active right now, which are blocking, which are public, and which ones are temporarily carried by a deviation?

A good first schema should let each warning say:

- `label` and `class`,
- `severity` — `advisory` or `blocking`,
- `audience` — `maintainer_only` or `public_contract`,
- `status` — `active`, `resolved`, or `suppressed_by_deviation`,
- `source_refs` and `surfaced_on_refs`,
- and optional `deviation_ref`.

Why it matters:

- compact warning labels are useful only if reviewers can trace them back to the receipts that caused them;
- public warning surfaces should not silently omit blocker severity or audience scope;
- and a deviation should carry a warning forward explicitly rather than erase it.

## Why this could matter

This is the crate that would let maintainers say:

- “Here is the supported migration path from our previous release.”
- “Here is which imported source surfaces were canonical enough to back the hazard story.”
- “Here is where the authorities disagreed and why we fell back to manual review.”
- “Here is which docs/config/example steps are still actively requested on this exact lane.”
- “Here is what tooling really auto-fixed, and what still needs a person.”

That is a more honest support layer than changelog prose, release PRs, or source-only codemods.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://doc.rust-lang.org/cargo/reference/publishing.html
- https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
- https://release-plz.dev/docs/usage/update
- https://release-plz.dev/docs/config
- https://docs.rs/crate/cargo-semver-checks/latest
- https://docs.rs/rustfix/latest/rustfix/enum.Filter.html


## Two more review objects worth freezing now

### 4. `import.receipt.json` should keep native tool truth separate from later normalization and summary

The archive already had the right instinct elsewhere: import truth should be reviewable before downstream explanation.
That applies directly here.

A good first schema should let each imported source say:

- `kind` — `cargo_semver_checks`, `cargo_fix`, `rustfix`, `clippy_fix`, `cargo_report_future_incompat`, `cargo_report_sessions`, `cargo_report_timings`, `cargo_report_rebuilds`, `cargo_metadata`, or `manual_annotation`;
- `source_ref` — the captured file, report ID, or canonical source pointer;
- `consumption_mode` — `verbatim_import`, `normalized_extract`, `summarized`, or `manual_note`;
- `stability_posture` — `stable`, `unstable`, `external`, `mixed`, or `unknown`;
- optional `native_identity` — report/session IDs, command lines, or metadata format details;
- and compact lossiness notes.

Why it matters:

- native tool output and later prose are different authorities,
- Cargo now has stable and unstable report lanes with different maturity,
- and upgrade packs will increasingly join data from `cargo semver-checks`, `cargo fix`, `cargo metadata`, and future Cargo-native report families.

Without this artifact, the pack can still look honest while hiding whether a fact came from native evidence or from a later summary.

### 5. `fixup-posture.report.json` should separate fix capability from permission to execute

`fixup-capability.receipt.json` answers **what kind of fix substrate exists**.
It does not yet answer **what the lane is willing to let that substrate do**.

A good first schema should let each fix say:

- `origin` — `cargo_fix`, `rustfix`, `clippy_fix`, `maintainer_codemod`, `manual_recipe_only`, or `no_fix_available`;
- `posture` — `manual_only`, `assisted_suggestion`, `approval_required_single_action`, `approval_required_sequence`, or `bounded_autorun`;
- `status` — whether the posture was observed, declared, blocked, or missing;
- optional `scope`, `stop_conditions`, `evidence_refs`, and notes.

Why it matters:

- `cargo fix` proving that a source rewrite exists does not imply manifest/config/docs follow-through is safe to run unattended,
- a bounded sequence can still require explicit readback and stop conditions,
- and uncertain or partial state should bias the pack toward downgrade/manual review, not optimism.

Without this artifact, upgrade packs will keep over-claiming what automation is allowed to do.


## Two final review objects worth freezing now

### 6. `source-heads.report.json` should keep operational guidance heads separate from citation-ready heads

`source-lineage.receipt.json` records one imported surface at a time.
That still leaves a lineage-level inheritor question unanswered:

> which imported migration surface is merely the latest useful operational guide, and which one is frozen tightly enough to cite as the reviewed release-pair head?

A good first schema should let each source family say:

- `source_family_id` plus `import_refs` and `tip_refs`,
- `operational_head_ref` and `operational_head_status`,
- `citation_head_ref` and `citation_head_status`,
- and explicit warnings such as `citation_head_missing`, `citation_head_not_exact_pinned`, `branch_ambiguous`, or `floating_alias_tip`.

Why it matters:

- a docs `latest` migration page may still be the best current operational guide while remaining too floating to cite,
- multiple live migration notes can make the operational head ambiguous even before citation safety is considered,
- and a source family can stay useful for operators while honestly lacking any citation-ready frozen head.

Without this artifact, reviewers must manually reconstruct lineage-head status from many individual source-lineage receipts.
That is exactly the kind of silent inference this lane should stop demanding.

### 7. `pack-readiness.report.json` should fuse review debt into one honest freeze verdict

The bundle now carries many truth surfaces, but a reviewer still has to merge them by hand to answer:

> is this upgrade pack merely useful working material, or is it actually ready to freeze as the public contract for this release pair?

A good first schema should let the pack say:

- `readiness_state` — `hold`, `candidate`, `freeze_ready`, or `manual_review_only`,
- which `freeze_target_refs` would be frozen if ready,
- review buckets for citation-head gaps, floating imports, authority conflicts, partial scope claims, active follow-through steps, posture blockers, and unstable imports,
- and one `next_safest_step`.

Why it matters:

- the archive already knows how to represent all of these debts individually,
- but future maintainers still need one fused review surface rather than a scavenger hunt across receipts,
- and the honest answer is often “keep this on hold” rather than “ship the polished pack because the pieces exist somewhere.”

Without this artifact, upgrade-pack maturity remains a vibes-based synthesis.
That is too much hidden judgment for a lane whose whole purpose is boring reviewability.


## Two more review objects worth freezing now

### 10. `export-posture.report.json` should keep internal maturity separate from public-shareable posture

`pack-readiness.report.json` tells reviewers whether the migration story itself is coherent enough to hold, candidate, or freeze.
That still leaves a different inheritor question unanswered:

> is this lane only good enough for maintainers inside one workspace, or is it actually safe to export as a public downstream contract?

A good first schema should let the pack say:

- `audience_class` — `maintainer_only`, `workspace_internal`, `organization_internal`, or `public_downstream`,
- `exposure_scope` — whether the bundle is still private-workspace, private-org, public-docs, or public-release material,
- `sensitivity_flags` — local paths, internal package aliases, private registries, private example context, or internal working notes,
- `redaction_status` — `not_needed`, `required_before_public`, `applied`, or `manual_review_required`,
- `decision_state` — `private_working`, `private_candidate`, `public_candidate`, `public_frozen`, or `withhold_publication`,
- and blocker refs back to queue/readiness/consistency work.

Why it matters:

- a pack can be epistemically strong yet still leak private paths or package names,
- internal review posture is not the same thing as public-shareable posture,
- and “freeze-ready” should not silently mean “ship everything in the working tree.”

Without this artifact, upgrade packs will keep confusing migration maturity with export maturity.

### 11. `publication-surface.manifest.json` should freeze the exact public contract surface

Once a lane is exportable, maintainers still need one tiny answer to a downstream question:

> what exactly is on the stable public surface, and what still stays off-surface as internal, floating, or redaction-bound working material?

A good first schema should let the pack say:

- `surface_state` — `candidate_public` or `frozen_public`,
- `entry_points` — the summary, recipe, supporting receipts, and warning-label surfaces that make up the contract,
- `context_refs` — the readiness, consistency, and export-posture inputs that justify the public surface,
- `omitted_refs` plus omission reasons such as `internal_working_only`, `redaction_pending`, `floating_source`, or `not_citation_ready`,
- and one compact set of `warning_labels` that travel with the public entry points.

Why it matters:

- maintainers should not have to infer the public contract by reading the whole working tree,
- floating imports and private notes can remain useful internally while staying off the public surface,
- and a downstream adopter should meet the warning labels at the same surface where they meet the summary and recipe.

Without this artifact, the lane can still publish a summary while leaving the actual exported contract implicit.

### 12. `review-provenance.report.json` should keep maker-only polish separate from independently checked public freeze

The bundle can now prove a lot about the migration story itself, but it still leaves one receiver-facing trust question under-specified:

> is this public/frozen upgrade pack just exact working material, or did anyone independent actually check the contract that downstream readers are being asked to trust?

A good first schema should let the pack say:

- `overall_posture` — `maker_only`, `maker_checker_separated`, `fallback_review_only`, `mixed`, or `unknown`,
- per-surface review posture for `internal_candidate`, `public_candidate`, and `frozen_public`,
- `maker_refs` and `checker_refs`,
- `separation_class` — same-author, same-team, independent, fallback, or not reviewed,
- `challenge_posture` — open, closed, closed-with-objection, or not applicable,
- and one bounded `decision` such as `candidate_ok`, `freeze_ok`, or `withhold`.

Why it matters:

- a mechanically precise pack can still overclaim social trust if maker-only review is left implicit,
- public freeze is a different promise from “the author believes the receipts look good,”
- and fallback review should be visible as a narrower trust posture, not a silently equivalent substitute for independent checking.

Without this artifact, a frozen/public pack can still sound like a reviewed contract when it is only well-organized maker-authored material.


### 23. `replay-bridge.receipt.json`
This receipt exists so replay posture stops sounding like a route when it is really only a hope, a copied snapshot, or a dead end.

A good first schema should let each bridge say:

- which import or capture refs it serves,
- whether the route is a direct command rerun, native-storage rerender, copied attachment open, manual reconstruction, or not replayable,
- which native ids, attachment refs, or prerequisites anchor that route,
- what copy provenance applies (`native_storage_only`, `copied_verbatim`, `copied_after_redaction`, `maintainer_rewritten`, or similar),
- what fidelity should be expected (`byte_exact_expected`, `semantically_equivalent_expected`, `manual_compare_required`, or `summary_only`),
- and whether the route is currently usable, blocked, stale, or missing.

This is the missing honesty layer between “the capture says replayable” and “a reviewer can actually rerun or reconstruct this evidence on purpose.”

### 24. `config-basis.receipt.json`
This receipt exists so ordinary-looking Cargo commands stop hiding the config hierarchy and override surfaces that materially changed what the lane witnessed.

A good first schema should let the pack say:

- which config sources mattered (`workspace .cargo/config.toml`, parent config, `CARGO_HOME` config, `--config`, environment variables, `rust-toolchain.toml`, manifest-declared overrides, or similar),
- whether each source was repo-checked-in, CI-injected, user-local, or ephemeral,
- which influence domains it touched (resolver, registry, compiler flags, toolchain, target defaults, network, cache paths, wrappers, output paths, aliases),
- and which override surfaces were active (`[patch]`, `replace`, source replacement, local path dependencies, alternate registries, git overrides, or none) together with their portability posture.

Why it matters:

- Cargo merges config hierarchically and also reads environment/config injection, so the same visible command can represent very different reviewed baselines,
- `[patch]`, source replacement, and local path overrides can make a lane less upstream-representative or less portable than the command line suggests,
- and an `env` digest alone is not a receiver-facing contract for *which* hidden basis changed the result.

Without this artifact, an upgrade pack can still sound like ordinary reviewed Cargo behavior when hidden config or override state materially shaped the witness family.


### 25. `baseline-state.receipt.json`
This receipt exists so exact command/config/session truth stops sounding like a clean release-pair contract when the checked subject was already locally drifted.

A good first schema should let the pack say:

- whether the lane was checked against a pinned published release, a reconstructible package extract, a git checkout, a live workspace working tree, or a synthetic fixture,
- what role each subject played (`from_subject`, `capture_workspace`, `comparison_baseline`, or similar),
- whether each subject was pristine, dirty, partially migrated, generated, or otherwise non-default,
- whether each subject was immutable, reconstructible, or live-mutable,
- and what claim posture remains honest (`safe_release_pair_contract`, `comparison_only`, `local_only`, or `manual_review_required`).

Why it matters:

- package/feature/target scope can still be exact while the starting subject is not a clean published baseline,
- config-basis truth can still be honest while a mutable workspace quietly inherits the aura of a release-pair contract,
- and replayability does not answer whether the replay reconstructs the right *subject* rather than a later partially migrated tree.

Without this artifact, an upgrade pack can still sound like a clean release-to-release contract when the actual checked subject was a dirty or partially migrated local workspace.
