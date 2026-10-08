# 741 With-undo all-buffer transaction, runtime hostcall preflight, and doctor batch control

Rev0784 focuses on two trust problems that were more dangerous than another registry pass: a real cross-buffer rollback bug in `ed.with-undo`, and mutation/deferred hostcalls that still consumed VM-stack evidence before authority checks.

## Severe bug fixed: `ed.with-undo` was only active-buffer transactional

Before this revision, `ed.with-undo` snapshotted only the active buffer. A quotation could switch to a second buffer with `ed.with-buffer`, edit it, then fail. The active buffer rolled back, but the second buffer kept the edit and dirty/version changes while no grouped undo entry represented that mutation.

Rev0784 reuses the editor's all-open-buffer macro snapshot shape for hostcall transactions. A failing `ed.with-undo` now restores every open buffer, MRU/active buffer state, dirty/fastdirty/version evidence, cursor/selection state, disk witnesses, and undo membership. A successful cross-buffer quotation records one undo entry that restores/redoes the whole transaction.

## Runtime hostcalls now preflight before consuming operands

`src/micromax_editor/hostcall_boundary.py` now includes quotation and execution-token peek helpers, matching the existing string/int/list stack helpers. `src/micromax_editor/micromax_bridge.py` uses peek-then-commit behavior for the highest-risk mutation/deferred hostcalls: key binding, key documentation, unbind, command add/remove, active keymode/group mutation, clipboard mutation, macro get/set/record/play, and `ed.with-buffer` / `ed.with-undo`.

The practical rule is: validate argument shape and runtime authority first, then mutate editor state and delete operands from the VM stack. Denied script attempts to replace trusted commands or keybindings leave their original operands available as failure evidence. Malformed macro/clipboard calls preserve the payload they failed to decode.

## Default doctor is less wasteful

The rev0783 default doctor was safer than the full suite, but one-file-per-pytest-child behavior created excessive interpreter churn in this cloudtainer. Rev0784 adds `MXDOCTOR_PREFLIGHT_GROUP_SIZE` and changes the archive default to grouped bounded preflight children. Operators can still force singleton children with `MXDOCTOR_PREFLIGHT_GROUP_SIZE=1` when bisecting a fragile file.

## Validation evidence

Focused validation covered the new all-buffer `ed.with-undo` rollback/undo behavior, runtime-registration hostcall stack evidence, clipboard/macro argument preservation, active keymode/group denial stack evidence, readonly/state hostcall boundaries, prompt/command completion integration, revision/context/archive guards, and the default bounded doctor lane. A full-suite aggregate pass is still not claimed.

## Remaining risk

Many display/query-only bridge hostcalls still use raw VM pops. They are lower risk than mutation/deferred surfaces, but should continue migrating to the shared stack helpers while the bridge and editor monolith are split.

## Rev0784 validation snapshot

- Focused runtime/with-undo/hostcall/doctor set: 77 passed.
- Prompt/command/core integration set: 140 passed.
- Revision/context guards: 5 passed.
- Archive guard tests: 4 passed.
- Default `python tools/mxdoctor.py`: passed, with four bounded pytest children reporting 106, 109, 50, and 147 tests.
- `tools/mxtest.py --plan --chunks 8 --strategy segment`: 1857 collected tests split into 233, 232, 232, 232, 232, 232, 232, 232.
