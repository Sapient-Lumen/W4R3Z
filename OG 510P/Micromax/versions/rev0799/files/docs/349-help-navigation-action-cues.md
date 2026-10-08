# Help navigation action cues

Micromax already had the right local docs-history machinery by rev406:

- exact topic + cursor history entries
- separate back and forward stacks
- same-page retrace for explicit `helpjump` / fragment follow moves
- a tiny plain `helphistory` register
- an explicit dormant-session `helpresume` path

But one small seam still lingered on the plainest surface.

`status_model()` and `helphistory` could already tell a caller that dormant/back/forward state existed, but the smallest human/headless summary (`showstatus` / `ed.status-summary`) still forced users, scripts, and future UIs/LLMs to translate that state back into exact commands by hand.

Rev407 keeps the follow-up deliberately small:

- `help_resume_command` is now `helpresume` only when the dormant target is actually actionable
- `help_back_command` is now `helpback` only when a back target exists
- `help_forward_command` is now `helpforward` only when a forward target exists
- `help_navigation_actions` keeps those commands in current action order
- `help_navigation_action_summary` gives a tiny comma-joined plain-text cue
- `status_summary()` / `showstatus` now surface those cues as `help_nav='...'` and `help_actions='...'`

The goal is not to invent a richer help browser.
The goal is simply to keep the last recovery step explicit: if local docs state is resumable or replayable, Micromax should name the exact command instead of making that translation implicit.
