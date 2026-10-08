# Debuggability support product plan — 2026-03-17

This note exists to keep **P-0486 Debuggability Support Contract Kit** disciplined.
The archive already decided that the missing value is a **release/support contract** for debuggability posture, symbol sidecars, visualizer assets, and drift.
This pass answers a narrower question:

> If somebody actually started building **P-0486** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- whether a given build is honestly `interactive_debugger`, `backtrace_only`, `crash_symbolication_only`, `internal_only`, or `manual_review_required`,
- where the relevant symbol sidecars actually live,
- whether those sidecars are expected, present, copied, missing, or ambiguous,
- which visualizer assets are embedded or expected externally,
- how path-hygiene settings affect source lookup,
- and what changed between releases even if the binary still “basically works”.

It should **not** try to become a debugger frontend, crash backend, source server, or giant IDE integration layer.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release engineers, and support engineers, the crate should provide:

1. **One compact debug-support contract** instead of a scavenger hunt across Cargo profiles, `rustc` flags, CI scripts, artifact directories, and release notes.
2. **A stable support-posture vocabulary** so `interactive_debugger`, `backtrace_only`, and `crash_symbolication_only` do not blur together.
3. **A sidecar-handoff manifest** that says which `pdb`, `dSYM`, `dwo`, or `dwp` artifacts are expected, where they were observed, and which ones must be archived or copied.
4. **A source-lookup impact report** so teams can see when path remapping or trimming improved privacy while weakening debugger/source lookup expectations.
5. **A short human summary** that can be pasted into release notes, issue templates, or downstream support docs.
6. **A drift artifact** so accidental debugger regressions become reviewable instead of folklore.
7. **A reusable library surface** so other tools do not all reinvent file-layout and posture heuristics.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. conservative receipts and manifests rather than a huge hosted service,
3. one explicit place to record manual-review zones,
4. artifact-handoff rules that survive build-dir churn,
5. and a CI gate for “this release got less supportable to debug”.

## Recommended `0.1` command surface

### `cargo debug-support init`
Create a starter `debuggability-policy.toml` by importing obvious facts from:

- `Cargo.toml` profile settings,
- optional profile overrides from env or config when explicitly provided,
- target triples / profile names the maintainer wants to reason about,
- and local artifact roots when the maintainer points at them.

The generated policy should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo debug-support capture`
Emit one normalized receipt bundle from a built artifact set.
This should capture:

- profile/debug/strip/split posture,
- primary artifact inventory,
- symbol-sidecar layout,
- visualizer assets,
- source-lookup impact hints,
- and artifact-handoff status.

`capture` should work on imported artifacts too.
It must not require that Cargo performed the build in the current invocation.

### `cargo debug-support check`
Run the local validation pass:

- do policy targets/profiles parse,
- do observed artifacts match sidecar expectations,
- does the observed posture satisfy the intended posture,
- did path-hygiene settings lower source-lookup expectations,
- are visualizer assets missing or obviously unmatched,
- and which parts remain manual-review-only?

### `cargo debug-support doctor`
Render receiver-facing warnings for suspicious situations such as:

- `interactive_policy_but_sidecar_missing`
- `interactive_policy_but_strip_debuginfo`
- `cargo_vs_rustc_split_default_mismatch_risk`
- `visualizer_asset_present_but_backend_unknown`
- `path_hygiene_reduces_source_lookup`
- `build_dir_relocation_without_handoff_manifest`
- `copied_binary_lost_symbol_attachment`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a separate inference engine.

### `cargo debug-support summary`
Render a short support note for release docs or support issue templates.
A good summary answers:

- what class of debugging the build supports,
- where symbols live,
- whether source lookup is likely to work,
- and what the main caveats are.

### `cargo debug-support diff <old> <new>`
Compare two receipts or packs and classify:

- `support_class_changed`
- `sidecar_added`
- `sidecar_removed`
- `sidecar_path_changed`
- `visualizer_asset_changed`
- `path_hygiene_changed`
- `source_lookup_expectation_changed`
- `artifact_handoff_policy_changed`
- `manual_review_required`

### `cargo debug-support pack`
Emit one compact `.debugcontract.zip` for CI artifacts, release review, downstream support, or customer handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `debug_support_model`
  - shared Rust types for policies, receipts, manifests, reports, evidence classes, and diffs
- `debug_support_discovery`
  - import logic for profile settings, artifact inventory, sidecar discovery, visualizer discovery, and path-hygiene hints
- `debug_support_check`
  - posture classification, policy validation, handoff validation, and drift classification
- `debug_support_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-debug-support`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `debug_support_obj`
- `debug_support_pdb`
- `debug_support_dsym`
- `debug_support_visualizers`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `debuggability-policy.toml`
- `debuggability.receipt.json`
- `symbol-layout.manifest.json`
- `visualizer.manifest.json`
- `support-posture.report.json`
- `debuggability-drift.diff.json`
- `notes.md`

This pass adds three more important artifacts:

- `support-class.policy.json` — what posture classes mean and what minimum evidence each class expects.
- `artifact-handoff.manifest.json` — which primary artifacts and sidecars were copied, archived, relocated, or left behind, plus retention/handoff expectations.
- `debugger-backend-coverage.report.json` — which debugger families / OSes / versions were actually checked and which capability classes remain inference-only or manual-review-only.
- `source-lookup-impact.report.json` — how remap/trim-paths and source-component expectations affect debugger/source lookup confidence.

Those files matter because debuggability gets vague again if the archive only records profile knobs and discovered files but not:

- what the support classes actually mean,
- whether sidecars survived the handoff path,
- and how privacy-oriented path changes alter source lookup promises.

## Discovery order

A disciplined capture order helps prevent false confidence.

1. **Declared posture**
   - `debuggability-policy.toml`
   - Cargo profile settings from manifests/config/env when explicitly supplied
2. **Observed artifact inventory**
   - binaries, libraries, sidecars, copied outputs, packaged outputs
3. **Sidecar/layout discovery**
   - `pdb`, `dSYM`, `dwo`, `dwp`, embedded-vs-sidecar hints
4. **Visualizer discovery**
   - embedded NatVis / GDB-script assets and explicit external/manual notes
5. **Path-hygiene and source-lookup hints**
   - `remap-path-prefix`, `trim-paths`, source-component expectations, manual notes
6. **Backend coverage import**
   - which debugger families, OSes, and version windows were actually reviewed
   - whether each capability class was observed, inferred, or still manual review
7. **Artifact handoff state**
   - where artifacts were copied or archived, and whether the support story survived relocation
8. **Manual policy notes**
   - anything still requiring a human signoff

The importer should prefer visible uncertainty over synthesis.

## Support-class policy

The first implementation should treat **support classes as first-class review objects** and keep them distinct from raw debug settings.

### What should count as support classes in `0.1`

- `interactive_debugger`
- `backtrace_only`
- `crash_symbolication_only`
- `internal_only`
- `manual_review_required`
- `unknown`

### What should *not* be encoded as support classes in `0.1`

- “debug = 2 therefore interactive debugging is guaranteed”
- “the binary runs therefore debugger support is fine”
- “symbols existed in build-dir therefore release handoff is fine”
- “visualizer asset exists therefore backend support is solved”
- “path trimming happened therefore source lookup is definitely impossible”

The support-class policy should be versioned and diffable.
If a maintainer cannot explain why the build qualifies for `interactive_debugger`, the posture should fall back to `manual_review_required` or a weaker class.

## Artifact-handoff policy

The first implementation should treat **artifact relocation and retention** as explicit review material.

A good `0.1` should model:

- canonical primary artifact paths,
- canonical sidecar paths,
- copied/repackaged/released paths,
- whether the handoff was verified or only declared,
- which sidecars are mandatory for the promised posture,
- and which artifacts are allowed to be omitted from downstream handoff.

This is where Build Dir Layout v2 matters.
A support contract crate should stay useful even when artifact locations move, because location churn and support truth are different questions.

## Source-lookup impact policy

The first implementation should treat **source lookup** as an adjacent but still necessary report.

A good `0.1` should record:

- whether path remapping or trimming was observed or declared,
- whether those settings likely preserve, weaken, or obscure source lookup,
- whether `rust-src` / `rustc-dev` or similar notes are required for expected lookup,
- and when the result should be `manual_review_required` rather than a fake verdict.

This report should stay narrower than **P-0493**.
Its job is not to fully solve source diagnosis.
Its job is to keep the debug-support contract honest about source lookup consequences.

## Scenario families worth owning in `0.1`

The fixture set should intentionally cover boring but painful drift:

- `release_debug_zero_implicit_strip_drift/`
- `build_dir_layout_v2_sidecar_relocation/`
- `trim_paths_with_source_lookup_boundary/`
- `windows_natvis_pdb_must_not_imply_uniform_backend_coverage/`
- `artifact_rich_build_still_needs_manual_review_for_async_and_expr/`
- `windows_msvc_pdb_interactive/`
- `linux_line_tables_only_backtrace/`
- `macos_dsym_missing_sidecar/`
- `linux_split_dwarf_sidecar/`

## Path to boring stability

- Freeze the support-class vocabulary before deep binary-format cleverness.
- Start with **read-only capture and diff**, not debugger orchestration.
- Keep manual-review zones visible and explicit.
- Prefer imported-artifact usefulness over Cargo-session coupling.
- Prove the handoff manifest survives path churn before adding more backend-specific automation.

## Minimum lovable MVP

A library and cargo subcommand that inspect a built artifact set, emit a debuggability receipt plus symbol-layout / visualizer / source-lookup / artifact-handoff reports, and diff two builds to show whether the support contract got better or worse.

## 0.1 boundaries

A good `0.1` should:

- inspect already-built artifacts rather than launch debuggers,
- classify posture conservatively,
- discover obvious sidecar layouts for Linux/ELF, Windows/MSVC, and macOS,
- record handoff/retention facts even when paths changed,
- report source-lookup impact without pretending to solve all source diagnosis,
- and export a portable bundle with a small vocabulary.

A bad `0.1` would try to:

- automate GDB/LLDB/WinDbg end to end,
- become a crash-reporting service,
- become a full source-server or source-packaging platform,
- or collapse P-0491 and P-0493 into the same crate.


## Backend-coverage policy

The first implementation should treat **debugger-family coverage** as a first-class report rather than a footnote inside `notes.md`.

A good `0.1` should keep at least these questions explicit:

- Which debugger family and operating system combination was actually reviewed?
- Was the claim observed in a real session, inferred from sidecars/assets, or merely declared by a maintainer?
- Do claims cover only basic symbol loading, or also type visualizers, async debugging, and Rust expression evaluation?
- What is the strongest **portable** claim the crate can make when only one backend family was actually exercised?

This report should stay narrower than a debugger frontend and broader than visualizer-only compatibility.
Its job is to keep the support contract honest about how far the evidence really reaches.


## 2026-03-22 artifact-completeness addendum

`0.2` should add three more first-class review artifacts above the existing posture / handoff / coverage surfaces:

- `backend-observation.receipt.json` for exact checked debugger-family / version / capability lanes,
- `source-material.manifest.json` for source archives, sysroot source packs, remapped-prefix hints, and share posture,
- `debug-support-bundle.manifest.json` for portable review handoff that keeps posture, sidecars, backend evidence, and source materials joined without flattening them.

These are the smallest additions that make the lane more useful in release review and downstream support without turning it into a debugger product.
