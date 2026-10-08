# Archived TODO-through-rev0951

This file preserves the rev0951 root TODO handoff block. The current TODO was compacted in rev0952 so the live handoff leads with the product-facing authority repair; older history remains in `docs/history/TODO-through-rev0950.md`.

---

Rev0951 note: mxtimely summaries now distinguish partial prefixes from completed lanes, and mxaudit hard-checks completion-honest summary evidence.

Latest tiny landing (rev0951): `tools/mxtimely.py` writes v3 summary JSON with `status`, `complete`, `planned_steps`, and `pending_steps`; interrupted cloudtainer prefixes now leave `ok: false` / `status: partial` instead of a success claim. `tests/test_mxtimely.py` pins the completed and interrupted cases, `mxaudit --check` reports `timely_summary_completion_honest`, and the old TODO trail is archived at `docs/history/TODO-through-rev0950.md` to keep the live handoff small.

# TODO (rev0951)

- [x] read the archive deeply as a product/mission system, not just a code tree.
- [x] research current resource-timeout, workspace-trust, WASI, Starlark, WIT, and SLSA guidance and apply it to the cloudtainer diagnosis.
- [x] reproduce the waste/failure mode where an outer-stopped timely lane left a fresh but over-optimistic summary prefix.
- [x] change `mxtimely` summary JSON to carry planned-step completion evidence and mark incomplete prefixes partial.
- [x] add focused tests for completed summaries and interrupted prefixes.
- [x] extend `mxaudit --check` with `timely_summary_completion_honest`.
- [x] archive the old TODO trail through rev0950 to keep the current living TODO under budget.
- [x] record the landing in `docs/909-timely-summary-completion-honesty.md`.
- [x] package rev0951 with the required filename structure.

## Landed this revision

- Added `micromax.mxtimely.summary.v3` with `status`, `complete`, `planned_steps`, `planned_step_count`, `completed_steps`, and `pending_steps`.
- Made incremental summary writes pass the full planned step list so an outer cloudtainer/tooltimer stop after a successful prefix cannot claim `ok: true`.
- Added mxtimely regressions for complete and interrupted summary semantics.
- Added `timely_summary_completion_honest` to release-hygiene audit checks and human output.
- Added a deep heart/gap/waste audit and validation notes in `docs/909-timely-summary-completion-honesty.md`.
- Archived the old root TODO body through rev0950 into `docs/history/TODO-through-rev0950.md` and kept this live TODO compact.

## Next up (high leverage)

1. Add an actual-summary verifier that reads `.artifacts/mxtimely-summary.json` and classifies full pass, skip-doctor pass, failure, or partial prefix.
2. Compact duplicated owner-row validation helpers in `effect_contracts.py` only after tests pin the shared behavior.
3. Decide whether successful plugin option and mark writes need explicit ownership or should stay committed editor effects.
4. Choose the next runtime survivor by concrete retained authority, rollback failure, or stale disclosure; avoid registry-completeness work.
5. Keep release locks/CI/signatures deferred until there is a real package or binary lane to protect.
