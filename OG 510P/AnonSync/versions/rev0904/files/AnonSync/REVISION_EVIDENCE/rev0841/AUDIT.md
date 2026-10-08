# AnonSync rev0841 deep audit

## Executive verdict

AnonSync has a coherent and technically serious heart: **turn observations into exact,
owned, bounded authority before any durable or externally visible transition**. Its best
work is the local authority kernel around process incarnation, SQLite connection and
transaction ownership, namespace-safe publication, replay ledgers, snapshot sealing,
owner generations, bounded verification, and crash-aware recovery.

The codebase is not yet what its name can lead a reader to assume. “Convergence” is not
backed by an executable distributed model, and “Anon” is not backed by a payload/privacy
protocol. The honest product description today is: **a fail-closed local evidence,
integrity, and recovery substrate for a future convergent private synchronizer**.

Rev0841 fixes one high-impact instance where the implementation violated its own doctrine:
a signed effect transition had two construction paths and ambient-locale security bytes.

## Heart of the mission

The central rule is stronger than ordinary input validation:

1. identify the invariant owner;
2. copy or move the exact value into that owner;
3. bind identity, generation, lifetime, policy, relationships, schema, and budgets;
4. derive signatures, hashes, database mutations, and publication bytes only from that
   exact value;
5. publish atomically and retain enough durable evidence to recover or reject after
   interruption; and
6. make replicas that receive equivalent authorized operations reach equivalent state.

Steps 1–5 are increasingly concrete in the repository. Step 6 remains mostly an
aspiration and should become the next center of gravity.

## Severe rev0840 defect: the signature did not own its publication

`make_effect_transition_intent_json_for_relay` assembled newline-delimited signature
bytes directly from `EffectOutboxClaimResult`, `RelayDownstreamResult`, and a reason. It
then opened a separate stream and assembled JSON by reading those broad objects again.
Validation, signature construction, and emission therefore did not share one immutable
source value. A future field addition, transformation, mutation, or validation mismatch
could produce a signed interpretation different from the emitted interpretation.

This is the same class of defect rev0840 removed from heartbeat publication. It was
especially serious here because the bytes authorize a durable terminal effect transition,
not merely a diagnostic heartbeat.

Rev0841 introduces `FrozenEffectTransitionIntentV3Payload`. The relay performs one mapping
into all signed fields, freezes and validates them, derives one v3 signing input, signs it,
binds the digest/signature back to the frozen payload, and emits JSON only from the bound
publication. The encoder cannot reach the broad claim or downstream result types.

## Severe rev0840 defect: ambient locale changed security bytes

The parent used `std::ostringstream` for both signed numeric material and JSON. Streams
inherit the global C++ locale at construction. The preserved witness installs a grouping
facet and turns sequence `7000` into `7_000`. A strict JSON parser rejects the output, and
the signing input differs from the classic-locale input.

Rev0841 uses `std::to_chars` in the v3 owner and never uses a stream for v3 signing or JSON.
Every older stream that remains in `sqlite_replay_ledger.cpp` now immediately imbues
`std::locale::classic()`. This seals one security-critical translation unit; it does not
claim the rest of the repository is classified.

## C++ correction

The new dependency-light leaf owns:

- all thirteen signed payload fields;
- exact fixed format/subject/backend constants;
- lowercase SHA-256 or genesis constraints;
- canonical UTC syntax and real calendar dates;
- terminal-state allowlisting;
- positive integer values no greater than `2^53 - 1`, matching the current JSON parser's
  exact integer domain;
- well-formed UTF-8 and ASCII-control rejection for free text and signer identity;
- explicit reason, signer, signature, signing-input, input-document, and JSON byte limits;
- unpadded base64url signature spelling;
- field-named, byte-length-prefixed v3 signing input;
- signing-input SHA-256 recomputation before publication binding; and
- JSON emission exclusively from the frozen publication.

Legacy v2 verification remains because removing historical readability would strand
valid durable evidence. Production minting selects v3 only. V2's newline format is not
renamed “canonical”; it is compatibility input.

## What is still missing

### 1. Executable convergence semantics

There is no small, deterministic reference model that defines which operations commute,
which require causal order, which are idempotent, which retract prior facts, how deletes
interact with concurrent updates, and when coordination is unavoidable. Without that,
local ledger integrity can prove that every replica kept a valid history while those
histories still disagree permanently.

The next major C++ feature should be an operation algebra and trace oracle that generates
and differentially checks duplicate, reordered, partitioned, concurrent, retried,
restart, schema-epoch, and key-epoch histories against production transitions.

### 2. Whole-protocol crash cuts

The repository has unusually strong component-level crash work, but the real protocol
crosses SQLite main/WAL files, manifests, receipts, checkpoint files, staging names,
directory sync, and external side effects. These resources need one recovery oracle.
Structural database validity alone does not prove that a downstream effect, receipt, and
ledger terminal transition agree after every cut.

### 3. Hostile-input process isolation

Hostile SQLite and document verification are bounded but still commonly execute inside
the main process. Budgets reduce denial-of-service risk; they do not contain memory-safety
or parser defects. A disposable descriptor-only worker should receive sealed bytes, run
under CPU/memory/wall-clock limits and layered syscall/filesystem/network restrictions,
return one bounded result, and be killed on protocol deviation.

### 4. Privacy and key lifecycle

No implemented layer currently justifies anonymity, confidentiality, metadata hiding,
forward secrecy, post-compromise recovery, multi-device enrollment, key rotation,
revocation, recovery after state loss, backup key handling, or secure deletion. A signed
heartbeat or signed transition authenticates a statement; it does not solve these
properties.

### 5. Serializer classification

The critical SQLite replay-ledger translation unit is now sealed, but the repository
still contains many stream-based reports, journals, operator JSON documents, and signing
inputs. Each site needs classification, not a blind helper call: diagnostics may remain
human-oriented; machine bytes need an owner, exact encoding contract, explicit locale or
locale-free formatting, UTF-8 policy, size budget, version, and perturbation tests.

## Where the project has become wasteful

### Monoliths are now correctness hazards

`src/sync_domain.cpp` is 15,287 lines and 1.12 MB;
`src/sync_domain_selftests.cpp` is 9,348 lines and 805 KB; and `CMakeLists.txt` is 2,258
lines and 115 KB. These are not merely aesthetic problems. They enlarge rebuilds, hide
ownership boundaries, make sanitizer/tool runs expensive, and encourage broad includes.
During rev0841, compiling the monolithic sanitizer executable exceeded the cloud command
window even though the new leaf and the exact relay implementation could be sanitized.

Continue extracting invariant-owned libraries, but require a measurable dependency and
semantic boundary for each extraction. Splitting by file size alone would only distribute
the monolith.

### Evidence volume is outgrowing implementation learning

Before rev0841, `REVISION_EVIDENCE` occupied about 23.7 MB while first-party `src/` occupied
about 4.4 MB. Historical evidence is useful, but copying every prior revision into each
new package makes transfer, review, and verification progressively more expensive. Use a
content-addressed evidence store or periodic checkpoint archives; keep the current package
self-verifying but include only the current handoff plus a compact lineage index.

### Lexical audits can create false confidence

The package registers 39 audit tests and carries 40 `audit_*.py` tools. Some guard valuable
architecture facts, but source-text matching is fragile under harmless refactors and
cannot prove runtime semantics. Every lexical audit should answer: what defect would a
typed API, compile-time dependency rule, property test, model checker, or runtime
invariant prevent more directly? Retire audits after the stronger mechanism exists.

### The name outruns the claims

The README has improved its caveats, but the project still risks optimizing local proof
artifacts while leaving the user-facing convergence and privacy protocols undefined.
Make the non-claims visible in interfaces and threat-model documents, not only release
notes. Otherwise a sophisticated local integrity kernel may be mistaken for a secure
anonymous synchronization product.

## Recommended architectural direction

Use a repeated **authority capsule** pattern:

- a narrow owning value with no access to broad mutable orchestration state;
- a total validator that returns a typed cause;
- deterministic versioned bytes;
- explicit maximum retained and emitted size;
- one consumer capability for the authorized transition; and
- a recovery receipt that names the exact capsule digest and generation.

Build the distributed layer around an explicit operation model rather than around files.
Separate data-plane ciphertext/chunks from control-plane causal operations, device/key
epochs, and revocation. Treat SQLite and atomic files as implementations of durable local
state, not as the convergence semantics themselves.

## Validation evidence

- active source delta: **6 files**, **1,101 insertions**, **103 deletions**;
- active projection: **236 files**, **17,025,831 bytes**;
- frozen publication leaf: **34/34**;
- signed-transition integration: **8/8**;
- relay crash/retry/idempotency under grouped locale: **11/11**;
- snapshot-manifest compatibility: **23/23**;
- complete final CTest inventory: **133/133**, including **39/39** audits;
- Clang 17 `-Werror` focused checks: pass;
- GCC 14 ASan+UBSan + leak detection: leaf and relay pass;
- final GCC Debug all-target build: pass; and
- final dependency closure: no work.

A full-project sanitizer, Release all-target build, arbitrary power-loss proof, Windows
runtime, distributed convergence proof, privacy protocol, hostile worker sandbox, and
secure erasure remain unclaimed.
