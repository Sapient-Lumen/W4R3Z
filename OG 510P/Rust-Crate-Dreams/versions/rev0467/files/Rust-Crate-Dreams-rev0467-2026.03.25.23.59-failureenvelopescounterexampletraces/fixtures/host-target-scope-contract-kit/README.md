# Host/Target Scope Contract Kit fixtures

This fixture family is for **Cargo host/target scope contracts, mixed-build observation receipts, and scope diagnosis reports**.

The point is not to prove that Cargo config exists.
The point is to make config-scope assumptions **portable and reviewable**.

## Suggested scenario corpus

1. `flags_leak_to_build_script_without_explicit_target/`
   - global `RUSTFLAGS` or `build.rustflags` affect build scripts / proc macros because no explicit `--target` was used
   - should classify `flags_leak_to_host`

2. `explicit_target_changes_host_scope/`
   - adding `--target <host-triple>` changes host-tool behavior even though the effective platform looks the same
   - should classify `host_flags_missing` or `same_triple_scope_ambiguous`

3. `nightly_host_config_split/`
   - `target-applies-to-host = false` with `[host]` and `[target.*]`
   - should preserve nightly-only provenance and explicit host/target separation

4. `rustdoc_buildscript_scope_split/`
   - docs-builder-like workflow where rustdoc cfgs do not imply equivalent build-script cfgs
   - should classify `rustdoc_buildscript_scope_split`

5. `same_triple_manual_review/`
   - host triple and target triple are equal, but different sysroots, linkers, runners, or support assumptions still matter
   - should preserve ambiguity instead of pretending scope is obvious

## Minimal bundle for 0.1

Core:
- `scope-policy.toml`
- `scope-snapshot.manifest.json`
- `scope-observation.receipt.json`
- `scope-diagnosis.report.json`
- `notes.md`

When comparing two runs or two command shapes:
- `scope-diff.report.json`
- `support-hints.md`

## Evidence-lane rule

Every scenario should preserve whether a fact came from:

1. `config_parse`
2. `command_capture`
3. `imported_verbose_log`
4. `manual_policy`

The kit should not silently blur parsed config, observed invocation facts, and conservative interpretation into one confidence tone.

## Minimal diagnosis vocabulary

Good:
- `flags_leak_to_host`
- `host_flags_missing`
- `host_config_ignored`
- `rustdoc_buildscript_scope_split`
- `same_triple_scope_ambiguous`
- `nightly_host_config_required`
- `same_triple_lane_changed`
- `manual_review_required`

Bad:
- pretending the crate can always infer Cargo intent from one command line without caveats
- pretending equal triples imply equal host/target support posture
