# Rev816 — visible-word register read authority

## Why this was risky

The command and keybinding registries already had explicit runtime-authority
read policies, but the visible Micromax word dictionary still behaved like a
raw public debugging surface. A lower-authority script could inspect dynamic
trusted/user or other-origin word names through help/topic completion, then ask
`ed.word-detail-row` / `showword` for effect strings, wordlist names, source
spans, and source text reconstructed through `xt-src`.

That is not just cosmetic metadata. Dynamic words are executable runtime state;
source spans and reconstructed source can expose plugin layout, local user init
code, and helper definitions that were never intended to become script-readable.

## What changed

New module:

`src/micromax_editor/word_policy.py`

New capability:

`cap.word-read` / `ed.word-read`

New/changed runtime seams:

- `VM.word_authority_stamp` lets an embedding attach authority metadata whenever
  `_add_word(...)` installs or replaces a word.
- `Editor._word_authority` records dynamic VM-word provenance beside the VM
  dictionary without making standalone `micromax.VM` depend on editor policy.
- `Editor._public_core_word_ids` captures the initial built-in/editor-hook word
  objects that stay public for help and completion compatibility.
- `Editor.visible_vm_word_names()` now respects VM search-order shadowing and
  filters dynamic protected words from script-context discovery.
- `Editor.word_detail_row(..., strict_denial=True)` raises on protected exact
  hits so `ed.word-detail-row` can preserve the queried word name on denial.

## Behavior

Trusted/interactive callers keep normal word discovery. Built-in/core words stay
public so the language remains self-describing. Script-origin callers can inspect
words they defined under the same script/plugin origin. Trusted/user or
other-origin dynamic definitions require `cap.word-read`.

The filter now applies to:

- `ed.word-detail-row`;
- `showword` / exact word prompt rows;
- help/topic word rows;
- `apropos` word rows;
- root `showword` inventory summaries;
- word-name completion using the shared visible-word helper.

Exact denied hostcalls leave the word-name operand on the VM stack for debugging
and recovery instead of consuming the evidence first.

## Rollback boundary

Dynamic word authority is now included in plugin-callback rollback. If a failed
plugin callback half-defines helper words and the VM dictionary rolls back, the
parallel word-authority sidecar also rolls back. Successful lazy helper loads
still persist with their captured script/plugin authority.

## Remaining risk

Action discovery is still intentionally treated as mostly public core editor
surface, but it has not yet had the same explicit audit as command, keybinding,
hook, and word discovery. A complete chunked `mxtest` aggregate is still the
right full-suite evidence lane.
