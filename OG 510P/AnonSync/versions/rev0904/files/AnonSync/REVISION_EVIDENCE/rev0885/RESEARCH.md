# rev0885 primary-source research, inference, and speculation

Research was checked online on 2026-07-22 against the OpenSSL 3.5 and Linux
interfaces used by this cloudtainer. The observed runtime is OpenSSL 3.5.5.

## OpenSSL nonblocking I/O

Primary sources:

- <https://docs.openssl.org/3.5/man3/SSL_read/>
- <https://docs.openssl.org/3.5/man3/SSL_write/>
- <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- <https://docs.openssl.org/3.5/man7/ossl-guide-tls-client-non-block/>

OpenSSL documents that nonblocking read can require either read or write
readiness and that a retryable operation must be repeated consistently. Error
classification belongs immediately to the exact preceding I/O call and its
thread-local error state.

Applied inference: a WANT result is not absence of state. The exact SSL object,
owner thread/process, function, heap-stable pointer, requested length, socket
lifetime, and exclusive stream reservation remain one incomplete operation.
AnonSync therefore performs only OS-level identity reproof before retry and does
not run certificate/exporter/BIO inspection through OpenSSL at that frontier.
After successful progress, the next read is fresh and may perform full live
session and BIO re-attestation.

Readiness is only advice about when retry may be useful. It is not application
progress, peer receipt, object identity, or authority to replace the pending
operation.

## OpenSSL descriptors and BIOs

Primary sources:

- <https://docs.openssl.org/3.5/man3/SSL_get_fd/>
- <https://docs.openssl.org/3.5/man3/SSL_get_rbio/>

OpenSSL can expose distinct read and write BIOs/descriptors. Applied inference:
strict mode must bind both directions even when a particular WANT asks the event
loop to watch only one. Poll-target disclosure may return one advisory integer,
but the authenticated owner retains and re-proves the complete pair.

## Descriptor replacement

Primary source:

- <https://man7.org/linux/man-pages/man2/dup.2.html>

Linux/POSIX descriptor numbers are process table entries and `dup2()` can
atomically replace the object named by a chosen number. Applied inference:
integer equality, `SO_TYPE`, and `O_NONBLOCK` can all survive an ABA sequence in
which the original socket has been replaced by another nonblocking stream
socket. The descriptor number is never sufficient lifetime authority.

## Linux socket cookie

Primary and maintainer-authored sources:

- Linux commit introducing `SO_COOKIE`:
  <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5daab9db7b65df87da26fd8cfa695fb9546a1ddb>
- Linux `socket(7)`:
  <https://man7.org/linux/man-pages/man7/socket.7.html>
- eBPF socket-cookie documentation:
  <https://docs.ebpf.io/linux/helper-function/bpf_get_socket_cookie/>
- systemd socket documentation:
  <https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html>

Linux provides a kernel-generated cookie stable for a socket lifetime and
exposes it to user space through `getsockopt(SO_COOKIE)`. Applied inference:
strict Linux reproof should require a nonzero cookie and exact equality rather
than treating it as optional diagnostics. Stat device/inode/mode and double
observation remain useful additional evidence and detect mixed captures.

The cookie is not a cryptographic credential, durable protocol identifier, or
proof against malicious kernel behavior. The source contract therefore keeps it
opaque and process-local.

## Race boundary

No sequence of independent `fstat`, `getsockopt`, and `fcntl` calls makes
unsynchronized descriptor mutation safe. An actor could theoretically perform
A→B→A substitutions between observations. Applied inference: raw descriptor and
BIO mutation must be serialized by the same higher-level owner as TLS use. The
reproofs detect ordinary contradictions and fail closed; they do not substitute
for synchronization.

## Speculation and next experiments

The next useful abstraction is a bounded reactor owner, not another free
function. It should retain one authenticated channel, one read continuation,
bounded pending writes, exact readiness interests, and aggregate memory/work
budgets. It should never hold a SQLite writer while waiting for socket
readiness.

A production-shaped adversarial matrix should combine transport and durable
cutpoints: descriptor ABA before poll registration and retry; peer close before
and after canonical admission; duplicate operation delivery on a fresh TLS
session; crash before/after immutable staging, rename, and directory durability;
terminal receipt byte frontiers; stale receipt replay; and queue pressure.

Partial TLS offsets should remain ephemeral because a dead TCP/TLS session
cannot truthfully resume at that byte. Durable retry should be defined over
canonical operations and bounded payload chunks, with the full-history owner
retained as a differential correctness oracle while an indexed production owner
is introduced.

The project name still exceeds implemented privacy. Pinned TLS provides an
authenticated confidential channel; it does not provide anonymity,
unlinkability, endpoint hiding, traffic-shape concealment, or resistance to a
global observer. Those properties require a separate threat model and protocol,
not inference from encryption.
