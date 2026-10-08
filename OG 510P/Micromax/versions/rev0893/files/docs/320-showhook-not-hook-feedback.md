# Showhook non-hook feedback (rev378)

Problem:
- `showhook NAME` already had strong count-aware handler/provenance output for real hooks
- but a non-hook target still failed as `NAME: (not a hook)`
- that hid the command family and fell back to an older placeholder-style dialect

Small fix:
- `showhook NAME` now fails as `showhook: not a hook: NAME`
- successful hook inspection output is unchanged

Why it matters:
- hook inspection is part of the live scripting/debugging loop
- typed failures are easier to scan in logs, tests, and future UI surfaces
- the editor-side hook path now matches the broader trust-first inspection cleanup
