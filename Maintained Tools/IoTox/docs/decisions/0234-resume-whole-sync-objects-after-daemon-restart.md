# ADR 0234: Resume exact whole-object prefixes after daemon restart

Status: accepted with deterministic and genuine direct-UDP/forced-TCP Sandwurm qualification,
2026-08-29.

## Context

ADR 0224 permits a live same-process carrier reassignment to inherit a strict whole-object prefix,
but startup recovery previously deleted every incomplete attempt. The deletion was safe, yet it
forced an explicit fresh pull to fetch bytes the device had already placed in a private canonical
inode. Resurrecting the old pull, Tox handle, online epoch, route, or worker would be unsafe: those
identities are process- and connection-local.

The signed attempt journal already binds the durable facts needed for a narrower construction: the
namespace, immutable object kind, SHA-256 identity, exact size, attempt ID, and the stable-device
signature. A fresh pull independently re-proves publisher authority and a signed candidate HEAD.
That makes it possible to reuse bytes without reviving any dead network state.

## Decision

- Preserve the ATM1 journal format and signature domains. Two previously-zero record padding bytes
  now canonically encode `active=0|restart-retained=1` and
  `whole-object=0|range-bundle=1`; every existing live whole-object ATM1 record remains byte-identical
  and readable. A range bundle can never be classified as a restart-retained whole-object prefix.
- Startup first commits a complete valid object as before. It retains only a canonical, owner-owned,
  mode-0600, single-link, strictly positive file shorter than the signed object size. Zero-byte,
  absent, temporary-only, complete-but-corrupt, malformed, or linked debris is still discarded or
  refused fail-closed.
- Retention changes no dead route into a live route. The old route/worker remain signed forensic
  binding only; the old job, online epoch, Tox file number, FileId, request ID, scheduler attempt,
  and transport descriptor are never reconstructed.
- A later fresh pull must authorize the current peer, verify its signed HEAD, and name the identical
  object kind, digest, and size. It burns a fresh attempt, message ID, and FileId. Under the namespace
  transaction it finishes the retained journal entry, no-clobber renames the inode to the fresh
  attempt, journals the new active attempt, and seeks the new Tox offer to the exact prefix length.
- Full size and SHA-256 verification still precede immutable-store commit. The signed HEAD is
  accepted last and activation remains an explicit independent operation.
- A freshly verified candidate HEAD prunes restart-only prefixes it does not name. If an exact object
  already exists and verifies locally, its redundant prefix is fenced. This prevents old retained
  work from becoming an indefinite staging or outstanding-attempt quota pin.
- `sync-status` adds content-free saturating `restart-resumed-attempts` and
  `restart-resumed-bytes`; the existing total resume counters include the same work. Agent startup
  reports the number of restart-retained attempts without exposing paths or object identities.
- This decision covers whole immutable objects only. A range-bundle prefix cannot be interpreted
  without its exact locally derived range plan, which is not yet durable.

## Deterministic evidence

Owned tests prove that startup commits one complete object, retains one strict positive prefix,
fences absent/temporary/complete-corrupt/inactive debris, repeats recovery idempotently, and prunes
an unmatched retained prefix. A fresh coordinator then consumes an exact device-signed three-byte
`pay` prefix under attempt 1, allocates attempt 2 on a different route, seeks to byte 3, receives only
`load`, verifies the complete `payload` digest, commits once, and clears signed active truth. A
different object identity cannot discover or claim the retained attempt.

The `sync-file-restart-resume` Sandwurm cell is distinct from the historical
`sync-file-restart` retry proof. It requires an unclean receiver exit after positive progress,
canonical partials with no disposable transport temporaries, exact retained/resumed aggregate byte
equality after a fresh authorized pull, stable Tox/device identities, HEAD-last convergence, and
explicit activation. Accepted compact proofs `pair.f20ma62y` and `pair.lj0pdz6a` resume two exact
prefixes totaling 115,164 direct-UDP bytes or 159,036 forced-TCP bytes respectively. See
`../evidence/2026-08-29-sandwurm-sync-restart-resume.md`.

## Consequences

Daemon restart no longer implies whole-object retransmission from byte zero when a trustworthy
strict prefix survived. The recovery authority remains the immutable digest plus a newly authorized
signed HEAD, not the dead carrier or journal route fields. Wire framing and protocol feature bits do
not change.

This does not provide automatic job resurrection, range-bundle restart continuation, clean-shutdown
checkpointing, remote cancellation, multi-source striping, guest/kernel power-loss qualification,
full-disk recovery, final-chunk crash linearization, two physical hosts, or a performance bound.
