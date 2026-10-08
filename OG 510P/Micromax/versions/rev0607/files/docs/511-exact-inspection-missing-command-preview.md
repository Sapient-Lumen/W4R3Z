# Rev569 — truthful missing-target rows for exact inspection commands

## Why

Micromax already had the important exact-inspection behavior after Enter:

- `showcmd NAME` already failed as `showcmd: no such command: NAME`
- `showaction NAME` already failed as `showaction: no such action: NAME`
- `showword NAME` already failed as `showword: no such word: NAME`
- `showdoc NAME` already failed as `showdoc: no such doc: NAME`
- `showtopic NAME` already failed as `showtopic: no such topic: NAME`

And for known targets, prompt completion already reused the same tiny exact metadata rows humans trust after Enter.

But one small trust seam still lingered across this family: completion only surfaced known names. When a user typed an unmatched exact target, the command bar dropped the token instead of saying what Micromax already knew would fail.

## What changed

- `_prompt_command_row(...)` now has strict missing-target mode and can say `missing command · no such command`
- `_prompt_action_row(...)` now has strict missing-target mode and can say `missing action · no such action`
- `_prompt_vm_word_row(...)` now has strict missing-target mode and can say `missing word · no such word`
- `_prompt_doc_row(...)` now has strict missing-target mode and can say `missing doc · no such doc`
- `_prompt_help_topic_row(...)` now has strict missing-target mode and can say `missing topic · no such topic`
- exact token completion for `showcmd`, `showaction`, `showword`, `showdoc`, and `showtopic` now preserves one unmatched typed token long enough to render that truthful row

## Why this shape

This keeps pre-Enter inspection aligned with the same plain miss feedback Micromax already trusted after Enter. The change stays deliberately narrow: known exact rows are unchanged, command semantics are unchanged, and only unmatched exact targets stop disappearing from the prompt.

Future humans and LLMs can now type a precise inspection guess and see whether Micromax thinks that name exists before submitting the command.

## Checks

Focused prompt-completion coverage now pins:

- preserved exact typed-token completion for `showcmd`, `showaction`, `showword`, `showdoc`, and `showtopic`
- missing-target rows for all five commands
- existing exact metadata rows for known commands/actions/words/docs/topics remain unchanged
