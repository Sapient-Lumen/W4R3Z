# Absolute command deadline, authenticated idle close, pre-claim cutpoint, and lease-horizon audit — rev0907

## Executive conclusion

AnonSync's heart remains **evidence-authorized, crash-consistent, bounded causal
convergence**. Exact validated history and explicit live capabilities authorize
state changes. Clocks, deadlines, leases, TLS sessions, close alerts, counters,
indexes, and reports may restrict or describe execution, but they must not
silently invent work, success, retry authority, or a newer durable cutpoint.

Rev0906 made one invocation finite by session count. This audit found that the
composition was still incomplete in four load-bearing ways:

1. a batch had no one absolute whole-command time cutpoint;
2. a sender's authenticated `no_ready_delivery` close became an erroneous
   receiver failure;
3. a client could finish authentication after its request budget and still
   begin a durable outbox claim before observing the request deadline; and
4. the former 30-second default claim lease could expire while the same
   invocation's own valid staged receipt window was still open.

Rev0907 corrects those contradictions in the shipping C++ path, extracts the
policy from the 3,600-line CLI translation unit into a typed library owner, and
adds deterministic plus real TLS/process proofs. It does **not** claim a hard
real-time preemptive supervisor, a daemon, or a complete sync loop.

## Scope and method

The audit followed the production path from command-line admission through:

`manifest/store/TLS preflight -> session admission -> peer authentication -> outbox claim -> request prefix -> request body -> receipt -> durable application -> shutdown`

It compared the following authorities rather than treating all time-like values
as interchangeable:

- process-local `std::chrono::steady_clock` network cutpoints;
- Linux `CLOCK_BOOTTIME` durable outbox observations;
- the durable outbox clock policy's forward-step, realtime-lag, and uncertainty
  envelope;
- the claim lease's integer-second exclusive expiry;
- TLS closure state; and
- application-frame and durable receipt state.

The audit also inspected CMake sanitizer topology. That found and corrected one
release-proof omission: the new supervisor test was initially compiled with
sanitizer instrumentation but was not linked to the sanitizer runtime.

## Finding 1: a session-count bound was not a command bound

Rev0906 required `--max-sessions`, but every session received a fresh set of
relative staged deadlines. Preflight time was uncharged, and a large session
count could keep an invocation alive far longer than an operator intended.
Session count is a resource bound, not a time cutpoint.

Rev0907 adds mandatory `--max-runtime-seconds` to `send-batch` and
`serve-batch`, restricted to `[1, 86400]`. One absolute steady-clock deadline is
created before deployment, database, payload, listener, membership, and TLS
preflight. A later session cannot be admitted after it. Every stage deadline is
the earlier of its natural staged deadline and that one command deadline.

This is deliberately cooperative rather than preemptive. Poll-driven network
work is bounded by the clamped deadlines, and elapsed synchronous work is
charged at the next admission or deadline observation. A blocking filesystem,
SQLite, crypto, scheduler, or kernel operation is not asynchronously cancelled.
Calling the feature a hard wall-clock kill switch would be false.

## Finding 2: a clean no-work sender session failed the receiver batch

With a batch bound larger than ready work, the sender could authenticate, find
no claimable delivery, send no application bytes, perform a one-way TLS
`close_notify`, and exit successfully as `no_ready_delivery`. The receiver saw
an authenticated peer close before a request prefix and classified the session
as failure. Thus two individually reasonable one-session owners did not compose
into a successful bounded drain.

Rev0907 introduces the exact receiver terminal state
`authenticated_peer_closed_idle`. It is accepted only when all of the following
are true:

- a socket was accepted and its policy was verified;
- the TLS handshake completed;
- peer actor and SPKI evidence are present;
- the receive owner reports peer closure;
- zero request-prefix, request-frame, and request-body bytes were observed;
- no inbound delivery decision exists; and
- no receipt write frontier or receipt bytes exist.

The state means only: **this authenticated receiver session spent no durable
file-delivery authority**. It is not evidence that the peer's queue was empty,
that a catalog was synchronized, or that no work exists elsewhere. TLS closure
is transport evidence; the zero-application-byte predicate is local protocol
evidence. Neither becomes a durable catalog assertion.

Stopping after the idle close is intentional. Continuing would let an
otherwise authenticated peer consume the remaining session quota with empty
connections. A future application-level signed `NO_READY` record could carry a
stronger named protocol meaning, but it would still need an exact queue/catalog
cutpoint and must not be inferred from TLS shutdown alone.

## Finding 3: request admission could begin after its deadline

The client previously checked connect and handshake deadlines, authenticated the
expected peer, and then entered the durable claim path. It did not re-observe the
absolute request deadline immediately before the first claim. Handshake and peer
profile work could therefore consume the request budget while the client still
minted a claim and potentially crossed the request-prefix frontier.

Rev0907 adds `DispatchDeadlineExpired` and checks the request-admission cutpoint
after authenticated-channel construction but before the first durable claim.
The exact clean result requires:

- socket creation, policy verification, connect, handshake, and authenticated
  peer evidence;
- no operation ID, claim ID, or request digest;
- zero request-prefix, frame, and body bytes;
- zero receipt-prefix, frame, and body bytes; and
- no receipt-application result.

Only when that clean result occurs under a command-clamped request stage and the
outer command deadline is actually reached may the supervisor map it to
`command_deadline_reached`. A claim-bearing, byte-bearing, unauthenticated, or
otherwise ambiguous request timeout remains `session_failed`.

The real TLS regression completes mutual authentication with an already expired
request-admission deadline and proves that the client emits no operation ID,
claim, prefix, frame, or body. The ready outbox row remains unleased with zero
dispatch attempts. The receiver observes only an authenticated clean close.

### Remaining frontier

One cooperative gap remains explicit. If the synchronous claim, payload reproof,
or dispatch-guard work starts before the request cutpoint but runs beyond it,
the current path does not perform a second deadline check immediately before
accepting the fixed request prefix. Closing that frontier safely requires a
deadline-aware pre-prefix guard that can release the same fenced claim before
any application byte is accepted. Merely adding a late clock check outside the
transaction would risk converting an authorized claim into an ambiguous retry.

## Finding 4: the default lease contradicted the valid receipt horizon

The former default lease was 30 seconds. The default staged session timeout was
10 seconds, producing these natural cutpoints from session admission:

| Stage | Natural deadline |
| --- | ---: |
| connect | `T` |
| handshake | `2T` |
| request | `3T` |
| receipt | `4T` |
| shutdown | `5T` |

A claim may be created before request transmission while a receipt remains valid
until `4T`. With `T = 10`, transport policy alone therefore admits a 40-second
claim-to-receipt horizon. A 30-second claim can expire while the sender is still
correctly waiting under its own receipt deadline.

The durable clock policy also admits bounded observation movement. For the
current default owner limits:

- maximum forward step `F = 300 s`;
- maximum realtime lag/catch-up `L = 300 s`;
- maximum uncertainty `U = 5 s` at each relevant anchor/endpoint observation;
- four uncertainty allowances are combined; and
- one second is added because durable epochs are floor-converted integer seconds
  and expiry is exclusive.

The necessary static lower bound is:

`minimum lease = 4T + F + L + ceil(4U) + 1`

Therefore:

- `T = 5 s` requires at least `20 + 300 + 300 + 20 + 1 = 641 s`;
- `T = 10 s` requires at least `40 + 300 + 300 + 20 + 1 = 661 s`; and
- `T = 3600 s` requires `15021 s`, still below the durable 86400-second maximum.

The CLI now derives the exact minimum from the same `SyncReplicaSqliteOwnerLimits`
used to construct the sender owner. An absent `--lease-seconds` selects the
minimum; an explicit shorter value is rejected before deployment, database,
payload, or TLS authority opens. A process test snapshots the database family
and payload directory and proves that rejection is mutation-free.

This formula is a **necessary protocol-and-clock lower bound**, not a completion
guarantee. It does not cover arbitrary process descheduling, SQLite writer
waits, local decoding/application work, system suspension, or external resource
starvation. Settlement remains fail-closed if the claim is expired.

The large minimum is also architectural feedback. Long static leases reduce
premature expiry but delay recovery after a dead sender. A mature product should
prefer an exact renewable lease/heartbeat tied to the same fenced claim, or
reduce the admitted clock envelope, rather than silently choosing an unsafe
short default.

## Refactor: one typed composition owner

`sync_replica_session_supervisor.hpp/.cpp` now owns only process-local
composition policy:

- validation of session, stage-timeout, and command-runtime limits;
- one optional absolute command deadline;
- per-session five-stage deadline plans clamped to that command cutpoint;
- typed sender and receiver terminal reasons;
- exact clean dispatch-expiry and authenticated-idle predicates; and
- derivation/validation of the necessary claim-lease horizon.

It does not open a database, claim work, create a listener, authenticate a peer,
write a file, sleep, retry, or persist scheduler state. `send-one` and
`serve-one` use the same executors with one session and no command-wide runtime,
while batch commands must supply both finite bounds.

The library was added to the existing file-TLS product archive rather than
creating another one-source static library. This reduces CLI policy duplication
without growing the already excessive archive/target surface.

## Terminal-policy matrix

### Sender

| Observation | Stop | Success |
| --- | --- | --- |
| session quota consumed | `max_sessions_reached` | yes |
| absolute command cutpoint reached cleanly | `command_deadline_reached` | yes |
| authenticated peer, no claimable delivery | `no_ready_delivery` | yes |
| authenticated receiver pressure deferral | `receiver_deferred` | yes |
| stale/missing/expired local receipt claim | `receipt_apply_conflict` | no |
| transport, authentication, or ambiguous deadline result | `session_failed` | no |

### Receiver

| Observation | Stop | Success |
| --- | --- | --- |
| session quota consumed | `max_sessions_reached` | yes |
| absolute command cutpoint reached at accept | `command_deadline_reached` | yes |
| ordinary first-stage listener deadline | `accept_deadline_expired` | yes |
| exact authenticated zero-application-byte close | `authenticated_peer_closed_idle` | yes |
| partial prefix/frame/body, effect ambiguity, or transport failure | `session_failed` | no |

## Validation

Final release evidence includes:

- GCC 14.2 Debug: **227/227** registered tests passed;
- Clang 17.0 Debug: **227/227** registered tests passed;
- Clang 17 ASan+UBSan focused product lane: **5/5** passed;
- supervisor unit proof: **75 checks**;
- deployment binding source audit: **27/27**;
- database-open policy source audit: **38/38**;
- bootstrap-authority source audit: **25/25**; and
- real multi-process TCP/TLS proof covering two settled deliveries, a third
  authenticated no-work session, receiver idle-close success, whole-command
  accept cutpoint, and mutation-free short-lease rejection.

## Research record and implications

Primary sources reviewed on 2026-07-26:

- TLS 1.3 closure and truncation semantics, RFC 8446:
  https://www.rfc-editor.org/rfc/rfc8446.html
- OpenSSL shutdown state and return semantics:
  https://docs.openssl.org/3.5/man3/SSL_shutdown/
- gRPC deadline model and explicit deadline guidance:
  https://grpc.io/docs/guides/deadlines/
- SQLite busy-timeout accumulated sleeping behavior:
  https://www.sqlite.org/c3ref/busy_timeout.html
- Linux `CLOCK_MONOTONIC` versus suspend-aware `CLOCK_BOOTTIME`:
  https://man7.org/linux/man-pages/man3/clock_gettime.3.html

The sources reinforce five design conclusions:

1. `close_notify` establishes orderly TLS write closure, not application queue
   emptiness. AnonSync must keep transport shutdown and application terminal
   state separate.
2. A timeout should become one absolute deadline at operation start and be
   propagated by reducing remaining budget, not restarted at every layer.
3. A server or local owner must cooperate with cancellation/deadline state;
   merely returning a timeout from an outer layer does not stop inner work.
4. SQLite busy handling can sleep repeatedly before returning `SQLITE_BUSY`, so
   database wait policy must eventually consume the same command budget rather
   than remain an uncharged nested timeout.
5. Linux `steady_clock` commonly follows `CLOCK_MONOTONIC`, which excludes
   suspend, while the durable outbox clock uses `CLOCK_BOOTTIME`, which includes
   it. A suspended machine can therefore age the durable claim while the
   transport deadline appears frozen. Production policy needs one explicit
   suspend model.

## What should change next

The next C++ product slice should close the remaining claim-to-prefix frontier
and begin a durable supervisor rather than adding another parallel assurance
subsystem:

1. propagate one named budget into SQLite busy handling, payload reproof, and
   the dispatch guard;
2. add a transactional pre-prefix deadline check that can release the exact
   fenced claim before any TLS application byte;
3. replace anonymous `First..Fifth` stages with named connect, handshake,
   request, receipt, and shutdown cutpoints;
4. persist typed terminal state so a crash can resume the larger
   scan/reconcile/claim/transfer/apply lifecycle; and
5. design renewable claims whose heartbeat authority is exact, fenced, bounded,
   and revoked on ambiguity.

Longer term, the product still needs complete filesystem semantics, explicit DAG
readiness, indexed anti-entropy checked against full-history truth, quarantine
and repair, retention/GC, cross-store cutpoints, key evolution, and a precise
anonymity/privacy threat model. Rev0907 narrows one critical time-and-session
boundary; it does not substitute for that continuous product spine.
