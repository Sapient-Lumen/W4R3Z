# Rev712 - macro recordability kind helper

## What changed

- added `Editor._macro_command_recordability_kind(...)`
- kept `_macro_should_record_command_name(...)` as the thin yes/no helper over that classifier

## Why

By rev711, Micromax already had a good recordability policy, but there was still one small inspection gap: the boolean helper could tell you whether a command records, but not *why* it was excluded.

Rev712 makes that tiny reason explicit:

- `exact` for exact-name exclusions like `macro`, `jumps`, `pwd`, `apropos`, `whichkey`, and `prefixmode`
- `prefix` for family exclusions like `show*` and `help*`
- `suffix` for family exclusions like `*pick`
- `recordable` for ordinary commands like `goto`
- `empty` for an empty command name

## Trust impact

This is an archive-maintenance win. The visible recording behavior stays the same, but future humans and LLMs can now inspect the reason behind a command's recordability without reverse-engineering the helper condition.
