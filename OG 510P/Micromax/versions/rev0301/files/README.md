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

Rev295 note: `mxportable --stdlib-manifest --show-impact` now also exposes a tiny recommended-next-cut inventory for the exact impacted slice already on screen, and shared helpers in `src/micromax/portability_suite.py` now rank real narrower facets by family and preview reduction so future Python/Rust/WASM hosts and future LLMs can start with the smallest useful coarse cut instead of hand-sorting a long facet list.

Latest tiny landing (rev295): the archive now turns rev294's preview-effect metadata into a tiny recommendation surface: `--show-impact` still explains what changed, why, and how to rerun it, and facet rows still carry exact filter fragments, full commands, family semantics, result counts, and signed deltas, but now the shared `impact_filter_options` payload also carries a `recommended` shortlist in both JSON and human modes so humans and future LLMs can see the best next narrows first. The handoff note is `docs/237-portability-impact-filter-recommendations.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

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

Rev283 note: `mxportable --stdlib-manifest --show-impact` can now also expose grouped impact provenance, and shared helpers in `src/micromax/portability_suite.py` now derive per-impact-word case groups plus shortest stdlib user paths so future Python/Rust/WASM hosts and future LLMs can see not just which cases to rerun, but which impacted word contributed them and why.

Latest tiny landing (rev283): the archive now turns the rev282 impact inventory into a small provenance handoff: `--show-impact` still gives exact retest commands and joined category/tag summaries, but now also reports grouped impacted words with their exact portability cases and shortest `root -> user` paths. The handoff note is `docs/225-portability-impact-groups.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev282 note: `mxportable --stdlib-manifest --show-impact` can now also rejoin selected impact-case names back to the portability corpus, and shared helpers in `src/micromax/portability_suite.py` now derive `impact_categories` / `impact_tags` for each selected boot word plus the combined `impact_summary`, so future Python/Rust/WASM hosts and future LLMs can see not just which exact cases to rerun, but what kind of contract slice a change actually touches.

Latest tiny landing (rev282): the archive now turns the rev281 exact replay command into a slightly richer impact handoff: `--show-impact` still gives exact `--name` rerun commands, but now also reports the joined portability category/tag inventory for that selected slice. The handoff note is `docs/224-portability-impact-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev281 note: `mxportable --stdlib-manifest` can now also surface a combined selected-word impact summary with exact `--name` rerun commands, and shared helpers in `src/micromax/portability_suite.py` now derive `impact_summary`, `retest_command`, and `retest_json_command` from the impacted portability case names, so future Python/Rust/WASM hosts and future LLMs can jump from a changed boot word straight to a copy-pasteable focused replay command.

Latest tiny landing (rev281): the archive now turns the rev280 impact map into an executable retest surface: instead of only listing impacted words/cases, `--show-impact` also gives the combined selected impact summary and exact rerun commands for that portability slice. The handoff note is `docs/223-portability-selected-retest-command.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev278 note: `mxportable --stdlib-manifest` can now also surface tiny boot-stdlib prerequisite-closure metadata through `--show-closure`, and shared helpers in `src/micromax/portability_suite.py` now derive `dependency_order`, `transitive_stdlib_refs`, `transitive_nonstdlib_refs`, and `stdlib_depth` from `core.mx` so future Python/Rust/WASM hosts and future LLMs can see the real bring-up prerequisites behind aliases and composite words.

Latest tiny landing (rev278): the archive now exposes a tiny machine-readable boot-stdlib prerequisite closure alongside the direct dependency inventory, so questions like "what kernel words does `finally` really need?" or "what order should I bring up `bi`?" stop requiring ad hoc recursive reading of `core.mx`. The handoff note is `docs/220-portability-stdlib-closure-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev277 note: `mxportable --stdlib-manifest` can now also surface tiny boot-stdlib dependency metadata through `--show-deps`, and shared helpers in `src/micromax/portability_suite.py` now classify each `core.mx` definition by body tokens, stdlib refs, non-stdlib refs, and simple aliases so future Python/Rust/WASM hosts and future LLMs can see how small words are built, not just where they live.

Latest tiny landing (rev277): the archive now exposes a tiny machine-readable boot-stdlib dependency inventory alongside the source inventory, so questions like "is `finally` just an alias?" or "does `bi` depend on `keep` or only kernel words?" stop requiring ad hoc token scraping over `core.mx`. The handoff note is `docs/219-portability-stdlib-dependency-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev276 note: `mxportable --stdlib-manifest` can now also surface boot-stdlib source metadata from `src/micromax/stdlib/core.mx` through `--show-source`, and shared helpers in `src/micromax/portability_suite.py` can now map each tiny stdlib word to its source line, stack-effect comment, and definition text so future Python/Rust/WASM hosts and future LLMs can jump straight from portability coverage to the actual boot source.

Latest tiny landing (rev276): the archive now exposes a tiny machine-readable boot-stdlib source inventory alongside the portability manifest, so coverage questions like "where is `ensure` defined and what stack effect does it claim?" stop requiring ad hoc regexes over `core.mx`. The handoff note is `docs/218-portability-stdlib-source-inventory.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev275 note: the boot-stdlib portability manifest now lives in shared source instead of only in pytest, and `mxportable` can inspect it directly through `--stdlib-manifest` / `--word` / `--word-contains` / `--json`, so future Python/Rust/WASM hosts and future LLMs can ask one tool both which tiny stdlib words are supposed to be covered and which portability case names provide that coverage.

Latest tiny landing (rev275): the archive now exposes the boot-stdlib portability coverage map as a shared machine-readable surface instead of burying it inside one test file. The handoff note is `docs/217-portability-stdlib-manifest-cli.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_mxcontext.py`.

Rev274 note: the JSON portability corpus now also covers handler-error precedence for `try` / `recover`, so future Python/Rust/WASM hosts can replay the rule that a failing recovery handler replaces the original body failure while preserving any stack effects the handler already performed.

Latest tiny landing (rev274): the JSON portability corpus now covers the failure-path branch where `try` / `recover` handlers themselves throw after doing some work. The handoff note is `docs/216-portability-try-handler-error-precedence.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_try_combinator.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev273 note: the JSON portability corpus now also pins down cleanup-error precedence for `ensure` / `finally`, so future Python/Rust/WASM hosts can replay the rule that a failing cleanup quotation replaces the original body result or body error while still preserving the correct visible stack shape.

Latest tiny landing (rev273): the JSON portability corpus now covers both success-path and failure-path cleanup-error precedence for `ensure` / `finally`, including the alias behavior of `finally`. The handoff note is `docs/215-portability-cleanup-error-precedence.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_ensure_finally.py`, and `tests/test_mxcontext.py`.

Rev272 note: docs-link query ranking now also reuses target doc titles and target heading titles, so generic-label searches like `image metadata` or `hidden image metadata anchor` work through `helplinkpick` and the link side of `helpnavpick` without widening visible rows or inventing a richer docs AST.

Latest tiny landing (rev272): docs-link navigation can now be disambiguated by destination doc/heading titles as well as visible labels, source-side section context, and raw targets. The handoff note is `docs/214-helplink-target-title-query-matching.md`, and the focused coverage lives in `tests/test_editor_helplinkpick.py`, `tests/test_editor_helpnavpick.py`, and `tests/test_mxcontext.py`.

Rev271 note: docs-heading query ranking now also reuses resolved heading fragments/ids, so stable-anchor queries like `custom-frag` work through `helpjump`, `helpoutlinepick`, and the heading side of `helpnavpick` without widening the visible row shape or inventing a richer docs AST.

Latest tiny landing (rev271): docs-heading navigation can now be disambiguated by stable fragment/id terms as well as visible titles and breadcrumbs. The handoff note is `docs/213-help-heading-fragment-query-matching.md`, and the focused coverage lives in `tests/test_editor_helpjump.py`, `tests/test_editor_helpoutlinepick.py`, `tests/test_editor_helpnavpick.py`, and `tests/test_mxcontext.py`.

Rev270 note: docs-link query ranking now also reuses nearest-heading and kind context, so section-aware queries like `External micro editor` or `Reference Vision ref` work through `helplinkpick` and the link side of `helpnavpick` without widening the row shape or inventing a richer docs AST.

Latest tiny landing (rev270): docs-link navigation can now be disambiguated by owning section terms, not just bare link labels or raw targets. The handoff note is `docs/212-helplink-heading-query-matching.md`, and the focused coverage lives in `tests/test_editor_helplinkpick.py`, `tests/test_editor_helpnavpick.py`, and `tests/test_mxcontext.py`.

Rev269 note: help-outline query ranking now reuses the same breadcrumb context already visible in `helpoutlinepick` / `helpnavpick`, so breadcrumb-aware queries like `Guide Links` and `Guide Deep dive` work through `helpoutlinepick`, `helpnavpick`, and direct `helpjump` without widening the row shape or inventing a richer docs AST.

Latest tiny landing (rev269): docs-heading navigation can now be disambiguated by parent breadcrumb terms, not just bare heading titles. The handoff note is `docs/211-help-breadcrumb-query-matching.md`, and the focused coverage lives in `tests/test_editor_helpoutlinepick.py`, `tests/test_editor_helpnavpick.py`, `tests/test_editor_helpjump.py`, and `tests/test_mxcontext.py`.

Rev268 note: `helpnavpick` now reuses the grouped heading-breadcrumb sections already exposed by `help_outline_section_rows(query)`, so empty-query browse, sticky headers, section jumps, and status/preview surfaces stop collapsing heading rows into one generic `Headings` bucket while link rows keep the existing `helplinkpick` grouping policy.

Latest tiny landing (rev268): the combined docs navigator now gives heading rows the same breadcrumb-grouped sections as `helpoutlinepick`, so `helpnavpick` stops flattening every heading into one fake `Headings` region. The handoff note is `docs/210-helpnav-heading-breadcrumbs.md`, and the focused coverage lives in `tests/test_editor_helpnavpick.py`, `tests/test_editor_help_picker_browse_budget.py`, and `tests/test_editor_statusline.py`.

Rev266 note: the docs-outline picker now also exposes grouped parent-heading sections through `help_outline_section_rows(query)` / `ed.help-outline-section-rows`, and empty-query `helpoutlinepick` now reuses those same visible breadcrumb labels (`Top`, `Guide`, `Guide › Links`, ...) for sticky headers, section jumps, and status/preview surfaces instead of one generic `Headings` bucket.

Latest tiny landing (rev266): the docs outline picker now speaks the same grouped-picker dialect as the other prompt surfaces, using parent-heading breadcrumb labels and a small hostcall for future UIs/scripts/LLMs. The handoff note is `docs/208-helpoutline-section-groups.md`, and the focused coverage lives in `tests/test_editor_helpoutlinepick.py`, `tests/test_editor_help_picker_browse_budget.py`, and `tests/test_editor_statusline.py`.

Rev265 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes row-local nearest-heading `section_entry` metadata plus small top-level section counts (`section_rows`, `section_distinct_count`), so future UIs/scripts/LLMs can tell which visible docs/help heading owns an ordinary prose/code/definition row without rerunning heading scans or inferring section context from nearby titles alone.

Latest tiny landing (rev265): the shared docs/help cue model now also exposes visible nearest-heading section ownership (`title`, `fragment`, `level`, breadcrumb `path`, source line/col) for each visible row, including fenced-code body rows. The handoff note is `docs/207-docs-cues-section-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev264 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `block_entries` plus small top-level block counts (`block_rows`, `block_entry_count`, fenced/html/indented totals), so future UIs/scripts/LLMs can inspect visible docs/help fenced-code info strings, raw HTML block rows, and indented-code runs without inferring them only from coarse `line_role` labels.

Latest tiny landing (rev264): the shared docs/help cue model now also exposes parsed visible block metadata for fenced-code opener/body/closer rows, raw HTML block rows, and indented-code rows. The handoff note is `docs/206-docs-cues-block-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, `tests/test_tui_md_indented_code_blocks.py`, and `tests/test_mxcontext.py`.

Rev263 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `definition_entries` plus small top-level definition counts (`definition_rows`, `definition_entry_count`, starter/continuation totals), so future UIs/scripts/LLMs can inspect visible docs/help reference definitions and footnote definitions without inferring them only from `definition_role` or reparsing starter tokens.

Latest tiny landing (rev263): the shared docs/help cue model now also exposes parsed visible definition metadata for reference-definition starters/continuations and footnote-definition starters/continuations. The handoff note is `docs/205-docs-cues-definition-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, `tests/test_tui_md_definitions.py`, `tests/test_editor_help_docs_navigation.py`, and `tests/test_mxcontext.py`.

Rev262 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `heading_entries` plus small top-level heading counts (`heading_rows`, `heading_entry_count`, title/underline totals), so future UIs/scripts/LLMs can inspect visible docs/help heading titles and resolved fragments without inferring them only from `line_role`, `heading_level`, or a second heading scan.

Latest tiny landing (rev262): the shared docs/help cue model now also exposes parsed visible heading metadata for title rows, underline rows, and resolved fragments. The handoff note is `docs/204-docs-cues-heading-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev261 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `table_entries` plus small top-level table counts (`table_rows`, `table_entry_count`, header/body/delimiter cell totals), so future UIs/scripts/LLMs can inspect visible docs/help pipe-table cells and delimiter alignment without reverse-engineering generic pipe spans or rerunning the tiny table helpers.

Latest tiny landing (rev261): the shared docs/help cue model now also exposes parsed visible table metadata for header/body cells and delimiter-row alignment. The handoff note is `docs/203-docs-cues-table-metadata.md`, and the focused coverage lives in `tests/test_tui_md_tables.py`, `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev260 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `structure_entries` plus small top-level structure counts (`structure_rows`, `structure_entry_count`, list/task/blockquote/thematic totals), so future UIs/scripts/LLMs can inspect visible docs/help list/task/blockquote/thematic cues without reverse-engineering generic bold/dim spans.

Latest tiny landing (rev260): the shared docs/help cue model now also exposes parsed visible structure metadata for list markers, task checkboxes, blockquote prefixes/alerts, and thematic breaks. The handoff note is `docs/202-docs-cues-structure-metadata.md`, and the focused coverage lives in `tests/test_editor_screen_layout.py`, `tests/test_editor_main_cli.py`, and `tests/test_mxcontext.py`.

Rev259 note: the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and the repo now carries a tiny manifest test that checks every `: word` in `src/micromax/stdlib/core.mx` against explicit portability case names so future Python/Rust/WASM hosts and future LLMs can verify boot-stdlib coverage mechanically instead of diffing it by hand.

Latest tiny landing (rev259): the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and `tests/test_portability_suite.py` now carries a tiny explicit manifest that maps every boot-stdlib word in `core.mx` to named portability cases. The handoff note is `docs/201-portability-stdlib-coverage-audit.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev258 note: the JSON portability corpus now also covers the tiny boot-stdlib assertion helper `assert`, so future Python/Rust/WASM hosts can replay both its success and failure-path stack behavior from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev258): the JSON portability corpus now also covers the tiny boot-stdlib assertion helper `assert`, including the failure-path contract that a thrown message still leaves older stack items intact. The handoff note is `docs/200-portability-assert.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev257 note: the JSON portability runner now also lets expected-error cases pin down the post-error stack, so future Python/Rust/WASM hosts can replay small cleanup/rethrow contracts like `ensure` / `finally` directly from JSON instead of leaving them trapped in Python-only tests.

Latest tiny landing (rev257): the JSON portability runner now also lets expected-error cases pin down the post-error stack, and the corpus now uses that to replay `try?` success plus `ensure` / `finally` cleanup-rethrow behavior directly from JSON. The handoff note is `docs/199-portability-recovery-error-stacks.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_try_combinator.py`, and `tests/test_ensure_finally.py`.

Rev256 note: the JSON portability corpus now also covers the tiny boot-stdlib preserving combinator `keep`, so future Python/Rust/WASM hosts can replay one more small quote-friendly stack contract from JSON alone instead of inferring it from `core.mx`, `bi` / `tri`, or ad hoc tests.

Latest tiny landing (rev256): the JSON portability corpus now also covers the tiny boot-stdlib preserving combinator `keep`, so future Python/Rust/WASM hosts can replay one more small quote-friendly stack contract from JSON alone. The handoff note is `docs/198-portability-keep.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev255 note: the JSON portability corpus now also covers tiny boot-stdlib `nip` / `tuck` / `2dup` / `2drop` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped stack-helper slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev255): the JSON portability corpus now also covers tiny boot-stdlib `nip` / `tuck` / `2dup` / `2drop` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped stack-helper slice from JSON alone. The handoff note is `docs/197-portability-basic-stack-pairs.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev253 note: the JSON portability corpus now also covers tiny boot-stdlib `2rdrop` behavior, so future Python/Rust/WASM hosts can replay one more small pair-return-stack cleanup slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev252 note: the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck` behavior, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev251 note: the JSON portability corpus now also covers tiny boot-stdlib `2>r` / `2r>` / `2r@` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-return-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev250 note: the JSON portability corpus now also covers tiny boot-stdlib `2rot` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack rotation slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev249 note: the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev248 note: the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev247 note: the JSON portability corpus now also covers tiny boot-stdlib `1+`, `1-`, `0>`, and `0<>` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic/predicate slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev246 note: the JSON portability corpus now also covers tiny boot-stdlib `max` / `min` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev245 note: the JSON portability corpus now also covers tiny boot-stdlib `negate`, `0<`, and `abs` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev243 note: the JSON portability corpus now also makes the `pick` / `roll` failure edges replayable — negative indices now have explicit `u must be >= 0` contracts and too-shallow stacks now expect `Stack underflow` — so future Python/Rust/WASM hosts do not have to guess how Micromax resolves the Forth standard's ambiguous out-of-range cases.

Rev242 note: the JSON portability corpus now also covers two deeper five-item stack-shuffle cases — `4 pick` copying the fifth item and `4 roll` rotating the top five items — so future Python/Rust/WASM hosts can replay one more general `pick` / `roll` indexing slice that is easy to get subtly off-by-one during a hand port.

Rev241 note: the JSON portability corpus now also covers two deeper four-item stack-shuffle cases — `3 pick` copying the fourth item and `3 roll` rotating the top four items — so future Python/Rust/WASM hosts can replay one more general `pick` / `roll` indexing slice that is easy to get subtly off-by-one during a hand port.

Rev240 note: the JSON portability corpus now also covers two adjacent `pick` / `roll` indexing edge cases — `0 roll` as a null op and `2 pick` copying the third stack item — so future Python/Rust/WASM hosts can replay one more tiny stack-shuffle slice that is easy to misindex during a hand port.

Rev239 note: the JSON portability corpus now also covers four tiny stack-shuffle contracts for `pick` / `roll` (`0 pick`=`dup`, `1 pick`=`over`, `1 roll`=`swap`, `2 roll`=`rot`), giving future Python/Rust/WASM hosts one more small replayable contract slice for stack-indexing behavior that is easy to get subtly wrong during a hand port.

Rev238 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `literal_entries` plus small top-level literal-source counts (`literal_rows`, `literal_entry_count`, `raw_html_entry_count`, `escaped_markdown_entry_count`), so future UIs/scripts/LLMs can inspect visible docs/help raw-HTML tags and escaped markdown tokens without reverse-engineering generic dim spans.

Rev237 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `markup_entries` plus small top-level inline-markup counts (`markup_rows`, `markup_entry_count`, `strong_entry_count`, `emphasis_entry_count`, `strike_entry_count`), so future UIs/scripts/LLMs can inspect visible docs/help strong/emphasis/strike tokens without inferring them from bold/italic/dim spans.

Rev236 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `code_entries` plus small top-level code counts (`code_rows`, `code_entry_count`), so future UIs/scripts/LLMs can inspect visible docs/help inline-code tokens without scraping raw backticks or rerunning the tiny code-span matcher.

Rev235 note: the shared `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot now also exposes parsed row-local `image_entries` plus small top-level image counts (`image_rows`, `image_entry_count`, local/fragment/external totals), so future UIs/scripts/LLMs can see what visible docs/help image tokens point to without scraping raw markdown or rerunning the tiny image matcher.

Rev229 note: `tools/mxcontext.py` now also has machine-readable `--json` output plus `--check` validation for its curated entry-doc/code list, `make context-json` / `make context-check` wrap those paths, and the archive now carries a sharper `docs/171-rust-vm-spike.md` plan so the one explicit Rust TODO stays concrete without pretending an untested second implementation already exists.

Rev228 note: `python -m micromax_editor` now also exposes a tiny non-interactive screen dump path (`--dump-screen LINES COLS`) plus `--help-doc TOPIC`, so future humans/LLMs can inspect the shared `screen_model(...)` / `docs_cues` story as formatted JSON without launching curses or writing ad hoc Python; the headless REPL now also accepts `:screen [LINES COLS]`, `tools/mxcontext.py` includes the recent screen/docs model docs, and `make revzip TAG=...` now wraps the standard release-archive helper.

Rev227 note: the shared editor core now also publishes one tiny `docs_cues_model(lines, cols)` / `ed.docs-cues` snapshot — visible docs/help scanability cues like headings, list/task/blockquote prefixes, link-label spans, dimmed source scaffolding, fenced/html/inert rows, table delimiters, and emphasis spans — and the composed `screen_model(lines, cols)` now includes that docs-help cue surface too, so future UIs/scripts/LLMs can inspect the same markdown-ish help emphasis the reference curses TUI paints without scraping curses output or re-parsing visible row fragments by hand.

Rev226 note: the shared editor core now also publishes one tiny `viewport_cues_model(lines, cols)` / `ed.viewport-cues` snapshot — visible edit-window cue spans for `cursorline`, `hlsearch`, `showchars`, `hltrailingws`, `hltaberrors`, `colorcolumn`, and `matchbrace` — and the composed `screen_model(lines, cols)` now includes that cue surface too, so future UIs/scripts/LLMs can inspect the same non-text overlays the reference curses TUI paints without scraping curses attributes or replaying row-local cue math by hand.

Rev225 note: the shared editor core now also publishes one tiny `display_rows_model(lines, cols)` / `ed.display-rows` snapshot — ordered visible screen rows carrying the final plain text the reference curses TUI paints after `showchars` and horizontal overflow-marker overlays — and the composed `screen_model(lines, cols)` now includes that painted-text row surface too, so future UIs/scripts/LLMs can inspect what the user actually sees without scraping curses or replaying tiny overlay rules by hand.

Rev223 note: the shared editor core now also publishes one tiny viewport-local `search_rows_model(lines, cols)` / `ed.search-rows` snapshot — visible edit-window row fragments plus per-row `spans` / `current_spans` for the active search — and the composed `screen_model(lines, cols)` now includes that cue model too, so future UIs/scripts/LLMs can inspect the same search highlighting the reference curses TUI paints without scraping curses attributes or reconstructing row fragments by hand.

Rev222 note: the shared editor core now also publishes one tiny flat `screen_rows_model(lines, cols)` / `ed.screen-rows` snapshot — ordered plain visible screen rows spanning viewport text, picker rows, and bottom chrome — and the composed `screen_model(lines, cols)` now includes that flat row surface too, so future UIs/scripts/LLMs can answer the boring but useful question “what plain text is on screen right now?” without scraping curses; the portability corpus now also pins down that after a nested *successful* inner `catch`, the outer user-pushed return-stack item stays visible through `r@` as well as `r>`.

Rev221 note: the shared editor core now also publishes one tiny `viewport_rows_model(lines, cols)` / `ed.viewport-rows` snapshot — visible edit-window rows already zipped together with line-number cells, scrollbar-thumb cells, and stable row/cursor positions — and the composed `screen_model(lines, cols)` now includes that row-ordered surface too, so future UIs/scripts/LLMs can answer the practical question “what visible edit rows are on screen?” without rejoining gutter + edit-window models by hand; the portability corpus now also pins down that after a nested inner `throw`, the outer user-pushed return-stack item stays visible through `r@` as well as `r>`.

# Micromax

Rev224 note: the shared editor core now also publishes one tiny viewport-local `showchars_rows_model(lines, cols)` / `ed.showchars-rows` snapshot — visible edit-window row fragments plus their visible `display_text` / replacement `spans` — and the composed `screen_model(lines, cols)` now includes that cue model too, so future UIs/scripts/LLMs can inspect the same invisible-character replacements the reference curses TUI paints without scraping curses or redoing fragment-local indent rules by hand.

Rev220 note: the shared editor core now also publishes one tiny `gutter_model(lines, cols)` / `ed.gutter-model` snapshot — visible line-number cells plus right-edge scrollbar-thumb rows — and the composed `screen_model(lines, cols)` now includes that gutter state so future UIs/scripts/LLMs can inspect essentially all of the tiny reference screen without scraping curses output; the portability corpus now also pins down that a nested inner `throw` still leaves only outer user-pushed items visible to `rdepth` once control returns to the outer protected region.

Rev219 note: the shared editor core now also publishes one tiny `prompt_panel_model(lines, cols)` / `ed.prompt-panel` snapshot — the visible picker suggestion panel with reserved geometry plus positioned rendered entries — and the composed `screen_model(lines, cols)` now includes that panel so future UIs/scripts/LLMs can inspect the whole reference screen more honestly; the portability corpus now also pins down that *nested successful* `catch` frames stay hidden from visible `rdepth`, so only outer user-pushed return-stack items count there.

Rev218 note: the shared editor core now also publishes one tiny composed `screen_model(lines, cols)` / `ed.screen-model` snapshot — layout geometry, visible edit-window rows, positioned bottom chrome, and active cursor placement — and the minimal curses TUI now reuses that same whole-screen model instead of stitching those recent shared helpers together itself; the portability corpus now also pins down that a nested inner `throw` still preserves the order of outer user-pushed return-stack items.

Rev216 note: the shared editor core now also publishes a tiny reference `screen_layout_model(lines, cols)` snapshot plus hostcall `ed.screen-layout`, so future UIs/scripts/LLMs can inspect viewport size, gutter widths, picker suggestion height, and bottom-row y-positions without reverse-engineering curses layout math; the portability corpus now also pins down that a successful `catch` preserves the order of outer user-pushed return-stack items too, not just throw-time unwinds.

Rev215 note: the shared editor core now also publishes a tiny width-aware `interaction_model(width)` snapshot plus hostcall `ed.interaction-model`, so future UIs/scripts/LLMs can inspect the visible prompt/capture row (`raw_line`, visible `text`, truncation, and shared prompt/capture metadata) without scraping curses output; the portability corpus now also pins down that `catch`/`throw` preserve the order of outer user-pushed return-stack items, not just their depth or one surviving value.

v127)
Micromax is a **small, embeddable, concatenative language + VM** designed to become the native
plugin/config/macro system for a lightweight terminal editor in the spirit of **micro**.

Rev214 note: the shared editor core now also publishes tiny `keymenu_model(width)` and `infobar_model(width)` snapshots plus hostcalls `ed.keymenu-model` / `ed.infobar-model`, so future UIs/scripts/LLMs can inspect bottom help/message row segments without scraping dimmed TUI text; the portability corpus now also pins down that `catch`/`throw` preserve an outer user-pushed return-stack value, not just its depth.

Rev213 note: the shared editor core now also publishes one tiny `statusline_model(width)` layout snapshot plus hostcall `ed.statusline-model`, so future UIs/scripts/LLMs can inspect the visible statusline's left/right/padding/truncation without re-parsing the final row text; the portability corpus now also pins down that an inner `throw` inside a successful outer `catch` still preserves outer user-owned return-stack items.

Rev212 note: the shared editor core now also publishes one tiny ordered bottom-row chrome model via `bottom_rows_model(width)` / `ed.bottom-rows`, so future UIs/scripts/LLMs can inspect the exact visible keymenu / interaction-or-infobar / statusline stack without scraping curses output; the portability corpus now also pins down that `throw` inside `catch` preserves outer user-pushed return-stack items.

Rev211 note: the shared editor status model now also publishes one tiny unified bottom-row interaction snapshot (`interaction_kind`, `interaction_summary`, `interaction_detail`, `interaction_position`, `interaction_line`) for ordinary prompts *and* capture keymodes, so future UIs/statuslines/scripts can inspect the active prompt/capture surface without reconstructing TUI text from scattered fields; the portability corpus now also pins down that successful `catch` counts only user-pushed return-stack items in visible `rdepth`.

Rev210 note: active capture keymodes now publish a shared status-model snapshot (`capture_kind`, `capture_summary`, `capture_detail`, etc.) so future statuslines/UIs/scripts can inspect `qreplace` / `openurl` without scraping TUI text, and the portability corpus now also pins down that a successful `catch` keeps internal exception frames out of visible `rdepth`.

Rev209 note: existing capture keymodes like `qreplace` and `openurl` now get a real one-line bottom-row prompt plus mode-aware keymenu hints in the minimal curses TUI, even when `infobar=false`, and the portability corpus now also pins down that `catch` restores return-stack depth on `throw` instead of leaking `>r` state across recovery.

Rev208 note: the minimal curses TUI now honors a tiny nano-esque `constantshow` option so the idle infobar can keep a right-aligned cursor summary (`Ln i/n, Col j (pct%)`) next to the last message without re-expanding the main statusline, and the portability corpus now makes the older `return-stack-roundtrip` case honest by actually round-tripping through `r>` while the separate peek/depth/`rdrop` case keeps covering that distinct return-stack contract.

Rev207 note: the minimal curses TUI now treats `statusline=false` as real layout policy instead of merely hiding status text, so the bottom status row is reclaimed for editing while prompt/infobar/keymenu rows still stack honestly above it.

Rev206 note: the minimal curses TUI now honors a tiny micro-esque `infobar` option so the idle message row disappears when disabled while active command/find/picker prompts still temporarily claim that same row, reclaiming one more visible buffer row without promoting new UI chrome into the headless editor model.

Rev205 note: the minimal curses TUI now has an optional tiny `keymenu` rail that shows a compact nano-style shortcut summary during ordinary editing and prompt-aware hints while command/find/picker prompts are active, keeping the whole feature renderer-local and out of the headless editor model.

Rev171 note: the minimal curses TUI now has an optional micro-esque `ruler` / `relativeruler` gutter that keeps wrapped continuation rows blank and shifts viewport/cursor math honestly, while the JSON portability corpus now also covers typed predicates, `m?`, `get-current`, `dict-version`, and `host.api-version` so future hosts can replay a little more of the real kernel contract.

Rev170 note: the tiny JSON portability suite now covers a few more missing but very contract-like kernel behaviors (`0=`, successful `catch`, list clone/pop isolation, `m-keys`, `m-items`, session-local query/removal, and `set-current` round-tripping), and `mxportable` now supports exact case-name filtering via `--name` so future hosts and future LLMs can ask for precise slices without fuzzy substring matching.

Rev169 note: the tiny JSON portability suite now covers a few more portable kernel behaviors Micromax already relies on (`when`, `to-int`, `to-str`, `m-del`, `m-merge`), and `mxportable` can now emit a lighter-weight inventory of matching categories/tags/case names so future hosts and future LLMs can inspect the contract without pulling full case bodies.

Rev168 note: the tiny JSON portability suite is now easier for future hosts and future LLMs to inspect directly: `mxportable` can emit machine-readable JSON summaries/results, the corpus is tagged much more broadly, and the portable contract now also covers `while`, `constant`, `variable`, and locals shadowing on top of the earlier return-stack / namespace / recovery coverage.

Rev167 note: the tiny JSON portability suite is now a stricter and more sliceable cross-host contract: it adds portable cases for return-stack basics, `execute`, wordlist/search-order lookup, `in`, `2dip`, `recover`, and `finally`, and `tools/mxportable.py` / `src/micromax/portability_suite.py` now validate corpus shape and support category/tag/name filtering for targeted bring-up runs.

Rev166 note: the tiny JSON portability corpus now covers more of the language the repo actually leans on day to day: quotation combinators (`dip`, `2keep`, `tri`), recovery/cleanup helpers (`try?`, `try`, `ensure`), and step-budget exhaustion under `catch`, giving future Rust/WASM hosts a better cross-host semantic floor than just arithmetic plus one `bi` example.

Rev165 note: tiny indented continuation lines under markdown footnote definitions in docs/help buffers now also render dim in the live TUI, while the visible `[^id]:` starter marker keeps its existing dim+bold treatment — reusing the shared definition-line roles instead of inventing another parser path.
Rev217 note: the shared editor core now publishes one tiny `edit_window_model(lines, cols)` / `ed.edit-window` snapshot — visible edit-window rows, viewport map, softwrap flag, and primary-cursor view/screen coordinates — and the minimal curses TUI now reuses that same model instead of recomputing visible rows + cursor mapping separately, keeping one more piece of renderer truth inspectable for future UIs/scripts/LLMs.
Rev164 note: backslash-escaped markdown punctuation pairs in docs/help buffers (for example visible `\[`, `\!`, `\<`, `\*`, `\_`, `\~`, and ``\``` source) now get a tiny source-view cue too — the live TUI dims the visible two-character escape pair while leaving the escaped form literal and non-navigable — reusing one small helper layered on the existing shared backslash-escape policy instead of another parser path.
Rev163 note: inline markdown code-span backtick delimiters in docs/help buffers (for example the visible backticks around `simple code` and the double-backtick runs around ``code with `literal backticks` inside``) now get a tiny source-view cue too — the live TUI renders those delimiter runs bold+dim while leaving the existing code-body dimming alone — reusing one small helper layered on the existing equal-length backtick scan instead of another parser path.
Rev162 note: inline markdown emphasis delimiters in docs/help buffers (for example the visible `**`, `*`, `_`, and `~~` around already-styled emphasis bodies) now get a tiny source-view cue too — the live TUI dims those delimiter tokens while leaving the body styling alone — reusing one small helper layered on the existing inline-emphasis regex helpers instead of another parser path.
Rev161 note: visible supported ordinary markdown links in docs/help buffers (for example `[Vision](00-vision.md)`, `[Vision ref][visionref]`, and `[Vision shortcut]`) now get a tiny source-view cue too — the live TUI dims the non-label scaffolding around the still-underlined live label — reusing one small helper layered on the existing shared link matcher instead of another parser path.
Rev160 note: visible inline raw HTML tags in docs/help buffers (for example `<kbd>` / `</kbd>` / `<a name=...>`) now get a tiny inert-source cue too — the live TUI dims the whole tag token — reusing one small helper layered on the existing shared inline raw-HTML span helper while keeping supported autolinks on their separate bold whole-token path.
Rev159 note: visible supported markdown image forms in docs/help buffers (for example `![alt](dest)` and `![alt][id]`) now get a tiny inert-source cue too — the live TUI dims the whole token — reusing one small helper layered on the existing shared markdown destination/reference helpers rather than another parser path.
Rev157 note: docs/help buffers now give visible markdown footnote references like `[^note]` a tiny source-view cue too — the whole token renders bold while the inner `^note` keeps the ordinary docs-link underline — continuing the shared-substrate-first docs-browser polish thread.
Rev156 note: GitHub-style alert opener tokens inside docs/help blockquotes (for example `> [!NOTE]` and `> [!WARNING]`) now get a tiny source-view cue too: the live TUI bolds the alert marker while keeping the quoted body dim, reusing one shared helper instead of growing an alert-specific parser path.
Rev155 note: nested markdown list/task markers in docs/help buffers now render like real nested list markers in the live TUI too, but only after the shared indented-code guard has already ruled out top-level code blocks, so sub-bullets in worklists/readmes scan better without making code examples look like lists.
Rev154 note: reference-style definition starter lines and footnote-definition starter lines in docs/help buffers now render dim with bold marker tokens in the live TUI, and tiny wrapped reference-definition continuation lines render dim too, reusing one shared definition-line helper instead of another render-only parser path.
Rev153 note: raw HTML comments and raw HTML block lines in docs/help buffers were already inert for `helpfollow`, `helplinkpick`, outline/definition parsing, and TUI docs-link underlining; the live TUI now dims those same comment spans / block lines too so commented-out notes and embedded HTML examples stop reading quite so much like ordinary prose.
Rev152 note: blank-separated indented code-ish markdown lines in docs/help buffers now stay inert for `helpfollow`, `helplinkpick`, and TUI docs-link underlining too, and the live TUI dims those lines so ordinary source-view code examples read like code instead of accidentally clickable prose.
Rev151 note: docs/help rendering now also makes fenced markdown examples look visibly code-ish in the live TUI: opening/closing fence lines render bold+dim, fenced body lines render dim, and the whole thing reuses the same shared fence scan already trusted for docs-link/definition precedence.
Rev150 note: docs/help rendering now reuses the same tiny heading scan already trusted for titles, outline rows, fragment jumps, and heading breadcrumbs, so setext heading title lines finally render like headings in the live TUI too while their `===` / `---` underline line gets a dim heading-ish treatment.
Rev149 note: the minimal TUI now gives ordinary markdown list markers a little scanability polish in docs/help buffers: bullet markers (`-` / `+` / `*`) and ordered markers (`1.` / `1)`) render bold via one tiny shared helper, while existing task-list styling layers cleanly on top.
Rev122 note: fenced code blocks in docs/help buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, TUI docs-link underlining, and markdown reference-definition parsing, so literal markdown examples inside triple-backtick/tilde fences no longer leak into the live help browser.
Rev124 note: raw HTML comments in docs/help buffers are now treated as inert prose for `helpfollow`, `helplinkpick`, outline scanning, TUI docs-link underlining, and markdown reference/footnote-definition parsing, so commented-out markdown examples stay literal instead of leaking back into the live help browser.
Rev123 note: single-line setext headings (`Title` + `===` / `---`) now participate in docs/help fragment jumps, outline rows, heading breadcrumbs, and docs-picker titles, reusing the same tiny heading-title cleanup and explicit `{#id}` handling as ATX headings without committing Micromax to a full markdown block parser.
Rev120 note: docs/help link parsing now handles balanced bracket labels like `[Vision [nested]](00-vision.md)`, `[Vision [nested]][id]`, and `[Vision [nested]]` via a small shared scanner used by `helpfollow`, `helplinkpick`, the docs TUI underline model, and reference-definition parsing. This keeps nested markdown examples navigable without committing Micromax to a full markdown parser.

The project deliberately grows in two directions at once:

Rev121 note: docs/help link destinations now use a slightly smarter tiny parser: balanced parentheses in bare destinations work, markdown-safe backslash escapes are unescaped in inline/reference destinations, and percent-encoded local doc paths are decoded before follow. This keeps local docs links like `104-paren\(topic\).md`, `103-space\ path.md`, and `103-space%20path.md` navigable without committing Micromax to a full destination/title parser.

- **language/VM**: tiny, inspectable, heavily tested, pleasant to evolve by hand offline
- **editor core**: headless-first, deterministic, and unit-testable before any terminal UI hardens

Rev119 note: docs/help markdown escapes now stay literal across both styling and actions: backslash-escaped links, refs, footnotes, images, and autolinks no longer leak into `helpfollow`, `helplinkpick`, or TUI link underlining, so docs that teach markdown stay prose instead of becoming accidentally navigable.

Rev118 note: docs-browser actions now respect inline-code precedence too: `helpfollow` and `helplinkpick` ignore markdown-looking links/autolinks that sit inside inline code spans, keeping editor behavior aligned with the tiny TUI link-highlighting policy.

Rev117 note: markdown image forms like `![alt](dest)` and `![alt][id]` are now ignored consistently by `helpfollow`, `helplinkpick`, and TUI docs-link underlining, so image alt text stays prose until Micromax grows a clearer image-aware docs policy.

Rev116 note: docs/help inline code spans now support equal-length backtick delimiters (so double-backtick forms can include literal backticks), and the TUI now masks code spans before link-underlining so code-ish text doesn’t accidentally look clickable.

Rev115 note: the minimal TUI now gives tiny markdown inline emphasis forms a little scanability polish in docs/help buffers: `**strong**` bodies render bold, `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline), and `~~strike~~` bodies render dim, all staying intentionally UI-only and inspectable.

Rev114 note: the minimal TUI now gives markdown thematic breaks a little scanability polish in docs/help buffers: common separators like `---`, `***`, `___`, and spaced forms such as `- - -` render dim with a bolder marker run, staying intentionally UI-only and inspectable.

Rev113 note: the minimal TUI now gives markdown blockquotes a little scanability polish in docs/help buffers: quote-marker prefixes render bold and quoted bodies dim, staying intentionally UI-only and inspectable.

Rev112 note: the minimal TUI now gives GFM-style task-list markers a little scanability polish in docs/help buffers: checkbox tokens render bold and checked task bodies are dimmed, staying intentionally UI-only and inspectable.

Rev111 note: the minimal TUI now gives GFM-style pipe tables a little scanability polish in docs/help buffers: table header rows render bold, delimiter rows dim, and `|` separators are dimmed without pulling in a full markdown parser or changing the headless core.

Rev110 note: docs/help buffers now recognize common markdown footnote references (`[^id]`) and jump to matching definitions (`[^id]: ...`) in-place. The same tiny footnote model now flows through `helpfollow`, `helplinkcopy`, `helplinkpick`, `helpnavpick`, and TUI underline/current-link detection so docs surfaces stay aligned without committing to a full markdown engine.

Rev109 note: the docs help browser now follows markdown heading fragments — both same-page `#section` links and cross-doc `page.md#section` links — using best-effort GitHub-style heading slugs plus explicit heading ids (`{#id}` / `{: #id }`). Outline rows and heading-based breadcrumbs also strip raw attr-list suffixes so picker/search surfaces show human titles instead of source syntax.

Rev108 note: the command palette now splits path-like results into clearer `Directories` / `Files` / `Open` sections instead of lumping everything under one `Open` bucket, and the repo now ships a tiny JSON portability corpus plus `tools/mxportable.py` so future Rust/WASM ports can validate core semantics against the Python oracle.

Rev107 note: the docs help navigator (`helpnavpick`) now reuses the same link grouping policy as `helplinkpick`, so `set help.linksections heading` affects both surfaces consistently. External-link confirmation prompts also name their source (`help`, `cursor`, or explicit `command`) for slightly better safety/clarity.

Rev69 note: improved VM decompiler surfaces: `see` now includes a compact tier-2 disassembly and const pool when available, and tooling can fetch structured disassembly via `disasm-rows`. The editor embedding also exposes a small regex hostcall set (`re.search`/`re.sub` etc.) aligned with `replace`/`replaceall`.

Rev67 note: the VM now has a **dev-mode stack effect checker starter kit** (`stackcheck!` warn/error modes, `infer-effect`, `check-effect`), and quotations preserve leading paren-comments so you can annotate quote effects like `[ ( x -- y ) ... ]`.

Rev66 added the portable syntax highlight span model (`ed.highlight`) and a deterministic timer queue (`ed.after`/`ed.pump-timers`). Rev65 added autoindent + `tabsize`/`tabstospaces`; rev64 added `jumppick`, user rc/init loading, and the `include`/`require` search convention.

Rev72 note: the editor statusline is now configurable via micro-esque `statusformatl`/`statusformatr` templates (a tiny `$()` renderer), and the stdlib adds `ensure`/`finally` for always-run cleanup built on `catch`/`throw`.

Rev82 note: the docs help browser got a little more micro-esque — `helplinkpick` now groups links into Docs/Files/External sections in the TUI, and external-link follow gives an explicit `cap.open-url` enable hint.

Rev83 note: docs navigation now recognizes **reference-style links** (`[text][id]` + `[id]: target`) and **autolinks** (`<https://...>`), so docs pages can use more idiomatic Markdown forms.

Rev90 note: picker-style prompts (buffer/doc/help pickers, palette, etc.) now support **Up/Down selection** without mutating the typed query, and `Ctrl-y` copies the selected row (for links: copies the target).

Rev91 note: picker-style prompts now also support **PageUp/PageDown selection jumps** (option: `prompt.page`, default 8), which makes long pickers (palette, docs link lists) feel much closer to a real command palette.

Rev92 note: picker-style prompts gain a `prompt.wrap` option (wrap vs clamp), support `Ctrl-Home`/`Ctrl-End` to jump to first/last selection, and the TUI repeats the current section header as a sticky header while paging through long mixed sections.

Rev93 note: picker-style prompts now support `Alt-Up`/`Alt-Down` section jumps (jump between section headers; `Alt-Up` also jumps to the start of the current section when used inside it), implemented in the headless core and used by the minimal TUI.

Rev94 note: the docs browser now understands **shortcut reference links** (`[id]` when a matching `[id]: target` definition exists), and the minimal TUI underlines inline/reference/shortcut/autolinks consistently so help pages feel more like a real in-editor browser.

Rev97 note: docs link pickers (`helplinkpick`) can optionally group links by nearest markdown heading (option: `help.linksections heading`), the host adds a capability-gated `ed.fs-stat` helper for portable path metadata, and the repo includes `tools/mkrevzip.py` to build standard-named offline archives.

Rev95 note: small repo + picker UX polish — the `Makefile` now runs scripts via `bash` (so `make test` works even when executable bits are lost in an archive), and the minimal TUI now highlights query-token substring matches in picker suggestion rows for faster scanning.

Rev84 note: docs navigation gained a combined picker (`helpnavpick`) that merges **Headings** + **Links** into one navigator, and the host now exposes grouped navigator sections via `ed.helpnav-section-rows`.

Rev85 note: the minimal curses TUI now interprets **Alt/Meta chords** (ESC-prefixed sequences) so default `Alt-*` bindings work, and maps **Ctrl-Space** (NUL) to `Ctrl-Space` for command palette muscle memory. Core defaults now include `Ctrl-b` buffer picker, `Ctrl-o` open (prefilled), `Ctrl-r` replace (prefilled), and `Alt-g` binding discovery.

Rev86 note: added an interactive **query-replace** loop (`qreplace` / `queryreplace`) that confirms each replacement with a tiny y/n/a/q keymode (capture mode so global bindings can't accidentally fire). Also unified Cursor<->offset conversion helpers (`micromax_editor.textpos`) used by search + replace.
Rev87 note: `replace` / `replaceall` and `qreplace` now respect the editor's `ignorecase` option (like `find`), and `qreplace` shows a small `match i/N` progress hint when it can pre-count matches.
Rev88 note: docs buffers gained `helplinkcopy` (and `y`) to copy the markdown link target under cursor, and external links now confirm by default when `cap.open-url` is enabled (capture keymode: y/open, n/cancel, c/copy).

Rev89 note: added `urlopen` / `urlcopy` (and default `Alt-o`/`Alt-y` bindings) to open/copy URLs under cursor in any buffer, reusing the same capability gate (`cap.open-url`) and confirmation keymode (`openurl`).

## What is already real

### Language / VM
- Python reference VM with wordlists, quotations, deferred words, hooks, maps, locals, and hostcalls
- two-tier execution path: token interpreter + optional bytecode/compiler scaffolding
- provenance/debug surfaces such as spans, `see`, `help`, `where`, and hook/keybinding inspection
- pure micromax stdlib loaded from `src/micromax/stdlib/core.mx`

### Editor substrate
- headless `Editor` core with buffers, cursors, selections, undo, and action chaining
- command bar + shell-ish parsing + prompt history
- searchable command/action palette, topic/help prompt, and current-binding prompt built on shared headless row metadata
- command palette now has a small MRU/recent section, grouped palette-section rows for future UIs/scripts, and clearer `Directories` / `Files` / `Open` buckets for path-like queries
- incremental search (`ignorecase`, `incsearch`), replace, and jump list
- multi-cursor primitives, macros, clipboard model, and statusline/infobar data model
- keybinding modes, one-shot/transient keymodes, `whichkey`-style discovery, binding docs, and prefix helpers
- micromax-defined commands, completion hooks, plugin lifecycle hooks, and grouped reload cleanup

### Archive ergonomics
- docs aimed at humans **and future LLMs** (`docs/01-llm-start-here.md`, `docs/02-repo-map.md`)
- `make context` for a curated snapshot
- `make doctor` for archive hygiene
- `make pack` for a clean zip archive

## Repository layout

- `docs/` — research notes, design docs, roadmap, decisions log, portability ledger
- `src/micromax/` — reference VM, core words, REPL, stdlib
- `src/micromax_editor/` — headless editor substrate + VM bridge
- `plugins/` — micromax plugins
- `examples/` — small language examples
- `tests/` — headless unit tests
- `tools/` + `scripts/` + `Makefile` — bootstrap/lint/test/context/pack helpers

## Quick start

Run the micromax REPL:

```bash
python -m micromax.repl
```

Run the headless editor prototype (REPL UI):

```bash
python -m micromax_editor
python -m micromax_editor path/to/file.txt
```

Run the minimal curses TUI:

```bash
python -m micromax_editor --tui
python -m micromax_editor --tui path/to/file.txt
```

## Development workflow

```bash
make bootstrap
make test
make doctor
make context
```

Optional local git bootstrap (no remote required):

```bash
make init-git
```

Build a clean archive zip:

```bash
make pack
make revzip TAG=screen-dump-headless-release-orbitfox
```

## Good entry points

Read these first:

1. `TODO.md` + `docs/43-worklist.md`
2. `docs/00-vision.md`
3. `docs/01-llm-start-here.md`
4. `docs/42-portability-ledger.md`
5. `docs/102-portability-suite.md`
6. `docs/22-two-tier-execution.md`
7. `docs/50-editor-behaviors.md`
8. `docs/64-editor-prompt-completion.md`
9. `docs/71-cookbook.md`

## Portability contract

The Python implementation is the **reference implementation** and **test oracle** for future ports
(such as Rust/WASM). If you add VM surface area, update `docs/42-portability-ledger.md`, and prefer adding at least one portable corpus case in `portability/kernel_cases.json` when the behavior is part of the portable kernel.

- Docs/help TUI scanability is deliberately tiny and local: headings are bold; markdown links are underlined (bold+underlined when the cursor is on them), with small whole-token cues for supported autolinks like `<https://...>` and footnote references like `[^id]`; visible ordinary markdown links now also dim their non-label source scaffolding while keeping the live label underlined; visible inline raw HTML tags like `<kbd>` / `<a name=...>` now dim as inert source too; inline code spans are masked first so code-ish text does not look clickable; inline code spans are dimmed (including equal-length multi-backtick forms for literal backticks inside code), and visible backtick delimiter runs now render bold+dim too; ordinary markdown list markers (`-` / `+` / `*`, `1.` / `1)`) render bold; `**strong**` bodies render bold; `*emphasis*` / `_emphasis_` bodies render italic when available (falling back to underline); `~~strike~~` bodies render dim; small pipe tables get bold headers, dim delimiter rows, and dim `|` separators; GFM-style task-list checkboxes are bolded and checked task bodies are dimmed; and editor-side docs actions (`helpfollow` / `helplinkpick`) now also ignore markdown-looking links that appear inside inline code spans; fenced code blocks are likewise treated as inert prose for docs-link actions and underlining, keeping docs-browser behavior aligned with the TUI's code-first scanability policy.
