# Rev815 — hook register read/fire authority

Rev815 closes the riskiest remaining hook-register gap in the protected-register lane.

## Failure mode

The command/key/macro/mark/plugin inventory work had already moved many long-lived editor registers onto runtime authority checks, but hooks still had two dangerous edges:

1. hook handler metadata could be exposed through hook rows, groups, prompt previews, `showhook`, and the core VM hook-inspection words;
2. a lower-authority script could explicitly execute a hook word and cause trusted/user hook handlers to run as a delayed callback path.

The second issue is the more severe one. Hook handlers are executable registry state. Even if they are intended as notifications, firing a trusted handler from script context can replay side effects that the script did not own.

## Changes

New policy seam:

- `src/micromax_editor/hook_policy.py`

New capability:

- `cap.hook-fire` / `ed.hook-fire`

Existing/finished capability:

- `cap.hook-read` / `ed.hook-read`

The final model is:

- hook names are public event/API names, so completion and `hooks` discovery remain useful;
- handler names, groups, source spans, and per-hook counts are filtered by runtime authority;
- same-origin script/plugin handlers remain visible and runnable;
- protected trusted/user or other-origin handler metadata requires `cap.hook-read`;
- protected handler execution requires `cap.hook-fire`;
- `hook@` uses the fire policy, not just the read policy, because it returns executable tokens;
- enabling `cap.hook-fire` does not make the caller trusted. Protected handlers run under the caller script context or the handler's captured script/plugin callback context.

The low-level VM hook execution path now asks the editor to filter handlers before running a hook word. That keeps command-bar `showhook` rows, bridge hostcalls, core VM `hook-detail`/`hook-rows`/`hook-groups`, and direct hook-word execution aligned to one policy.

## Corrections made during this pass

While finishing the seam, I found that the previous partial hook-read work had left a latent import/policy alias gap. `editor.py` imported a generic hook policy helper that was not present in the packaged source. Rev815 supplies that policy module and tests it through the editor path.

I also tightened `hook@`: read authority alone is not enough, because the returned objects are executable tokens. A script with only `cap.hook-read` may inspect protected handler metadata, but it still cannot fetch and execute protected handlers through `hook@` unless `cap.hook-fire` is enabled.

A small display bug was fixed too: hook rows with group `0` no longer render as `handler#0` in exact/detail summaries.

## Remaining risk

VM word and action dictionary discovery are still the main adjacent public-vs-protected decision. Hooks now have explicit semantics: event names are public, handler metadata/execution is protected. The next audit should give visible VM words and action details the same explicit treatment rather than leaving their publicness accidental.

Full-suite confidence still depends on a complete chunked `mxtest` aggregate manifest.

## Validation

Focused hook authority tests cover:

- script-origin hook inventory hiding trusted handlers while preserving public hook names;
- `cap.hook-read` revealing protected handler metadata;
- same-origin script hooks remaining visible and runnable;
- independent script origins being unable to inspect or fire one another's handlers;
- script-origin hook execution skipping trusted handlers by default;
- `cap.hook-read` not granting execution;
- `cap.hook-fire` allowing explicit protected execution under script authority;
- core VM `hook-detail`, `hook-rows`, `hook-groups`, and `hook@` using the same boundaries.
