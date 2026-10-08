# Rev709 - keep help-family commands read-only while recording

## What changed

- `MACRO_NONRECORDABLE_COMMAND_PREFIXES` now includes `help`
- `_macro_should_record_command_name(...)` therefore treats the broader `help*` family as non-recordable
- successful docs-buffer commands like `helpfollow` and `helpback` no longer append command steps to the macro buffer

## Why

Rev705 put `help` and `apropos` on the read-only side of macro recording, but the broader docs-help navigation family still depended on whether a given command happened to fail. In a real docs buffer, commands like `helpfollow` and `helpback` can succeed — and before rev709, they still became macro steps.

That made docs navigation feel more like accidental UI automation than trustworthy inspection.

## New contract

While recording a macro:

- docs/query commands like `help`, `apropos`, and `helphistory` stay out of the macro buffer
- docs navigation commands like `helpfollow` and `helpback` stay out of the macro buffer too
- other observer families like `show*` and `*pick` still stay out of the macro buffer
- an ordinary successful command like `goto 1:1` still records exactly once

## Trust/flow impact

This is a small trust and flow cleanup. Docs-help navigation should help you inspect automation, not become the automation.
