# Active help page vs actionable `helpresume`

The comparison datacubes kept repeating one small trust rule in different
language: **remembered state is not the same thing as actionable state**.

Micromax already applied that split to stale missing docs targets in rev408:
`help_session_available`, `help_back_count`, and `help_forward_count` kept
witnessing remembered local history, while `help_*_available`,
`help_*_command`, and `help_actions=` stopped pretending blocked replay
commands still worked.

One active-state seam still remained, though. When the current help page was
already on-screen, `status_model()` still set `help_resume_available = 1`
simply because the session-local current target existed and resolved, even
though `helpresume` itself was not actionable there and `help_resume_command`
was intentionally blank.

Rev413 closes that tiny split-truth gap:

- `help_session_*` still witness the session-local current help target
- `help_resume_target` / `help_resume_title` / `help_resume_position` still
  describe the dormant replay destination when one exists
- but `help_resume_available` is now `1` **only** when `helpresume` is
  actually actionable right now: the current docs target is dormant and still
  resolves locally

That keeps the tiny docs-navigation model honest for humans, scripts, tests,
future UIs, and future LLMs: the session head may still exist while the resume
command is correctly unavailable because there is nothing off-screen to resume.
