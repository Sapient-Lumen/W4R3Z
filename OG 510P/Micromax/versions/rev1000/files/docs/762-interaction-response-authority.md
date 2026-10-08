# Rev0804 — delayed interaction response authority

Rev0804 keeps the focus on concrete runtime trust boundaries.  Rev0800 added
rollback for failed plugin callbacks that create prompts, query-replace sessions,
keymode captures, or external URL confirmations.  The remaining gap was the
successful/live side: once one of those interactions existed, direct action calls
could still answer it without proving they owned the delayed state.

## Failure mode found

A query-replace session or external URL confirmation can outlive the command or
script that created it.  The active capture keymode already preserved script
origin for ordinary physical keypresses, but the direct action path was weaker.
A lower-authority script could call `QueryReplaceYes`, `QueryReplaceAll`,
`QueryReplaceQuit`, `OpenUrlYes`, `OpenUrlNo`, or `OpenUrlCopy` through an action
surface and respond to a trusted/user pending interaction.

That is a delayed-authority bug: the prompt-like state is the authority object,
not the later action name.

## Code changes

New seam:

- `src/micromax_editor/interaction_policy.py`

It exposes `interaction_response_policy(...)`, a small wrapper over the existing
runtime-authority policy.  Trusted interactive callers keep normal control.  A
script-origin caller may respond to an interaction it created itself, but not to
a trusted/user interaction or another script/plugin generation's interaction.

`QueryReplaceSession` now stores the `RuntimeRegistrationAuthority` captured when
the session starts.  The direct response methods now preflight that authority:

- `qreplace_yes()`
- `qreplace_no()`
- `qreplace_last()`
- `qreplace_all()`
- `qreplace_quit()`

External URL confirmation state now stores `_pending_open_url_authority` beside
the pending URL/source.  The confirmation actions delegate through editor-owned
methods that preflight the captured authority before opening, canceling, or
copying the URL:

- `open_url_confirm_yes()`
- `open_url_confirm_no()`
- `open_url_confirm_copy()`

The creation/replacement path is guarded too.  A lower-authority script cannot
start a new query-replace or URL confirmation over an existing trusted/user or
other-origin pending interaction; the old interaction remains active and
unchanged.

The plugin callback interaction snapshot now includes the pending URL authority,
so failed plugin callback rollback restores not only the URL text/mode but also
who is allowed to answer it.

## Guarantees

- A script cannot approve/cancel/skip/finish or replace a trusted query-replace
  session.
- A script-created query-replace can still be answered later by its captured
  active keymode origin.
- Independent script origins cannot answer each other's pending query-replace
  sessions.
- A script cannot approve, cancel, copy, or replace a trusted pending external
  URL confirmation by directly invoking the action name.
- Script-created URL confirmations still work through later capture-key response
  when the origin matches.
- Denied responses leave the delayed interaction active rather than consuming or
  laundering it.

## Remaining risk

This is still an in-process authority model, not an event-loop sandbox.  Trusted
interactive code can intentionally take over or cancel lower-authority pending
interactions.  The next related audit should look for any newly added delayed UI
objects that are not represented by `Prompt`, `QueryReplaceSession`, the open-URL
pending fields, or `ActiveKeyMode`.

## Validation evidence

Focused validation performed for this revision:

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_editor_interaction_authority.py

8 passed in 2.27s
```

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/test_editor_interaction_authority.py \
  tests/test_editor_qreplace_interaction_boundary.py \
  tests/test_editor_query_replace.py \
  tests/test_editor_helplinkcopy_and_openurl_confirm.py \
  tests/test_editor_url_under_cursor.py \
  tests/test_plugin_containment_and_caps.py --durations=10

78 passed in 2.15s
```
