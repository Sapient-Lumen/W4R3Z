# Revision 0963 audit

## Priority judgment

The riskiest unfinished path was the rev0962 atomic-save crash window. Correct
bytes could survive at the private staging mode while restart retired the only
witness, and hard death could leave private payload temps with no safe cleanup
proof. Rev0963 fixes those product failures directly rather than adding a general
ownership registry.

## Corrected findings

1. **Witness loss after replacement:** matching target bytes no longer imply the
   permission transaction completed. Recovery retains the record when the
   versioned mode contract is present.
2. **Missing final intent:** an atomic write plan now pins target authority,
   parent device/inode, permission policy, and exact final mode before checkpoint
   publication; the writer rejects drift.
3. **Incomplete owner-only recovery:** `recovermode` verifies exact bytes,
   parent/name/inode authority, regular-file type, owner, link count, and allowed
   mode; it performs `fchmod`, file sync, directory sync, final verification, and
   only then record retirement.
4. **False completion for intended `0600`:** equal private and intended modes
   still take the explicit sync-and-retire lane.
5. **Unsafe cleanup premise:** private temp v3 names bind boot, PID namespace,
   PID, process start tick, random save lease, and random filename token. Missing
   or cross-namespace proof is unknown, never stale.
6. **Uninspectable residue:** `recovertemps` inventories bounded metadata without
   opening payloads; `recoverclean` deletes one definitively stale row after
   descriptor-relative revalidation.
7. **Probe residue window:** Linux mode discovery prefers unnamed `O_TMPFILE`;
   unsupported filesystems retain the empty immediately-unlinked fallback.
8. **Redundant timeout cleanup:** nominal and concrete names in one parent now
   cause one lease/PID scan, not two basename-keyed scans.
9. **Repair race:** the target name and mode are rechecked immediately before
   `fchmod`; an injected external mode change is refused and leaves the witness.
10. **Identity parsing:** reliable tokens require lowercase hexadecimal grammar,
    and temp construction rejects nonpositive PIDs.
11. **Audit drift:** the save-effect audit depended on a particular docstring
    line break and could report a false missing timeout boundary after the planning
    refactor. It now parses the owning functions and follows the effective timeout
    directly or through one local alias into both bounded sinks.

## Cloudtainer observations

- `/proc/<pid>/ns/pid` link text is stable, while this environment's followed
  namespace-handle `stat` inode was synthesized differently across lookups. The
  implementation therefore prefers canonical `pid:[N]` text and retains
  device/inode as the standards-based fallback.
- The workspace filesystem rejected `O_TMPFILE`; the named, payload-free,
  unlink-while-open fallback was exercised here. The unnamed path has isolated
  deterministic tests.
- Long mixed multiprocessing runs can suffer cloudtainer contention, so
  acceptance was split into behavior-focused invocations. No broad/full-suite
  result is inferred from those slices.

## Waste avoided

No general temp registry, startup sweep, age heuristic, advisory-lock protocol,
or Linux-only `renameat2` dependency was added. The process proof is encoded in
the existing temp name, document-temp discovery is constrained by an existing
journal lease and parent authority, and cleanup is an explicit one-row command.
The implementation returns unknown instead of performing speculative deletion.

## Residual risk

- Unpublished document temps cannot be correlated after restart and are not
  guessed into the inventory.
- Cross-namespace or procfs-restricted residue remains visible only to external
  administration, not cleanup eligible.
- The named mode-probe fallback can strand an empty file in its small
  open-to-unlink death window; it never contains document bytes.
- There is no POSIX atomic compare-and-chmod primitive; the checked race boundary
  is narrow but not a hostile-peer filesystem sandbox.
- Process-death evidence is not sudden-power-loss or remote-filesystem evidence.
- Direct writes remain non-atomic after truncate.
