# Query-replace buffer witness and archive lineage (rev0957)

Rev0957 repairs two trust failures that share one rule: a delayed operation must
remain bound to the exact state it described, and release evidence must not let a
mutable label pretend to be that state.

## Forensic starting point

The received file was named as rev0956, but its manifest archive name, embedded
context, `TODO.md`, `README.md`, and revision index all still declared rev0955.
Its package payload was therefore not a trustworthy rev0956 successor. Rev0957
is recorded as the next real repository revision after rev0955; the ledger does
not manufacture a rev0956 entry for a filename alias.

The same label-versus-identity defect existed in query replace. A live session
remembered only a buffer name. After one accepted replacement:

- switching buffers could clear the session without committing its undo;
- renaming the target could strand selection and lookup;
- cleanup could clear selection on an unrelated active buffer;
- closing the target and later reusing its name risked retargeting delayed state;
- failed plugin cleanup could commit a provisional undo row and then restore the
  live interaction, leaving both representations active.

## Editor repair

`query_replace.py` now owns a weak `QueryReplaceBufferWitness`. A session captures
the exact `EditorBuffer` object and treats its name as diagnostic metadata only.
`Editor._qreplace_dispose()` is the single finalization path for selection,
accepted-edit undo, and session removal.

Observable behavior is now explicit:

- rename follows the same object;
- buffer activation finalizes accepted edits on the original object as one undo;
- close drops the session before object removal and cannot retarget name reuse;
- cleanup clears only the target's primary selection;
- replacing a live session commits its accepted edits before validating the new
  request;
- accepted edits mark dirty/provenance at mutation time under captured authority;
- successful plugin cleanup commits one undo entry;
- failed group or generation cleanup restores the live interaction and rewinds
  only the provisional query-replace undo state that cleanup introduced.

The plugin rollback addition is deliberately scoped. Global undo membership is
snapshotted only when query replace is among the interaction rows being swept;
unrelated cleanup does not gain a broad undo transaction claim.

## Archive and audit repair

`tools/mkrevzip.py` now treats repository revision as fail-closed evidence:

- six durable breadcrumbs—two TODO rows, README, revision-index current/head, and
  context—must agree;
- `--rev` asserts that agreement rather than overriding it;
- the canonical filename, manifest revision/name/tag/timestamp/timezone, context,
  and archived source breadcrumbs must agree during verification;
- generation writes a temporary candidate, verifies it completely, then
  publishes atomically with `os.replace`;
- existing output is never overwritten;
- raw member names are checked before path normalization, so aliases such as
  `a//b`, `./a`, parent components, backslashes, drives, and absolute paths fail;
- invalid IANA timezone names fail before publication and during verification.

The packaging tests now build the full tree once per module-scoped integration
fixture; inexpensive synthetic archives cover malformed lineage, provenance,
paths, budgets, duplicate members, CRC/digest behavior, and timezone policy.
This removes repeated whole-tree packaging work without weakening the contract.

`mxaudit` now pins both the query-replace witness/rollback owner and the strict,
atomic archive-lineage lane. `mxcontext` keeps the new identity owner in the
stable executable handoff.

## Evidence and limits

The bounded behavior lane passed 36 query-replace/authority tests and all 74
plugin-runtime policy tests. It covers navigation, rename, close/name reuse,
target-only selection cleanup, mutation-time dirty provenance, successful
cleanup undo, and failed group/generation rollback. Adjacent buffer creation,
close, MRU, undo-authority, transaction, and autosave impact lanes also passed.

The archive lane passed all 30 packaging tests in about 25 seconds, with one
full-tree build and inexpensive synthetic corruption cases. Two structural-audit
tests, six context-contract tests, the living-doc/revision/help checks, lint, and
all 156 portability cases passed. The four-step timely summary records context,
audit, lint, and portability as complete; doctor passed independently in its
19-test, 9-test, and 3-test bounded groups. Package-input policy remained clean.

No full-suite claim is made. The 2,595-test suite was only collected inside the
available bounded window, and the cloud command wrapper could not contain the
combined timely-plus-doctor lane even though its constituent checks passed
separately. This is not content-version isolation: unsupported out-of-band
mutation of the same target while a session is live can still invalidate match
coordinates or be grouped with accepted replacements. The weak object witness
is not a durable buffer ID. The archive verifier proves internal consistency and
package inputs; it is not a signature or reproducible-build attestation.

## Judgment and next work

The product rule is now clearer: names are for people, identity witnesses are for
delayed consent/effects, and every claimed revision must be supported by
independent durable evidence. Next prioritize a complete save-failure or
recovery/restart journey, then establish one restrained highlight precedence in
the shared screen model. Add a query-replace content-version witness only if a
supported concurrent/out-of-band mutation path makes the residual risk real.
