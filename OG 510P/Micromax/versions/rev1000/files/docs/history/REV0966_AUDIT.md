# Revision 0966 audit

## Priority judgment

The riskiest unfinished work was not another visual or registry layer. A
supported `InsertText` action could consume query-replace's visible selection,
leave old match offsets live, and let a later confirmation corrupt different
text. This violated the editor's core trust promise in a high-frequency loop.

## Corrected findings

1. **Identity without generation:** the delayed session named the right object
   but not the text state that produced its coordinates. The witness now carries
   the monotonic buffer version and every response validates it.
2. **Selection consumed by an unrelated action:** mutating actions now finish the
   live session before running, so they start from a cleared transient mark.
3. **Wrong undo chronology:** accepted replacements finalize before a later
   action; commands/hostcalls that record after mutation are split centrally at
   their pre-edit snapshot.
4. **Unsafe stale grouped undo:** untracked text drift no longer permits a broad
   snapshot undo that could erase outside text. The session fails closed and
   reports when grouped undo cannot be supplied safely.
5. **False success from `all`:** stale/error exits now propagate `False`.
6. **Version disappearance:** a witness that captured a real version treats an
   unreadable current version as authority loss.

## Research reviewed on 2026-07-18

Neovim's `b:changedtick` and API guidance, LSP document/edit version checks, and
CodeMirror's start-state/change/new-document transaction model all reinforce the
same small rule: delayed coordinates and edits apply only to the document
version they observed. Exact links and Micromax implications are in
`docs/922-query-replace-generation-undo-interleaving.md`.

## Waste avoided

No immutable-buffer-ID migration, generic transaction manager, edit journal,
owner registry, or new plugin lifecycle row was added. The repair reuses the
existing buffer version, query-replace witness, action classification, snapshot
undo owner, and screen contract.

## Residual risk

- Private raw line-list mutation that omits `touch_external()` is outside the
  supported editor boundary and can evade generation checks.
- Snapshot undo and retained exact transaction text remain whole-buffer costs.
- Untracked interleaving text is preserved, but safe grouped query-replace undo
  may be unavailable.
- This revision does not claim a complete repository suite.

## Cloudtainer provenance correction

An unlinked process was discovered writing a separate selection/rendering
rev0966 attempt into the first shared work directory. That tree was discarded.
The final change was replayed into a fresh extraction of the exact rev0965 input,
and the source/test diff was checked against that archive before packaging.
Unrelated `/mnt/data/work0966` processes and files were neither copied nor
terminated. Build trees, egg-info, caches, and test byproducts are removed from
the final source tree.
