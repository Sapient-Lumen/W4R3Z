# Micromax revision 0963

## Outcome

Rev0963 turns the owner-only post-replace crash state and private-temp residue
from documented risks into explicit, testable recovery paths. Atomic permission
intent is durable before document mutation; restart can safely finish or refuse
the permission transaction; stale temp cleanup requires a process-instance and
save-lease proof.

## Product changes

- Added a pre-checkpoint atomic write plan that pins concrete target authority,
  containing-directory identity, permission policy, and exact final mode.
- Retained versioned permission-repair metadata in recovery records.
- Added `recovermode [#N|ID]` for fingerprint- and authority-verified mode repair,
  file/directory synchronization, final verification, and record retirement.
- Prevented ordinary `recover` from discarding a matching-byte record while its
  permission transaction remains pending or conflicted.
- Added `recovertemps` bounded metadata inventory and explicit
  `recoverclean [#N|ID]` stale-temp removal.
- Added v3 private temp names carrying save lease, boot token, PID namespace,
  PID, process start tick, and random token.
- Made active, cross-namespace, malformed, legacy, permission-denied, and other
  unprovable creators fail closed.
- Preferred unnamed `O_TMPFILE` mode probes where supported; retained the empty
  POSIX unlink-while-open fallback.

## Audit/refactor changes

- Revalidated name/inode/mode immediately before `fchmod` and added a concurrent
  mode-change regression.
- Made intended mode `0600` use the same explicit sync/verification path.
- Removed basename from worker cleanup authority and deduplicated same-parent
  directory scans.
- Tightened process token grammar and PID validation.
- Preserved legacy v2 parsing solely for visibility; v2 cannot establish cleanup
  eligibility because it lacks PID-namespace identity.
- Replaced the save-timeout audit's source-wrapping substring with a small AST
  flow check that requires one effective timeout to reach both atomic planning and
  document writing; added regressions for local aliases and wrapped docstrings.

## Honest boundary

Cleanup is deliberately manual and conservative. It does not use file age, does
not cross PID namespaces, does not open payloads, and does not infer ownership
when procfs evidence is unavailable. The repair operation is not generic chmod
and cannot protect against an adversarial peer with equivalent filesystem
rights. The tested model remains Linux/POSIX process death, not universal power
loss.
