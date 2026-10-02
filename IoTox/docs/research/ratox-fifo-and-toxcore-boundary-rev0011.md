# Research note — ratox FIFO inheritance and toxcore boundary, rev0011

Date: 2026-08-14

## Question

What is the smallest writable ratox-successor surface IoTox can ship now without confusing a FIFO
with durable command truth or violating current c-toxcore ownership rules?

## Primary sources reviewed

- ratox upstream repository and README: <https://github.com/pranomostro/ratox>
- ratox upstream commit `99b652c0c07c6acf81b6a8cf36a107be76fbe98d`, “Add fifos for incoming requests and remove cmd-parser”: <https://git.2f30.org/ratox/commit/99b652c0c07c6acf81b6a8cf36a107be76fbe98d.html>
- ratox upstream log: <https://git.2f30.org/ratox/log.html>
- c-toxcore v0.2.23 public header: <https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h>
- c-toxcore v0.2.23 release: <https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23>
- Linux `fifo(7)`: <https://man7.org/linux/man-pages/man7/fifo.7.html>
- Linux `pipe(7)`: <https://man7.org/linux/man-pages/man7/pipe.7.html>
- POSIX `write(3p)` and `fpathconf(3p)` as published by man7.org:
  <https://man7.org/linux/man-pages/man3/write.3p.html> and
  <https://man7.org/linux/man-pages/man3/fpathconf.3p.html>

The links are provenance, not vendored authority. The source-linked c-toxcore gate still compiles
against the pinned official archive when a networked command line is available.

## Findings

### Ratox's simplicity is architectural, not cosmetic

Ratox describes itself as a FIFO-based Tox client and expects external scripts to implement some
higher functions. Its examples compose ordinary programs with `file_in` and `file_out`. The 2014
upstream change removed a generic command parser and added request FIFOs. That history supports the
IoTox direction: project a small set of capability-shaped files rather than exposing one sprawling
shell command language.

The lesson is not “every product state is a FIFO.” The lesson is “make the network composable with
ordinary Unix I/O.” IoTox can preserve that property while retaining explicit durable semantics
underneath.

### A FIFO has a name, not contents

`fifo(7)` states that data passes internally through the kernel; the filesystem entry is only a
reference point. A nonblocking read open can succeed before an external writer. A nonblocking write
open fails with `ENXIO` until a reader exists. Linux permits `O_RDWR` on a FIFO, but POSIX leaves
that behavior undefined.

rev0011 therefore opens a nonblocking reader and a separate nonblocking hold writer after the
reader exists. This avoids Linux-only `O_RDWR`, prevents EOF churn between short-lived writers, and
makes the absence of durability explicit.

### FIFO records must be application-framed

Pipes and FIFOs are byte streams. Read boundaries do not preserve write boundaries. POSIX requires
writes of `PIPE_BUF` bytes or fewer to be atomic with respect to other writers and requires
`PIPE_BUF` to be at least 512 bytes; Linux exposes 4096 bytes. IoTox bounds the body at 256 printable
ASCII bytes and recommends one body-plus-LF write of at most 257 bytes. This is portable within the
minimum guarantee.

Because writer close is not a message delimiter while a daemon-held writer exists, an incomplete
fragment needs a policy. rev0011 expires it after bounded inactivity instead of allowing a later
writer to complete another process's prefix.

### The c-toxcore owner-thread boundary remains correct

The pinned v0.2.23 header states that no more than one API function may operate on one `Tox*` at a
time and presents the common `tox_iterate` owner-loop shape. IoTox continues to serialize every
consumed toxcore call on one owner thread. The FIFO monitor never calls toxcore. It submits to the
Agent, which enters the existing durable command path and then the owner-thread transport queue.

The same header reports a 1,373-byte maximum custom packet. The FIFO's 256-byte local record ceiling
is not derived from that transport ceiling; it is a deliberately smaller operator grammar. The
canonical IoTox wire encoder remains responsible for the actual custom-packet bound.

### Current release boundary

c-toxcore v0.2.23 remains the pinned target. Its release notes identify a critical bug fixed after a
manual audit and state that the public APIs were not modified or removed for the release. IoTox
still treats the exact ABI mock as adapter evidence, not proof of native network behavior. The
source-linked and real-peer scripts remain mandatory external gates.

## Resulting implementation rules

```text
FIFO path is private and type-checked.
FIFO bytes never become the durable queue.
One completed record enters one existing command operation.
Durable record commit precedes toxcore send.
Admission evidence names the durable key.
Terminal evidence lives in the signed store and typed projection.
No arbitrary shell evaluation exists.
No new public binary exists.
```

## Next research seam

The next ratox-like write surface should probably be human text, because c-toxcore already provides
native message typing and receipts and IoTox already has the transport/journal path. It must still
answer framing, offline behavior, message splitting, local correlation, and send-receipt semantics
before a `text_out` or `text_in` compatibility name is frozen. Friend lifecycle FIFOs and file
streaming follow later; physical operations do not.
