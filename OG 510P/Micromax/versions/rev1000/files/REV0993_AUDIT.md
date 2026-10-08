# Rev0993 audit — persistent recovery truth and atomic recovery history

## Priority chosen

Rev0992 left sustained-use evidence as the highest product risk. Rev0993 ran the
complete startup/project/edit/search/save/plugin/recovery journey rather than
opening another doctrine or registry track.

## Severe findings corrected

- Unresolved interrupted-save records disappeared from view after ordinary
  messages replaced the startup warning.
- A transactional plugin command could fail and roll back its own message while
  leaving an older success message visible.
- Undo after opening a recovery could restore pre-recovery text while retaining
  the crash-record identity. A later save could then delete unreviewed recovery
  data.

## Landing

- Cached event-refreshed recovery presence is now part of `status_model()` and
  the default right status row as `[recovery:N]`, `[recovery:N+]`, or
  `[recovery:?]`; rendering performs no filesystem scan.
- The command dispatcher emits one generic failure only when false returned and
  no command-specific message survived.
- Recovery-open into an existing clean buffer is one history decision over
  shallow line vectors, their content signatures, cursors/selections,
  codec/filetype metadata, dirty provenance, recovery id, journal entry, target,
  and force-save authority.
- Undo/Redo compares the retained generation signature with the *current* saved
  baseline instead of restoring historical dirty/version/save-signature
  snapshots. This stays exact in `fastdirty` buffers without a document join.
- Bounded no-follow regular-record presence prevents history from resurrecting
  authority after save, dismissal, or a known unusable replacement.
- Aggregate macro/`ed.with-undo` snapshots now include recovery authority
  sidecars for exact rollback. Recovery inventory/review/repair/cleanup and
  disposition commands are nonrecordable macro boundaries, preserving the
  specialized save-baseline-aware recovery history row.

## Audit/refactor result

Recovery is no longer modeled as ordinary text plus unrelated metadata. Text and
journal authority move atomically, while save-baseline truth remains monotonic.
The row retains a signature of each text generation—not a historical baseline—
so even `fastdirty` replay can compare against whichever generation is saved
now. This removes the dangerous save/Undo seam without a generic transaction
registry, filesystem watcher, or second document model.

## Evidence and qualification

Focused command/status/journey, atomic large-recovery, and explicit
save-failure/restart/recover/save tests pass. The cloudtainer's monolithic
3,456-test run exceeded its 30-minute supervisor. One command diagnostic column
assertion fails identically in the rev0992 baseline (expected 36, observed 31),
so rev0993 makes no fresh complete-suite claim.

The full design, online comparison, test surfaces, and residual risk are in
`docs/950-sustained-use-recovery-attention-command-failure-audit.md`.
