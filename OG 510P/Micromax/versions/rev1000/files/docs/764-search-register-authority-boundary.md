# Rev806 active-search register authority boundary

## Why this was risky

The active search query is a small but persistent editor register. It appears in
status/search-row models, controls visible highlighting, and drives later
`findnext` / `findprev` navigation. Before this revision, lower-authority
script code could borrow a trusted user's active search in three ways:

- read the query and match counts through status/search-row surfaces;
- replay the trusted query later with `findnext` / `findprev`;
- replace or retag the trusted query through `ed.find` or find-mode actions.

That made search state unlike the rest of the recently protected register
family: marks, macros, undo/redo, prompt history, recent rows, jumplists,
selection stacks, clipboard state, savecursor rows, and delayed interactions all
carry runtime authority, but search still behaved like ambient editor state.

## What changed

New module:

`src/micromax_editor/search_policy.py`

New capabilities:

- `cap.search-read` / `ed.search-read`
- `cap.search-replay` / `ed.search-replay`

`Editor.search_authority` now records the runtime authority that last created
the active search. Trusted interactive code keeps normal behavior. Inside
`script_context()`, scripts can read and replay their own same-origin active
search, but trusted/user and other-origin search state is hidden or blocked by
default.

Read surfaces now redact protected search state for lower-authority callers:

- `Editor.search_position_model()`
- `Editor.status_model()` search fields
- `Editor.search_rows_model()` / TUI search cue model

Replay and replacement surfaces now check provenance:

- `findnext` / `findprev`
- `ed.find-next` / `ed.find-prev`
- `ed.find`
- `Find`, `FindLiteral`, and `FindRegex` flavor changes
- incremental find refreshes that would replace a protected search

Denied `ed.find` requests preflight before consuming the query operand, so the
failed request remains inspectable on the VM stack.

## Rollback/audit coverage

The plugin callback rollback snapshot now includes active search state and its
authority sidecar. A failed deferred plugin callback can no longer leave behind
a half-mutated active search after its dictionary/runtime registrations were
restored.

Macro/buffer transaction snapshots also carry active search state, keeping the
search register aligned with other editor-local registers when a transactional
macro or scoped edit path aborts.

## Capability split

The two capabilities are deliberately separate:

- `cap.search-read` allows status/search-row inspection of protected search
  state but does not allow navigation replay.
- `cap.search-replay` allows replay/replacement of protected active search state
  but does not reveal another authority's query through status/search-row
  models.

This lets trusted automation grant a narrow operation without turning search
state into a general side channel.

## Validation

Focused regression coverage:

- script-origin status/search-row reads redact trusted search state;
- script-origin `findnext` cannot replay trusted search without
  `cap.search-replay`;
- denied `ed.find` preserves the query operand and leaves trusted search intact;
- same-origin script search remains usable;
- independent scripts cannot replay each other's active search;
- `cap.search-read` and `cap.search-replay` remain separate;
- script-origin `FindRegex` cannot retag a trusted active search;
- plugin callback rollback restores active search state.

## Remaining risk

This is still editor-runtime provenance, not an operating-system isolation
boundary. The broader protected-register audit should continue looking for any
remaining long-lived state that can be read, replayed, cleared, or retagged from
script-origin code without a sidecar.
