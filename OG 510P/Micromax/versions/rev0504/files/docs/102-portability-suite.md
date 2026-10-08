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

Rev273 note: the JSON portability corpus now also covers cleanup-error precedence for `ensure` / `finally`, so future Python/Rust/WASM hosts can replay the rule that a failing cleanup quotation replaces the original body result or body error while still preserving the correct visible stack shape.

Latest tiny landing (rev273): the JSON portability corpus now covers both success-path and failure-path cleanup-error precedence for `ensure` / `finally`, including the alias behavior of `finally`. The handoff note is `docs/215-portability-cleanup-error-precedence.md`, and the focused coverage lives in `tests/test_portability_suite.py`, `tests/test_vm_rev11.py`, `tests/test_ensure_finally.py`, and `tests/test_mxcontext.py`.

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

Latest tiny landing (rev253): the JSON portability corpus now also covers tiny boot-stdlib `2rdrop` behavior, so future Python/Rust/WASM hosts can replay one more small pair-return-stack cleanup slice from JSON alone. The handoff note is `docs/195-portability-2rdrop.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev252 note: the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck` behavior, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev252): the JSON portability corpus now also covers tiny boot-stdlib `2nip` / `2tuck` behavior, so future Python/Rust/WASM hosts can replay one more small pair-stack convenience slice from JSON alone. The handoff note is `docs/194-portability-2nip-2tuck.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev251 note: the JSON portability corpus now also covers tiny boot-stdlib `2>r` / `2r>` / `2r@` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-return-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev251): the JSON portability corpus now also covers tiny boot-stdlib `2>r` / `2r>` / `2r@` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-return-stack slice from JSON alone. The handoff note is `docs/193-portability-2returnstack-pairs.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev250 note: the JSON portability corpus now also covers tiny boot-stdlib `2rot` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack rotation slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev249 note: the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev248 note: the JSON portability corpus now also covers tiny boot-stdlib `2*` / `2/` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped shift/arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Latest tiny landing (rev250): the JSON portability corpus now also covers tiny boot-stdlib `2rot` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack rotation slice from JSON alone. The handoff note is `docs/192-portability-2rot.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Latest tiny landing (rev249): the JSON portability corpus now also covers tiny boot-stdlib `2over` / `2swap` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped pair-stack slice from JSON alone. The handoff note is `docs/191-portability-2over-2swap.md`, and the focused coverage lives in `tests/test_portability_suite.py` and `tests/test_vm_rev11.py`.

Rev247 note: the JSON portability corpus now also covers tiny boot-stdlib `1+`, `1-`, `0>`, and `0<>` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic/predicate slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev246 note: the JSON portability corpus now also covers tiny boot-stdlib `max` / `min` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev245 note: the JSON portability corpus now also covers tiny boot-stdlib `negate`, `0<`, and `abs` behavior, so future Python/Rust/WASM hosts can replay one more small standard-shaped arithmetic slice from JSON alone instead of inferring it from `core.mx` or ad hoc tests.

Rev243 note: the JSON portability corpus now also makes the `pick` / `roll` failure edges replayable — negative indices now have explicit `u must be >= 0` contracts and too-shallow stacks now expect `Stack underflow` — so future Python/Rust/WASM hosts do not have to guess how Micromax resolves the Forth standard's ambiguous out-of-range cases.

Rev242 note: the kernel portability corpus now also pins down five-item `pick` / `roll` indexing (`4 pick`, `4 roll`) so future Python/Rust/WASM hosts can replay one more deeper stack-shuffle slice from JSON alone.

*Rev241 note:* the kernel corpus now also includes `pick-three-copies-fourth-item` and `roll-three-rotates-four-items`, extending the small `stack-shuffle` slice from named shallow equivalences to one more general four-item indexing/rotation point for future hosts.

*Rev240 note:* the corpus now also includes two adjacent `pick` / `roll` indexing edge cases — `0 roll` as a null op and `2 pick` copying the third stack item — making one more tiny stack-shuffle slice replayable for future Rust/WASM hosts.

*Rev239 note:* the corpus now also includes four tiny stack-shuffle cases for `pick` / `roll` (`0 pick`=`dup`, `1 pick`=`over`, `1 roll`=`swap`, `2 roll`=`rot`), making one more easy-to-misindex kernel slice replayable for future Rust/WASM hosts.

*Rev222 note:* the kernel corpus now also includes `nested-catch-success-preserves-outer-visible-return-stack-value`, which makes the nested success-path exception contract a little more explicit for future hosts: once control returns to the outer protected region, an outer user-pushed return-stack item should still be observable through `r@` as well as `r>`.

*Rev221 note:* the kernel corpus now also includes `nested-catch-throw-preserves-outer-visible-return-stack-value`, which makes the nested exception contract a little more explicit for future hosts: once control returns to the outer protected region, an outer user-pushed return-stack item should still be observable through `r@` as well as `r>`.

*Rev220 note:* the kernel corpus now also includes `nested-catch-throw-counts-only-outer-user-return-stack-items`, which makes the nested exception contract a little more explicit for future hosts: after an inner `throw` is caught and control returns to the outer protected region, visible `rdepth` should count only outer user-pushed items.

Rev215 note: the JSON portability corpus now also pins down that `catch`/`throw` preserve the order of outer user-pushed return-stack items, not just their depth or one surviving value.

# Portability suite

Rev213 note: the corpus now includes `nested-catch-throw-preserves-outer-user-return-stack-item`, a small nested-recovery case proving that an inner `throw` inside a successful outer `catch` still preserves outer user-owned `>r` state.

Micromax now ships a tiny **JSON portability corpus** for the parts of the language we expect future Rust/WASM hosts to preserve exactly.

Artifacts:
- corpus: `portability/kernel_cases.json`
- runner: `src/micromax/portability_suite.py`
- CLI: `tools/mxportable.py`
- tests: `tests/test_portability_suite.py`

## Why this exists

The ordinary pytest suite is still the main test harness, but it is Python-shaped: it imports helpers, reaches into objects directly, and sometimes validates reference-only tooling behavior.

For portability work, that is heavier than necessary. A future host should be able to load a tiny data file, execute snippets, and compare stacks/errors to the Python reference VM.

## Corpus shape

Each case is a JSON object like:

```json
{
  "name": "int-add",
  "category": "kernel",
  "source": "1 2 +",
  "expect_stack": [3]
}
```

Or, for expected failures:

```json
{
  "name": "uncaught-stack-underflow",
  "category": "kernel",
  "source": "1 drop drop",
  "expect_error_contains": "Stack underflow"
}
```

The corpus intentionally stays small and data-only:
- source text
- category
- optional tags
- optional `host_features` seed list for host-boundary probes
- expected final stack, expected error substring, and optionally a post-error stack snapshot when cleanup/rethrow behavior matters
- broad but simple optional tags for sliceable bring-up work (`memory`, `locals`, `namespaces`, `combinators`, ...)
- enough namespace/search-order coverage to teach future hosts the difference between search order and compilation wordlist (for example `definitions` persistence and `set-current` not making a wordlist searchable by itself)
- no host-specific side effects
- no opaque runtime objects in expected values

The loader also now fails fast on:
- duplicate case names
- missing categories / source text
- malformed cases that specify neither a stack expectation nor an error expectation
- non-portable expected values

## Running it

From the repo root:

```bash
PYTHONPATH=src python tools/mxportable.py
```

You can also point the runner at another corpus file:

```bash
PYTHONPATH=src python tools/mxportable.py path/to/cases.json
```

And you can inspect or run targeted slices during bring-up work:

```bash
PYTHONPATH=src python tools/mxportable.py --list --category kernel
PYTHONPATH=src python tools/mxportable.py --tag namespaces
PYTHONPATH=src python tools/mxportable.py --name set-current-roundtrip --name map-keys-return-sorted-list
PYTHONPATH=src python tools/mxportable.py --name-contains recover
PYTHONPATH=src python tools/mxportable.py --tag memory --json
PYTHONPATH=src python tools/mxportable.py --tag memory --inventory
PYTHONPATH=src python tools/mxportable.py --tag memory --inventory --json
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word try --word ensure
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word-contains try --json
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-source
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word bi --show-deps
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word finally --show-closure
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word finally --show-source --show-deps --show-closure --json
```

## What belongs here

Good corpus candidates:
- portable kernel words
- boot stdlib combinators we expect every serious host to ship
- stable error behavior that future hosts should mirror closely enough for tooling

The current corpus now covers not just kernel basics, but also a few real boot-stdlib/safety behaviors Micromax actually leans on: `0=`, tiny boot-stdlib arithmetic/predicate helpers (`1+`, `1-`, `0>`, `0<>`, `?dup`, `negate`, `0<`, `abs`, `max`, `min`) plus tiny pair-stack helpers (`2over`, `2swap`), successful and failing `catch`, `while`, `when`, return-stack basics, `execute`, `constant`, `variable`, list clone/pop isolation, `to-int`, `to-str`, map inspection/mutation (`m@` missing=>`0`, `m-del` missing=>no-op for existing pairs, `m-keys`, `m-items`, `m-del`, `m-merge`), locals shadowing plus session-local query/removal, wordlist/search-order lookup plus duplicate-name precedence both across wordlists and within one wordlist, `set-current`, `in`, `dict-version` bump/stability cases (including `find`, `get-order`, `get-current`, `host.api-version`, and `host.features` lookup-only stability), positive + missing `host.feature?`, including missing-`host.feature?` lookup-only `dict-version` stability, bare-VM and seeded `host.features` (including duplicate-seed deduplication while staying sorted), quotation combinators (`bi`, `dip`, `keep`, `2dip`, `2keep`, `tri`), recovery/cleanup aliases (`try?`, `try`, `recover`, `ensure`, `finally`), explicit `rdrop` helper cases, and budget exhaustion observed through `catch`.

When you need machine-readable output during bring-up, `mxportable --json` now emits selected case records plus summary/result metadata instead of only human text. When you need a lighter-weight view of what a slice covers, `mxportable --inventory` / `--inventory --json` report matching categories, tags, and case names without the full case bodies. And when you need *precise* replay of one or two known behaviors, repeatable `--name` filters now avoid fuzzy substring matching entirely. Rev275 also makes the boot-stdlib coverage map itself inspectable: `mxportable --stdlib-manifest` shows which explicit portability case names belong to each tiny stdlib word, and the same view can be filtered by exact `--word` matches or `--word-contains` plus JSON output. Rev276 adds optional source-aware handoff on top: `--show-source` surfaces the matching `core.mx` line, stack-effect comment, and normalized definition text for the selected boot-stdlib words. Rev277 adds one more tiny machine-readable layer on top of that: `--show-deps` surfaces tokenized word references, stdlib-vs-nonstdlib dependencies, and simple aliases like `finally -> ensure`. Rev278 adds the next tiny bring-up-oriented layer: `--show-closure` surfaces dependency order, transitive stdlib refs, transitive nonstdlib refs, and a small stdlib depth so future ports can see the real prerequisites hidden behind aliases and composite words like `finally`, `recover`, and `bi`. Rev279/280/281 keep the same thread moving forward without widening the default output: `--show-users` names reverse stdlib dependents, `--show-impact` names the impacted words/cases after a change, and the selected-slice `impact_summary` now also carries exact `retest_command` / `retest_json_command` strings so a focused replay command is copy-pasteable instead of reconstructed by hand. Rev282/283/284/285 keep the same thread small but more descriptive and executable: the same impact slice can now also carry joined category/tag inventories, grouped impacted-word provenance, exact per-group replay metadata in both shell-command and structured env/argv form, and a root-first staged replay plan keyed by shortest impact distance. Rev286/287/288/289/290/291/292/293/294/295/296/297/298/299/300 keep refining the same inspectable handoff instead of widening it: the same impact slice can now be filtered by exact impacted word/depth/case metadata, can expose valid next-step structural and semantic facets, can attach exact filter fragments plus full slice commands, can say whether a facet replaces or appends within its family, can preview the resulting slice size, can explicitly mark whether a visible facet is a `same-slice` no-op or a real narrowing with signed delta metadata, and can now recommend, dedupe, group, explain, and rank-cover distinct representative cuts without forcing humans or future LLMs to jump back to the original ranked shortlist.

Bad corpus candidates:
- editor hostcalls
- filesystem / shell / clipboard integration
- debug-only object identity details
- anything whose result shape depends on Python internals

## Maintenance rule of thumb

When you add or change **portable** VM behavior:
1. update `docs/42-portability-ledger.md` if the contract changed
2. add focused pytest coverage
3. add or update a portability corpus case when the behavior is part of the portable kernel / boot stdlib


Recent additions: `catch-throw-preserves-outer-user-return-stack-items` now also pins down that an inner `throw` restores only the protected return-stack depth, preserving outer user-pushed `>r` items across recovery.

Recent additions: `catch-throw-preserves-outer-return-stack-value` now also pins down that the surviving outer `>r` item keeps its original value, not just its visible depth count.

Recent additions: `catch-success-counts-only-user-return-stack-items` now also pins down that visible `rdepth` inside a successful `catch` counts only user-pushed `>r` items, not hidden exception-frame bookkeeping.

Recent additions: `catch-throw-restores-return-stack-depth` pins down that `catch` trims the return stack back to its entry depth when a protected quotation throws, matching the recovery contract Micromax already wants future Rust/WASM hosts to preserve.

Recent additions: `dict-version-stable-across-host-feature-predicate` and `dict-version-stable-across-missing-host-feature-predicate` pin down that `host.feature?` stays lookup-only with respect to dictionary/search-order cache invalidation whether the feature is present or absent.
Another tiny recent case, `return-stack-peek-and-depth`, pins down that `r@` peeks without consuming and that `rdepth` reflects the resulting return-stack depth.

Another tiny recent case, `return-stack-lifo-peek-roundtrip`, now also pins down a legal two-item LIFO return-stack pattern: after `>r >r`, `r@` sees the most recently pushed item, `r> r>` restores those values in LIFO order, and `rdepth` returns to zero.



Recent additions: `map-fetch-missing-returns-zero` pins down that `m@` returns `0` for missing keys, matching the contract Micromax already documents and tests elsewhere.

Recent additions: `map-delete-missing-preserves-existing-pairs` pins down that `m-del` is a no-op for existing entries when the requested key is absent.

Recent additions: `map-keys-empty-map-returns-empty-list` pins down that `m-keys` returns `[]` for an empty map rather than a sentinel or error.



## rev200 follow-up

The corpus now also includes `map-items-empty-map-returns-empty-list`, pinning down that `m-items` on an empty map yields `[]` rather than a host-shaped null/zero sentinel.

Recent additions: `map-merge-empty-source-preserves-destination` pins down that `m-merge` is a no-op for existing destination pairs when the source map is empty.


Recent tiny corpus additions include empty-map edge cases such as `map-merge-empty-source-preserves-destination` and now `map-merge-empty-destination-adopts-source`, so future hosts can validate both sides of the merge contract from JSON alone.


Recent additions: `map-has-missing-key-is-false` pins down that `m?` returns `0` for an absent key rather than a host-shaped sentinel or error.


Recent additions: `map-store-overwrite-updates-value` pins down that `m!` overwrites an existing key's value rather than creating host-shaped duplicate entries.


Rev210 follow-up: the corpus now also includes `catch-success-hides-exception-frame-from-rdepth`, a tiny recovery/return-stack contract that keeps successful protected execution from exposing internal exception-frame bookkeeping through Micromax's visible `rdepth` word.


- rev218 adds `nested-catch-throw-preserves-outer-return-stack-order`, extending the recent return-stack recovery thread to the nested-throw case.
