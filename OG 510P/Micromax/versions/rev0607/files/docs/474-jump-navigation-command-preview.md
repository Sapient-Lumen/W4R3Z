# Rev532 — preview plain `jumpback` / `jumpforward` targets in command completion

## Why

Micromax's jumplist loop is already fairly truthful once a navigation command has
actually run:

- `jumpback` / `jumpforward` preserve visible `#N [lane depth]` truth on success
- `status_model()` / `showstatus` expose the immediate back/forward targets headlessly
- `showjump INDEX|#N` and `jumppick N|#N` already preview exact row truth before submit

But one small flow seam still remained at the simplest command-bar entry point.
Typing plain `jumpback` or `jumpforward` still showed only the generic command
row, so callers had to press Enter, reopen `showstatus`, or inspect `jumps`
just to learn what that no-arg command would do right now.

## What changed

Rev532 keeps the fix deliberately small:

- add `_prompt_jump_navigation_command_row(insert, direction=...)`
- keep the ordinary exact command row/doc text
- replace the generic info hint with the exact next target when one exists:
  - `next #1 [back 1] a @ 1:0`
  - `next #3 [forward 1] a @ 5:0`
- keep explicit no-op cues when the command would do nothing:
  - `no earlier jump`
  - `no later jump`

## Why this tiny change matters

This is mostly a trust/flow cleanup.

Once Micromax already knows the exact next jumplist row side-effect-free, the
command bar should surface that truth before Enter instead of making humans and
future LLMs infer it from later status/messages.

The change stays deliberately narrow:

- no new public command was added
- no jumplist state shape changed
- ordinary command docs still stay visible in the completion row
- only the info slot becomes action-aware

## Result

Plain command-bar completion now makes the no-arg history loop more legible:

- `jumpback` — `jump to the previous jumplist entry | next #1 [back 1] a @ 1:0`
- `jumpforward` — `jump to the next jumplist entry | next #3 [forward 1] a @ 5:0`
- edge state still stays explicit:
  - `jumpback` — `no earlier jump`
  - `jumpforward` — `no later jump`

That keeps the inspect → choose → jump loop tighter without widening the API.
