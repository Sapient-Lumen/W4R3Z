# Archived LLM start guide through rev0951

Preserved before the rev0952 living-document compaction.

---

Rev0951 note: mxtimely summaries now distinguish partial prefixes from completed lanes, and mxaudit hard-checks completion-honest summary evidence.

# LLM start here (rev0951)

## Heart of the project

Micromax is a least-authority automation language with a recoverable editor host.
The small concatenative VM is intended to be one substrate for configuration,
macros, and plugins. The editor is the proving ground for explicit effects,
capability checks, provenance, bounded host work, headless truth, honest recovery,
and taste/trust/flow.

Do not reduce the mission to “build a terminal editor.” Do not describe the
current in-process capability model as a hostile-code sandbox.

The shortest useful mission phrase is:

> powerful end-user programmability with explicit effects, visible provenance,
> recoverable failure, bounded host work, and headless truth.

## Current landing

Rev0951 records the deep cloudtainer heart/gap/waste read in
`docs/909-timely-summary-completion-honesty.md` and fixes an evidence truth bug:
`tools/mxtimely.py` summary JSON is now v3 with `status`, `complete`,
`planned_steps`, and `pending_steps`. A stopped lane that completed only a prefix
now leaves `status: partial`, `complete: false`, and `ok: false`; completed
planned lanes still report `status: passed`. `mxaudit --check` enforces
`timely_summary_completion_honest`, and the old root TODO trail through rev0950
is archived under `docs/history/TODO-through-rev0950.md`.

Rev0950 moves named mark rollback behind a public editor-owned owner seam.
`MarkRegisterEntry` / `MarkRegisterSnapshot` capture named marks plus
`RuntimeRegistrationAuthority` sidecars; `Editor.snapshot_mark_group_state` /
`Editor.restore_mark_group_state` are now the preferred group and broad rollback
route before legacy alternate-embedder fallback. The generated effect/resource
contract includes `ed.mark-register`, and `mxaudit --check` enforces
`mark_owner_snapshot_present`. The revision note is
`docs/908-mark-owner-contract.md`. The audit/refactor also removed a duplicate
recent-files group-restore call from `restore_runtime_group_state`.

Rev0949 moved failed plugin option rollback behind a public editor-owned owner
seam. `Editor.snapshot_option_state` / `Editor.restore_option_state` wrap the
existing global and buffer-local `OptionStateSnapshot` machinery;
`plugin_runtime.py` uses those methods for broad failed source/lifecycle
registration restore and scoped plugin callback rollback before legacy
alternate-embedder fallback. The generated effect/resource contract includes
`ed.option-state-register`, and `mxaudit --check` enforces
`option_state_owner_snapshot_present`. The revision note is
`docs/907-option-state-owner-contract.md`.

Rev0948 made the generated effect/resource contract a product-visible installed
help page. `docs/33-effect-resource-contract.md` is generated from the live
contract payload; `tools/mxeffects.py` can emit, write, and stale-check the
markdown; `mxaudit --check` fails if that generated help page is missing,
uninstalled, or stale. This closed the prior gap where the contract was
executable but mostly visible only through tools and revision notes. The
revision note is `docs/906-effect-contract-installed-help.md`.

Rev0947 moved selection-stack and jump-list recovery rows from raw buffer
`sel_stack` / `jump_list` rewrites into an editor-owned owner seam.
`RecoveryRegisterEntry`, `RecoveryBufferRegisterSnapshot`, and
`RecoveryRegisterSnapshot` capture retained cursor/selection recovery rows plus
`RuntimeRegistrationAuthority`; `plugin_runtime.py` now calls
`Editor.snapshot_recovery_*` / `restore_recovery_*` for group cleanup,
generation cleanup, and broad registration restore before using
alternate-embedder legacy fallbacks. The generated contract includes the
`ed.recovery-register` owner row, and `mxaudit --check` enforces
`recovery_owner_snapshot_present`. The revision note is
`docs/905-recovery-owner-contract.md`.

Rev0946 moved help-history rows from raw help back/forward/session stacks into
an editor-owned owner seam and generated the `ed.help-history-register` owner
row in `docs/904-help-history-owner-contract.md`.

Rev0945 moved command-palette recent rows from raw runtime list/authority sidecar
rewrites into an editor-owned owner seam and generated the
`ed.palette-recent-register` owner row in
`docs/903-palette-recent-owner-contract.md`.

Rev0944 moved saved cursors from raw runtime dictionary/authority sidecar
rewrites into an editor-owned owner seam and generated the
`ed.saved-cursor-register` owner row in
`docs/902-saved-cursor-owner-contract.md`.

Rev0943 moved recent files from raw runtime list/authority sidecar rewrites into
an editor-owned owner seam and generated the `ed.recent-files-register` owner
row in `docs/901-recent-files-owner-contract.md`.

Rev0942 moved prompt history from raw runtime dictionary/authority sidecar
rewrites into an editor-owned owner seam and generated the
`ed.prompt-history-register` owner row in
`docs/900-prompt-history-owner-contract.md`.

Rev0941 moved active search from an ambient runtime tuple into an editor-owned
owner seam and generated the `ed.active-search-register` owner row in
`docs/899-active-search-owner-contract.md`.

Rev0940 started the generated effect/resource-contract lane in
`docs/898-generated-effect-resource-contract.md`. It added
`src/micromax_editor/effect_contracts.py`, `tools/mxeffects.py --json --check`,
and the audit-integrity bridge for generated high-risk host-effect rows.

Rev0939 was a cloudtainer sequencing correction. It recorded the deep-read
mission/gap/waste audit in `docs/897-cloudtainer-entrypoint-freshness-audit.md`,
refreshed stale curated handoff entrypoints, and made `mxaudit --check` fail if
`README.md`, `TODO.md`, `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, or
`docs/43-worklist.md` point at a stale revision.

The current runtime state remains the rev09xx resource-boundary sequence:
script-visible and editor filesystem reads/lists/stats/open/source/help paths,
regex hostcalls, shell/external clipboard helpers, source loading, prompt scans,
atomic writes, save preflights, docs catalog scans, plugin discovery, project-root
marker grouping, help-doc reads, plugin metadata existence, prompt path
completion, bundled stdlib startup, canceled timer lifetime, query-replace all
responses, pending external-URL confirmation rollback, query-replace rollback,
prompt rollback, keymode rollback, broad failed-callback interaction rollback,
clipboard broad/group/generation rollback, macro generation rollback,
active-search group/generation/broad rollback, prompt-history
group/generation/broad rollback, recent-files group/generation/broad rollback, saved-cursor
group/generation/broad rollback, palette-recent group/generation/broad
rollback, help-history group/generation/broad rollback, recovery
group/generation/broad rollback, failed option source/lifecycle/callback
rollback, and mark group/broad rollback have named
contained/budgeted/provenance or owner seams. Rev0941 added the first generated
owner row, rev0942 added the retained replay-history row, rev0943 added the
retained path-history row, rev0944 added the retained path+position row, rev0945 added the retained
command/action launch row, rev0946 added retained help-navigation authority,
rev0947 added retained cursor/selection recovery authority, rev0948 rendered the generated contract as installed help, rev0949 added
configuration/capability option rollback authority, rev0950 adds named mark buffer+position authority, and rev0951 makes cloudtainer summary evidence completion-honest on top of the
machine-readable contract slice over the highest-risk effect subset. These are application-level guardrails, not
hostile-code containment.

## Highest-leverage next work

1. Compact duplicated owner-row validation helpers in `effect_contracts.py` only
   after tests pin the shared behavior.
2. Decide whether successful plugin option writes need explicit ownership or
   should stay committed configuration effects.
3. Pick the next runtime survivor by concrete stale lifetime, authority clobber,
   retained disclosure, or rollback failure; do not add a broad ownership registry first.
4. Keep expanding generated owner rows only when live owner methods and focused route tests can supply facts.
5. Keep release locks, CI, signatures, and SLSA-like provenance deferred until
   there is a real package or binary lane to protect.
6. Keep short-window validation honest by splitting selected commands instead of
   claiming timed-out combined runs as passes.

## Avoid

- another sidecar-specific rollback patch without placing the sidecar under an
  owning lifecycle contract;
- a universal untyped ownership registry;
- broad `Editor` rewrites;
- treating more revision notes or evidence-runner features as product progress
  unless they remove real stale/failing handoff evidence;
- letting curated entrypoints lag behind the archive revision;
- claiming that timely, `release-next`, or partial release-suite evidence is a
  complete full-release claim;
- claiming snapshots cover arbitrary edits, durable/external effects, wall-clock
  blocking, memory pressure, native code, or hostile code;
- moving the current implicit internal API wholesale into a process or Wasm
  boundary.
