# Dormant current help target + explicit `helpresume`

Rev405 already made docs history reviewable through `helphistory` and
`ed.helphistory-rows`, but one small seam still remained: once the user left a
docs buffer, Micromax still knew enough to resume the current help page yet its
inspectable summary degraded toward a generic `help -> ...` shape.

Rev406 keeps that seam small and session-honest instead of inventing
persistence:

- leaving or closing a docs buffer now preserves one session-local current help target
- `status_model()` / `help_navigation_model()` expose that dormant target through
  `help_navigation_active`, `help_navigation_dormant`, `help_session_*`, and
  `help_resume_*`
- `helphistory` / `help_history_rows()` / `ed.helphistory-rows` now show a first
  `dormant` row when the current docs target exists off-screen
- plain `helpresume` / `ed.help-resume` reopen that dormant target without
  consuming `helpback` / `helpforward` history
- if the remembered dormant target disappears before replay, the miss stays in the
  same typed dialect as the status warning: `helpresume: missing doc: TOPIC`

The goal is simple: local docs state should stay witnessable and explicitly
resumable even when it is no longer the active buffer.
