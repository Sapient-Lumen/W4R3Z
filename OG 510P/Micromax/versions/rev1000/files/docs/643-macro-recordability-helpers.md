# Rev702 - macro recordability helpers

## What changed

- added `Editor._macro_should_record_command_name(...)`
- added `Editor._macro_should_record_action_name(...)`
- reused those helpers in the command and action recording paths

## Why

Rev698 through rev701 tightened Micromax's recording honesty in a good way:

- `show*` inspectors stopped polluting recorded macros
- failed command lines stopped becoming recorded command steps
- blocked actions stopped becoming recorded action steps

Those visible fixes were good, but the tiny allow/deny policy behind them had started to spread across raw conditionals in multiple places. That made the archive a little harder to trust because another small recording tweak could update one path and quietly miss the other.

## Helper contracts

`_macro_should_record_command_name(...)`

- records ordinary commands like `goto`
- skips `macro`
- skips the read-only `show*` inspector family

`_macro_should_record_action_name(...)`

- records ordinary actions like `InsertText`
- skips the macro-control actions `ToggleMacro`, `PlayMacro`, and `CancelMacro`

## Trust impact

This is mostly an archive-maintenance win. The visible recording behavior stays the same, but the rules behind that behavior now live in one small, test-pinned place instead of two drifting conditionals.
