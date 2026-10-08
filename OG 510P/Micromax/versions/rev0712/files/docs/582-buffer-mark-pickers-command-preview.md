# Rev641 - bufferpick / markpick command previews

Problem:
- `bufferpick` and `markpick` already opened grouped searchable pickers backed by stable section rows.
- `showbuffergroups` and `showmarkgroups` already exposed the same section counts and sample buckets headlessly and at the command line.
- But the plain no-arg picker entry points still fell back to generic command metadata right before Enter.

Why this matters:
- Trust: picker entry points should advertise whether there is anything real to browse.
- Flow: one calm section/sample witness reduces blind Enter presses and makes command discovery more legible.
- Coherence: grouped picker roots should speak the same section-summary dialect as the grouped summary commands beside them.

What changed:
- Added `_prompt_bufferpick_command_row(...)` and `_prompt_markpick_command_row(...)`.
- Both helpers reuse `_prompt_section_summary_command_row(...)` with `showbuffergroups` / `showmarkgroups` rather than building picker-only preview state.
- Added focused prompt tests for populated and empty `bufferpick` / `markpick` root previews.

Result:
- Plain `bufferpick` now previews grouped buffer sections before Enter.
- Plain `markpick` now previews grouped mark sections before Enter.
- Empty startup state stays explicit as `0 section(s), 0 buffers` or `0 section(s), 0 marks`.
