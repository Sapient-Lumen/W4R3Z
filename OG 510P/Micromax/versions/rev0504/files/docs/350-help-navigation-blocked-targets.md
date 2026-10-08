# Help navigation blocked targets

Micromax already had the right local docs-history machinery by rev407:

- exact topic + cursor history entries
- separate back and forward stacks
- same-page retrace for explicit `helpjump` / fragment follow moves
- a tiny plain `helphistory` register
- an explicit dormant-session `helpresume` path
- exact `help_actions` cues on the plainest headless surface

But one small split-truth seam still lingered.

Rev402 intentionally kept stale missing-doc history/session targets on the local stacks until they actually reopened, which was the right trust move. Yet rev407 still advertised `helpresume`, `helpback`, or `helpforward` anywhere a remembered target existed, even when that target no longer resolved and the command would fail immediately. Rev408 fixed the inspectable model first; rev415 closes the matching command seam by keeping those misses in the same typed `helpresume:` / `helpback:` / `helpforward:` dialect instead of falling back to generic `help docs:` wording.

Rev408 keeps the follow-up deliberately small:

- `help_session_available`, `help_back_count`, and `help_forward_count` still witness remembered local state even when the target doc is gone
- `help_resume_available`, `help_back_available`, and `help_forward_available` now mean *replayable right now*, not merely remembered
- `help_resume_command`, `help_back_command`, `help_forward_command`, and ordered `help_navigation_actions` now only appear for resolvable targets
- `help_resume_warning`, `help_back_warning`, `help_forward_warning`, and `help_navigation_warning_summary` name blocked missing-doc replay paths explicitly
- `help_navigation_summary`, `showstatus`, and `helphistory` now mark stale replay targets as `[missing]` instead of flattening them into ordinary actionable rows
- `help_history_rows()` / `ed.helphistory-rows` gain one tiny trailing state cell (`active`, `ready`, `missing`) so scripts and future UIs do not have to rediscover that split by probing commands

The goal is not to invent a richer help browser.
The goal is simply to keep remembered local docs state witnessable without letting remembered targets masquerade as actionable replay paths.
