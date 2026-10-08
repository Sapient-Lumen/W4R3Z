# Revision 0347 — next-action review queue and recorder debt triage

Revision 0347 strengthens the resident i3/X11 control plane instead of broadening Linux scope:

- `next_action_json.sh` now consumes macro inventory and latest-run health in addition to runtime/prereq checks
- added `macro_review_queue` buckets to the next-action payload so operators and a private LLM can see stale recorder sidecars, recorder evidence newer than source, exact-selector segments, and title-bound segments without stitching helper calls together
- upgraded primary-action selection so healthy runtime states can still point at recorder/cleanup debt, while latest-run failures still take precedence over macro hygiene work
- `next_action.sh` now prints concise queue summaries for those recorder-review buckets
- tightened stack docs and issue tracking so recorder review debt is explicit product truth in the warm control plane
