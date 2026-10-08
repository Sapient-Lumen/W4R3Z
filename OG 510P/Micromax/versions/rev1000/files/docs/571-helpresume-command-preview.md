# Rev630: `helpresume` command preview tells the truth before Enter

## Why

Micromax already kept dormant docs-session recovery honest after Enter: `helpresume` reopened the exact off-screen help target when it was still resolvable and failed in typed ways when it was already active, missing, or absent. But the command-bar row still flattened that same state back to generic command metadata right before execution. That made the smallest recovery loop less trustworthy than neighboring `helpback` / `helpforward` previews even though the editor already knew the answer.

## What changed

- added `_helpresume_preview_summary()` as one tiny shared witness for plain `helpresume`
- exact command-bar completion for `helpresume` now previews one of:
  - `resume TOPIC @ line:col`
  - `already active: TOPIC @ line:col`
  - `missing doc: TOPIC`
  - `no session help target`
- added focused prompt tests for dormant, active, missing, and empty-session states

## Why it matters

This keeps docs-session recovery in the same trust-first dialect as the other help-browser previews: Micromax should say what it is actually about to reopen, or why it cannot, before the user presses Enter. That makes the archive easier for future humans and LLMs to inspect because the exact local replay state is visible through one tiny deterministic row instead of hidden behind static prose.
