Rev302 note: `tools/mxcontext.py` now also exposes one compact portability snapshot — corpus counts, manifest coverage, source-shape facts, and direct pointers to `portability/kernel_cases.json` / `src/micromax/portability_suite.py` — so future Python/Rust/WASM hosts and future LLMs can answer basic bring-up and coverage questions without reopening half the archive.

Latest tiny landing (rev302): the archive now turns the curated repo-context helper into a small portability-aware handoff too: `mxcontext --json` still reports the current revision, priorities, entry docs/code, and checkable breadcrumbs, but now it also carries a `portability` block with total case counts, per-category/tag/host-feature summaries, boot-stdlib manifest coverage (`word_count`, `manifest_case_count`, `all_cases_present`, `missing_words`), and tiny boot-stdlib source facts (`source_path`, definition count, alias inventory, max dependency depth), while the curated code/command lists now point straight at `src/micromax/portability_suite.py`, `portability/kernel_cases.json`, and a few high-value `mxportable` commands. The handoff note is `docs/244-context-portability-snapshot.md`, and the focused coverage lives in `tests/test_mxcontext.py`.

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

Rev259 note: the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and the repo now carries a tiny manifest test that checks every `: word` in `src/micromax/stdlib/core.mx` against explicit portability case names so future Python/Rust/WASM hosts and future LLMs can verify boot-stdlib coverage mechanically instead of diffing it by hand.

Latest tiny landing (rev259): the JSON portability corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and `tests/test_portability_suite.py` now carries a tiny explicit manifest that maps every boot-stdlib word in `core.mx` to named portability cases. The handoff note is `docs/201-portability-stdlib-coverage-audit.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, and `tests/test_mxcontext.py`.

Rev258 note: the JSON portability corpus now also covers the tiny boot-stdlib assertion helper `assert`, so future Python/Rust/WASM hosts can replay both its success and failure-path stack behavior from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

*Rev259 follow-up:* the JSON corpus now also covers tiny boot-stdlib `rdrop` behavior plus the success path of `recover`, and `tests/test_portability_suite.py` now carries a tiny manifest that checks every `: word` in `src/micromax/stdlib/core.mx` against named portability cases so future hosts can verify boot-stdlib coverage mechanically instead of diffing files by hand.

Rev257 note: the JSON portability runner now also lets expected-error cases pin down the post-error stack, so future Python/Rust/WASM hosts can replay small cleanup/rethrow contracts like `ensure` / `finally` directly from JSON instead of leaving them trapped in Python-only tests.

Latest tiny landing (rev257): the JSON portability runner now also lets expected-error cases pin down the post-error stack, and the corpus now uses that to replay `try?` success plus `ensure` / `finally` cleanup-rethrow behavior directly from JSON. The handoff note is `docs/199-portability-recovery-error-stacks.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_try_combinator.py`, and `tests/test_ensure_finally.py`.

- Shared portability follow-up (rev256): the JSON portability corpus now also covers the tiny boot-stdlib preserving combinator `keep`, so future Python/Rust/WASM hosts can replay one more small quote-friendly stack contract directly from JSON instead of inferring it from `core.mx` or larger composed words; see `docs/198-portability-keep.md`.
- Shared portability follow-up (rev255): the JSON portability corpus now also covers tiny boot-stdlib `nip` / `tuck` / `2dup` / `2drop`, so future Python/Rust/WASM hosts can replay one more small standard-shaped stack-helper slice directly from JSON instead of inferring it from `core.mx`; see `docs/197-portability-basic-stack-pairs.md`.
- Shared portability follow-up (rev254): the JSON portability corpus now also covers tiny boot-stdlib `<>`, so future Python/Rust/WASM hosts can replay one more small comparison slice directly from JSON instead of inferring it from `core.mx`; see `docs/196-portability-not-equals.md`.
- Shared portability follow-up (rev253): the JSON portability corpus now also covers tiny boot-stdlib `2rdrop`, so future Python/Rust/WASM hosts can replay one more small pair-return-stack cleanup slice directly from JSON instead of inferring it from `core.mx`; see `docs/195-portability-2rdrop.md`.
- Shared portability follow-up (rev252): the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck`, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice directly from JSON instead of inferring it from `core.mx`; see `docs/194-portability-2nip-2tuck.md`.
- Shared portability follow-up (rev250): the JSON portability corpus now also covers tiny boot-stdlib `2rot`, so future Python/Rust/WASM hosts can replay one more small pair-stack rotation slice directly from JSON instead of inferring it from `core.mx`; see `docs/192-portability-2rot.md`.
- Shared portability follow-up (rev249): the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap`, so future Python/Rust/WASM hosts can replay one more small pair-stack slice directly from JSON instead of inferring it from `core.mx`; see `docs/191-portability-2over-2swap.md`.
Rev248 note: the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev247 note: the JSON portability corpus now also covers tiny boot-stdlib `1+`, `1-`, `0>`, and `0<>` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic/predicate slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev246 note: the JSON portability corpus now also covers tiny boot-stdlib `max` / `min` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

*Rev222 follow-up:* the JSON corpus now also covers the symmetric nested success-path visibility contract for `r@`: after an inner successful `catch` returns to the outer protected region, an outer user-pushed return-stack item should still remain visible through `r@` and later removable through `r>`.

*Rev221 follow-up:* the JSON corpus now also covers one more nested recovery visibility contract: after an inner `throw` is caught and control returns to the outer protected region, an outer user-pushed return-stack item should still be visible through `r@` and later removable via `r>`, not hidden behind nested exception bookkeeping.

*Rev220 follow-up:* the JSON corpus now also covers one more nested recovery visibility contract: after an inner `throw` is caught and control returns to the outer protected region, visible `rdepth` should count only outer user-pushed return-stack items, not hidden nested exception bookkeeping.

*Rev219 follow-up:* the JSON corpus now also covers one more subtle success-path recovery contract: nested successful `catch` frames must stay hidden from visible `rdepth`, so only outer user-pushed return-stack items count there and future hosts do not accidentally make exception bookkeeping observable.

*Rev216 follow-up:* the JSON corpus now also covers the successful path of the same outer-return-stack contract: when `catch` returns normally, outer user-pushed `>r` items must keep both their values and their order, so future hosts do not accidentally make exception frames observable or destructive on success.

*Rev215 follow-up:* the JSON corpus now also covers one more small but realistic recovery contract: if two user-owned values are on the return stack outside a protected region, an inner `throw` must preserve their order as well as their survival, so future hosts do not accidentally trim too aggressively or restore in the wrong order.

*rev213 follow-up:* the JSON corpus now also covers one more small but realistic recovery contract: an inner `throw` inside a successful outer `catch` must still preserve outer user-owned return-stack items, so future hosts and future LLMs do not accidentally bless nested recovery paths that flatten too much of `rstack`.

*rev212 follow-up:* the JSON corpus now also covers one more small but important recovery contract: an inner `throw` inside `catch` must preserve user-pushed return-stack items that live outside the protected region, so future hosts and future LLMs do not accidentally bless recovery paths that over-trim `rstack`.

*rev209 follow-up:* the JSON corpus now also covers one small but important recovery contract: `catch` must restore return-stack depth on `throw`, not just the data stack, so future hosts and future LLMs do not accidentally bless exception paths that leak `>r` state across recovery.

*rev208 follow-up:* the JSON corpus now makes the older `return-stack-roundtrip` case honest by actually round-tripping a value through `>r ... r>`, while the separate `return-stack-peek-and-depth` case keeps covering `r@`, `rdepth`, and `rdrop`, so future hosts and future LLMs do not have to mentally correct misleading case names during bring-up.

*rev207 follow-up:* the JSON corpus now also covers one more tiny legal return-stack pattern: a two-item `>r >r r@ r> r>` sequence peeks the most recently pushed item first, restores the stack in LIFO order, and leaves `rdepth` back at zero, so future hosts can validate a little more than single-item roundtrips from JSON alone.

*rev206 follow-up:* the JSON corpus now also covers one more tiny return-stack contract: `r@` can peek the top return-stack value without consuming it and `rdepth` reports the resulting depth, so future hosts do not need to infer that behavior only from Python tests.


*rev198 follow-up:* the JSON corpus now also pins down that deleting a missing map key leaves existing entries intact, so future hosts do not need to infer that small mutation/no-op contract only from Python tests.


# Portability ledger (Rust/WASM)

*rev197 follow-up:* the JSON corpus now also pins down another already-promised map behavior: `m@` returns `0` for a missing key, so future hosts do not need to infer that contract from Python tests alone.


This file is the *contract* that keeps the Python reference VM from drifting away from the eventual Rust/WASM VM.

Anything in the **portable kernel** must have an obvious Rust/WASM implementation.
Anything outside it must be explicitly marked as **reference-only** or **host-provided**.

## 1) Portable kernel (rev14)

These categories should remain small and stable.

### Stack + return stack
- `dup drop swap over rot`
- `>r r> r@ rdepth`

### Control / execution
- quotations: `[ ... ]`
- `call` (execute a quotation)
- `execute` (execute an XT)
- `'` (push XT)
- `if when while`

### Arithmetic / comparison (int-only)
- `+ - * / mod`
- `= < >`
- `0=` (may become stdlib later)

### Memory / state
- `cell` via `variable/constant` (Cells)
- `@ !`

### Collections (lists)
- `list push pop len nth set-nth clone`

### Type predicates + conversions
- `int? str? list? map? quote? xt?`
- `to-int to-str`
- `s= s<` (typed string comparisons)

### Collections (maps)
- `map map? m@ m! m? m-del m-keys m-items m-merge`
  - policy: keys are strings in portable mode

### Dictionary + compilation
- `find` (string name -> xt|0)
- `dict-version` (global dictionary/search-order version; used for tier-2 cache invalidation; lookup-only operations like successful `find`, `get-order`, `get-current`, `host.api-version`, `host.feature?`, or `host.features` should not bump it)
- `compile` / `compiled?` (tier-2 tooling; optional but portable)

### Namespaces + module hygiene
- `wordlist set-current get-current set-order get-order`
- `only also previous definitions`
- `module endmodule use in modules` (portable, but can be stubbed in tiny embeddings)

### Errors + safety
- `catch throw`
- `last-error last-error.`
- `set-budget budget with-budget` (step budget; portable)

### Host boundary
- `hostcall`
- `host.api-version host.feature? host.features`
- `host.capabilities` (optional registry; hostcall)

### Locals sugar (portable but optional)
- `locals local@ local? local! unlocal locals-clear`

## 2) Stdlib words (loaded at boot)

These are defined in `src/micromax/stdlib/core.mx` and are intentionally *not* VM primitives.

- `nip tuck ?dup 1+ 1- 2dup 2drop 2over 2swap 2rot negate 0< 0> 0<> <> abs max min`
- `rdrop`
- `dip keep 2dip 2keep bi tri`

Rule: new convenience words should land in stdlib first unless there is a strong reason.

## 3) Reference-only (allowed to diverge)

These are useful for hacking and debugging, but are not required in a minimal embedded VM:

- printing/debug: `. cr emit .s words see help where order disasm`
- introspection helpers: `words-list words-rows wid-words wid-word-rows wid-name` (useful for tooling; optional in tiny embeddings)
- xt introspection: `xt-kind xt-effect xt-doc xt-src xt-src-rows xt-span here-span` (optional; helpful for tooling and docs)
- hook inspection: `hook-rows`, `hook-detail`, `hook-groups`, and best-effort hook spans are tooling-oriented (optional)
- hook grouping: `hook-group! hook-group@ hook-rm-group` are optional portability-friendly cleanup helpers
- tier-2 inline caching is keyed by `dict-version` (implementation detail; portable to Rust/WASM)
- tier-2 bytecode uses a constant pool (instruction operands are indexes into `consts`)
- tier-2 bytecode supports tiny control flow (`JMP`/`JZ`) and direct quotation calls (`CALL_Q`); jump operands are signed relative instruction offsets
- bytecode JSON serialization (`bytecode-json` / `bytecode-load-json`) is tooling-oriented (optional)
- convenience stack ops: `pick roll clear` (may move in/out depending on needs)
- any direct filesystem access baked into the VM (prefer hostcalls)

## 3b) Editor host surface (host-provided; must stay "portable on the wire")

The editor's hostcalls are not VM primitives, but their *data representations*
must stay portable (ints/strings/lists only).

- cursors are `[[line col] ...]` in document order
- primary cursor is an integer index into the cursor list
- selections are `[[aL aC cL cC] ...]` (directed anchor/cursor) or `[]` for none
- cursorstate snapshots are `[primary [[id line col aL aC] ...]]` with `aL/aC = -1/-1` for none
- messages are `["...", ...]` (list of strings); exposed via `ed.messages` / `ed.pop-message` / `ed.clear-messages` / `ed.with-messages` / `ed.capture-messages`
- statusline/infobar state is a string-keyed map returned by `ed.status` (see `docs/69-editor-statusline-model.md`)
- viewport state is a string-keyed map returned by `ed.viewport` and set by `ed.viewport!` (top/left/height/width)
- macros are a list of tagged steps: `["a", ACTION, [[key val] ...]]` for actions and `["c", CMDLINE]` for commands (see `docs/58-editor-macros.md`)
- clipboard text is a string (may include trailing newline when linewise)
- clipboard items are `["...", ...]` plus a kind string: "items"|"lines"
- selection recovery stack is host-local (no wire format; exposed only via push/pop hostcalls)
- jumplist is host-local (cursor/selection snapshots); exposed via push/jump hostcalls and `ed.jump-info` returning `[index size]`
- editor command metadata can be exposed as `[[name doc group|0 [file line col]|0] ...]` (tooling-oriented)
- editor binding metadata can be exposed as `[[key action-spec group|0 [file line col]|0] ...]` (tooling-oriented)
- binding descriptions are plain strings and can be exposed as `desc|0` fields in keymap rows
- keymode rows can be exposed as `[[mode once?] ...]` with `once?` as `0|1`; `ed.press-key` is a host convenience wrapper around key dispatch
- keymap discovery can be exposed as `ed.binding-rows-for`, `ed.available-bindings`, `ed.resolve-key`, plus description-rich siblings (`ed.binding-info-for`, `ed.available-binding-info`, `ed.resolve-key-info`), using only strings / ints / lists
- editor registration grouping via `ed.group!` / `ed.group@` is an optional cleanup/debugging helper

### 3c) Reference host helpers (host-provided)

These are not VM primitives. Editor embeddings install them as hostcalls and
also define convenience words that call them.

- string helpers: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format`

## 4) Policy for adding surface area

Before adding a primitive or hostcall, record:

- **category**: kernel / stdlib / host / reference-only
- **porting plan**: how it works in Rust/WASM
- **tests**: at least 2 targeted tests
- **docs**: stack effect + 1 example


- prefix maps are represented as ordinary key bindings whose action-spec enters a one-shot keymode (`command:prefixmode MODE`); `ed.bind-prefix` and `ed.bind-mode-prefix` are convenience sugar, not new binding classes.


## 5) Portability corpus

The repo now carries a tiny **JSON portability corpus** in `portability/kernel_cases.json`.

Purpose:
- capture a few stable, data-only expectations for the portable kernel + boot stdlib
- make it easy for future Rust/WASM ports to validate semantics without importing Python-specific pytest helpers
- keep the corpus small enough to evolve by hand when the language grows

Runner surfaces:
- library: `src/micromax/portability_suite.py`
- CLI: `tools/mxportable.py`
- tests: `tests/test_portability_suite.py`

Runner/CLI policy:
- corpora should fail fast on duplicate names, missing categories, or malformed expectations
- optional `tags` are allowed for coarse-grained grouping (for example `namespaces`, `recovery`, `combinators`)
- the CLI now supports targeted bring-up runs via `--category`, `--tag`, exact-name `--name`, `--name-contains`, `--list`, and `--inventory`
- the CLI also supports `--json` so selected cases/results or inventory views can be consumed mechanically during host bring-up

Policy:
- prefer corpus cases for behavior that is part of the **portable kernel** or boot stdlib
- corpus cases may also optionally include `host_features: ["..."]` to seed the VM feature inventory before evaluation, keeping positive host-boundary probes data-only instead of baking them into the runner
- current examples now include kernel arithmetic/control/modules plus `0=`, successful and failing `catch`, successful `catch` keeping internal exception frames out of visible `rdepth`, `while`, `when`, return-stack basics, `execute`, `constant`, `variable`, typed predicates, typed string ordering via `s<`, `find` success/missing behavior, `dict-version`, lookup-only `find` + `get-order` + `get-current` stability around `dict-version`, `compile`/`compiled?` positive + primitive-negative behavior, `host.api-version`, positive + missing `host.feature?`, `host.feature?` lookup-only `dict-version` stability for both present and absent probes, bare-VM and seeded `host.features` plus `host.features` lookup-only `dict-version` stability, list clone/pop isolation, `to-int`, `to-str`, map mutation/inspection (`m?`, `m!`, `m-del`, `m-merge`, `m-keys`, `m-items`), locals shadowing plus session-local query/removal, wordlist/search-order lookup, same-wordlist latest-definition precedence, `get-current`, `set-current`, the fact that `set-current` alone does not add a wordlist to the search order, `get-order`/`set-order` round-tripping, `definitions` including persistence across later `set-order` changes, `also`, `previous`, `only`, duplicate-name search-order precedence, `in`, and boot-stdlib helpers/combinators/recovery helpers (`?dup`, `negate`, `0<`, `abs`, `max`, `min`, `bi`, `dip`, `2dip`, `2keep`, `tri`, `try?`, `try`, `recover`, `ensure`, `finally`, `assert`) plus a budget-exhaustion case observed through `catch`
- prefer broad but simple tags (`memory`, `locals`, `combinators`, `namespaces`, `budget`, etc.) so corpus slices stay easy to inspect during Rust/WASM bring-up
- keep cases data-only (`source`, expected stack, or expected error substring)
- avoid host-specific side effects or non-portable runtime objects in corpus expectations

- rev199 follow-up: the JSON portability corpus now also pins down that `m-keys` returns an empty list for an empty map, keeping the map-inspection contract explicit for future hosts.


- `m-items` on an empty map returns `[]` (not `0`, null, or an omitted value).


- rev202 portability follow-up: the JSON corpus now also covers `m-merge` with an empty destination map adopting the source pairs (`map-merge-empty-destination-adopts-source`).


- The tiny JSON portability corpus now also covers the negative `m?` case (`map-has-missing-key-is-false`) so future hosts pin down that missing-key predicates return `0`.


- rev204 portability follow-up: the JSON corpus now also covers overwriting an existing map key updating its value (`map-store-overwrite-updates-value`).


- rev210 portability follow-up: the JSON corpus now also covers successful `catch` keeping internal exception-frame bookkeeping out of visible `rdepth` (`catch-success-hides-exception-frame-from-rdepth`).


Rev211 follow-up: the JSON portability corpus now also includes `catch-success-counts-only-user-return-stack-items`, making one more tiny visible-return-stack contract explicit for future hosts: successful protected execution should let `rdepth` see only user-pushed `>r` items, not hidden exception-frame bookkeeping.

Rev214 follow-up: the JSON portability corpus now also includes `catch-throw-preserves-outer-return-stack-value`, making the newer recovery story slightly less depth-only: after an inner protected `throw`, an outer user-pushed `>r` item should still be retrievable with its original value.


Rev217 follow-up: the JSON portability corpus now also includes `nested-catch-success-preserves-outer-return-stack-order`, making the newer success-path recovery story a little less flat: even with one successful `catch` nested inside another, outer user-pushed `>r` items should keep their original order.


Rev218 follow-up: the JSON portability corpus now also includes `nested-catch-throw-preserves-outer-return-stack-order`, making the newer nested recovery story symmetric on the throw path too: even with an inner protected `throw`, outer user-pushed `>r` items should keep their original order.


Rev251 follow-up: the JSON portability corpus now also includes `stdlib-2to-r-2r-from-roundtrip`, `stdlib-2r-fetch-preserves-pair-on-return-stack`, and `stdlib-2r-fetch-keeps-return-stack-depth`, making one more tiny standard-shaped pair-return-stack slice explicit for future hosts.
