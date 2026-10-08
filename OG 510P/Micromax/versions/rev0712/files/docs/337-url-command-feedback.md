# URL command feedback (rev395)

`urlopen` and `urlcopy` are a tiny but real trust boundary: they cross from headless editor state into external URL handling and clipboard state. That loop was already safe-by-default, but its wording had drifted into a mixed dialect: the under-cursor action path still used `openurl: ...`, successful opens collapsed to `opened url`, and successful copies fell back to a generic multi-line `copied url` block.

Rev395 keeps the fix deliberately small. Successful opens now report `urlopen: URL`, successful copies report `urlcopy: URL`, and the under-cursor miss/disabled path now uses `urlopen` consistently too. The goal is not more verbosity; it is a single typed surface that stays easy to scan in logs, tests, and future LLM traces.
