# Ratox signed restart-fence source review — rev0020

Date: 2026-08-17 America/New_York

## Question

How can an enabled Ratox host reserve a restart-unique attachment incarnation before advertising the
service, without trusting pathname races, an unsigned counter, or a process-local identifier?

## Sources rechecked

```text
https://man7.org/linux/man-pages/man2/open.2.html
https://man7.org/linux/man-pages/man2/flock.2.html
https://man7.org/linux/man-pages/man2/rename.2.html
https://man7.org/linux/man-pages/man2/fsync.2.html
https://man7.org/linux/man-pages/man7/path_resolution.7.html
https://man7.org/linux/man-pages/man2/close.2.html
https://cwe.mitre.org/data/definitions/367.html
```

These references define Linux descriptor-relative/no-follow traversal, advisory open-file-description
locking, atomic rename, file and directory synchronization, close semantics, and the general TOCTOU
weakness class. They are design inputs, not review or approval of IoTox.

## Applied construction

rev0020 adds a move-only lifetime lease backed by one exact signed 128-byte device-bound record. The
record is decoded before increment, committed through a private temporary file plus `renameat`, and
strictly reopened after file and directory synchronization. The final owner-private lane, lock, and
state inode are inspected without following symlinks; hard links, unsafe modes, wrong owner/type/size,
identity mismatch, tamper, zero, and wraparound are refused.

The final audit closed a first-start durability gap: for every hierarchy component created by this
transaction, the implementation fsyncs the new directory after mode enforcement and separately fsyncs
its containing directory before descending. This follows the Linux requirement that synchronizing a
file or child directory does not by itself make the directory entry naming it durable. Interrupted
`fsync` and `mkdirat` calls are retried before failure classification.

The host acquires this lease before Ratox construction can select feature bit 23. The resulting
nonzero value is injected into OPEN results and appears in content-free runtime status. The lock is
held until Ratox shutdown. Client-only activation does not touch the lane.

The shipped-binary process fixture starts one real `iotox run`, observes the held lease and signed
record, starts a second daemon with separate runtime/transport state but the same identity and
incarnation lane, requires an exact contention failure with no counter advance, stops the first, and
requires a successor to publish exactly the prior value plus one. Unit tests separately exercise
signature, identity, malformed record, link/mode/type, nested traversal, contention, and exhaustion
boundaries.

## Security conclusions

- Attachment incarnation is reserved before network advertisement rather than inferred after OPEN.
- A rejected contender cannot consume an incarnation.
- The signed counter is device-bound; copying it to another identity fails verification.
- `flock` provides cooperative exclusion only; strict signed/inode validation remains required.
- Atomic rename without directory `fsync` would be an incomplete durability claim.
- Synchronizing only the final state lane would also be incomplete when the private hierarchy itself
  was created during first startup; each new component and containing entry now has an ordered sync.
- Enabled direct-service construction defaults to the invalid zero sentinel and must receive the
  reserved value explicitly; disabled construction remains valid without touching the lease lane.
- Cleanup preserves a startup failure in runtime status, improving postmortem truth.
- A bounded pre-OPEN deadline prevents one silent local connection from monopolizing the sole
  controller slot indefinitely.

## Limits

The lane is not rollback-resistant against a privileged owner, storage snapshot restore, or an
attacker with equivalent filesystem authority. The deterministic process fixture uses the exact
c-toxcore ABI double and does not prove public Tox routing, NAT traversal, relay behavior, hardware
power-cut durability, or PTY survival across daemon restart.
