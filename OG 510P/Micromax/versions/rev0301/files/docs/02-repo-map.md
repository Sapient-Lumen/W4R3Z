Rev301 note: `mxportable --stdlib-manifest --show-impact` now also exposes one explicit primary next-cut recommendation plus its exact full command, and shared helpers in `src/micromax/portability_suite.py` now preserve that distinct representative directly so future Python/Rust/WASM hosts and future LLMs can ask "what should I try first?" without re-deriving it from the longer ranked shortlist.

Latest tiny landing (rev301): the archive now turns rev300's rank-aware distinct shortlist into a directly actionable one: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows/recommendations still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, same-result hints, `recommended_distinct`, `recommended_distinct_groups`, representative-reason metadata, and covered full-list ranks, but now the shared payload also carries `recommended_primary`, `recommended_primary_group`, `recommended_primary_command`, and `recommended_primary_json_command` so humans and future LLMs can lift the single best next cut straight into a replayable command without scanning the rest of the shortlist. The handoff note is `docs/243-portability-impact-primary-recommendation.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev300 note: `mxportable --stdlib-manifest --show-impact` now also preserves the original shortlist ranks covered by each distinct representative cut, and shared helpers in `src/micromax/portability_suite.py` now carry small source-rank metadata so future Python/Rust/WASM hosts and future LLMs can see not just which representative won, but where its absorbed alternatives sat in the full ranked shortlist.

Latest tiny landing (rev300): the archive now turns rev299's self-explaining distinct shortlist into a rank-aware one: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows/recommendations still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, same-result hints, `recommended_distinct`, `recommended_distinct_groups`, and representative-reason metadata, but now distinct rows/groups also carry `source_recommendation_rank`, `represented_recommendation_ranks`, `represented_alternative_ranks`, plus tiny rank min/max metadata so humans and future LLMs can see which full-list ranks each representative absorbed without jumping back to the original shortlist. The handoff note is `docs/242-portability-impact-recommendation-ranks.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev299 note: `mxportable --stdlib-manifest --show-impact` now also explains why each distinct representative cut won over its interchangeable alternatives, and shared helpers in `src/micromax/portability_suite.py` now preserve small representative-reason metadata so future Python/Rust/WASM hosts and future LLMs can see not just which cut stands for a slice, but why that cut was preferred.

Latest tiny landing (rev299): the archive now turns rev298's grouped distinct shortlist into a self-explaining one: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows/recommendations still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, same-result hints, `recommended_distinct`, and `recommended_distinct_groups`, but now distinct rows/groups also carry `representative_reason_code` / `representative_reason` plus alternative label/family inventories so humans and future LLMs can see why `words:finally` was kept instead of `distances:1` or `tags:aliases`. The handoff note is `docs/241-portability-impact-representative-reasons.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev298 note: `mxportable --stdlib-manifest --show-impact` now also exposes one tiny grouped view of the already deduped next-cut shortlist, and shared helpers in `src/micromax/portability_suite.py` now preserve the representative recommendation together with the ranked alternatives it absorbed so future Python/Rust/WASM hosts and future LLMs can explain one distinct cut without jumping back to the full shortlist.

Latest tiny landing (rev298): the archive now turns rev297's distinct-next-cut shortlist into a self-contained one: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows/recommendations still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, same-result hints, plus `recommended_distinct`, but now distinct rows also carry `represented_options` / `represented_alternatives` and the shared payload also carries `recommended_distinct_groups` in both JSON and human modes so humans and future LLMs can see which ranked alternatives each representative cut stands for. The handoff note is `docs/240-portability-impact-distinct-groups.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev297 note: `mxportable --stdlib-manifest --show-impact` now also exposes a tiny deduped recommendation shortlist for interchangeable next cuts, and shared helpers in `src/micromax/portability_suite.py` now collapse rev295's ranked candidates through rev296's same-result keys so future Python/Rust/WASM hosts and future LLMs can take one representative narrowing per exact slice instead of comparing several interchangeable suggestions.

Latest tiny landing (rev297): the archive now turns rev296's same-result facet metadata into a small distinct-next-cut handoff: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows/recommendations still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, and same-result hints, but now `impact_filter_options` also carries `recommended_distinct` in both JSON and human modes so humans and future LLMs can start from one representative cut per exact impacted slice. The handoff note is `docs/239-portability-impact-distinct-recommendations.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev296 note: `mxportable --stdlib-manifest --show-impact` now also exposes tiny equivalence metadata for visible facet rows, and shared helpers in `src/micromax/portability_suite.py` now derive exact same-result groups from the already previewed impacted-word/case slice so future Python/Rust/WASM hosts and future LLMs can tell when two suggested cuts are interchangeable instead of rerunning both.

Latest tiny landing (rev296): the archive now turns rev295's recommended-next-cut shortlist into a tiny same-result surface: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows still carry exact filter fragments, full commands, family semantics, result counts, signed deltas, and a small recommended shortlist, but now visible rows also carry `equivalent_options` plus inline `same-result: ...` hints so humans and future LLMs can see when two cuts land on the exact same slice. The handoff note is `docs/238-portability-impact-equivalent-cuts.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev294 note: `mxportable --stdlib-manifest --show-impact` now also exposes exact preview-effect metadata for visible facet rows, and shared helpers in `src/micromax/portability_suite.py` now derive `preview_effect`, `preview_is_current_slice`, and signed word/case/stage deltas so future Python/Rust/WASM hosts and future LLMs can tell whether a candidate facet is a no-op or a real narrowing before executing it.

Latest tiny landing (rev294): the archive now turns rev293's result previews into an explicit refinement-effect surface: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows still carry exact filter fragments, full commands, family semantics, and result counts, but now each visible facet also says whether it is `same-slice`, `narrower`, and so on, with signed `delta:w...,c...,d...` metadata in both JSON and human modes. The handoff note is `docs/236-portability-impact-preview-effects.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev292 note: `mxportable --stdlib-manifest --show-impact` now also exposes explicit same-family transition metadata for visible facet rows, and shared helpers in `src/micromax/portability_suite.py` now derive `filter_family`, `family_mode`, and current/effective family argv/suffixes so future Python/Rust/WASM hosts and future LLMs can tell whether choosing a facet replaces a word/distance/category/name family or appends another conjunctive tag.

Latest tiny landing (rev292): the archive now turns rev291's exact slice commands into explicit facet-family semantics: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows still carry exact filter fragments plus exact full commands, but now each visible facet also says whether it is a same-family replacement or additive narrowing, with current/effective family args and suffixes. The handoff note is `docs/234-portability-impact-filter-family-modes.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev290 note: `mxportable --stdlib-manifest --show-impact` now also exposes executable impact-filter metadata for the exact slice you selected, and shared helpers in `src/micromax/portability_suite.py` now derive exact `filter_argv` / `filter_suffix` values for impacted words, distances, categories, tags, and exact case names so future Python/Rust/WASM hosts and future LLMs can paste a discovered next cut straight back into the CLI instead of retyping flags by hand.

Latest tiny landing (rev290): the archive now turns rev289's semantic facet inventory into an executable one: `--show-impact` still explains what changed, why, and how to rerun it, and it still carries structured word/depth/category/tag/name filter options, but now every row in that facet inventory also carries exact filter args/suffix text like `--impact-word finally` or `--impact-tag errors` in both JSON and human modes. The handoff note is `docs/232-portability-impact-filter-suffixes.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev289 note: `mxportable --stdlib-manifest --show-impact` now also exposes semantic impact-filter options for the exact slice you selected, and shared helpers in `src/micromax/portability_suite.py` now derive structured portability-category / tag / exact-case-name inventories from the already-filtered impact groups so future Python/Rust/WASM hosts and future LLMs can see the valid next `--impact-category`, `--impact-tag`, and `--impact-name` cuts before guessing them by hand.

Latest tiny landing (rev289): the archive now turns rev288's word/depth next-step filter inventory into a fuller semantic facet inventory: `--show-impact` still explains what changed, why, and how to rerun it, and it still carries exact word/depth/case filters plus exact replay commands, but now the shared row/summary payload also carries structured semantic `impact_filter_options` for categories, tags, and exact case names so humans and future LLMs can discover valid semantic cuts for the current slice in both human and JSON modes. The handoff note is `docs/231-portability-impact-semantic-filter-options.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev288 note: `mxportable --stdlib-manifest --show-impact` now also exposes tiny impact-filter options for the exact slice you selected, and shared helpers in `src/micromax/portability_suite.py` now derive structured impacted-word / distance inventories from the already-filtered impact groups so future Python/Rust/WASM hosts and future LLMs can see the valid next cuts before guessing `--impact-word` or `--impact-distance` by hand.

Latest tiny landing (rev288): the archive now turns rev287's exact slice filters into discoverable next-step filter options: `--show-impact` still explains what changed, why, and how to rerun it, and it still accepts exact impacted-word/depth/case filters, but now the shared row/summary payload also carries structured `impact_filter_options` so humans and future LLMs can see the valid word/depth refinements for the current slice in both human and JSON modes. The handoff note is `docs/230-portability-impact-filter-options.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev285 note: `mxportable --stdlib-manifest --show-impact` can now also expose staged replay metadata, and shared helpers in `src/micromax/portability_suite.py` now derive shortest-path `distance` plus ordered `impact_stages` with exact replay commands so future Python/Rust/WASM hosts and future LLMs can start with root-word checks before widening to downstream slices.

Latest tiny landing (rev285): the archive now turns rev284's per-group replay metadata into a tiny ordered retest plan: `--show-impact` still shows per-word provenance and exact commands, but now also groups the same impacted slice into root-first depth stages with copy-pasteable commands. The handoff note is `docs/227-portability-impact-stages.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev284 note: `mxportable --stdlib-manifest --show-impact` can now also expose exact per-impact-word replay metadata, and shared helpers in `src/micromax/portability_suite.py` now derive `retest_name_args`, `retest_env`, `retest_argv`, and copy-pasteable per-group replay commands so future Python/Rust/WASM hosts and future LLMs can jump either to the whole impacted slice or to one exact impacted-word replay path without rebuilding shell args by hand.

Latest tiny landing (rev284): the archive now turns the rev283 provenance view into an executable per-group handoff: `--show-impact` still explains why `bi` or `finally` is in the rerun set, but now also carries exact replay metadata for each impacted word in both shell and structured argv/env form. The handoff note is `docs/226-portability-impact-group-retest-metadata.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev282 note: `mxportable --stdlib-manifest --show-impact` can now also rejoin selected impact-case names back to the portability corpus, and shared helpers in `src/micromax/portability_suite.py` now derive `impact_categories` / `impact_tags` for each selected boot word plus the combined `impact_summary`, so future Python/Rust/WASM hosts and future LLMs can see not just which exact cases to rerun, but what kind of contract slice a change actually touches.

Latest tiny landing (rev282): the archive now turns the rev281 exact replay command into a slightly richer impact handoff: `--show-impact` still gives exact `--name` rerun commands, but now also reports the joined portability category/tag inventory for that selected slice. The handoff note is `docs/224-portability-impact-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev281 note: `mxportable --stdlib-manifest` can now also surface a combined selected-word impact summary with exact `--name` rerun commands, and shared helpers in `src/micromax/portability_suite.py` now derive `impact_summary`, `retest_command`, and `retest_json_command` from the impacted portability case names, so future Python/Rust/WASM hosts and future LLMs can jump from a changed boot word straight to a copy-pasteable focused replay command.

Latest tiny landing (rev281): the archive now turns the rev280 impact map into an executable retest surface: instead of only listing impacted words/cases, `--show-impact` also gives the combined selected impact summary and exact rerun commands for that portability slice. The handoff note is `docs/223-portability-selected-retest-command.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev278 note: `mxportable --stdlib-manifest` can now also surface tiny boot-stdlib prerequisite-closure metadata through `--show-closure`, and shared helpers in `src/micromax/portability_suite.py` now derive `dependency_order`, `transitive_stdlib_refs`, `transitive_nonstdlib_refs`, and `stdlib_depth` from `core.mx` so future Python/Rust/WASM hosts and future LLMs can see the real bring-up prerequisites behind aliases and composite words.

Latest tiny landing (rev278): the archive now exposes a tiny machine-readable boot-stdlib prerequisite closure alongside the direct dependency inventory, so questions like "what kernel words does `finally` really need?" or "what order should I bring up `bi`?" stop requiring ad hoc recursive reading of `core.mx`. The handoff note is `docs/220-portability-stdlib-closure-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev277 note: `mxportable --stdlib-manifest` can now also surface tiny boot-stdlib dependency metadata through `--show-deps`, and shared helpers in `src/micromax/portability_suite.py` now classify each `core.mx` definition by body tokens, stdlib refs, non-stdlib refs, and simple aliases so future Python/Rust/WASM hosts and future LLMs can see how small words are built, not just where they live.

Latest tiny landing (rev277): the archive now exposes a tiny machine-readable boot-stdlib dependency inventory alongside the source inventory, so questions like "is `finally` just an alias?" or "does `bi` depend on `keep` or only kernel words?" stop requiring ad hoc token scraping over `core.mx`. The handoff note is `docs/219-portability-stdlib-dependency-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev275 note: the boot-stdlib portability manifest now lives in shared source instead of only in pytest, and `mxportable` can inspect it directly through `--stdlib-manifest` / `--word` / `--word-contains` / `--json`, so future Python/Rust/WASM hosts and future LLMs can ask one tool both which tiny stdlib words are supposed to be covered and which portability case names provide that coverage.

Latest tiny landing (rev275): the archive now exposes the boot-stdlib portability coverage map as a shared machine-readable surface instead of burying it inside one test file. The handoff note is `docs/217-portability-stdlib-manifest-cli.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev265 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes row-local nearest-heading `section_entry` metadata plus small top-level section counts (`section_rows`, `section_distinct_count`), so future UIs/scripts/LLMs can tell which visible docs/help heading owns an ordinary prose/code/definition row without rerunning heading scans or inferring section context from nearby titles alone.

Latest tiny landing (rev265): the shared docs/help cue model now also exposes visible nearest-heading section ownership (`title`, `fragment`, `level`, breadcrumb `path`, source line/col) for each visible row, including fenced-code body rows. The handoff note is `docs/207-docs-cues-section-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev264 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `block_entries` plus small top-level block counts (`block_rows`, `block_entry_count`, fenced/html/indented totals), so future UIs/scripts/LLMs can inspect visible docs/help fenced-code info strings, raw HTML block rows, and indented-code runs without inferring them only from coarse `line_role` labels.

Latest tiny landing (rev264): the shared docs/help cue model now also exposes parsed visible block metadata for fenced-code opener/body/closer rows, raw HTML block rows, and indented-code rows. The handoff note is `docs/206-docs-cues-block-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, `tests/test_tui_md_indented_code_blocks.py`, and `tests/test_mxcontext.py`.

Rev263 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `definition_entries` plus small top-level definition counts (`definition_rows`, `definition_entry_count`, starter/continuation totals), so future UIs/scripts/LLMs can inspect visible docs/help reference definitions and footnote definitions without inferring them only from `definition_role` or reparsing starter tokens.

Latest tiny landing (rev263): the shared docs/help cue model now also exposes parsed visible definition metadata for reference-definition starters/continuations and footnote-definition starters/continuations. The handoff note is `docs/205-docs-cues-definition-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, `tests/test_tui_md_definitions.py`, `tests/test_editor_help_docs_navigation.py`, and `tests/test_mxcontext.py`.

Rev262 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `heading_entries` plus small top-level heading counts (`heading_rows`, `heading_entry_count`, title/underline totals), so future UIs/scripts/LLMs can inspect visible docs/help heading titles and resolved fragments without inferring them only from `line_role`, `heading_level`, or a second heading scan.

Latest tiny landing (rev262): the shared docs/help cue model now also exposes parsed visible heading metadata for title rows, underline rows, and resolved fragments. The handoff note is `docs/204-docs-cues-heading-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Latest tiny landing (rev261): the shared docs/help cue model now also exposes parsed visible table metadata (`table_entries` plus small top-level table counts), so future UIs/scripts/LLMs can inspect why visible docs/help pipe-table rows read as header/body/delimiter cells without inferring that from generic pipe spans alone. The handoff note is `docs/203-docs-cues-table-metadata.md`, and the focused coverage lives in `tests/test_tui_md_tables.py`, `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev259 note: the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and the repo now carries a tiny manifest test that checks every `: word` in `src/micromax/stdlib/core.mx` against explicit portability case names so future Python/Rust/WASM hosts and future LLMs can verify boot-stdlib coverage mechanically instead of diffing it by hand.

Latest tiny landing (rev259): the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and `tests/test_portability_suite.py` now carries a tiny explicit manifest that maps every boot-stdlib word in `core.mx` to named portability cases. The handoff note is `docs/201-portability-stdlib-coverage-audit.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev258 note: the JSON portability corpus now also covers the tiny boot-stdlib assertion helper `assert`, so future Python/Rust/WASM hosts can replay both its success and failure-path stack behavior from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev258): the JSON portability corpus now also covers the tiny boot-stdlib assertion helper `assert`, including the failure-path contract that a thrown message still leaves older stack items intact. The handoff note is `docs/200-portability-assert.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev257 note: the JSON portability runner now also lets expected-error cases pin down the post-error stack, so future Python/Rust/WASM hosts can replay small cleanup/rethrow contracts like `ensure` / `finally` directly from JSON instead of leaving them trapped in Python-only tests.

Latest tiny landing (rev257): the JSON portability runner now also lets expected-error cases pin down the post-error stack, and the corpus now uses that to replay `try?` success plus `ensure` / `finally` cleanup-rethrow behavior directly from JSON. The handoff note is `docs/199-portability-recovery-error-stacks.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_try_combinator.py`, and `tests/test_ensure_finally.py`.

Latest tiny landing (rev257): the JSON portability runner now also lets expected-error cases pin down the post-error stack, and the corpus now uses that to replay `try?` success plus `ensure` / `finally` cleanup-rethrow behavior directly from JSON. The handoff note is `docs/199-portability-recovery-error-stacks.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_try_combinator.py`, and `tests/test_ensure_finally.py`.

Rev255 note: the JSON portability corpus now also covers tiny boot-stdlib `nip` / `tuck` / `2dup` / `2drop` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped stack-helper slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev255): the JSON portability corpus now also covers tiny boot-stdlib `nip` / `tuck` / `2dup` / `2drop` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped stack-helper slice from JSON alone. The handoff note is `docs/197-portability-basic-stack-pairs.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev253 note: the JSON portability corpus now also covers tiny boot-stdlib `2rdrop` behavior, so future Python/Rust/WASM hosts can replay one more small pair-return-stack cleanup slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev253): the JSON portability corpus now also covers tiny boot-stdlib `2rdrop` behavior, so future Python/Rust/WASM hosts can replay one more small pair-return-stack cleanup slice from JSON alone. The handoff note is `docs/195-portability-2rdrop.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev252 note: the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck` behavior, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev251 note: the JSON portability corpus now also covers tiny boot-stdlib `2>r` / `2r>` / `2r@` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-return-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev251): the JSON portability corpus now also covers tiny boot-stdlib `2>r` / `2r>` / `2r@` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-return-stack slice from JSON alone. The handoff note is `docs/193-portability-2returnstack-pairs.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev250 note: the JSON portability corpus now also covers tiny boot-stdlib `2rot` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack rotation slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev249 note: the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev248 note: the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev247 note: the JSON portability corpus now also covers tiny boot-stdlib `1+`, `1-`, `0>`, and `0<>` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic/predicate slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev246 note: the JSON portability corpus now also covers tiny boot-stdlib `max` / `min` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev245): the JSON portability corpus now also covers tiny boot-stdlib `negate`, `0<`, and `abs` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from `mxportable` without importing pytest helpers. The handoff note is `docs/187-portability-negate-abs-zero-less.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev250): the JSON portability corpus now also covers tiny boot-stdlib `2rot` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack rotation slice from JSON alone. The handoff note is `docs/192-portability-2rot.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev248): the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from `mxportable` without importing pytest helpers. The handoff note is `docs/190-portability-twostar-twoslash.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev243): the JSON portability corpus now also makes the `pick` / `roll` failure edges replayable — negative indices now have explicit `u must be >= 0` contracts and too-shallow stacks now expect `Stack underflow` — so future Python/Rust/WASM hosts do not have to guess how Micromax resolves the Forth standard's ambiguous out-of-range cases. The handoff note is `docs/185-portability-pick-roll-errors.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev242): the JSON portability corpus now also covers two deeper five-item stack-shuffle cases — `4 pick` copying the fifth item and `4 roll` rotating the top five items — so future Python/Rust/WASM hosts can replay one more deeper general indexing slice from `mxportable` without importing pytest helpers. The handoff note is `docs/184-portability-pick-roll-five-item.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev239): the JSON portability corpus now also covers four tiny stack-shuffle contracts for `pick` / `roll` (`0 pick`=`dup`, `1 pick`=`over`, `1 roll`=`swap`, `2 roll`=`rot`), so future Python/Rust/WASM hosts can replay one more easy-to-get-wrong stack-indexing slice from `mxportable` without importing pytest helpers. The handoff note is `docs/181-portability-pick-roll-cases.md`, and the focused coverage lives in `tests/test_portability_suite.py`.

# Repo map (rev261)

Latest tiny landing (rev242): the JSON portability corpus now also covers two deeper five-item stack-shuffle cases — `4 pick` copying the fifth item and `4 roll` rotating the top five items — so future Python/Rust/WASM hosts can replay one more deeper general indexing slice from `mxportable` without importing pytest helpers. The handoff note is `docs/184-portability-pick-roll-five-item.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev238): the shared docs/help cue model now also exposes parsed visible literal-source metadata (`literal_entries` plus small top-level raw-html/escaped counts), so future UIs/scripts/LLMs can inspect why visible docs/help source tokens are dim without inferring that from generic spans alone. The handoff note is `docs/180-docs-cues-literal-source-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.


## Key files

### Priorities
- `TODO.md` — current priorities
- `docs/43-worklist.md` — detailed tiered worklist (living)

### Language / VM
- `src/micromax/vm.py` — tokenizer, VM, wordlists, locals, budgets, tier-2 scaffolding
- `src/micromax/core.py` — core words (portable kernel + a little debug tooling)
- `src/micromax/stdlib/core.mx` — boot stdlib (convenience words; includes `try`/`recover` + `ensure`/`finally` helpers)
- `docs/96-try-catch.md` — stdlib `try?`/`try`/`recover` + `ensure`/`finally` patterns and examples
- `src/micromax/host_strings.py` — reference string helpers (installed as hostcalls)
- `src/micromax/host_regex.py` — reference regex helpers (installed as hostcalls)
- `src/micromax/regex_tools.py` — shared replacement-template conversion + flag parsing
- `src/micromax/portability_suite.py` — JSON portability corpus runner for future Rust/WASM hosts
- `portability/kernel_cases.json` — small cross-host semantic corpus for the portable kernel / boot stdlib
- `docs/102-portability-suite.md` — what belongs in the portability corpus and how to run it

### Editor core
- `src/micromax_editor/editor.py` — buffers, actions, keymaps, search, selections, multicursor, macros, status model + viewport/softwrap rendering helpers (`statusline_text`)
- `src/micromax_editor/statusformat.py` — micro-esque statusformat template renderer (`$()` directives)
- `docs/97-statusline.md` — status model fields + statusformat templating + reference formatter
- `docs/116-scrollmargin.md` — shared `scrollmargin` viewport/context policy
- `docs/126-pageoverlap.md` — shared `pageoverlap` paging/context policy
- `docs/127-rmtrailingws.md` — shared save-time trailing-whitespace cleanup policy
- `docs/128-eofnewline.md` — shared save-time final-newline normalization policy
- `docs/129-mkparents.md` — shared save-time parent-directory creation policy
- `docs/117-cursorline.md` — tiny `cursorline` current-row policy for the curses TUI
- `docs/118-hltrailingws.md` — tiny `hltrailingws` trailing-whitespace policy for the curses TUI
- `docs/119-hltaberrors.md` — tiny `hltaberrors` indentation-mismatch policy for the curses TUI
- `docs/120-colorcolumn.md` — tiny `colorcolumn` guide-column policy for the curses TUI
- `docs/121-scrollbar.md` — tiny `scrollbar` thumb policy for the curses TUI
- `docs/122-scrollbarchar.md` — tiny `scrollbarchar` thumb-glyph policy for the curses TUI
- `docs/113-search-highlighting.md` — tiny `hlsearch` rendering policy for the curses TUI
- `docs/114-search-position-summary.md` — shared whole-buffer search-position/status contract (`i/n`)
- `src/micromax_editor/buffer.py` — line-based buffer operations (easy to swap later)
- `src/micromax_editor/filetypes.py` — tiny filetype detection (extension + shebang)
- `src/micromax_editor/undo.py` — tiny linear undo stack
- `src/micromax_editor/micromax_bridge.py` — hostcalls (stable scripting surface)
- `src/micromax_editor/highlight.py` — syntax highlight span model + micromax line highlighter
- `src/micromax_editor/timers.py` — deterministic timer queue (after/cancel/pump)


- `docs/81-editor-marks.md` — named marks + buffer switching (navigation primitives)
- `docs/86-editor-lifecycle-hooks.md` — editor hook names + stack contracts
- `docs/87-editor-config.md` — rc/init loading conventions
- `docs/88-require-and-paths.md` — `include`/`require` search convention
### Example scripts
- `examples/combinators.mf` — small quotation combinator examples
- `examples/editor_completion_rows.mf` — custom editor command completion with richer suggestion rows

## Tests
- `tests/test_smoke.py` — basic language smoke tests
- `tests/test_features.py` — lists/hooks/modules/locals/host API features
- `tests/test_editor_core.py` — editor behaviors without any UI
- `tests/test_maps.py` — portable map/dict primitives
- `tests/test_portability_suite.py` — verifies the JSON portability corpus stays runnable and useful
- `tests/test_tui_hltrailingws.py` — renderer-local trailing-whitespace cue under plain/softwrapped views
- `tests/test_tui_hltaberrors.py` — renderer-local tab/indentation-mismatch cue under plain/fragmented views
- `tests/test_tui_colorcolumn.py` — renderer-local guide-column cue under plain/scrolled/softwrapped/help views
- `tests/test_tui_scrollbar.py` — renderer-local right-edge scrollbar cue under plain/softwrapped/help views
- `tests/test_tui_hlsearch.py` — renderer-local `hlsearch` spans + find-prompt search-position summary
- `tests/test_tui_cursorline.py` — tiny `cursorline` current-row rendering policy
- `tests/test_xt_span.py` — spans + xt-span introspection
- `tests/test_editor_prompt_completion_hostcalls.py` — prompt completion via hostcalls, including fuzzy fallback for command-ish tokens and richer argument completion (option values / keymodes / hook topics)
- `tests/test_editor_prompt_path_completion.py` — prompt completion for filesystem paths (open/save/cd), including quote-aware completion for spaces and embedded quotes
- `tests/test_editor_mx_commands_and_completion.py` — micromax-defined command-bar commands + completion hooks, including plugin-provided suggestion metadata rows
- `tests/test_here_span.py` — here-span + vm.last_span provenance
- `tests/test_stack_effect_checking.py` — dev-mode stack effect checking + inference tools
- `tests/test_editor_keybinding_provenance.py` — keybinding provenance, `showkey`, `ed.bindings`, `ed.unbind`
- `tests/test_hook_provenance.py` — hook definition/handler provenance, `hook-rows`, `xt-span` for hooks
- `tests/test_editor_showhook.py` — editor command-bar hook inspection
- `tests/test_editor_statusline.py` — portable statusline/infobar model + `showstatus`
- `tests/test_editor_softwrap.py` — visual-row movement/scrolling + wrapped `scrollmargin` / `pageoverlap` behavior
- `tests/test_hook_groups.py` — hook groups, `hook-detail`, and plugin-reload hook cleanup
- `tests/test_editor_registration_groups.py` — grouped editor commands/keybindings and plugin reload cleanup
- `tests/test_editor_keymap_modes.py` — mode-aware keybindings, keymode stack, and plugin reload cleanup for mode bindings
- `tests/test_editor_transient_keymodes.py` — one-shot keymodes, centralized key dispatch, and fallthrough semantics
- `tests/test_editor_keymap_discovery.py` — resolved keymap discovery, filtered binding rows, and `whichkey`/`showbindings`
- `tests/test_editor_keybinding_docs.py` — derived/custom binding descriptions and machine-readable keymap info rows
- `tests/test_editor_tier0_basics.py` — Tier-0 editor basics (open/save/quit/delete/word/page, including shared `pageoverlap`)
- `tests/test_editor_viewport_and_typing.py` — viewport model + unbound typing + prompt-mode editing
- `tests/test_string_hostcalls.py` — string hostcall MVP
- `tests/test_type_predicates_and_conversions.py` — typed predicates + conversions (`to-int`/`to-str`)
- `tests/test_editor_filetypes.py` — filetype detection
- `tests/test_editor_lifecycle_hooks.py` — open/save/change hooks
- `tests/test_editor_prefix_maps.py` — one-shot prefix-mode helpers (`prefixmode`, `bindprefix`, `bindmodeprefix`, `ed.bind-prefix`, `ed.bind-mode-prefix`)
- `tests/test_editor_highlight_and_timers.py` — syntax highlight spans + deterministic timers
- `tests/test_statusformat_templating.py` — statusformat directive rendering (opt/bind/escaping)
- `tests/test_ensure_finally.py` — `ensure`/`finally` cleanup combinators

## Docs worth skimming
- `docs/20-language-design.md`, `docs/21-language-spec-sketch.md`
- `docs/24-bytecode-format.md`, `docs/25-inline-caching.md`
- `docs/31-host-api.md`
- `docs/61-editor-cursorstate.md`
- `docs/63-editor-jumplist.md`
- `docs/64-editor-prompt-completion.md`
- `docs/65-debugging-spans.md`
- `docs/66-editor-micromax-commands.md`
- `docs/67-editor-keybinding-provenance.md`
- `docs/68-hook-provenance.md`
- `docs/69-editor-statusline-model.md`
- `docs/73-hook-groups.md`
- `docs/74-editor-registration-groups.md`
- `docs/75-editor-keymap-modes.md`
- `docs/76-editor-transient-keymodes.md`
- `docs/77-editor-keymap-discovery.md`
- `docs/78-editor-binding-descriptions.md`
- `docs/79-editor-prefix-maps.md`
- `docs/80-editor-mode-prefix-maps.md`
- `docs/89-syntax-highlight-spans.md`
- `docs/90-timers.md`
- `docs/91-stack-effect-checking.md`
- `docs/57-editor-multicursor.md`

## Tools (for future LLMs + humans)

- `tools/mxdoctor.py` — run lint + tests; emits archive hygiene warnings
- `tools/mxcontext.py` — print a curated project-context snapshot (human text, JSON, or path validation)
- `docs/170-context-cli-json.md` — machine-readable repo-context helper
- `docs/171-rust-vm-spike.md` — focused plan for the remaining Rust VM spike TODO
- `tools/mxpack.py` — build a clean zip archive (excludes caches)

- `tests/test_vm_require_paths.py` — include/require path resolution (caller-relative, MICROMAX_PATH, host load_paths)
- `tests/test_editor_user_init.py` — user init loading via MICROMAX_INIT
- `tests/test_editor_jumppick.py` — jumplist picker behavior
- `tests/test_plugin_load_errors.py` — plugin load error recovery + cleanup


## rev72 notes
- Statusline is now configurable via `statusformatl`/`statusformatr` templates (micro-esque `$()` directives).
- Stdlib now includes `ensure`/`finally` for always-run cleanup.
- `docs/123-matchbrace.md` — tiny visible match-brace cue in the curses TUI (`matchbrace`, `matchbraceleft`)

- `docs/125-statusline-bufferpos.md` — shared current-buffer position model + `$(bufpos)` statusline cue
- `docs/126-pageoverlap.md` — shared `PageUp` / `PageDown` overlap policy

- `docs/178-docs-cues-code-metadata.md` — shared visible inline-code metadata in docs cues.
- `docs/203-docs-cues-table-metadata.md` — shared visible pipe-table cell/alignment metadata in docs cues.
- `docs/205-docs-cues-definition-metadata.md` — shared visible reference-definition / footnote-definition metadata in docs cues.


Recent tiny portability handoff notes also include `docs/190-portability-twostar-twoslash.md` for the current boot-stdlib shift/arithmetic slice and `docs/189-portability-oneplus-oneminus-zeropreds.md` for the adjacent arithmetic/predicate slice.

- `docs/192-portability-2rot.md` — tiny boot-stdlib `2rot` portability note.

- `docs/194-portability-2nip-2tuck.md` — tiny pair-stack convenience follow-up for boot stdlib + replayable JSON portability cases
- `docs/200-portability-assert.md` — assertion-helper follow-up for boot stdlib + replayable JSON portability cases
- `docs/201-portability-stdlib-coverage-audit.md` — tiny explicit coverage audit for every boot-stdlib word in `core.mx`
- `docs/217-portability-stdlib-manifest-cli.md` — shared manifest + CLI view for boot-stdlib portability coverage
- `docs/218-portability-stdlib-source-inventory.md` — source-line / stack-effect / definition inventory for boot stdlib words
- `docs/219-portability-stdlib-dependency-inventory.md` — direct token/dependency inventory for boot stdlib words
- `docs/220-portability-stdlib-closure-inventory.md` — transitive prerequisite / bring-up-order inventory for boot stdlib words
- `docs/221-portability-stdlib-user-inventory.md` — reverse user/dependent inventory for boot stdlib words
- `docs/222-portability-stdlib-impact-map.md` — impacted-word / retest-case inventory after changing a boot stdlib word
- `docs/223-portability-selected-retest-command.md` — exact `--name` replay commands for selected impacted boot-stdlib slices
- `docs/224-portability-impact-inventory.md` — joined category/tag inventory for selected impacted boot-stdlib slices
- `docs/225-portability-impact-groups.md` — per-impacted-word provenance groups for selected boot-stdlib slices
- `docs/226-portability-impact-group-retest-metadata.md` — exact per-group replay metadata for selected impacted slices
- `docs/227-portability-impact-stages.md` — root-first staged replay plans for selected impacted slices
- `docs/228-portability-impact-slice-filters.md` — impacted-word / depth filters for selected impacted slices
- `docs/229-portability-impact-case-filters.md` — semantic portability case filters for selected impacted slices
- `docs/230-portability-impact-filter-options.md` — structured next-step impacted-word / depth filter options for selected impacted slices
- `docs/231-portability-impact-semantic-filter-options.md` — structured next-step category/tag/exact-case filter options for selected impacted slices
- `docs/232-portability-impact-filter-suffixes.md` — exact filter fragments for each visible impacted-slice facet
- `docs/233-portability-impact-filter-commands.md` — exact full impacted-slice commands for each visible facet
- `docs/234-portability-impact-filter-family-modes.md` — explicit replace-vs-append family semantics for visible impacted-slice facets
- `docs/235-portability-impact-filter-previews.md` — exact resulting slice preview counts for each visible impacted-slice facet
