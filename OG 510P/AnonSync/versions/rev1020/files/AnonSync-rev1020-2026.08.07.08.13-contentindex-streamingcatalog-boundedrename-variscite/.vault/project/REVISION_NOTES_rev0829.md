# AnonSync rev0829 — protocol owner, typed recovery, nested-cause proof

Rev0829 turns the destructive SQLite reset plus immutable receipt publication
from caller choreography into one typed C++ protocol owner.

## Heart of the change

AnonSync's central mission is not merely moving or deleting bytes. It is making
each durable state transition carry enough exact evidence that a caller can tell
what authority still exists after concurrency, retry, process loss, or partial
failure. Rev0828 proved the individual reset and publication frontiers, but the
CLI still assembled them manually:

1. render and prepare a receipt;
2. reset SQLite;
3. remember a Boolean saying the reset looked durable;
4. publish the receipt; and
5. reinterpret unrelated exceptions into retry advice.

That sequence was a second, weaker protocol implementation. Rev0829 replaces it
with `execute_sqlite_replay_ledger_reset_receipt_protocol_or_throw()`. The owner
pre-binds the exact canonical receipt and create-new publication capability,
executes the reset, verifies the returned evidence against the original request
and expected receipt digest, consumes the prepared publication exactly once,
and returns either complete success or a typed failure carrying the strongest
recovery authority established at the failure frontier.

The public failure classification distinguishes preparation, reset failure
before a durable outcome, reset failure after a durable outcome, and receipt
publication failure after a durable outcome. It separately reports the only
authorized recovery action: none, or exact replay of the same request to a fresh
receipt path. Publication outcome and residue remain typed rather than inferred
from an error string.

## Severe audit correction

The reset layer attempted to preserve a post-commit root cause with
`std::throw_with_nested(SqliteReplayLedgerResetDurableOutcomeError(...))`, but
the error type was `final` and did not inherit `std::nested_exception`. Under the
standard `throw_with_nested` rules, no derived wrapper could be formed, so the
original exception was silently discarded. A source-shape audit asserted cause
preservation even though no runtime test traversed the chain.

The error now inherits `std::nested_exception`, and both reset and protocol
oracles traverse the real nested chain to find the injected post-commit or
publication cause. This is a material false-proof repair: the type carried the
durable outcome correctly, but had lost the diagnostic evidence needed to
explain why completion failed.

## Refactor and dependency audit

The CLI no longer renders receipts, owns a prepared publication capability,
tracks a durable-reset Boolean, or manually maps publication failures. The
combined crash/frontier oracle also enters the exact production protocol through
an internal observer seam; it does not maintain look-alike choreography.

The new focused static library declares its contract dependencies explicitly:
reset and atomic-publication types are public dependencies, while reset-document
rendering and SHA-256 are private implementation dependencies. The initial
focused link exposed that this edge had been implicit. A new 24-check structural
audit now protects API ownership, dependency visibility, no-core isolation,
runner delegation, single implementation, typed phase/recovery consistency, and
package inclusion.

## Executable evidence

The combined oracle passes **442 checks**. It covers:

- public first-attempt success;
- receipt preparation denial with no ledger or unrelated-object mutation;
- stale reset denial before durability with no output or temp residue;
- injected reset failure after commit with retained nested cause and exact
  fresh-path recovery;
- all eleven caught publication frontiers with exact outcome/residue evidence;
- all eleven process-exit publication frontiers;
- post-commit parent-directory replacement and competing final objects; and
- exact recovery through the public protocol owner.

Final validation on the frozen source:

- parent ZIP **25/25** and extracted directory **21/21**;
- active-source patch replay **197/197 files**, byte exact;
- source delta **13 files, 1,596 insertions, 217 deletions**;
- GCC 14 Debug all-target build and dependency-closure no-work check: passed;
- complete CTest inventory **116/116** in four disjoint final-source ranges;
- focused final CTest **7/7**;
- reset oracle **68/68**;
- protocol/crash-frontier oracle **442/442**;
- structural audits **223/223**;
- Clang 17 warnings-as-errors focused gate **10/10**; and
- Clang 17 ASan/UBSan focused gate **8/8** with leak detection disabled.

A sustained synchronous-I/O run completed all 25 protocol/crash iterations
(**11,050 checks**) and two reset iterations before the outer tool invocation was
time-limited under cloud-overlay pressure. The reset lane then passed **12/12**
in isolation. This evidence does not establish a product deadlock, nor does the
release claim an uninterrupted stress sequence beyond the completed iterations.

## Claim boundary

The protocol deliberately does not claim a transaction spanning SQLite and an
arbitrary filesystem receipt. It records a recoverable frontier instead. It
also does not prove arbitrary VFS failures, torn writes, storage reordering,
power loss, Windows behavior, hostile-database process isolation, distributed
convergence, payload confidentiality, anonymity, metadata hiding, key lifecycle,
or secure erasure. The focused sanitizer lane does not instrument bundled
SQLite and is not a full-project or leak-safety claim.
