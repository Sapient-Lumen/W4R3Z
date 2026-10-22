# REV0613 DISPATCH RECONCILIATION INVENTORY — /run handoff

## Verified product boundary

Revision 0613 is the current verified release. The public handoff contains
exactly two root-level files: the single static `natravcube` executable and this
`BOOTSTRAPROSE.md`. Complete source custody, verification evidence, build logs,
and reconstruction material remain separate artifacts rather than additional
runtime products.

The promoted binary reports `version: 0613` and these authority markers:

```text
custody_dispatch_policy: V24_EXPLICIT_OWNER_CUSTODY_DISPATCH_V1
custody_dispatch_reconciliation: READ_ONLY_STATUS_AND_CURSOR_INVENTORY_V1
explicit_owner_custody_dispatch: true
automatic_custody_sender: false
automatic_route_relay: false
open_relay: false
```

## Authority established in revision 0613

1. Authenticated owner commands now reconcile one exact V24 dispatch identity
   or enumerate its finite dispatch index without resubmitting a mutating
   request. Both operations lease the current accepted configuration and resolve
   the exact current V24 activation, its V23 receiver, outbound V22 rule, V21
   grant, route commitment, signing generations, peer certificate commitment,
   and local certificate commitment.
2. Exact status follows one existing `dispatch-index` entry to one exact V22
   case and one exact owner-dispatch record. It validates the retained signed
   offer, custody envelope digest, reverse envelope index, attempt reservation,
   result metadata, acceptance metadata, and current activation commitment.
3. Inventory validates every bounded index entry before pagination, rejects
   symlinks and noncanonical names, sorts canonical request identities
   lexicographically, and returns finite cursor-bounded metadata pages with
   explicit record-count and JSON-byte ceilings.
4. Historical records remain observable after later explicit attempts advance
   the shared V22 counter. Only the exact one-increment crash boundary is
   accepted as pending; broader counter disagreement fails closed.
5. `ACTIVE`, `RETIRED`, expired, and `REVOKED` authority remain observable as
   metadata. Revocation never replays acceptance bytes or creates a network
   action. Missing, malformed, zero, conflicting, or cross-bound retained state
   fails closed.
6. The observation implementation uses read-only path checks and the existing
   authenticated daemon control channel. It performs no filesystem mutation,
   index repair, attempt reservation, network exchange, retry, route discovery,
   fallback, export, import, forwarding, or delivery inference.
7. UID/class authorization, restart and stale-seed reconstruction, quiesce and
   drain observation, bounded ordinary-worker progress, and concurrent ordinary
   application traffic remain governed by the existing daemon.
8. The release remains one executable. No second listener, protocol, daemon,
   scheduler, forwarding queue, database, helper executable, or runtime sidecar
   was added.

The owner reconciliation surface is:

```text
natravcube custody-dispatch-status \
  --control PATH \
  --activation ID --activation-generation N \
  --dispatch-request HEX64 [--deadline-ms N]

natravcube custody-dispatch-inventory \
  --control PATH \
  --activation ID --activation-generation N \
  [--cursor HEX64] [--limit N] [--max-bytes N] [--deadline-ms N]
```

The earlier explicit dispatch and custody service commands remain separate and
unchanged.

## Next mandatory construction step

Build revision 0614 as stable read-only inventory reconciliation, not another
attempt or forwarding surface:

1. Add an optional exact inventory-snapshot commitment to the authenticated
   inventory request and return one canonical commitment over the current V24
   authority, accepted configuration, sorted validated dispatch identities, and
   metadata rows used by the page.
2. A first page without an expected commitment may compute and return the
   commitment. Every later page that supplies it must fail closed if any
   relevant authority, index, record, offer, envelope, attempt, result, or
   acceptance metadata changed. Never silently combine pages from different
   inventory states.
3. Preserve finite scan, row, JSON, cursor, deadline, and control-frame bounds.
   Snapshot computation must remain read-only and must not acquire mutation
   authority, repair an index, reserve an attempt, hold a long-lived global
   write lock, or block ordinary daemon progress.
4. Keep `ACTIVE`, `RETIRED`, expired, and `REVOKED` metadata semantics exact.
   A snapshot commitment is observation evidence only; it is not a receipt,
   acceptance, delivery claim, retry token, forwarding grant, or authority to
   reveal retained acceptance bytes.
5. Test a dispatch committed between pages, lifecycle/configuration changes,
   malformed and symlinked state, restart, lost control responses, real-UID
   authorization, drain, bounded capacity, exact duplicate pages, and concurrent
   ordinary traffic while proving zero filesystem mutation and zero network
   attempts.
6. Before promotion, repeat closed-world source verification, strict static and
   ASan/UBSan builds, focused custody/reconciliation suites, risk-adjacent
   suites, the complete registered matrix, exact predecessor reconstruction,
   frozen-archive extraction, and a byte-identical clean rebuild.

## Promotion rule

Promote a later revision only if every required gate passes and its public
handoff again contains exactly `natravcube` and `BOOTSTRAPROSE.md`. Otherwise
keep revision 0613 as latest verified and label later work as construction only.

---

# REV0612 EXPLICIT OWNER CUSTODY DISPATCH — /run handoff

## Verified product boundary

Revision 0612 is the current verified release. The public handoff contains
exactly two root-level files: the single static `natravcube` executable and this
`BOOTSTRAPROSE.md`. Complete source custody, verification evidence, build logs,
and reconstruction material remain separate artifacts rather than additional
runtime products.

The promoted binary reports `version: 0612` and these negative-authority
markers:

```text
custody_dispatch_policy: V24_EXPLICIT_OWNER_CUSTODY_DISPATCH_V1
explicit_owner_custody_dispatch: true
automatic_custody_sender: false
automatic_route_relay: false
open_relay: false
```

## Authority established in revision 0612

1. Canonical V24 dispatch authority binds one exact immutable local V23 receiver
   activation, one exact outbound V22 rule, one explicitly named enabled route
   commitment, finite concurrent-dispatch and attempt bounds, finite expiry, and
   monotonic `ACTIVE`, `RETIRED`, or `REVOKED` lifecycle. Absence of V24 leaves
   ordinary-daemon dispatch disabled.
2. The authenticated local-control command `custody-dispatch` names one exact
   retained receiver request, one fresh owner dispatch request identity, and a
   bounded reason. It exposes no route override or retry flag and can commit at
   most one outbound attempt for that owner request.
3. Before carrier use, the daemon proves from the authenticated custody journal
   that it is still the exact current nonterminal custodian and that the retained
   offer, acceptance, envelope, capsule, grants, and record prefix are exact. It
   derives the outbound case from those retained bytes rather than accepting an
   owner-supplied replacement bundle.
4. The dispatch request and exact authority commitments are durably reserved
   before the attempt counter or network I/O. An exact duplicate recovers the
   retained result and performs no connection. Reusing the identity with
   different bytes is a hard conflict. Restart after reservation cannot invent a
   second attempt.
5. A later attempt against unresolved V22 state requires another fresh explicit
   owner request. Each request reuses the existing V22 sender state machine,
   signed offer and acceptance, response-loss uncertainty, finite attempt
   counter, peer certificate checks, configuration lease, and custody journal.
6. `ACTIVE` may reserve one new request. `RETIRED` or expired V24 may return only
   the exact locally retained result for an already recorded request. `REVOKED`
   permits neither a new attempt nor replay of a remote acceptance. Downgrade,
   redefinition, removal, and lifecycle rollback are rejected during activation
   and authenticated journal replay.
7. Bounded concurrency reserves ordinary control and peer progress. The command
   obeys the existing UID/class authorization and lifecycle gates, while
   concurrent ordinary application traffic continues through the same daemon.
8. First-hop receipt never invokes V24. The daemon has no forwarding queue,
   background retry, timer, route discovery, route search, fallback, export,
   final-recipient import, delivery inference, second protocol, second daemon,
   or second executable.

The owner dispatch surface remains inside the one executable:

```text
natravcube custody-dispatch \
  --control PATH \
  --activation ID --activation-generation N \
  --receiver-request HEX64 --dispatch-request HEX64 \
  --reason TEXT [--deadline-ms N]
```

The earlier explicit custody service commands remain available and separate.

## Next mandatory construction step

Build revision 0613 as bounded read-only owner reconciliation, not another
attempt surface:

1. Add an authenticated local-control status operation naming one exact V24
   activation and dispatch request identity. Resolve the current accepted
   configuration and read only the existing bounded record colocated with the
   V22 case.
2. Add finite cursor-bounded inventory over the existing dispatch index so an
   owner can reconcile a lost local-control response without resubmitting the
   mutating request. Return identities, lifecycle, attempt count, result state,
   and cryptographic commitments, not an owner-selectable route or invented
   acceptance.
3. The observation path must perform no network I/O, attempt, mutation, index
   repair, retry, route discovery, fallback, export, import, forwarding, or
   delivery inference. It must not bypass V24 revocation's prohibition on remote
   acceptance replay.
4. Preserve UID/class authorization, configuration leases, bounded reads,
   quiesce/drain semantics, stale-seed reconstruction, and ordinary application
   progress. Missing, malformed, or conflicting record/index bytes fail closed.
5. Test lost control responses, duplicate and conflicting identities,
   ACTIVE/RETIRED/REVOKED policy, expiry, restart, malformed state, pagination,
   authorization, drain, and concurrent ordinary traffic.
6. Before promotion, repeat source-manifest verification, strict static and
   sanitizer builds, focused custody suites, risk-adjacent suites, the complete
   registered matrix, and frozen-archive extraction with a byte-identical clean
   rebuild.

## Promotion rule

Promote a later revision only if every required gate passes and its public
handoff again contains exactly `natravcube` and `BOOTSTRAPROSE.md`. Otherwise
keep revision 0612 as latest verified and label later work as construction only.

---

# REV0611 PASSIVE DAEMON CUSTODY RECEIVER — /run handoff

## Verified product boundary

Revision 0611 is the current verified release. The public handoff contains
exactly two root-level files: the single static `natravcube` executable and this
`BOOTSTRAPROSE.md`. Complete source custody, verification evidence, build logs,
and reconstruction material remain separate artifacts rather than additional
runtime products.

The promoted binary reports `version: 0611`. Custody receipt in the ordinary
daemon is default-off unless the accepted configuration contains one exact V23
activation:

```text
custody_receiver_policy: V23_PASSIVE_DAEMON_CUSTODY_RECEIVER_V1
passive_daemon_custody_receiver: true
native_custody_session: NATIVE_DURABLE_CUSTODY_SESSION_SERVICE_V1
automatic_custody_sender: false
automatic_route_relay: false
open_relay: false
```

## Authority established in revision 0611

1. A canonical V23 receiver-activation record binds one exact immutable V22
   rule id, generation, and commitment, a finite in-flight limit, a finite
   expiry, and monotonic `ACTIVE`, `RETIRED`, or `REVOKED` lifecycle state.
   Absence of such a record leaves ordinary-daemon custody receipt disabled.
2. V23 is accepted only at the exact V21 next-hop endpoint and cannot outlive,
   weaken, redefine, remove, or downgrade its retained V22/V21 authority.
   Receiver retirement and revocation are monotonic through live activation and
   authenticated configuration-journal replay.
3. The ordinary daemon owns one passive receiver callback inside its existing
   authenticated NOS1 listener. It reuses the existing listener, TLS context,
   peer-session framing, `NodeState`, configuration journal, custody journal,
   worker pool, and state directory. No custody listener, protocol, daemon,
   executable, queue, scheduler, or authority ledger was added.
4. Every custody operation leases the live accepted configuration. Live V23
   activation is visible to a previously opened authenticated NOS1 session;
   retirement waits for an in-flight durable operation and governs the next
   operation. Restart from a stale startup seed reconstructs the latest accepted
   V23 lifecycle from the authenticated journal.
5. `ACTIVE` may admit a new exact offer. `RETIRED` or expired authority may
   return only a byte-identical acceptance already retained for that exact
   request. `REVOKED` admits and replays nothing. The existing V22/V21 rule,
   endpoint role, signing generation, certificate commitment, limits, bundle,
   signed offer, signed acceptance, and custody journal remain authoritative.
6. The finite V23 in-flight limit must reserve at least one ordinary peer
   worker. Concurrent tests prove that a paused custody admission cannot consume
   all ordinary application progress. Exhaustion returns an explicit busy
   result and creates no invented acceptance.
7. Response loss, process death after durable acceptance publication, restart,
   duplicate recovery, expiry, retirement, revocation, and stale configuration
   preserve the exact retained bytes and uncertainty semantics. Receipt creates
   no ordinary outbox work or implicit second-hop custody case.
8. The daemon receiver has no authority to originate offers, export bundles,
   choose routes, retry, discover peers, fail over, schedule onward custody,
   import final application evidence, or infer application success or delivery.
   Explicit owner commands from earlier revisions remain separate and unchanged.

The explicit owner command surface remains inside the one executable:

```text
natravcube custody-service-v1-send \
  --config FILE --rule ID --rule-generation N --route ROUTE_ID --bundle FILE
natravcube custody-service-v1-serve \
  --config FILE --rule ID --rule-generation N [--once yes|no]
natravcube custody-service-v1-status \
  --config FILE --rule ID --rule-generation N [--bundle FILE]
natravcube custody-service-v1-export \
  --config FILE --rule ID --rule-generation N --request HEX64 --output NEWFILE
natravcube custody-service-v1-version
```

The passive ordinary-daemon receiver is controlled only by accepted V23 policy;
it adds no separate public command.

## Next mandatory construction step

Build revision 0612 from this verified tree without introducing autonomous
forwarding:

1. Add a default-off, monotonic V24 owner-dispatch activation that binds one
   exact local V23 receiver authority to one exact outbound V22 rule and one
   explicitly named enabled route. Give it finite concurrent-dispatch, attempt,
   and expiry limits and explicit `ACTIVE`, `RETIRED`, and `REVOKED` semantics.
2. Add one authenticated local-control operation that names an exact retained
   receiver request and explicitly performs at most one newly committed outbound
   custody attempt through the ordinary daemon's existing NOS1 client path. It
   must first prove from the authenticated custody journal that the local node
   is the current nonterminal custodian and that the retained bundle is exact.
3. Reuse the existing V22 sender state machine, signed offer and acceptance,
   response-loss uncertainty, attempt counter, configuration lease, peer
   authentication, and custody journal. Add no forwarding queue, background
   worker, timer, discovery, route search, fallback, second protocol, daemon,
   executable, or parallel ledger.
4. A first-hop acceptance must never invoke V24 automatically. Each outbound
   attempt requires a fresh explicit owner request; retirement allows only exact
   retained result recovery, and revocation permits neither an attempt nor
   replay of remote acceptance.
5. Define and test duplicate local-control requests, process death at every
   durable boundary, lost control and peer responses, live policy changes,
   route and certificate changes, capacity, expiry, stale startup seeds,
   graceful drain, and concurrent ordinary application traffic.
6. Before promotion, repeat source-manifest verification, strict static and
   sanitizer builds, focused receiver/sender/custody suites, risk-adjacent
   suites, the complete registered matrix, and frozen-archive extraction with a
   byte-identical clean rebuild.

## Promotion rule

Promote a later revision only if every required gate passes and its public
handoff again contains exactly `natravcube` and `BOOTSTRAPROSE.md`. Otherwise
keep revision 0611 as latest verified and label later work as construction only.

---

# REV0610 EXPLICIT TWO-HOP CUSTODY AND DURABILITY CUTPOINTS — /run handoff

## Verified product boundary

Revision 0610 is the current verified release. The public handoff contains
exactly two root-level files: the single static `natravcube` executable and this
`BOOTSTRAPROSE.md`. Complete source custody, verification evidence, build logs,
and reconstruction material remain separate artifacts rather than additional
runtime products.

The promoted binary reports `version: 0610`. Custody remains an explicit owner
maintenance action:

```text
native_custody_session: NATIVE_DURABLE_CUSTODY_SESSION_SERVICE_V1
custody_retained_export: EXPLICIT_CURRENT_CUSTODIAN_BUNDLE_EXPORT_V1
custody_session_transport: NOS1_BOUNDED_REUSE_V1
configured_custody_relay: true
automatic_route_relay: false
open_relay: false
```

## Authority established in revision 0610

1. Deterministic test-only pauses bracket all required durability boundaries:
   before and after offer publication, envelope-index reconstruction, attempt
   increment, receiver acceptance publication, receiver journal commit, sender
   acceptance publication, and sender journal commit. The fixture kills the
   process externally; the normal executable has no crash or fault-schedule
   command.
2. Restart at every boundary preserves exact signed bytes, finite counters,
   uncertainty, duplicate recovery, and the existing authenticated custody
   journal. No cutpoint mints a second request identity or acceptance.
3. `custody-service-v1-export` reads one exact retained offer and acceptance and
   requires the authenticated journal to prove that the local node is still the
   current nonterminal custodian. It does not repair or mutate the authenticated
   custody journal or retained service case, select a route, or perform network
   I/O. It preserves the canonical envelope, capsule, grants, and record prefix.
4. A composed `A → R → B` transfer requires two separate V22 rules, V21 grants,
   certificate commitments, explicit routes, finite limits, signed offers,
   signed acceptances, and owner invocations. Receipt of `A → R` does not create,
   schedule, or connect the `R → B` transition.
5. The second hop preserves response-loss uncertainty, byte-identical replay,
   restart recovery, route immutability, certificate binding, capacity and
   attempt bounds, expiry, retirement, revocation, and stale-seed rejection.
6. Neither acceptance grants discovery, route search, fallback, opportunistic
   forwarding, open relay, final-recipient import, application success, an exact
   application receipt, or delivery evidence.

The command surface remains inside the one executable:

```text
natravcube custody-service-v1-send \
  --config FILE --rule ID --rule-generation N --route ROUTE_ID --bundle FILE
natravcube custody-service-v1-serve \
  --config FILE --rule ID --rule-generation N [--once yes|no]
natravcube custody-service-v1-status \
  --config FILE --rule ID --rule-generation N [--bundle FILE]
natravcube custody-service-v1-export \
  --config FILE --rule ID --rule-generation N --request HEX64 --output NEWFILE
natravcube custody-service-v1-version
```

## Next mandatory construction step

Build revision 0611 from this verified tree without adding sender or forwarding
authority to the ordinary daemon:

1. Add a monotonic accepted V23 receiver-activation record for one exact local
   V22 rule id and generation. It is default-off when absent and has explicit
   finite `ACTIVE`, `RETIRED`, and `REVOKED` semantics without weakening V22 or
   V21 history.
2. Dispatch enabled custody offers through the ordinary daemon's existing NOS1
   listener, TLS context, authenticated peer session, `NodeState`, configuration
   journal, and custody journal. Do not add another listener, socket protocol,
   thread-owned service, daemon, executable, or state ledger.
3. Keep the daemon receiver passive. It may admit and exactly replay an
   authorized offer; it must not originate offers, export bundles, choose routes,
   retry, discover peers, schedule onward custody, or infer application delivery.
4. Define and test live activation, retirement, revocation, in-flight sessions,
   graceful shutdown, process death, restart, stale startup seeds, capacity,
   expiry, wrong rules, generations, roles, and certificate commitments.
5. Run enabled and disabled custody receipt concurrently with ordinary
   application operations and prove bounded fairness, unchanged application
   semantics, exact response-loss recovery, and no automatic second hop.
6. Before promotion, repeat source-manifest verification, strict static and
   sanitizer builds, focused native and custody suites, risk-adjacent suites,
   the complete registered matrix, and frozen-archive extraction with a
   byte-identical clean rebuild.

## Promotion rule

Promote a later revision only if every required gate passes and its public
handoff again contains exactly `natravcube` and `BOOTSTRAPROSE.md`. Otherwise
keep revision 0610 as latest verified and label later work as construction only.

---

# REV0609 NATIVE DURABLE CUSTODY SESSION SERVICE — /run handoff

## Verified product boundary

Revision 0609 is the current verified release. The public handoff contains
exactly two root-level files: the single static `natravcube` executable and this
`BOOTSTRAPROSE.md`. Complete source custody, verification evidence, build logs,
and reconstruction patches remain separate artifacts; they are not additional
runtime products.

The promoted binary is built from the complete revision-0609 source tree and
reports `version: 0609`. Its explicitly invoked custody service is configured,
but ordinary routes still do not relay automatically:

```text
native_custody_session: NATIVE_DURABLE_CUSTODY_SESSION_SERVICE_V1
custody_session_transport: NOS1_BOUNDED_REUSE_V1
configured_custody_relay: true
automatic_route_relay: false
open_relay: false
```

## Authority established in revision 0609

1. `CustodyTransferOffer` and `CustodyTransferAcceptance` are bounded NOA1
   application messages carried only inside the existing mutually authenticated,
   reusable NOS1 peer session. The custody-only socket, TLS context, framing,
   and duplicate peer-authentication path are removed.
2. Each invocation resolves one accepted V22 rule and its exact immutable V21
   grant, endpoint signing generations, local accepted-configuration digest,
   local DER-certificate SHA-256, authenticated peer DER-certificate SHA-256,
   and one explicitly named enabled sender route. The shared V22 rule contains
   no route, carrier, host, port, discovery, failover, or forwarding choice.
3. The sender durably commits the complete signed `NHCSO001` offer before any
   carrier use and durably increments its finite attempt counter before each
   network attempt. Failure or response loss remains unresolved.
4. The receiver verifies the exact signed offer and authority, durably commits
   the complete signed `NHCSA001` acceptance before its NOS1 response, and then
   records the same transition in the existing authenticated custody journal.
   Exact duplicate requests recover only byte-identical retained acceptance.
5. Request identity covers the complete signed offer. One custody envelope may
   bind only one request identity. Recovery reconstructs missing derived
   envelope metadata and its reverse index from the retained canonical signed
   offer, closing the process-crash interval immediately after `offer.bin`.
6. ACTIVE authority may create a transition. RETIRED authority may recover only
   retained exact facts. REVOKED authority cannot originate, retry, listen, or
   replay acceptance. Accepted V22 history cannot be erased, redefined,
   downgraded, or moved to a less restrictive lifecycle.
7. Custody acceptance is one transition of responsibility. It is not capsule
   import, application admission, action execution, an exact application
   receipt, or delivery. No discovery, route search, automatic failover,
   background retry, onward forwarding, transparent bridge, global consensus,
   or open relay is introduced.

The command surface remains inside the one executable:

```text
natravcube custody-service-v1-send \
  --config FILE --rule ID --rule-generation N --route ROUTE_ID --bundle FILE
natravcube custody-service-v1-serve \
  --config FILE --rule ID --rule-generation N [--once yes|no]
natravcube custody-service-v1-status \
  --config FILE --rule ID --rule-generation N [--bundle FILE]
natravcube custody-service-v1-version
```

## Next mandatory construction step

Build revision 0610 from this verified tree without broadening relay authority:

1. Exercise deterministic process-death cutpoints at every service durability
   boundary: before and after offer publication, envelope-index reconstruction,
   attempt increment, receiver acceptance publication, receiver journal commit,
   sender acceptance publication, and sender journal commit. A test fixture may
   control process death; the normal product must not gain a fault-schedule or
   crash-injection command.
2. Compose two separately authorized transitions `A → R` and `R → B`. Each
   transition must have its own exact V22 rule, V21 grant, certificate
   commitments, explicit route, finite limits, signed offer, signed acceptance,
   and owner invocation. Prove that receipt of the first acceptance does not
   schedule or initiate the second transition.
3. If retained receiver bytes need an owner export or send-retained command,
   make it read only the already authenticated custody case, require that the
   local node is the exact current custodian, preserve the original envelope and
   capsule bytes, and create no parallel authority ledger or autonomous queue.
4. Across both transitions, prove response-loss uncertainty, exact replay,
   restart recovery, route-switch rejection, certificate mismatch, capacity and
   attempt bounds, expiry, retirement, revocation, and stale-seed resistance.
5. Prove negative authority explicitly: no discovery, route search, fallback,
   opportunistic forwarding, open relay, final-recipient import, application
   success, or delivery receipt follows from either custody acceptance.
6. Before promotion, repeat source-manifest verification, strict static and
   sanitizer builds, the focused native service and custody-authority suites,
   risk-adjacent suites, the complete registered matrix, and frozen-archive
   extraction/rebuild equivalence.

## Promotion rule

Promote a later revision only if every required gate passes and its public
handoff again contains exactly `natravcube` and `BOOTSTRAPROSE.md`. Otherwise
keep revision 0609 as latest verified and label later work as construction only.

---

# REV0608 NATIVE CUSTODY SESSION AUTHORITY — /run handoff

## Status and product boundary

This tree is a **construction candidate, not a promoted release**. The latest
verified handoff remains rev0606 and consists of exactly the root-level
`natravcube` binary and this `BOOTSTRAPROSE.md`. Keep complete source custody,
verification logs and patches outside that two-file product handoff.

Do not promote rev0608 merely because it compiles. Promotion requires removal
of the remaining dedicated custody transport path and completion of the native
NOS1 durable service described below.

## Authority established in rev0608

Rev0608 introduces a bounded native seam without granting routing authority:

1. `CustodyTransferOffer` and `CustodyTransferAcceptance` are first-class
   NOA1 `ApplicationMessage` variants and therefore travel only inside an
   authenticated reusable NOS1 peer session. The legacy one-operation path
   cannot carry either variant.
2. The secure server dispatches an offer only through an explicit custody
   callback. A node without that callback returns the typed
   `CUSTODY_SESSION_NOT_CONFIGURED` failure.
3. V22 adds a canonical monotonic `custody_service_hex` rule. One shared rule
   commits the exact V21 grant, endpoint certificate SHA-256 commitments,
   finite pending/bundle/attempt/window bounds and expiry. It contains no
   route, carrier, host, port, discovery or forwarding choice.
4. Active V22 authority is accepted only when the exact V21 grant is active,
   the local and peer generations match, the peer generation is retained and
   active, at least one explicit peer route is enabled, and V22 limits do not
   exceed V21. Accepted V22 history and lifecycle state cannot be removed,
   redefined or downgraded during replay.
5. TLS session evidence now records both the existing SPKI pin and the exact
   peer-certificate DER SHA-256 commitment so the service can enforce the V22
   certificate identity without weakening ordinary peer admission.

These facts do **not** yet make rev0608 promotable. The inherited
`custody-service-v1-*` implementation still owns a separate framed mTLS
transport. It remains construction material only and must not be treated as
native service completion.

## Next mandatory construction step

Build the next revision directly from this tree:

1. Migrate the durable sender and receiver state machines behind
   `custody-service-v1-send`, `custody-service-v1-serve` and status recovery to
   `OutboundPeerSession::exchange_message` and the secure server's explicit
   `CustodySessionHandler`. Delete the private TCP/TLS custody framing and all
   duplicate peer-authentication code after parity is proven.
2. Bind each invocation to one active V22 rule, its exact V21 grant, the
   accepted local configuration digest, the exact local certificate digest,
   the authenticated peer certificate digest and an explicitly named peer
   route. Never choose another carrier or next hop automatically.
3. Durably commit the byte-identical signed offer and incremented attempt
   counter before any network I/O. On the receiver, durably commit the
   byte-identical signed acceptance before returning it. On timeout or lost
   response, retain unresolved state; retry only the same offer and recover
   only the same acceptance after restart.
4. Make duplicate handling idempotent by request id plus complete offer bytes.
   A reused id with different bytes is a hard conflict. A retained exact
   acceptance may be replayed; no delivery receipt or application success may
   be inferred.
5. Prove that two enabled carriers remain only two explicitly selectable
   routes. They must not create discovery, failover, forwarding, route search,
   open relay, onward custody or final-recipient import.
6. Add focused response-loss/restart, exact-replay, wrong-certificate,
   retired/revoked-rule, expiry, attempt/window/capacity and two-carrier
   non-router tests. Then run source-manifest verification, strict static and
   sanitizer builds, custody-authority and risk-adjacent suites, and the full
   matrix before considering promotion.

## Promotion rule

Promote only a revision that passes every required gate and whose public
handoff again has exactly two root files: `natravcube` and
`BOOTSTRAPROSE.md`. Otherwise retain rev0606 as latest verified and package the
new work only as separately labelled construction source and evidence.

---

# NATravOverlay rev0607 — ExactCustodySessionService

## Current construction authority

This tree advances the rev0606 durable custody authority by adding one deliberately opt-in, one-transition live custody exchange **inside the existing `natravcube` executable**.  The canonical delivery boundary remains exactly two root files: `natravcube` and this `BOOTSTRAPROSE.md`.  Complete source custody and gate evidence are separate construction artifacts, not additional runtime products.

The service is entered only by the explicit commands below.  It does not participate in ordinary evidence routing, source subscriptions, discovery, opportunistic forwarding, transparent bridging, or application delivery:

```text
natravcube custody-service-v1-send   --policy FILE --bundle NHCB_FILE
natravcube custody-service-v1-serve  --policy FILE [--once]
natravcube custody-service-v1-status --policy FILE [--bundle NHCB_FILE]
natravcube custody-service-v1-version
```

The policy is a finite `key=value` authority record with format `NATRAV_CUSTODY_SERVICE_POLICY_V1`.  It binds one exact accepted-configuration SHA-256 commitment, one exact V21 grant identifier/generation/commitment, one current custodian identity/generation, one next-hop identity/generation, and one pinned authenticated peer certificate.  Sender and receiver roles are derived from those exact endpoints and cannot be inverted.  Policy lifecycle is `ACTIVE`, `RETIRED`, or `REVOKED`; a retired receiver may return only an already durable byte-identical acceptance, while a revoked policy cannot serve.

### Non-negotiable transition semantics

1. Only canonical `NHCB0001` bundles within the configured byte bound are eligible.
2. The sender signs and fsyncs the exact offer before the first carrier write.
3. Every network attempt is counted and fsynced before connection; the total survives restart and is bounded by policy.
4. Mutual TLS chain verification and an exact DER-certificate SHA-256 pin are both required.  Carrier or TLS failure never means acceptance.
5. The receiver verifies the sender signature and every authority field, fsyncs the offer, separately signs one acceptance, and fsyncs that acceptance before replying.
6. A lost reply leaves the sender explicitly unresolved.  Repetition of the exact offer returns the same retained acceptance; a request-id collision with different bytes is rejected.
7. Pending cases, bundle bytes, attempts, transfer window, I/O timeout, frame bytes, metadata bytes, signatures, and listener backlog are finite.
8. Acceptance transfers custody for exactly one transition.  It does not manufacture final-recipient import, evidence application, delivery receipt, or application success.
9. Nothing automatically forwards the newly accepted bundle.  A later transition requires a separate exact grant, policy, durable offer, and explicit invocation.
10. No open relay, peer discovery, route selection, global consensus, background retry loop, or second executable is introduced.

The focused rev0607 gate exercises normal acceptance, response loss after receiver commit, restart/retry with byte-identical acceptance, retired duplicate recovery, wrong peer pin, malformed bundle rejection, persistent attempt exhaustion, and absence of application-delivery artifacts.  Promotion still requires the pre-existing source, build, custody-authority, and risk-adjacent suites to remain green.

## Mandatory next run after rev0607

Repair any failing current gate first.  Once green, integrate this exact transition into the native authenticated peer-session message family and accepted configuration history without broadening its authority: add a monotonic V22 service rule, preserve all finite bounds and durable uncertainty semantics, and prove that two configured carriers still cannot create an automatic router.  Do not add multi-hop scheduling, discovery, open relay, opportunistic forwarding, transparent bridging, or application-success inference.

---

# NATravOverlay autonomous construction mandate — revision 0606

## Current authority: revision 0606

Read `validation/revision-0606/STATUS.json` and
[the V21 durable custody contract](docs/DURABLE-CUSTODY-AUTHORITY.md) before
continuing. Revision 0605 is the verified construction base. Historical records
remain provenance and cannot override the current source and gate account.

Revision 0606 binds the private `NHCE0001` / `NHCR0001` state machine to exact
V21 configuration grants and to the existing authenticated NodeState journal.
Every route party and signing generation resolves through accepted configuration.
Every hop names an immutable grant generation and commitment with finite lifetime,
hop, active-envelope and capsule-byte bounds. The existing configuration journal
is the only authority ledger. Custody registration, transfer, acceptance,
uncertainty, expiry and final import are durable, bounded and checkpointed. A
stale seed cannot erase accepted grants or revocation. Exact duplicate evidence
is idempotent; conflict, wrong next hop, loop, revoked authority and broken
provenance are rejected.

Owner-only offline commands exchange canonical finite `NHCB0001` bundles. Final
recipient custody acceptance is still not capsule import, application admission,
action execution or delivery. Only the existing exact authenticated receipt path
may complete an obligation. `configured_custody_relay` remains false: ordinary
peer routes do not relay custody, and no discovery, opportunistic forwarding,
parallel outbox, global consensus or second executable has been added.

## Mandatory next run after 0606

Repair any non-passing revision-0606 build, focal, sanitizer, registered-matrix,
reconstruction, extraction or clean-rebuild gate first. Preserve each failed
attempt and its corrected rerun separately.

After every current gate is green, add the narrowest explicitly configured
one-transition custody service over an existing authenticated peer session. It
must accept only a canonical bundle whose exact current custodian and next hop
match an accepted V21 grant, durably commit the transfer offer before sending,
return a separately signed acceptance, retain an unresolved outcome when the
response is lost, and reconstruct after restart without manufacturing custody or
application success. Use finite per-peer queues, bytes, active cases, retries,
expiry and work. The failed carrier or TLS session must never be treated as
custody acceptance. Final-recipient import and exact application receipts remain
separate.

That service must be opt-in and exact. Do not enable open relay, route discovery,
opportunistic forwarding, transparent bridging, carrier-derived identity or
global consensus. A node with two carriers still must not become a router by
accident. Missing independent hosts, hostile-custody labs and physical media are
verification debt, not shame and not a construction veto. Always hand off the
complete source tree.

## Retained prior mandates

# NATravOverlay autonomous construction mandate — revision 0605

## Current authority: revision 0605

Read `validation/revision-0605/STATUS.json` and [the private custody model](docs/CUSTODY-ENVELOPE-MODEL.md) before continuing. Revision 0604 is the verified construction base. Historical records remain provenance and must not override the current source and gate account.

Revision 0605 places a canonical finite custody-envelope state machine in the ordinary product build and reports its marker from the existing executable. `NHCE0001` binds one opaque unchanged `NHCP0001` capsule digest, an explicit ordered loop-free route, exact node and signing-generation keys, finite expiry, and an exact hop bound. `NHCR0001` records alternate an exact signed transfer and exact signed acceptance for each route transition. Sequence, predecessor digest, duplicate history, event time, party indices, and final state are all bounded. Exact duplicate evidence is idempotent; conflicting or out-of-order evidence is rejected.

This is a PRIVATE model. `configured_custody_relay` is false. No configuration field, route kind, connector, listener, daemon path, durable journal transition, automatic forwarding, discovery, or open relay consumes the model. Route public keys are explicit cryptographic inputs, not authority; future integration must bind them to accepted configuration. Final custody acceptance is not capsule import, application admission, action execution, or delivery. Existing exact receipts remain the only completion evidence.

## Mandatory next run after 0605

Repair any non-passing revision-0605 build, focal, sanitizer, matrix, reconstruction, extraction, or clean-rebuild gate first. Preserve failed attempts separately from corrected evidence.

After every current gate is green, connect the model to existing authenticated configuration and durable state without creating a parallel authority ledger. Add explicit relay grants for exact origins, final recipients, custodians, next hops, signing generations, envelope lifetime, hop bounds, and quotas. Persist custody offers, acceptances, expiry, duplicates, and unresolved transfer outcomes under the existing authenticated state boundary. Prove restart reconstruction, stale-seed resistance, unauthorized-next-hop rejection, loop rejection, custody loss uncertainty, and final-recipient import without confusing custody acceptance with application completion.

Ordinary routes must remain non-relaying until that policy and durable-state integration is complete. Do not add discovery, opportunistic forwarding, global consensus, or open relay. No unnamed human decision or unavailable hardware is a prerequisite. Missing independent hosts and physical custody facilities are verification debt, not shame and not a construction veto. Always hand off the complete source tree.

## Retained prior mandates

# NATravOverlay autonomous construction mandate — revision 0604

## Current authority: revision 0604

Read `validation/revision-0604/STATUS.json` and
[the V20 handoff-key contract](docs/HANDOFF-KEY-POLICY.md) before continuing.
The outside archive/rebuild and delivery postcheck records describe the frozen
ZIP; the in-tree status describes source/build/behavioral gates. Never infer a
release PASS from ZIP existence alone. Independently inspect the actual files.

Revision 0603's 5,400 source-file byte hashes equal revision 0602; its permissions
were repackaged, but its claimed V20 implementation and Unix-datagram repair were
not present. Its `REPAIR_REQUIRED` result is failed provenance, not source work.
0604 is constructed directly from the verified complete 0602 tree. Preserve the
failed account; do not reuse its unsupported narrative as a feature or test.

0604 puts exact signed handoff-binding commitments and monotonic lifecycle state
inside the EXISTING authenticated runtime configuration history, using V20. It
adds no parallel catalog, outbox, receipt ledger, key-discovery mechanism or relay.
The public immutable commitment excludes mutable ACTIVE/RETIRED/REVOKED state;
the accepted full configuration authenticates both. Numeric per-node sequences
are consecutive; labels and encryption keys cannot be reassigned. Retain history.
Only the newest key may be ACTIVE; retirement must be explicit. REVOKED keys
cannot be resurrected, including by rollback or stale seed replay. An empty V20
policy is deny-all, and V20 cannot downgrade to signature-only compatibility.

New exports require exact ACTIVE commitments at both ends. Imports permit exact
RETIRED keys for delayed recovery but reject REVOKED ones; current identity,
signing-generation and operation/receipt policy remain additional requirements.
Retirement does not prove when a capsule was created. Revocation is local accepted
policy, not global knowledge or a mechanism to undo an admitted operation.
External private key directories still require separate protected backup.

No new capsule cryptography, peer bytes, local-control protocol, journal envelope,
checkpoint envelope, storage schema, adapter execution or normal executable is
introduced by this increment. V6–V19 behavior remains compatible. Authenticated
configuration publication and offline exclusive-state reconstruction are the
policy boundaries. Preserve export-not-delivery and exact receipt semantics.

## Mandatory next run after 0604

Repair any non-passing observed gate first and keep failed attempts separate from
corrected reruns. Do not broaden protocol merely to avoid a compiler, state,
negative-control, regression, source-reconstruction or package-integrity failure.

After current gates pass, build a private finite custody-envelope model around an
OPAQUE unchanged NHCP0001 capsule. The final recipient remains the only decryptor.
Choose explicit origin, final recipient, allowed next hop and signing generations;
bind an immutable capsule digest, finite expiry and hop bound; retain signed
custody acceptance/transfer records and loop/duplicate controls. Custody acceptance
is NOT final application admission or delivery. First prove the small state machine
and negative paths, then connect it to existing configuration and durable state.
No ordinary route may relay before that authority and admission work is complete.
Do not implement open relay, discovery, opportunistic forwarding or global consensus.

Continue without waiting for unnamed human choices or unavailable hardware. Missing
independent hosts, physical media, hostile-custody labs or power-failure rigs is
verification debt, not shame and not a construction veto. Implementation is mandatory;
unsupported assurance is forbidden. ALWAYS hand off the complete source tree.

## Retained instructions and earlier milestones

The material below is historical context. This current authority and mandatory next
run take precedence over older headings that called themselves current or next.

# NATravOverlay autonomous construction mandate — revision 0602


## Current authority for this run: revision 0602

Read `validation/revision-0602/STATUS.json` and [the offline contract](docs/OFFLINE-HANDOFF.md).
Historical revision accounts below remain provenance, not instructions to redo
completed work or evidence for the current executable. The delivered revision-0601
archive contained no product sources. Preserve that failure and use the verified
complete revision-0600 archive as the reconstruction base for 0602. Do not reuse
0601's unsupported implementation or packaging claims.

The current increment is an owner-only, OFFLINE one-hop capsule over the existing
journal. It does not add a live configured capsule transport. Three commands in
the normal executable initialize dedicated identity-signed X25519 key material,
export one existing operation or exact receipt, and import one capsule under the
state lock. They replay accepted V7-or-later policy and enforce current identity,
key-generation, scope, outbox and receipt rules. Live TLS and storage encodings
remain unchanged. A valid signature is not scope permission; an admission receipt
is not proof that a deferred action executed.

Export is not delivery. Possession is not authority. Decryption is not application
success. Do not synthesize a receipt or erase uncertain outcomes. Duplicate
suppression and receipt reconciliation belong to the existing durable ledger.

The custom NHCP0001 construction uses OpenSSL X25519, HKDF-SHA-256, AES-256-GCM
and Ed25519. It is NOT RFC 9180 HPKE and has not received an independent security
audit or formal cryptographic proof. Keep the exact transcript, bounded parser,
independent Python encoder/decoder, mutation tests and explicit security limits.
Do not infer hardware verification or a proof from passing tests.

Dedicated handoff keys are owner-private external identity material. The full
signed binding digest identifies a key; a handoff generation label alone is not
a global registry. No automatic revocation of older X25519 keys under a still
active signing generation is implemented. Back up the exact private key directory
separately; it is not inside the state backup. A future durable key-policy feature
must make succession and revocation explicit before claiming more.

The deliverable is always the whole source tree. Before announcing a link, reopen
the actual ZIP, require node/src/main.cpp, every compiler input, foundation, tests,
and current status, verify its manifest and modes, and inspect the result. A ZIP
containing status files is not a product. Patches are supplemental. Never write a
fallback empty archive, silently copy an old executable, or label an unobserved
gate PASS. Missing output is not an output-channel excuse: inspect saved result
files and independently check the artifacts that will be handed to the custodian.

## Read this as an instruction, not a proposal

Continue building NATravOverlay.

Do not wait for an unspecified human decision merely because preferred
hardware, independent hosts, external services, laboratory access, or complete
end-to-end verification are unavailable.  There is no shame in missing those
facilities.  Record the resulting verification debt precisely, avoid claims
the evidence cannot support, choose the smallest conservative and reversible
design, and keep constructing.

Implementation is mandatory.  Fabricated assurance is forbidden.

When several reasonable choices remain, do not stop at a menu of options.
Select one by the following order:

1. preserve authenticated identity and explicit authority;
2. preserve durable obligations and uncertainty;
3. preserve existing protocol bytes and compatibility;
4. bound memory, work, retries, queues, and evidence;
5. prefer a narrow reversible seam over a broad abstraction;
6. preserve the single `natrav-overlay` product executable;
7. document the assumptions and rejected alternatives;
8. build and exercise the choice now.

A human may later reverse a documented choice.  The possibility of reversal is
not permission to leave the choice unmade.

## Assurance vocabulary

Use these claims independently.  Never silently promote one into another.

- `IMPLEMENTED`: the source and product boundary exist.
- `COMPILED`: the declared build completed for the recorded source.
- `LOCALLY_EXERCISED`: recorded tests ran on the available host.
- `MODEL_VERIFIED`: deterministic or simulated evidence covers the stated
  model and negative controls.
- `INDEPENDENT_HOST_VERIFIED`: distinct physical hosts were used.
- `HARDWARE_VERIFIED`: the named physical carrier and failure modes were
  actually exercised.

A missing later claim does not cancel an earlier legitimate one.  A model test
is useful evidence and is not hardware evidence.

Every non-passing, interrupted, timed-out, undiscovered, or unexecuted gate
must remain visible.  Do not convert absence of output into success.  Do not
erase an earlier failure after a repair; retain it as provenance.

## North star

NATravOverlay is a sovereign, carrier-independent, delay-tolerant fabric for
authenticated evidence, durable obligations, and explicitly authorized action.

Its fundamental promise is not merely:

> send these bytes to that address

It is closer to:

> this authenticated node, at this key generation and under this bounded
> authority, created or accepted this exact obligation; here is the durable
> evidence of delivery, rejection, action, uncertainty, retry, custody, or
> unresolved outcome.

A carrier supplies connectivity.  NATravOverlay supplies identity, authority,
meaning, durable state, and honest uncertainty.

IP addresses, UDP endpoints, radio addresses, serial paths, USB identifiers,
Bluetooth addresses, adapter process identities, and link identifiers are
locators only.  None may become peer identity or trust.  TLS identity and
pinned overlay policy remain above every carrier.

## Product boundary

Continue the existing `natrav-overlay` executable.  Do not start a replacement
binary merely because a refactor or new carrier would be easier in isolation.
The accumulated identity, journal, authorization, retry, receipt, custody,
recovery, framing, projection, and action machinery is the scarce asset.

New carrier work must enter through the existing carrier-neutral boundaries:

- `TransportLocator` describes explicit reachability;
- `TransportConnector` owns outbound establishment;
- `TransportListener` owns bind/listen/accept behavior where meaningful;
- `OwnedCompleteDatagramPacketPort` owns one complete-datagram carrier endpoint;
- `PacketPortOrderedByteStream` reconstructs a bounded ordered stream above it;
- `OrderedByteStream` owns an established reliable ordered carrier;
- the custom OpenSSL BIO carries TLS over `ByteChannel` without recovering a
  native socket descriptor;
- TLS, HELLO, NOS1, application operations, durable receipts, and close remain
  above the carrier.

The Unix local-control socket remains local IPC, not a peer carrier.

Do not turn NATravOverlay into a transparent Ethernet bridge, a general IP
router, an unrestricted remote-code system, an automatic peer-discovery mesh,
or a system that confuses cryptographic validity with global freshness.

## Completed architectural sequence

The construction sequence to date is intentional:

1. Detached custody-promotion intent closed the bounded custody outcome work.
2. TCP connect/listen/accept ownership moved behind carrier-neutral contracts.
3. Peer TLS moved to an owned OpenSSL BIO over `ByteChannel`.
4. A deterministic virtual ordered carrier exercised the real TLS/session
   stack under controlled stream adversity.
5. An explicitly configured POSIX serial/TTY carrier proved that a non-IP
   stream can use the same authenticated stack.
6. A private finite packet-link core defined canonical framing, bounded
   fragmentation/reassembly, acknowledgment, retransmission, duplicate
   suppression, expiry, backpressure, deterministic fault schedules, and
   canonical evidence.
7. Revision 0582 repairs the revision-0581 strict-build defect and places a
   fixture-owned `PacketLinkOrderedByteStream` over that finite packet service,
   beneath the real OpenSSL BIO, TLS 1.3, HELLO, NOS1, operation, receipt, and
   authenticated-close path.
8. Revision 0583 closes the revision-0582 evidence defects without broadening
   product behavior: it repairs brittle source-contract predicates, reruns the
   original finite core and authenticated packet-stream focal work, executes
   the registered matrices, reproduces the executable from frozen source, and
   verifies patch/archive reconstruction before allowing UDP work to begin.
9. Revision 0584 adds one canonical numeric point-to-point UDP carrier beneath
   the finite packet service. It binds exact local and remote endpoints, MTU,
   link identifier, epoch, and finite profile; owns a nonblocking connected
   datagram socket; rejects truncation; and carries the unchanged authenticated
   stack without treating an IP address or port as identity.
10. Revision 0585 adds a fixture-owned deterministic UDP datagram
    adversary around two complete persistent nodes. Canonical bounded schedules
    inject loss, duplication, corruption, delay, and reordering; canonical
    traces account for the fixture's actions; and the real scheduler, TLS,
    HELLO, NOS1, operation, receipt, stop, restart, and recovery lifecycle runs
    through the configured UDP carrier without adding product forwarding.
11. Revision 0586 extracts the owned complete-datagram packet-port seam that
    the finite packet service actually needs. UDP keeps every locator byte,
    socket rule, MTU rule, source filter, error class, queue bound, and
    authenticated outcome while moving its descriptor ownership and bounded
    progress contract behind `OwnedCompleteDatagramPacketPort`. The reusable
    `PacketPortOrderedByteStream` now owns finite packet reconstruction above
    any complete-datagram carrier, and a fixture-owned Unix datagram socketpair
    proves the seam without registering another product carrier.
12. Revision 0587 is a retained failed construction attempt. Its wrapper ran
    `bash node/build.sh static` from the wrong directory, exited `127`, produced
    no product binary or source snapshot, and correctly recorded
    `REPAIR_REQUIRED`. The delivery of failure ledgers is provenance, not an
    implementation and not a release.
13. Revision 0588 reconstructs from the verified revision-0586 source and adds
    one explicit owner-controlled Unix-domain datagram carrier as the second
    production `OwnedCompleteDatagramPacketPort`. Canonical absolute local and
    remote paths, owner-only parent directories, exact source credentials and
    paths, no-follow traversal, path replacement detection, truncation
    rejection, finite packet bounds, listener leasing, exact-object cleanup,
    and the unchanged TLS/HELLO/NOS1/application/receipt lifecycle are all
    part of the carrier boundary.
14. Revision 0589 adds a private supervised external process implementation
    of `OwnedCompleteDatagramPacketPort`. The core creates a full-duplex Unix
    `SOCK_SEQPACKET` pair, inherits only descriptor 3 into an exact absolute
    executable and exact argument vector, negotiates canonical bounded
    `NAPA0001` capabilities, retains finite evidence, and converts process
    death or protocol violation into explicit carrier failure. A fixture
    process carries the real finite packet, TLS, HELLO, NOS1, application,
    receipt, and close path under deterministic packet and process adversity.
    Runtime endpoint death is accounted exactly once even when EOF/HUP precedes
    observable child wait status. The boundary remains absent from ordinary
    route configuration.
15. Revision 0590 is a retained failed packaging attempt, not a product
    implementation. Its authoritative status is `REPAIR_REQUIRED`; it records
    zero changed paths, an empty patch, no product binary, and no focal or
    model-verification result. A successful build observation from an unchanged
    tree does not turn an empty delta into the requested adapter-profile work.
16. Revision 0591 constructs and exercises the security-critical profile and
    exact-image launch slice as an apply-ready delta against the exact
    revision-0589 adapter files. It defines canonical profile and locator
    records, authorized profile succession, no-symlink exact-image opening,
    SHA-256 pinning, a sealed executable image, descriptor-based execution,
    launch-option drift rejection, bounded restart policy, and profile evidence
    in the supervised-adapter snapshot. The slice passes strict, sanitizer,
    integration, and repeated-process probes. It is not yet a product release:
    the complete revision-0589 source snapshot was unavailable to this run, so
    durable owner-authorized storage, configured route/listener resolution, the
    full product build, complete matrices, and source-archive reconstruction
    remain mandatory integration gates.
17. Revision 0592 extends that apply-ready slice with the durable configuration
    seam that can be proved without inventing the unavailable product APIs. It
    adds an owner-private append-only hash-chained profile catalog, an opaque
    authority-verifier adapter, bounded rejection evidence, exact profile and
    endpoint generations, canonical route/listener endpoint records, strict
    profile-digest binding, deterministic incomplete-tail recovery, and the
    configured preparation path that derives launch options only through the
    pinned-profile factory. Strict, ASan/UBSan, persistence, corruption,
    process-death, reconstruction, path-replacement, and repeated-launch probes
    pass. The complete product state remains `REPAIR_REQUIRED` because the full
    revision-0589 source snapshot, real owner/admin command wiring, transport
    registry integration, two complete nodes, full matrices, and clean product
    rebuild remain unavailable in this execution environment.

Revision 0581 is not to be rewritten as a success. Its retained status records
that an explicit constructor carrying a default argument failed the strict
build. Revision 0582 is also not to be rewritten as a pass: its authoritative
status records failed packet-stream, private-boundary, full-matrix, patch, and
archive gates. Revision 0587 must likewise remain a failed wrapper attempt: it
never compiled or produced a source archive. Revision 0590 must remain an
empty-delta `REPAIR_REQUIRED` attempt. Revisions 0591 and 0592 are bounded
apply-ready deltas, not complete product releases. Later repairs preserve every
one of these records rather than laundering them into retrospective success.

## Packet-port, UDP, and Unix-datagram rules retained through revision 0588

The private packet adapter is evidence infrastructure, not a configured route.
It must remain unavailable to ordinary locator parsing, connector registries,
and listener registries until its real-stack path passes.

It must:

- consume the finite packet state machine rather than bypassing it with a
  second simulated stream;
- expose two explicitly owned `OrderedByteStream` endpoints and one bounded
  control/evidence object;
- use finite queues and finite work per I/O call;
- preserve caller-supplied absolute wall-clock deadlines;
- advance deterministic logical packet time without an unowned scheduler
  thread;
- distinguish EOF, timeout, reset, exhaustion, malformed input, and retry
  failure;
- preserve canonical `NPLS0001` schedules and `NPLT0001` traces;
- carry the real TLS/HELLO/NOS1/application/receipt/close stack;
- keep packet metadata outside identity and authority;
- have no normal locator, discovery, relay, or forwarding behavior.

The configured UDP carrier is the first production packet port. It must:

- accept only canonical `udp-v1` locators with explicit numeric local and
  remote endpoints, MTU, nonzero link identifier, nonzero epoch, and a
  versioned finite profile;
- perform no DNS, service lookup, broadcast, multicast, discovery, source
  learning, migration, forwarding, or relay;
- own a nonblocking bound and connected datagram socket;
- use connected-UDP filtering only as reachability hygiene, never identity;
- detect and reject oversized datagrams rather than accepting a truncated
  prefix;
- retain finite socket, packet, reassembly, delivery, in-flight, retry, expiry,
  and per-pump bounds;
- feed the existing finite packet state machine and reconstructed ordered
  stream rather than bypassing them;
- keep TLS identity and authorization above every endpoint and link field; and
- remain in the single `natrav-overlay` executable.

The configured Unix-domain datagram carrier is the second production packet
port. It must:

- accept only canonical `unix-dgram-v1` locators with explicit absolute local
  and remote paths, MTU, nonzero link identifier, nonzero epoch, and finite
  profile;
- use no abstract namespace, directory scan, automatic attachment, source
  learning, path migration, forwarding, or relay;
- traverse parent components without following symlinks and require the final
  parent directory to be owned by the effective user and inaccessible to group
  and other users;
- refuse every pre-existing local path rather than guessing that a socket is
  stale or safe to unlink;
- bind with owner-only socket permissions, remember exact device and inode
  observations, and remove only the exact socket object it created and still
  observes;
- require the configured remote path to be an owner-controlled socket and
  filter received datagrams by both the exact configured path and effective
  user credentials;
- reject truncation, replacement, missing paths, unsafe ownership, and
  unauthorized senders without treating any filesystem coordinate as peer
  identity;
- preserve finite packet, queue, retry, expiry, logical-time, and listener
  lease rules above the carrier; and
- retain TLS identity, HELLO, NOS1, application authority, durable obligations,
  receipts, and recovery above all filesystem coordinates.

The available POSIX interfaces cannot make the final check-and-unlink sequence
mathematically race-free against a hostile process running as the same user.
Use exact-object checks, minimize the interval, retain replacement negatives,
and record the residual same-UID race as verification debt. Do not pretend it
vanished.

### Replay claim boundary

For fixed raw bytes and a fixed schedule, require byte-identical canonical
packet traces.

Do not require independent TLS handshakes to produce byte-identical encrypted
packets.  Fresh TLS cryptographic randomness is a security property, not a
failure of deterministic scheduling.  Across independent authenticated runs,
compare the deterministic structural facts that should remain stable:

- injected-fault disposition;
- direction;
- per-direction ordinal;
- packet size structure;
- authenticated application operations;
- bound receipts and terminal outcomes.

Never normalize away cryptographic randomness to manufacture a stronger claim.

## Revision-0588 construction requirements

Revision 0588 repairs revision 0587 before broadening the architecture. It
must:

- consume revision 0587's machine-readable `REPAIR_REQUIRED` and preserve its
  `127` wrapper failure as provenance;
- reconstruct only from the verified revision-0586 source archive rather than
  implying that the failed run produced usable implementation state;
- implement one canonical `unix-dgram-v1` locator with exact local and remote
  absolute paths, MTU, nonzero link identifier, nonzero epoch, and finite
  profile;
- make Unix socket ownership explicit, no-follow, owner-only, finite, and
  destruction-based, without automatic stale-path deletion;
- reject unsafe parents, symlinks, pre-existing occupants, self-routes,
  duplicate local leases, role conflicts, truncation, unauthorized sources,
  and path replacement;
- preserve the generic finite packet service and ordered-stream reconstruction
  rather than duplicating fragmentation, reassembly, retry, duplicate
  suppression, expiry, or semantic finish in the Unix carrier;
- carry real TLS 1.3 mutual authentication, HELLO, NOS1, application
  operations, bound receipts, authenticated close, orderly stop, restart, and
  reconnect over the configured carrier;
- preserve the single executable and every existing peer, local-control,
  journal, checkpoint, backup, custody, authorization, and storage encoding;
- compile with strict warnings, execute focal and sanitizer negatives, run the
  adjacent and complete matrices, reconstruct the textual patch, extract and
  retest the source archive, and reproduce the executable from frozen source;
  and
- classify same-host Unix datagram evidence honestly: it proves local
  filesystem ownership and packet-port behavior, not independent hosts,
  Bluetooth, radio, USB hardware, electrical behavior, range, interference,
  driver quality, or physical power loss.

## Revision-0589 construction requirements

Revision 0589 must:

- remain a private packet-port implementation rather than a configured route;
- use one core-created full-duplex Unix `SOCK_SEQPACKET` socketpair and inherit
  only the exact child endpoint as descriptor 3;
- launch only one canonical absolute executable path with an exact bounded
  argument vector and a minimal explicit environment;
- close unrelated file descriptors, set parent-death behavior, set
  `no_new_privs`, and use an owner-only umask;
- negotiate one finite MTU, frame bound, queue bound, outstanding-request
  bound, and versioned profile without allowing the child to expand them;
- use canonical request, response, fault, and shutdown frames with exact
  lengths, nonzero sequences, deadline budgets, and integrity checking;
- retain bounded launch attempts, bounded exponential startup backoff, bounded
  evidence, explicit liveness checks, and destruction-based shutdown;
- fail the current carrier on runtime death or protocol violation rather than
  transparently resurrecting a possibly ambiguous encrypted stream;
- prove descriptor and environment isolation, startup retry, backpressure,
  loss, duplication, corruption, delay, reordering, crash, malformed output,
  resource exhaustion, and orderly shutdown through a deterministic fixture;
- carry the unchanged finite packet service, ordered stream, OpenSSL BIO, TLS
  identity, HELLO, NOS1, operations, exact receipts, and authenticated close;
- preserve the one product executable and every existing configured carrier,
  wire encoding, journal, checkpoint, backup, custody, authorization, and
  storage format; and
- state honestly that the fixture is same-host model evidence and that a
  same-UID child is not yet a complete hostile operating-system sandbox.

## Immediate run order

For every autonomous run:

1. Read the prior machine-readable status and retained attempts.
2. If any required prior gate is non-passing, repair that exact gate first.
3. Compile with the project’s strict warning policy.
4. Exercise the smallest focal model and negative controls.
5. Exercise the real authenticated stack over the new seam.
6. Run sanitizer coverage where available.
7. Run the risk-adjacent and complete registered regression matrices when the
   environment permits.
8. Rebuild from frozen source and compare the executable digest.
9. Package a complete source snapshot, exact textual patch, checksums,
   verification ledger, retained failures, and machine-readable status.
10. State the physical assurance boundary without apology and continue to the
    next bounded target.

A timeout or orchestration failure is evidence about that attempt.  Diagnose
it, preserve it, and rerun or repair.  It is not automatically a product
failure and is never automatically a pass.

## Revision-0591 bounded profile-core requirements

The current bounded delta must—and now does—provide the narrow security seam
that can be proved without inventing a full product tree:

- a canonical `NATRAV_ADAPTER_PROFILE_V1` record binding a stable lowercase
  profile identifier, nonzero generation, predecessor-record SHA-256, exact
  canonical absolute executable path, exact executable SHA-256, exact bounded
  argument vector, MTU, capability profile, queue and frame bounds, launch
  budget, deadlines, evidence bound, and restart policy;
- byte-exact canonical parsing with no leading-zero numbers, lowercase digest
  text, uppercase minimal percent escapes, fixed field order, bounded record
  size, bounded arguments, and a re-encode equality check;
- creation at generation one with a zero predecessor and replacement only by
  the same stable identifier, exactly the next generation, and the exact
  SHA-256 of the predecessor's canonical record;
- one canonical
  `adapter-v1|profile=<id>|generation=<u64>|link=<hex>|epoch=<u32>` locator
  whose profile reference, link identifier, and epoch remain reachability and
  policy coordinates rather than peer identity or authority;
- exact profile-generation resolution from retained history, with duplicate
  exact generations rejected rather than guessed;
- component-by-component `openat` traversal with `O_NOFOLLOW`, regular-file,
  ownership, executable-mode, size, set-id, and writable-mode checks;
- SHA-256 over the exact opened bytes, constant-time digest comparison, ELF
  format rejection, copying into a private `memfd`, and immutable write/grow/
  shrink/seal seals;
- execution of the sealed descriptor with `execveat(..., AT_EMPTY_PATH)` or
  `fexecve`, never a second unchecked pathname resolution after validation;
- complete launch-option/profile equality checks before `fork`, including the
  canonical profile-record digest and executable-image digest;
- preservation of the existing descriptor-3 `NAPA0001` boundary, minimal
  environment, closed unrelated descriptors, parent-death behavior, and
  `no_new_privs`;
- bounded capped restart backoff and reuse of the approved sealed image after
  pathname replacement or disappearance; and
- strict warning-as-error, ASan/UBSan, real fork/`SOCK_SEQPACKET`/NAPA
  integration, mutation negatives, authorized replacement, path replacement,
  path disappearance, and repeated-launch evidence.

The profile record is structural authorization evidence, not authorization by
itself. The persistent configuration command that creates or replaces a
profile must still pass the existing authenticated owner/admin authority
boundary and durably record the accepted canonical bytes.

## Revision-0592 bounded durable-catalog requirements

The current bounded delta must—and now does—add the persistence and exact-route
seam that can be exercised without pretending the complete product tree exists:

- one canonical `NATRAV_ADAPTER_ENDPOINT_V1` record binding a stable endpoint
  identifier, exact generation, exact predecessor digest, immutable route or
  listener role, exact `adapter-v1` locator, and SHA-256 of the exact retained
  profile record;
- exact endpoint succession with no generation skipping, role confusion, or
  implicit upgrade to a newer profile generation;
- an integration-supplied authority verifier that receives operation, canonical
  object bytes, and opaque authority evidence, while the catalog retains only
  the evidence digest and a bounded decision code;
- an owner-private append-only journal with fixed header, length-delimited
  canonical events, monotonic sequence, prior-record hash, payload hash, record
  hash, and commit trailer;
- strict replay of every accepted transition and exact profile reference;
- automatic repair only for an incomplete final frame, with the discarded byte
  count and SHA-256 immediately committed as recovery evidence;
- hard failure for complete-frame corruption, broken chains, noncanonical
  encodings, duplicate generations, missing profiles, stale profile digests,
  unsafe permissions, symlinks, hard-link aliases, or exhausted bounds;
- finite file, record, profile, endpoint, rejection, and authority-evidence
  limits;
- a configured preparation function that resolves an exact endpoint generation
  and derives immutable launch options only through
  `external_packet_adapter_options_from_profile`; and
- strict warning-as-error, ASan/UBSan, durable reopen, denied transition,
  corruption, interrupted append, exact-image replacement, process death,
  carrier reconstruction, restart-style revalidation, and repeated-process
  evidence.

This catalog still does not decide who is an owner or administrator. The full
product must connect its existing authenticated authority boundary to the
verifier and durably account for the resulting command in the product's normal
configuration history.

## Retained policy milestone — revision 0595

The full revision-0593 source archive is available and is the construction base.
Do not repeat the obsolete missing-source diagnosis. Its profile/catalog code
was present but its runtime parser stopped at V18. The mounted revision-0594
"delivery" is 552 bytes and contains only a failure account, not a source tree.
That failed handoff must remain preserved, not relabeled as a completed release.

Revision 0595 adds V19 retained adapter policy to the real product. Canonical
profile and endpoint records are embedded as bounded lowercase hexadecimal in
the existing canonical configuration. Their exact generations, predecessor
digests and profile bindings are validated. Existing local-startup and
owner/delegated-CONFIGURATION admission authorizes them; the authenticated
NodeState configuration journal and checkpoint persist them. Every accepted
profile/endpoint generation is immutable and retained across later activation,
rollback and restart. Rejected proposals do not reserve generations.

This supersedes the earlier proposal for a separately committed runtime catalog
file: the ordinary authenticated configuration event is the durable authority.
The standalone catalog remains a component, not a second truth source. Do not
introduce a split-journal publication ambiguity merely to preserve a provisional
design made before the complete product source was available.

V19 policy admission does NOT launch an executable and does NOT make adapters
available to configured routes. Missing executable hardware and files may be
represented as policy without an unsupported execution claim. The release
metadata explicitly reports configured adapter transport as false. A successful
whole-product build is not a claim that every planned feature is integrated.

The policy-only milestone is recorded in `validation/revision-0595/STATUS.json`. Historical
validation files at the root of `validation/` are preserved as provenance and
must not override the current whole-tree status recorded below. Give the next custodian the COMPLETE source
archive and delivery bundle. Deltas and patches are reconstruction evidence,
never substitutes for the whole product, even when some gates remain open.

## Current execution integration — revision 0596

The exact complete revision-0595 archive was restored and verified; all 1,390
manifest entries matched. Do not repeat any obsolete missing-source diagnosis.
Historical private-only adapter restrictions in earlier milestone descriptions
are superseded by this exact V19 execution boundary, not by arbitrary launching.

Configured `adapter-endpoint-v1|id=<id>|generation=<u64>` locators now resolve
retained endpoint/profile commitments from the accepted immutable V19 snapshot.
Outbound construction runs under the existing generation lease. Each new
carrier revalidates and seals the image; the failed carrier and TLS session
are never resurrected. Listener work is single-lease and deferred into bounded
peer workers, not the main control/accept thread. Existing immutable listener
layout is preserved. No separate runtime catalog is authoritative.

Use `validation/revision-0596/STATUS.json` for retained execution-integration gates and the
complete delivery's archive-verification record for packaging evidence. Check
results rather than inferring success from the presence or size of a ZIP.
The whole source tree is the handoff. Deltas remain supplementary evidence.

## Current configured-adapter adversity — revision 0597

Revision 0597 closes the deterministic packet/process adversity sequence around
configured V19 adapters without moving fault authority into the product. The
existing canonical `NATRAV_UDP_ADVERSARY_SCHEDULE_V1` relay injects bounded
loss, duplication, corruption, delay and reordering between two complete
persistent nodes. A separately compiled pinned ELF fixture consumes canonical
`NATRAV_CONFIGURED_ADAPTER_PROCESS_SCHEDULE_V1` records and writes bounded
`NATRAV_CONFIGURED_ADAPTER_PROCESS_TRACE_V1` evidence for launch ordinal,
startup failure or silence, per-request response behavior and process death.
The product never parses either schedule and neither fixture possesses peer
keys, configuration authority, application receipt authority, custody or relay
permission.

The recorded lifecycle proves that exhaustion of the bounded adapter startup
budget before TLS authentication leaves the obligation pending without
consuming an application attempt. It separately proves that a silent NAPA
response or process death during an already authenticated application write may
consume an application attempt while preserving the obligation, and that
recovery requires a new process, a new carrier, fresh TLS/HELLO authentication
and an exact authenticated receipt. Fixed packet schedules retain the same
path, direction, ordinal, action and packet-size structure under CPU
contention. TLS ciphertext hashes are deliberately excluded from replay
identity because fresh handshake randomness remains a security property.

Use `validation/revision-0597/STATUS.json` for retained adversity gates once the source
archive is frozen. Historical status files remain provenance rather than
current truth. The whole source tree remains the handoff; patches and fault
traces are supplementary reconstruction and evidence artifacts.

## Retained framed serial packet adapter — revision 0598

Revision 0598 builds the explicitly pinned POSIX serial packet role into the
existing `natrav-overlay` executable. V19 profiles bind this same ELF and its
exact `serial-packet-adapter` argv; no second normal binary is needed. NSP1
canonical escaped frames carry bounded complete datagrams with explicit MTU,
link/epoch, length and CRC, finite queues, deadlines, and bounded resynchronization.
The existing finite packet service, TLS, HELLO, NOS1, obligations and receipts
remain above the adapter. A TTY pathname remains a locator, not authority.

The complete source tree and exact release identity are mandatory handoff
artifacts. `validation/revision-0598/STATUS.json` is the retained gate record
for that milestone. Historical status files and prior prose remain provenance,
not current truth. A ZIP is not behavioral evidence. Never link to a file that does not exist.

## Retained strengthened serial model — revision 0599

Revision 0599 retains NSP1 and every authenticated or durable encoding while
closing the next model boundary. The product computes the exact maximum escaped
frame size and rejects a frame lifetime shorter than the idealized worst-case
line serialization time for the configured baud and character format. This is a
lower bound, not a physical timing promise.

The complete-node fixture now includes true whole-frame reordering, not only
delay; whole-datagram receive-queue exhaustion and retransmission recovery; an
actual route-side PTY replacement; exact owner-authorized profile and endpoint
generation succession onto the new path; fresh child/TLS/HELLO reconstruction;
and independent TCP progress to a third peer while the serial carrier is
unavailable. Stale startup policy cannot roll back the accepted replacement.
The old path is not rediscovered. The adapter, TTY, link, and epoch remain
carrier coordinates rather than identity or receipt authority.

Use `validation/revision-0599/STATUS.json` as the current product gate record
once the whole tree is frozen. Historical status files remain provenance. The
complete source tree remains the handoff; patches are supplementary evidence.

## Current removable-media packet model — revision 0600

Revision 0600 adds one explicit operator-pinned removable-media packet adapter
as a supervised role of the existing `natrav-overlay` executable. Exact V19
profiles bind three canonical owner-only directory objects: inbound, outbound,
and bounded quarantine. The adapter uses no mount scan, volume-label trust,
USB identifier, automatic attachment, discovery, forwarding, or relay.

`NRMB0001` bundles are finite, content-addressed, owner-only regular files with
an explicit link identifier, carrier epoch, creation time, expiry, payload
length, complete NAPA datagram, and SHA-256 trailer. Publication uses a
same-directory temporary file, complete write, file `fsync`,
`renameat2(RENAME_NOREPLACE)`, and directory `fsync`. Queue bytes, queue files,
directory entries, scan work, bundle lifetime, duplicate history, quarantine
bytes, and quarantine files are all explicit finite bounds.

A persistent file carrier creates an additional incarnation hazard that UDP or
a live stream does not: valid packets from a dead finite stream may appear
after a replacement process starts. Revision 0600 therefore gives every new
configured outbound adapter carrier a fresh nonzero NPL1 epoch. A listener
begins unbound, binds once to the first valid frame for the configured stream
identifier, and ignores packets from other epochs for that stream lifetime.
This epoch is an anti-confusion namespace, not identity or authentication. TLS
and HELLO still establish the peer; exact authenticated receipts still complete
obligations.

The complete-node model deliberately kills an adapter without draining the
carrier, retains delayed and interrupted files, reconstructs a different child
and carrier, requires fresh TLS/HELLO authentication, exercises corruption,
duplication, delay, drop, interrupted copy, directory replacement, exact
profile/endpoint succession, pending work, orderly stop, restart, and exact
receipt recovery. Local directories are model evidence only. They do not prove
USB/SD hardware, filesystem power-loss behavior, flash endurance, independent
hosts, or physical removal.

Use `validation/revision-0600/STATUS.json` as the current product gate record
once the whole tree is frozen. Historical status files remain provenance. The
complete source tree remains the handoff; patches are supplementary evidence.

## Mandatory next run

Repair any non-passing revision-0602 gate first. Do not broaden the protocol while
build, focal, sanitizer, matrix, reconstruction, extraction or clean-rebuild
evidence is missing. Retain the failed attempts and their corrected reruns.

Then implement exact durable handoff-key policy under the existing authenticated
configuration authority: canonical signed-binding commitments, retained exact
generations, explicit authorized succession and revocation, bounded historical
records, and restart reconstruction. Do not add a second independently committed
authority ledger or silently follow a newer key. Preserve side-effect-free config
parsing. Keep offline key material outside the application state unless an explicit
protected backup/restore design is implemented and tested.

The next tests must show old and new binding commitments, rejected unauthorized
successors, current-policy rejection of revoked decryption keys, receipt recovery
across an authorized change, crash/restart, stale seed configuration, and a whole
product build and registered matrix. Improve the current one-hop custody and
key lifecycle before any multi-hop envelope. Multi-hop is not authorized merely
because a capsule can be carried by several people or devices.

No human decision, hardware purchase or external lab is a prerequisite for those
bounded changes. Missing independent hosts and physical media are verification
debt, not shame and not a construction veto. Preserve the complete source tree.

## Later packet and physical carriers

After the explicit Unix-domain datagram carrier is sound, use the same
packet-port boundary for carefully bounded adapters such as:

- explicitly selected Bluetooth transports;
- packet radio;
- LoRa-like constrained links;
- store/carry/forward adapters;
- removable or intermittently attached media.

Do not pretend these media have identical MTUs, duplex behavior, timing,
failure modes, or hardware semantics.  Normalize only what the finite packet
service can honestly provide.  Carrier-specific limitations remain explicit.

## Multi-hop remains later protocol work

A node with two carriers must not accidentally become an open router.
Multi-hop relay is a separate authenticated protocol feature requiring at
least:

- identified origin and final recipient;
- explicit relay authority;
- versioned relay envelope;
- hop bound and loop detection;
- quotas, expiry, and duplicate suppression;
- durable custody acceptance and transfer evidence;
- route policy and negative controls;
- preservation of unresolved outcomes rather than guessed success.

Do not implement relay as a side effect of adding UDP or another adapter.

## Durable truth and uncertainty

Continue treating uncertainty as a first-class state.

A lost response does not prove an operation failed.  A valid state image does
not prove it is globally latest.  A route failure does not necessarily consume
an application retry.  A caller missing a shutdown response does not prove the
remote side remained live.  A relay accepting custody is not the same as the
final recipient accepting the obligation.

Preserve enough authenticated evidence to classify what is known, what is not
known, and what can later be reconciled.  Never collapse uncertainty by
convenient guesswork.

## Final instruction

Build the strongest bounded system the available evidence permits.

Do not wait for perfect verification.  Do not claim verification that did not
occur.  Do not apologize for unavailable hardware.  Do not use unavailable
hardware as an excuse to leave architecture, finite-state behavior, negative
controls, deterministic evidence, packaging, or documentation unfinished.

Make the decision.  Record the debt.  Preserve the authority boundary.
Continue.
