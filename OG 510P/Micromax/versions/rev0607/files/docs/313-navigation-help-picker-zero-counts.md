# Rev371: navigation/help picker zero-count submit feedback

Rev370 made search-first submit failures explicit for `commandpick`,
`topicpick`, and `bindingpick`: when a typed query produced zero reachable
results, the prompt stopped collapsing back to `(none)` and instead said which
query failed and how many results existed.

One small mismatch still lingered in the rest of the picker family. The editor
already had grouped searchable prompts for buffers, plugins, recent files, docs,
docs links/headings, marks, and jumps, but failed submit in many of those
prompts still fell back to a vague `(none)` message. That was slightly worse for
trust and flow because the empty result told you less exactly when the answer was
zero.

This revision keeps the change deliberately small:

- `bufferpick QUERY` now says `bufferpick QUERY: 0 buffer(s)`
- `pluginpick QUERY` still says `pluginpick QUERY: 0 plugin(s)` when a real plugin manager exists but the query matches nothing
- `pluginpick` now says `pluginpick: no plugin manager` when the plugin subsystem itself is unavailable
- `recentpick QUERY` / `recentdirpick QUERY` now say `0 recent file(s)`
- `helppick QUERY` now says `docpick QUERY: 0 doc(s)`
- `helplinkpick QUERY` now says `0 link(s)`
- `helpoutlinepick QUERY` now says `0 heading(s)`
- `helpnavpick QUERY` now says `0 help target(s)`
- `markpick QUERY` now says `0 mark(s)`
- `jumppick QUERY` now says `0 jump(s)`

The implementation simply reuses the same tiny zero-count helper already used by
rev370's picker cleanup, so the surface stays inspectable without inventing a
new formatting subsystem.

Why it matters:

- picker-driven navigation stays structurally honest at zero, one, or many
- query failures are easier for humans and future LLMs to interpret from logs
- grouped searchable prompts no longer fall back to a lower-fidelity dialect at
  submit time

Focused coverage lives in `tests/test_editor_picker_zero_summaries.py`.
