# REV0346 — recorder-drift visibility in the warm control plane

Revision 0346 tightens the X11/i3-first, private-LLM-friendly control plane around one practical authoring problem: recorder evidence drift.

## What changed

- added recorder-side freshness/drift status to `macro_source_json` and `macro_recording_json`
- rolled recorder-side counts into `macro_inventory_json` so the project surface shows how many macros have aligned, stale, or newer-than-source sidecars
- extended generated `stack_state_json.sh` / `stack_state.sh` so the fused warm-runtime surface carries recorder-drift counts for operators and a private LLM
- kept the change X11/i3-first and resident-runtime-oriented: no new broad Linux abstraction layer, no extra Wayland-first detour

## Why it matters

Recorded selectors and window segments are most useful immediately after capture, cleanup, and retime. Once the YAML source drifts ahead of the sidecar, a private LLM or human operator needs to know that the recorder evidence is advisory rather than current truth. REV0346 makes that explicit in the generated control plane instead of leaving it implicit in file mtimes.
