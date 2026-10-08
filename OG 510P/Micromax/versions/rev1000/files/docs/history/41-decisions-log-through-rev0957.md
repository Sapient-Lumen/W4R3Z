# Historical snapshot: Decisions log through rev0957

This file preserves `docs/41-decisions-log.md` as received through rev0957. It is not current guidance.

---

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

## rev299 — explain why each distinct representative cut won

**Decision**: keep `mxportable --stdlib-manifest --show-impact` in the same tiny inspectable portability/tooling thread and enrich the distinct shortlist with representative-choice reasons instead of widening into a planner or scheduler.

**Why**: rev298 already made each distinct next cut self-contained by preserving the interchangeable alternatives it absorbed, but a future human or future LLM still had to infer *why* `words:finally` was preferred over `distances:1` or `tags:aliases`. Current Factor docs still expose cross-referencing as an explicit inspectable tool surface, current pytest docs still emphasize exact selection and deselection around concrete node IDs and collection previews, and current micro docs still center direct help/keybinding/plugin surfaces rather than orchestration. So the honest next step was one more tiny explanatory layer, not a planner.

**What changed**:
- added shared `IMPACT_FILTER_FAMILY_PRIORITY` and `impact_filter_option_preference_reason(...)` helpers in `src/micromax/portability_suite.py`
- distinct recommendation rows now carry `representative_reason_code`, `representative_reason`, `represented_alternative_labels`, and `represented_alternative_families`
- grouped distinct recommendation payloads mirror the same representative-reason metadata
- human CLI output now shows compact `why: ...` hints for distinct rows and distinct groups
- added handoff note `docs/241-portability-impact-representative-reasons.md` and refreshed the repo-context breadcrumbs

**Consequence**: future humans and future LLMs can now see both the representative cut and the explicit rationale for why it won, without reverse-engineering family priority from the shortlist ordering.



