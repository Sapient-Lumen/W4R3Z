# Rev401: typed docs fragment-jump miss feedback

Problem:
- docs navigation cleanup already made `helpfollow`, `helpback`, and explicit `help docs TOPIC` paths keep their own command family visible on success and failure
- same-page fragment and footnote jumps still had one tiny wording seam: when `#fragment` or `[^footnote]` resolution failed inside the current docs buffer, the shared helper logged `help: no section or footnote for #target`
- that was accurate, but it hid the actual jump surface right where users and future LLMs inspect navigation failures

Why this tiny change:
- internal docs links and fragment anchors are part of the headless-first help browser, not a side channel
- when those jumps fail, the log should still identify the action that failed
- the smallest useful move is to keep the existing semantics and tighten only the message dialect

What changed:
- unresolved fragment/footnote jumps now report `helpjump: no section or footnote: #target`
- successful fragment jumps still report `helpjump: topic @ line:col`
- missing docs pages still report `help docs: no such doc: TOPIC`

Validation:
- added a focused docs-navigation regression that follows `[Missing section](#zzz-no-such-section)` and asserts the typed `helpjump:` miss line
- kept the broader docs-navigation and CLI/context/archive checks green
