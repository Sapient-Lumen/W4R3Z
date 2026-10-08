# rev0883 primary-source research, inference, and speculation

Research was checked online on 2026-07-22. The design record uses primary
OpenSSL and C++ specification sources.

## OpenSSL thread safety

Source: <https://docs.openssl.org/3.5/man7/openssl-threads/>

OpenSSL documents that most objects are not safe for simultaneous use and that
thread safety does not generally mean one object may be mutated by multiple
threads. Applied inference: the AnonSync authenticated-state flags and `SSL*`
form one logical stream owner. Cleanup that changes reservation/poison state is
not exempt from execution affinity merely because it is `noexcept`.

## OpenSSL final release

Source: <https://docs.openssl.org/3.5/man3/SSL_free/>

`SSL_free()` decrements the SSL reference count and may release the SSL object,
buffering BIO, read/write BIOs, cipher lists, and session references. Applied
inference: final release must use the same process/thread proof as stream
progress, and the proof must occur before any earlier wrapper mutation that can
lead to that release.

## OpenSSL write retry semantics

Source: <https://docs.openssl.org/3.5/man3/SSL_write/>

OpenSSL documents WANT_READ/WANT_WRITE behavior and the requirement to retry a
blocked write with the same arguments. Applied inference: a future resumable
sender needs a stable event-loop owner retaining exact immutable write arguments.
Moving the current synchronous continuation among arbitrary threads would be
false authority. Rev0883 continues to poison rather than claim resumable WANT
progress.

## C++ thread transfer

Source: <https://eel.is/c++draft/thread.thread.constr>

`std::thread` construction transfers/copies its callable state into the new
thread's execution context. Applied inference: language-level movement of a
wrapper is not proof that an external OpenSSL object or AnonSync capability has
transferred its execution owner. The capability must define that transition;
rev0883 deliberately does not.

## Speculation and next experiments

The next useful abstraction is not another movable synchronous wrapper. It is a
single-owner event-loop service with explicit states for incomplete prefix,
incomplete body, WANT_READ, WANT_WRITE, peer close, cancellation, timeout, and
stream poison. It should keep SQLite transactions outside readiness waits and
use immutable application chunks whose identities can be retried on a fresh TLS
channel. Persisting TCP/TLS byte offsets would be misleading because those
positions are connection-local; durable chunk identity and receiver chunk
idempotency are more plausible.

The receiver should be implemented before durable sender in-flight expansion.
A real receiver loop must bind the exact authenticated peer/session, canonical
request, bounded payload, evidence admission, immutable staging, atomic visible
publication, directory durability, terminal effect receipt, and duplicate
replay. Crash injection should cover every byte frontier and every durable
cutpoint.

ThreadSanitizer would add useful race-oriented evidence where supported, but it
would not replace deterministic capability fail-stop tests or prove OpenSSL's
internal behavior. The strongest eventual design is one where illegal
cross-thread ownership is unrepresentable at the service boundary, with the
current runtime fail-stop retained as defense in depth.

The name AnonSync still exceeds implemented privacy properties. TLS and pinned
keys provide channel confidentiality/authentication, not anonymity,
unlinkability, endpoint hiding, or traffic-analysis resistance. Those remain
separate adversary-model and protocol work.
