# Rev708 - macro recordability pattern constants

## What changed

- kept `MACRO_NONRECORDABLE_COMMANDS` for exact-name exclusions
- added `MACRO_NONRECORDABLE_COMMAND_PREFIXES`
- added `MACRO_NONRECORDABLE_COMMAND_SUFFIXES`
- kept `_macro_should_record_command_name(...)` as the thin behavioral helper over those three shapes

## Why

By rev707, Micromax had three kinds of command-recordability policy in play:

- exact command names like `macro`, `jumps`, `pwd`, `helphistory`, `help`, and `apropos`
- whole observer families like `show*`
- whole picker families like `*pick`

That behavior was already correct, but the archive still hid those three shapes inside one helper condition. Rev708 makes the shape of the policy explicit before anyone has to read the helper logic.

## Trust impact

This is an archive-maintenance win. The visible recording behavior stays the same, but future humans and LLMs can now see the exact-name versus family-pattern exclusions at a glance.
