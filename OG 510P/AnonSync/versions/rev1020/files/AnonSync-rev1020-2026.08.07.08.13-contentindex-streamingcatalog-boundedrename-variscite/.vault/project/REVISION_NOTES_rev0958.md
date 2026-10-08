# Revision notes — rev0958

## Mission

AnonSync remains one C++ product intended to replace Resilio Sync for a named
real folder workflow. Rev0958 closes a payload-integrity restart authority gap
and refactors the existing bounded scrub transition path; it does not add a
parallel daemon, scanner, or synchronization algorithm.

## Primary C++ correction

- Added canonical scrub disposition `Prepared = 4` without changing the fixed
  v1 record width or the established Idle/Progress/IntegrityFailure encodings.
- A newly selected payload must publish and exactly re-observe `Prepared` under
  the live exclusive store lease before opening or reading its first byte.
- `Prepared` binds the exact store identity, generation, active digest, canonical
  eleven-field payload metadata, zero offset, initial resumable SHA-256 state,
  and an empty terminal digest.
- A fresh process observing `Prepared` or `Progress` forbids both process-cache
  and durable verification-index reuse for the active payload. The ordinary
  complete scanner must hash current bytes before returning authority.
- An owner may reuse only its process-local verified entry after it either
  committed/re-observed the exact active state or completed a current-byte scan
  while that exact state was frozen. Exact state value and exact scrub-state-
  file metadata prevent another process's replacement from borrowing that
  exception.
- A completed mismatch installs the allocation-free process integrity fault and
  clears active acceleration before terminal strings, durable failure
  serialization, or typed-exception construction.

## Adjacent refactor

- `publish_payload_scrub_state_with_reconciliation()` now returns the exact
  re-observed committed state-file metadata rather than a Boolean.
- Normal publication and rename-cutpoint exception reconciliation share one
  exact parse/identity/byte-comparison rule.
- One `publish_working` transition owner increments generations, commits and
  re-observes state, records the same-process witness, and advances the expected
  observation.
- No selected payload is opened or read when `Prepared` publication is missing,
  replaced, malformed, or otherwise unproved.
- Scrub reports treat both `Prepared` and `Progress` as active scheduling state.

## Hard regression

The new process regression forges the precise dangerous composition: a valid
metadata-exact verification index over metadata-hidden corrupt bytes plus a
valid `Prepared` state. A child process holds a shared store lease, allowing the
fresh owner's complete scan but mechanically blocking the optional exclusive
scrub. The fresh owner still hashes the active payload in the ordinary scan and
throws the exact integrity error with no falsely claimed durable failure record.

The rotating one-payload regression now also proves:

- same-owner throttled passes perform zero new hashes, reuse one process entry,
  and never reuse the durable index for active work;
- every fresh owner while `Progress` is active hashes once before authority; and
- durable reuse becomes available again only after the state returns to `Idle`.

The scrub-state codec adds canonical `Prepared` round trips, including a
zero-byte payload, and rejects consumed-byte or terminal-digest variants.

## Audit conclusions

- Best-effort terminal failure evidence cannot also be the sole durable restart
  revocation. Mandatory pre-read intent and optional terminal evidence are now
  separate responsibilities.
- Optional scrub scheduling and lease acquisition are performance policy, not
  content-authority policy.
- The change follows a general write-ahead ordering principle and conservative
  persistent-scan-progress patterns, without claiming database WAL, Btrfs, or
  OpenZFS semantics.
- Older AnonSync binaries do not understand `Prepared`; downgrade safety is not claimed.
  A future release must define explicit format migration and a cold
  verification procedure before downgrade is supported.

See `SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md`.

## Preserved boundaries

- The complete descriptor-rooted payload scan remains namespace, capacity, and
  current-byte authority.
- `ReadOnlyInspect` remains byte-cold with respect to acceleration and does not
  advance scrub scheduling state.
- Payloads remain immutable digest-named regular files under the existing
  cooperative writer lease and rooted no-follow/no-mount-crossing resolver.
- Durable verification metadata, `Prepared`, `Progress`, and
  `IntegrityFailure` are never content proof by themselves.
- The peer-service degraded recovery, exact-owner snapshot handoff, folder
  convergence, authenticated transport, and atomic replica publication paths
  are unchanged except for consuming the safer payload-store result.

## Nonclaims

Rev0958 does not claim power-loss proof, hostile same-UID protection, filesystem
checksum integration, kernel immutability, downgrade compatibility, quarantine,
restore, bounded history, garbage collection, rename identity, directory
semantics, selective synchronization, many-share device ownership, cross-platform
qualification, live public Tor/I2P privacy qualification, or completion of the
first Resilio uninstall workload.

## Validation

The final sealed evidence records focused codec and payload-store tests, the
structural authority audit, complete GCC registry and product lanes, fresh Clang
ASan/UBSan product validation, parent/package verification, exact active-source
patch reconstruction, projection binding, manifest sealing, and clean extraction
comparison. Numerical results are bound in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0958/validation/` rather than guessed in this note before
release sealing.
