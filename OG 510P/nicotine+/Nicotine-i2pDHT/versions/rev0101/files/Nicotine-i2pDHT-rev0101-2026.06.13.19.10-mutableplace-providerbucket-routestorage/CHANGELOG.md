# rev0101 — mutableplace-providerbucket-routestorage

- Added `mutableplacement.py` for local mutable-head observation placement after record ingress, without claiming latestness.
- Added `providerbucket.py` for bounded provider-index bucket admission after semantic proof.
- Added `routestorage.py` for I2P-bound route storage/replacement-cache decisions after routing anchor acceptance.
- Added `substrateplacementfold.py` and extended `substratespine.py` through rev0101.

# rev0100 — recordingress-providersemantics-routingspine

- Returned active work to the generic Python-owned I2P DHT substrate after rev0099 closed the native/GCC branch as shadow-only.
- Added `recordingress.py`, `providersemantics.py`, and `routinganchor.py` to gate records, provider claims, and route contacts before local usefulness.
- Added `substratespine.py` and `substratecenturyfold.py` as the new post-native substrate audit spine.
- Updated docs, surface ledger, fold map, fold registry, public pointers, evidence scripts, and verification summary for rev0100.

# rev0099 — substratereturn-recordoracle-spineaudit

- Added `recordplaneoracle.py` to assert Python ownership over record validation, mutable-head latestness, provider semantics, parsing, crypto, transport, and persistence finality after the native branch close.
- Added `substratereentry.py` to gate the return to generic I2P DHT substrate design on native branch close + record-plane oracle + native fold-spine agreement.
- Added `substratereturnfold.py` and extended `nativefoldspine.py` so rev0099 is auditable as a pivot from native/GCC exploration back to DHT substrate semantics.
- Verification recorded through surface check, micro-simulation, targeted rev0098/rev0099 tests, deterministic chunk/filewise pytest, compile checks, cube/fold audits, and zip integrity.

# rev0091 — nativereentry-oracleseal-preflight

- Added `nativeoracleseal.py` to keep the Python oracle and fallback/fault memory explicit before any native re-entry.
- Added `nativepreflight.py` so relaunch evidence can route only back to the native load gate, not directly to load or dispatch.
- Added `nativereentryjournal.py` so preflight/oracle evidence survives restart with fallback/tombstone/quarantine/crash memory.
- Added `nativereentryfold.py` and extended `nativefoldspine.py` so the GCC/native branch remains one auditable chain through rev0091.
- Verification recorded through current/predecessor tests, deterministic chunked pytest, compile checks, cube/fold audits, and zip integrity.

# rev0088 — nativeunload-sandboxstub-crashgc

- Added `nativeunload.py` so loaded native leaves can be unloaded/quarantined after faults, operator disable, profile demotion, or upgrade replacement while preserving Python fallback memory.
- Added `nativesandboxstub.py` as a no-network, nonproduction sandbox-stub boundary that rejects parser/crypto/secret-key ownership and I/O/process/thread/dynamic-load power.
- Added `nativecrashgc.py` so crash-ledger GC can compact soft evidence without erasing hard fault/quarantine memory.
- Added `nativecontrolfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, head registry, and evidence scripts for rev0088.
- Verification: surface check, micro-simulation, targeted rev0087/rev0088 tests, deterministic chunked/filewise pytest, compile check, compileall, cube audit, fold map, fold registry, nativelifecycle predecessor, and nativecontrolfold passed.

# rev0086 — nativeselection-fallbackjournal-promotehold

- Added `nativeselection.py` so native artifacts are selected only at an exact operation boundary after provenance, corpus, quarantine, budget, artifact/source digests, fallback digest, and diversity agree.
- Added `fallbackjournal.py` so Python fallback routing becomes restart-sticky memory instead of invisible control flow.
- Added `nativepromotion.py` so promotion back to native preserves prior fallback/quarantine memory.
- Added `nativeselectionfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, head registry, and evidence scripts.
- Verification: surface check, micro-simulation, targeted rev0085/rev0086 tests, chunked pytest, compile check, compileall, cube audit, fold map, fold registry, predecessor nativeprovenancefold, and nativeselectionfold passed.

# rev0079 — summaryexportreceipt-importgate-retentionaudit

- Added `summaryexportreceipt.py`, `summaryimportgate.py`, and `exportretentionaudit.py`.
- Added `summaryexportreceiptfold.py` and current-path docs/tests.
- Continued no-network exact-boundary pressure after rev0078's summary export fence.


## rev0075 — summarysendcanary-redactiongc-outboxsettlement

- Added `summarysendcanary.py` for no-network send-canary readiness after summary outbox/redaction archive/publish fence agreement.
- Added `redactiongc.py` so redaction evidence can be compacted only while preserving contradiction memory.
- Added `outboxsettlement.py` for prepared/aborted/suppressed summary outbox markers.
- Added `summarysendfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, and evidence scripts.


## rev0071 — handoffreceipt-importsummary-ledgerfold

- Added `handoffreceipt.py` for recipient ACK/refusal memory after redacted closure handoff.
- Added `handoffimport.py` so accepted receipt still cannot import state without exact-boundary redacted markers.
- Added `summarylineage.py` for redacted operator/garden/public-summary lineage after import.
- Added `handoffreceiptfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, and evidence scripts.
- Verification: surface check, micro-simulation, targeted rev0071 tests, full pytest, compile check, compileall, cube audit, fold map, fold registry, exporthandoff predecessor, and handoffreceipt fold passed.


## rev0069 — closureseal-retentionproof-exportaudit

- Added `closureseal.py`, `retentionproof.py`, and `auditexport.py` after rev0068 closure audit.
- Added `closuresealfold.py` and rev0069 docs/tests.
- Verified surface check, micro-simulation, full pytest, compile check, compileall, cube audit, fold map/registry, predecessor archivejournalfold, and closuresealfold.

# rev0065 — remotewitness-repairoutbox-conflictcooldown

- Added remote witness ledger rounds for replay/fork/drift/contradiction-carrying pressure.
- Added repair outbox staging after remote duplicate conflicts.
- Added conflict cooldown for repeated duplicate-delivery evidence.
- Added `remoterepairfold` audit/refactor and updated current public-edge surfaces.


## rev0061 — deliverysettlement-ackarchive-prunejoin

- Added `deliverysettlement.py` for settled-delivery markers after live-send/delivery/fence acceptance.
- Added `ackarchive.py` for restart-sticky archive memory and idempotency conflict pressure.
- Added `ackprunejoin.py` to prevent archive/prune laundering of hard-negative or pending delivery evidence.
- Added `ackfold.py` audit/refactor surface preserving rev0060 `fenceaudit` as predecessor.
- Verified current/predecessor surface through chunked pytest, micro-simulation, compile check, compileall, cube audit, fold map, fold registry, and zip integrity.


## rev0059 — settlementstore-tombmesh-canaryjoin

- Folded the alternate rev0058 settlement/attestation/tombstone-repair branchlet into active source history.
- Added `settlementstore.py` to make finality and settlement agree before sticky local truth.
- Added `tombrepairjoin.py` to carry tombstone repair through prune pressure.
- Added `canaryjoin.py` to bind no-network SAM/router canaries to post-settlement state.
- Added `settlementstorefold.py` and rev0059 docs/tests/surface-ledger entries.

# rev0059 — settlementstore-tombmesh-canaryjoin

- Folded alternate rev0058 settlement/attestation/tombstone-repair branchlet into the current finality/prune lineage.
- Added/active tested settlement store and terminal receipt joined-boundary surfaces.
- Updated settlementfold audit, surface ledger, fold map, fold registry, docs, and public pointers for rev0059.

# Changelog

## rev0058 — finalityledger-retryescrow-pruneguard

- Added `finalityledger.py` for signed finality markers after effect reconciliation.
- Added `retryescrow.py` so retry attempts carry dead-letter lineage and exact idempotency.
- Added `pruneguard.py` to keep hard negatives, accepted finality, and pending retry/dead-letter memory through storage pressure.
- Added `finalityfold.py` and current docs/tests/fold-map/registry/surface-ledger entries.
- Kept the cube no-network: no live SAM/I2P side effects, no production finality consensus, and no production persistence database.

## rev0056 — recoverymesh-safecleanup-chaosbudget

- Added `sealreplay.py` for effect-seal restart-generation observations.
- Added `corpuswitness.py` for fuzz-shrink witness receipts.
- Added `recoverymesh.py` to join effect seal, restart chaos, seal replay, and corpus evidence.
- Added `safecleanup.py` so cleanup preserves accepted seals and hard negatives.
- Added `chaosbudget.py` for bounded post-effect rehearsal/cleanup/fuzz work.
- Added `recoveryfold.py` and current docs/tests/public pointers.

# rev0054 — replaylab-handlerquench-fuzzledger

- Added `handlerreplay.py` for signed restart replay frames around handler-capsule, side-effect-journal, and adapter-fuzz reports.
- Added `handlerquench.py` for repeated near-miss inbound handler cooldown, useful-refusal loop pressure, and raw-key metadata budget pressure.
- Added `fuzzledger.py` for persistent adapter-fuzz coverage with sequence, previous-link, generator, report, and coverage digest checks.
- Added `replayfold.py` audit path and rev0054 docs/tests.
- Kept the cube no-network: no live SAM/I2P side effects and no production handler dispatcher/database/fuzz engine.

---

# rev0053 — handlercapsule-sideeffectjournal-adapterfuzz

- Added `handlercapsule.py` for exact-boundary inbound handler permission after profile-edge/live-adapter acceptance.
- Added `sideeffectjournal.py` for signed prepare/commit/abort local side-effect memory with idempotency and phase pressure.
- Added `adapterfuzz.py` for deterministic mismatch coverage summaries.
- Added `handlerfold.py` audit path and rev0053 docs/tests.
- Continued no-network posture: no live SAM/I2P side effects and no production handler dispatcher.

---

## rev0052 — liveadapter-backpressure-profileedge

- Added `liveadapter.py` as a no-network live side-effect seam after router/ingress/backpressure/effect evidence.
- Added `backpressuremesh.py` to join inbound, outbound, router, reserve, raw-key, refusal, and hard-negative pressure.
- Added `profileedge.py` to bind live adapter, profile budget, negative scan, and exact profile/service/scope/request before side effects.
- Added `edgefold.py` and updated fold map/registry/surface ledger/docs for current-path auditability.

## rev0051 — ingressdrain-routercanary-redteamfold

- Added `routercanary.py` for no-network router/session/public-edge checks after SAM canary acceptance.
- Added `ingressdrain.py` for inbound public-bridge work draining before handler side effects.
- Added `redteamfold.py` and docs/tests/ledger entries to pin the two-sided public-edge boundary.

## rev0049 — publishdryrun-witnesscompact-scopejournal

- Added publicoutbox, auditgap, and outboxfold surfaces.
- Tested no-network public side-effect staging, idempotency conflict, watch debt, hard-negative pressure, and audit-gap repair planning.


## rev0048 — bridgeshadow-auditquorum-redressgc

- Added `bridgeshadow.py` signed no-network dry-run plans before public bridge side effects.
- Added `auditquorum.py` local audit statements as evidence, not truth.
- Added `redressgc.py` hard-negative-preserving cleanup pressure for moderation/redress evidence.
- Added `shadowauditfold.py` and moved stale alternate rev0048 branchlets into artifacts for wake-from-amnesia preservation.

# rev0048 — bridgeshadow-auditquorum-redressgc

- Added `bridgeshadow.py`, `auditquorum.py`, `redressgc.py`, and `shadowauditfold.py`.
- Added tests for public bridge shadow side-effect gating, local audit receipt diversity, and redress/moderation evidence retention.
- Updated surface/fold registries for rev0048.

# rev0048 — bridgeshadow-auditquorum-redressgc

- Added `auditquorum.py` for transparency-style checkpoint witnesses around public bridge publication observations.
- Added `bridgeshadow.py` for a no-network exact-boundary side-effect gate after publication guard acceptance.
- Added `redressgc.py` for hard-negative-preserving redress/evidence cleanup.
- Added `shadowauditfold.py` and rev0048 docs/tests/public pointers.

# Changelog

## rev0047 — appealmesh-publicationquench-branchfold

- Added witness-appeal mesh for watched public bridge decisions.
- Added publication ledger boundary for public publish/withdraw/repair records.
- Added bridge quench lane for stale public replay, hard negatives, false service, and refusal/watch loops.
- Added policy-source portfolio pressure so subjective policy is not a singleton authority surface.
- Added publication guard as the final no-network gate before future public bridge refresh/withdraw/repair side effects.
- Folded sibling rev0046 public-bridge branchlets into visible historical artifacts.
- Added rev0047 fold audits and metadata pointers for both appeal/publication and policy/publication lanes.

# rev0044 — compartmentfirewall-controlreceipt-foldbridge

- Folded the alternate rev0043 controlintent/bridgefirewall branchlet into active code and branchlet artifacts.
- Added compartmentfirewall joined-boundary reducer.
- Added signed controlreceipt restart-memory lane.
- Added foldbridge audit/refactor path.

---

# rev0043 — keycompartment-authoritysplit-fold

- Added `keycompartment.py` for role-separated public-key binding capsules.
- Added `authoritysplit.py` to join component reports at exact profile/scope/object/request boundaries.
- Added `compartmentfold.py` and updated foldmap/foldregistry/surfaceledger metadata for current path visibility.
- Verification: 581 tests passed, compile check covered 313 files, cube audit reported 0 warnings / 56 info findings / 0 errors.

---

# rev0041 — routerstop-sessionresume-exitjournal

- Added router-stop shadow plans.
- Added joined session-resume gate.
- Added exit/control journal restart memory.
- Added controlfold audit/refactor lane.

---

# rev0039 — continuityjournal-probeloop-successionrepair

- Added `servicehealth.py`, a post-continuity health window that rejects active withdrawal, replay, metadata-budget overrun, one-family monoculture, refusal-heavy loops, and scope drift.
- Added `servicedrain.py`, a safe drain/stop pressure lane that preserves withdrawal evidence, receipts, public-announcement state, protected work, and hard-negative memory.
- Added `continuityjournal.py`, a continuity-specific restart journal for replay memory, monotonic links, scope binding, and hard-negative preservation.
- Added `serviceopsfold.py`, a current-revision fold audit preserving the rev0038 servicecontinuity predecessor.
- Parked earlier speculative rev0039 branchlet tests under `artifacts/branchlets/rev0039_unintegrated_tests/`.

# rev0039 — servicelease-sessionledger-fold

- Added `servicelease.py`, a short-lived ongoing-service lease after service-continuity acceptance with sequence, previous-link, exact-boundary, replay, budget, and renewal drift pressure.
- Added `sessionledger.py`, a repeated-window service-session ledger for replay, same-window fork, binding drift, active withdrawal, quota overspend, refusal-only loops, low family diversity, and hard-negative contradictions.
- Added `sessionfold.py` and updated foldmap/foldregistry/surfaceledger metadata so rev0039 is visible while preserving rev0038 servicecontinuityfold predecessor history.

# rev0038 — servicecontinuity-branchfold

- Folded alternate rev0037 garden-service branchlets into the active cube: catalogwire, serviceprobe, profilegcjoin, catalogsuccession, servicewithdrawal, servicerelay, serviceusegate, handofflane, and receiptveil.
- Added `servicecontinuity.py`, a joined boundary that rejects active withdrawal, replay, duplicate branch reports, quarantined branch reports, catalog/scope/request drift, missing required branches, and refusal-only/watch-only acceptance.
- Added `servicecontinuityfold.py` to audit the folded branchlets through code, tests, docs, public pointers, foldmap, foldregistry, and surfaceledger while preserving rev0037 ticketfold/serviceguardfold predecessors.
- Verification: 512 tests passed, compile check covered 274 files, cube audit reported 0 warnings / 49 info findings / 0 errors.

# rev0037 — ticketlane-servicereceipt-registryfold

- Added exact-scope `serviceticket.py` grants after servicecatalog/loadsheath acceptance.
- Added signed `servicereceipt.py` observations for completion, useful refusal, and partial service.
- Added `ticketfold.py` and updated foldregistry/foldmap/surfaceledger for current path visibility.
- Preserved rev0036 servicefold as predecessor history.

# Changelog

## rev0036 — servicecatalog-loadsheath-profilegc

- Added signed service catalog capsules bound to accepted start/router surfaces.
- Added per-service load sheath and useful-refusal budget pressure.
- Added profile/config GC preserving hard negatives.
- Added foldregistry/servicefold audit/refactor path.

## rev0035 — startmatrix-telemetrydebt-routerharness

- Added `startmatrix.py` for leaf/garden/bridge/offline profile acceptance after launch quorum and router harness checks.
- Added `routerharness.py` for bundle-first/external-SAM/offline config capsule pressure before live router side effects.
- Added `telemetrydebt.py` so retained veiled diagnostics are budgeted and cannot compact away hard-negative evidence.
- Added `startfold.py` and updated foldmap/surfaceledger metadata for rev0035 while preserving rev0034 foldmerge history.


## rev0034 — launchquorum-metricsveil-foldmerge

- Added `launchquorum.py` to join safe-start, durable restart memory, and explicit SAM probe outcomes before local launch.
- Added `metricsveil.py` to redact and budget diagnostics before operator feedback can leak raw keys/destinations.
- Folded the parallel rev0033 `persistjoin` / `samprobe` / `foldreduce` branchlet into active source/test surfaces and branchlet docs.
- Added `foldmerge.py` and updated foldmap/surfaceledger metadata for rev0034.


## rev0032 — scopeledger-storedebt-samtrace

- Added `scopeledger.py`, `storedebt.py`, `samtrace.py`, and `scopefold.py`.
- Added joined-boundary tests for scope/probe/obligation, store/custody/tombstone/repair, and SAM shadow/egress/scope boundaries.
- Updated fold/audit metadata for rev0032 while preserving rev0031 foldmap history.

# Changelog

## rev0031 — probeledger-crisisroute-sketchboundary

- Added `probeledger.py` for repeated-round bootstrap/live-probe/absence memory before sticky entrance advance.
- Added `crisisroute.py` to join key-crisis gates with contact leases, successor evidence, tombstones, and revocations before route use.
- Added `sketchboundary.py` as the explicit boundary between exact toy reconciliation and future native minisketch/IBLT adapters.
- Added `foldmap.py` so current and historical fold surfaces are audited declaratively.
- Folded the scopefence/obligationdebt/decaymesh branchlet into the visible rev0031 path and preserved predecessor fold audits.

## rev0031 — scopefence-obligationdebt-decaymesh

- Added `scopefence.py` for exact signed scope/object/request/purpose fences before joined evidence can authorize work.
- Added `obligationdebt.py` for proof debt left by provisional local accepts.
- Added `decaymesh.py` for typed evidence aging that preserves hard negatives while dropping stale soft evidence.
- Replaced the active rev0031 branchlet path with `auditmesh.py` and kept a compatibility alias for the discarded spelling.
- Added rev0031 docs, ADRs, tests, and active surface-ledger entries.


## rev0031 — leaseprobe-repairdebt-auditmesh

- Added `leaseprobe.py` for challenge-bound, metadata-budgeted contact-lease liveness receipts.
- Added `repairdebt.py` for hard-negative-first repair planning across tombstones, revocations, key crisis, provider-false evidence, and soft repairs.
- Added `auditmesh.py` as a declarative current-revision audit/refactor surface preserving rev0030 keycrisisfold.
- Added rev0031 docs, ADRs, tests, public pointers, and active surface-ledger entries.

## rev0031 — leaseprobe-repairdebt-auditmesh

- Added lease-bound probe join across contact leases, live probes, egress budgets, and key-crisis gates.
- Added typed repair-debt scheduling with tombstone-first, conflict, family, and budget pressure.
- Added auditmesh current-fold audit/refactor surface.

## rev0030 — negspace-peerdelta-keycrisisfold

- Added `negspace.py` for signed absence observations and positive-evidence contradiction pressure.
- Added `peerbook.py` for contact-lease entrance views with channel/family diversity.
- Added `peerdelta.py` for exact toy peer-book delta sketches.
- Added `keycrisis.py` for local compromise/freeze/fork/succession gates.
- Added `keycrisisfold.py` and rev0030 docs/tests/ledger entries for audit/refactor visibility.
- Folded joined branchlet tests forward: `bootstrapjoin.py`, `livesmoke.py`, `deltarepairjoin.py`, and `keycrisisjoin.py`.

## rev0030 — negspace-peerdelta-keycrisisfold

- Folded parallel rev0029 absence/key-crisis and peerbook/delta/live-probe branchlets into the active cube surface.
- Added `absencegate.py`, `keycrisis.py`, `peerbook.py`, `deltasketch.py`, `rangesetdelta.py`, `liveprobe.py`, and `branchrecoverfold.py`.
- Added tests for tombstone-supported absence, fast-empty capture, key compromise recovery rotation, introducer capture, no-router SAM skip, SAM-shadow destination binding, delta-sketch repair pressure, and branchrecoverfold audit.
- Updated public/current surfaces, proof obligations, surface ledger, and historical supersession map.


## rev0029 — checkpointlane-egressmeter-foldseal

- Added `checkpointlane.py` for signed checkpoint summaries with generation, previous-link, journal-tip, hard-negative preservation, rollback, fork, and conflict pressure.
- Added `egressmeter.py` for outbound byte/stream/raw-key/family/decoy/replay budget pressure.
- Added `dispatchjoin.py` to bind misbind-guard acceptance to same-scope same-object egress before handler dispatch.
- Added `foldseal.py` as the rev0029 audit/refactor seal and predecessor foldspine check.
- Added rev0029 docs, ADRs, proof obligations, and tests.

## rev0028 — journallane-generatorfuzz-foldspine

- Added crash-cut append-only journal replay pressure and hard-negative compaction tests.
- Added generated deterministic fuzz corpus expansion from accepted fuzzwire seeds.
- Added refusal/schedule join pressure so useful-refusal loops affect scheduling.
- Added no-network SAM-wire scripts carrying canonical wire frames.
- Added foldspine declarative audit/refactor and preserved unintegrated rev0028 branchlet tests under artifacts.

## rev0028 — `journallane-generatorfuzz-foldspine`

- Added `journallane.py` for signed append-only toy journal frames, hash-chain replay, tail repair, and hard-negative preservation after restart.
- Added `generatorfuzz.py` for deterministic seed-based malformed-input sweeps over parseguard, wirecanon, and transportshadow.
- Added `refusalschedule.py` to feed repeated useful-refusal pressure into future scheduling/backoff decisions.
- Added `foldspine.py` as a current-revision audit/refactor spine.
- Added rev0028 docs, ADRs, proof obligations, and tests.

# Changelog

## rev0027 — branchmerge-persistfuzz-refusalloop

- Folded the parallel rev0026 lineage/workmeter branchlet into the spoken schedjoin/custody/transport-shadow branch instead of discarding it.
- Added `persistlane.py` for signed, parseguarded local snapshots, crash/reload rollback/fork/prev-link pressure, and hard-negative-preserving compaction.
- Added `fuzzwire.py` for deterministic malformed parser/wire/shadow fixture generation.
- Added `refusalloop.py` for repeated useful-refusal laundering pressure across garden windows.
- Added `branchmergefold.py` and updated surface ledgers/audits so both rev0026 branchlets and rev0027 surfaces are navigation-visible.


## rev0026 — schedjoin-custodygc-transportshadow

- Added joined scheduling after capability/admission to protect control-plane work from bulk pressure and refusal laundering.
- Added custody/evidence GC normalization across custody audits, tombstone mesh, witness cache, and revocation-head pressure.
- Added partition witness merge so split-merge commits wait for route and witness gates.
- Added transport shadow canonical report frames before live SAM/I2P.
- Added joinfold current-surface audit/refactor and updated active surface ledger.


## rev0025 `capgate-evidencegc-splitmerge`

- Added `src/i2p_dht_lab/capgate.py` to join namespace dispatch, delegated capability validation, revocation sets, and admission budgets before handler dispatch.
- Added `src/i2p_dht_lab/evidencegc.py` for local evidence retention/GC under tombstone, fork, revocation, family-cap, expiry, and byte-budget pressure.
- Added `src/i2p_dht_lab/splitmerge.py` for mutable epoch-head split-brain/partition merge pressure with previous-link and diversity checks.
- Added `src/i2p_dht_lab/riskfold.py` to audit rev0025 current-surface visibility across code, tests, docs, public pointers, and the active surface ledger.
- Added `tests/test_rev0025_capgate_evidence_splitmerge.py` and docs `231` through `239`.
- Updated the micro-simulation and assurance lane to include capgate/evidencegc/splitmerge/riskfold.

# rev0024 — interestpolicyrelay-gatefold

- Folded three risk-first surfaces into one current cube: interest-mixed provider probes, lease-bound route attestations plus dispatch-gate auditing, and policy/range/queue repair work.
- Recovered and tested clock guard, relay ticket, gossip sieve, interest ledger, pressure ledger, and region receipt branchlets under an explicit branchlet-fold audit.
- Added gate-fold and clock-fold audit/refactor surfaces; active surface ledger now lists folded branchlets rather than hiding them as orphan speculation.
- Verification lane: 347 pytest tests passed; cube audit passed with 0 warnings / 49 info findings / 0 errors.

# Changelog

## rev0024 — interestpolicyrelay-gatefold

- Added `policyepoch.py` for mutable namespace-policy epoch heads with digest binding, previous links, rollback/fork pressure, family diversity, and watch-mode behavior.
- Added `rangemerkle.py` for Merkle-ish range repair fixtures, inclusion proofs, exact repair, bad-proof rejection, and tombstone-first repair.
- Added `queueforge.py` for garden admission queue scheduling under latency, bulk flood, family flood, reserve-slot, and useful-refusal pressure.
- Added `policyfold.py` and active surface-ledger entries for rev0024 navigation/audit hygiene.

## rev0024 `interestmix-routeattest-gatefold`

- Folded the alternate `interestmix-routeattest-gateaudit` branchlet into the active mainline as rev0024.
- Added `interestmix.py` for metadata-budgeted provider probe rounds with real/cover targets, repeat-memory pressure, raw-key exposure budgets, and family-spread checks.
- Added `routeattest.py` for lease-bound route attestations with contact-family, attester-family, and path-family pressure.
- Added `gateaudit.py` for dispatch-gate auditing after validator-wall success.
- Added `gatefold.py` for branchlet fold visibility across public surface, docs index, surface ledger, and historical supersession map.
- Added `tests/test_rev0024_interestmix_routeattest_gatefold.py`.
- Updated docs 213 through 221 and ADRs 0096 through 0099.


## rev0023 `rangesketch-admissionwall-namespacefold`

- Added `rangesketch.py` for signed range-root anti-entropy repair hints, tombstone-first repair pressure, same-sequence fork quarantine, stale replay quarantine, and source-family diversity.
- Added `admissionwall.py` for namespace/family/budget admission before expensive handler work, with signed useful-refusal receipts and replay quarantine.
- Added `namespaceregistry.py` for local signed namespace validator policies with rollback/fork, role/kind, TTL/size, flag, and scope pressure.
- Added `namespacefold.py` to audit current namespace/admission/range surfaces across docs and active surface ledger.
- Added `tests/test_rev0023_rangesketch_admission_namespace.py`.

## rev0022 `antientropy-validatorwall-parseguard`

- Added `parseguard.py` for strict bounded canonical bdecode before inbound wire payloads are trusted.
- Added `validatorwall.py` for namespace, role/kind, scope, body digest, flag, and request-id conflict checks before handler dispatch.
- Added `antientropy.py` for signed short-lived summaries that request repair without deciding truth.
- Added `surfaceindex.py` to audit current-revision navigation across public surface, head registry, docs index, and active surface ledger.
- Added `tests/test_rev0022_antientropy_validatorwall_parseguard.py`.


## rev0021 — `epochsplit-storewire-repairreplay`

- Added `epochsplit.py` for repeated mutable-head split-view, stale replay, same-sequence fork, previous-link split, and latest-diversity pressure.
- Added `storewire.py` for exact-digest STORE/custody wire transcript fixtures over canonical signed frames.
- Added `repairreplay.py` for garden repair-market replay, sequence rollback, useful-refusal backoff, and family-capture pressure across windows.
- Refactored `surfacefold.py` to discover current docs from the requested revision instead of hard-coding rev0020.
- Updated `surfaceledger.py`, docs, ADRs, claim surfaces, and proof obligations for rev0021.

# rev0020 `epochgate-repairmarket-wirecanon`

- Added `epochgate.py` for purpose/scope-bound mutable epoch heads, local monotonic memory, previous-digest linkage, rollback/fork/gap pressure, and path/source diversity gates.
- Added `repairmarket.py` for garden repair-capacity selection without currency, global reputation, or authority transfer.
- Added `wirecanon.py` for deterministic signed wire-frame fixtures and transcript digests before live SAM/I2P transport.
- Added `surfacefold.py` for current-revision navigation audit/refactor.
- Added tests in `tests/test_rev0020_epochgate_repairmarket_wirecanon.py`.

# Changelog

## rev0019 `leaseroute-storemesh-budgetreceipt`

- Added `src/i2p_dht_lab/leaseroute.py` for lease-bound route gossip: fresh route-purpose contact leases, stale eviction, rollback/fork pressure, unleased selection quarantine, and captured-introducer pressure.
- Added `src/i2p_dht_lab/storemesh.py` for joining sibling store acknowledgements across mutable heads, tombstones, providers, exact digests, useful refusals, and repair pressure.
- Added `src/i2p_dht_lab/budgetreceipt.py` for signed garden budget receipts bound to sweep-audit decisions, including digest mismatch, replay, rollback, and same-sequence fork pressure.
- Added `src/i2p_dht_lab/roundledger.py` for repeated-round pressure across liveness budgets, provider proofs, witness-cache summaries, and stale/captured fast windows.
- Added `src/i2p_dht_lab/storecontract.py`, `custodyaudit.py`, and `storerepair.py` for STORE contracts, custody challenges, repair planning, renewals, refusal semantics, and quarantine triggers.
- Preserved the `storeflight.py` / `leasequorum.py` branchlet as an active risk-first lane and archived unintegrated branchlet tests under `artifacts/branchlets/rev0019_unintegrated_tests/` instead of deleting them.
- Refactored/audited active surfaces with `surfaceclean.py`, `surfaceledger.py`, `HISTORICAL_SUPERSESSION.json`, and cache-safe evidence scripts; pytest now covers 238 active tests in the cloudtainer lane.


## rev0018 `livenessmesh-contactcast-surfaceaudit`

- Added `src/i2p_dht_lab/livenessbudget.py` for liveness/metadata budgeting between adaptive lookup pressure and private-ish provider probe plans.
- Added `src/i2p_dht_lab/tombmesh.py` for tombstone mesh pressure across tombstone-cache reports, witness summaries, and mutable head events.
- Added `src/i2p_dht_lab/provider_compat.py` and `src/i2p_dht_lab/providerwrap.py` to classify and wrap legacy provider-plane surfaces before deletion or silent aliasing.
- Added `src/i2p_dht_lab/contactlease.py` for signed, sequence-aware contact leases, rollback/fork detection, purpose coverage, and family-diverse entrance portfolios.
- Added `src/i2p_dht_lab/siblingbroadcast.py`, `src/i2p_dht_lab/siblingcast.py`, and exact-digest store-ack tests for family-diverse replica evidence.
- Added `src/i2p_dht_lab/keyspacecartography.py` for local XOR-region holes, stale regions, family/introducer monoculture, and scout planning.
- Added `src/i2p_dht_lab/sweepaudit.py` for garden region-sweep budget/diversity/tombstone-priority audits.
- Added `src/i2p_dht_lab/surfaceaudit.py` and `src/i2p_dht_lab/surfaceledger.py` for audit/refactor hygiene: JSON pointer checks and active module/test/doc pinning.
- Refined `sweepaudit.py` so source-family monoculture is visible even when the region ledger quarantines before producing batches.
- Added `tests/test_rev0018_liveness_tombmesh_providerwrap.py`, `tests/test_rev0018_sibling_cartography_surfaceaudit.py`, and `tests/test_rev0018_contactlease_siblingcast_sweepaudit.py`; pytest now covers 188 tests in the cloudtainer lane.
- Added combined rev0018 docs 160–163, contact/sibling/sweep docs 151–155, and preserved earlier liveness/tombmesh/providercompat docs 143–149 with supersession mapping.

## rev0017 `regionledger-adaptivealpha-witnessrepair`

- Added `src/i2p_dht_lab/adaptivealpha.py` for transcript-driven adaptive alpha/beta lookup pressure, including fast-window capture quarantine, timeout expansion, useful-refusal hold, and diverse-success acceptance.
- Added `src/i2p_dht_lab/regionledger.py` for garden region-sweep memory, source-family pressure, tombstone suppression, weight-capped batches, and deterministic ledger digests.
- Added `src/i2p_dht_lab/tombstonecache.py` for signed tombstone records, resurrection-pressure blocking, same-sequence tombstone fork quarantine, and key-compromise diversity pressure.
- Added `src/i2p_dht_lab/witnessrepair.py` for bounded witness-cache repair actions and contradiction quarantine.
- Extended `src/i2p_dht_lab/provider_refactor.py` to distinguish historical legacy imports from active legacy imports.
- Added `tests/test_rev0017_regionledger_adaptivealpha_witnessrepair.py`; pytest now covers 160 tests in the cloudtainer lane.
- Added docs `134` through `142` and ADRs `0070` through `0074`.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, and micro-simulation report for rev0017.

## rev0016 `routegossip-cachepoison-samgarden`

- Added `routegossip.py` for route-gossip repair pressure: stale-contact eviction, family caps, introducer-capture quarantine, and deterministic repair transcripts.
- Added `cachepoison.py` to connect lookup transcripts with witness-cache summaries across repeated rounds, including replay monoculture, fast-capture reinforcement, and contradiction quarantine.
- Added `samgarden.py` for SAM shadow transcript families needed by future garden nodes: outbound connect, inbound accept, reconnect after close, naming failure, and datagram-primary negative tests.
- Extended `samshadow.py` with STREAM ACCEPT/CLOSED fixture support.
- Extended `provider_refactor.py` with legacy import scanning and migration recommendations before converting `providerpoison.py` into a wrapper.
- Added `tests/test_rev0016_routegossip_cachepoison_samgarden.py`; pytest now covers 148 tests in the cloudtainer lane.
- Added docs 126 through 133 plus ADRs 0065 through 0069.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, micro-simulation report, and audit report for rev0016.

## rev0015 `witnesscache-routingpressure-samshadow`

- Added `witnesscache.py` for local witness receipt aging, duplicate collapse, family caps, weight decay, contradiction quarantine, and deterministic evidence summaries.
- Added `lookuptranscript.py` for explicit transport-neutral lookup transcripts, path/family pressure, captured fast-window detection, timeout/bad-response pressure, and evidence-only proof/witness surfaces.
- Added `samshadow.py` for no-network SAM transcript fixtures that validate streaming-first, persistent-destination assumptions before live I2P transport.
- Added `gardenscheduler.py` for multi-window garden admission/refusal scheduling that protects head-watch, witness-query, and seed-gate work from bulk provider floods.
- Added `provider_refactor.py` to audit the providerpoison/provider_poison split and record `provider_poison.py` as canonical while preserving legacy history.
- Added `tests/test_rev0015_witnesscache_routingpressure_samshadow.py`; pytest now covers 137 tests in the cloudtainer lane.
- Added docs 117 through 125 plus ADRs 0059 through 0064.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, micro-simulation report, and audit report for rev0015.

## rev0014 `proofprobe-gardensentinel-sweepgrid`

- Added `familydiversity.py` as a shared local helper for family caps, diversity reports, and monoculture pressure; explicitly not an independence oracle.
- Added `proofprobe.py` to connect private-ish provider probe plans with provider proof handshakes, including decoys, raw-key exposure pressure, false-provider quarantine, useful-refusal handling, and true-provider family diversity.
- Added `gardensentinel.py` to turn provider proof reports and witness mesh reports into local garden/sentinel salience decisions without global reputation.
- Added `sweepgrid.py` for deterministic adversarial sweeps across captured families, false providers, stale heads, and latency advantage.
- Added `supersession.py` and `HISTORICAL_SUPERSESSION.json`; updated `cubeaudit.py` so documented historical duplicate docs/ADRs/module names become info-level findings.
- Added `tests/test_rev0014_proofprobe_gardensentinel_sweepgrid.py`; pytest now covers 125 tests in the cloudtainer lane.
- Added docs 109 through 116 plus ADRs 0054 through 0058.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, micro-simulation report, and audit report for rev0014.

## rev0013 `proofhandshake-headwitness-latencyforge`

- Added `proofhandshake.py` for provider availability claims, nonce-bound proof challenges, proof responses, wrong-content rejection, useful refusal handling, replay/deadline checks, and metadata exposure pressure.
- Added `headwitness.py` for path-family-aware mutable-head lookup pressure, garden witness statements, stale/fork/previous-link decisions, and accept-with-watch behavior.
- Added `latencyforge.py` for fake SAM-like latency/churn/retry tests with timeouts, useful refusals, captured fast windows, and deterministic transcript digests.
- Added `cubeaudit.py` plus `scripts/evidence/run_cube_audit.py` for non-failing cube surface audit warnings.
- Pruned transient pytest cache from the packaged artifact and set the CI lane to avoid bytecode/cache emission.
- Added `tests/test_rev0013_proof_head_latency_audit.py`; pytest now covers 116 tests in the cloudtainer lane.
- Added docs 102 through 108 plus ADRs 0049 through 0053.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, micro-simulation report, and audit report for rev0013.

## rev0012 `probewitness-privateprovider-chaossweep`

- Added `privateprovider.py` for metadata-budgeted provider probe planning, decoy probes, commitment-only witness surfaces, raw-key exposure counts, and family caps.
- Added `probewitness.py` for signed witness receipts, family-diversity pressure, and self-contradiction quarantine.
- Added `chaossweep.py` for deterministic captured-fast-window and family-cap sweeps.
- Added `wiretranscript.py` for signed transport-neutral frame fixtures and transcript digests.
- Added `tests/test_rev0012_privateprovider_witness_sweep.py`; pytest now covers 103 tests in the cloudtainer lane.
- Added docs 95 and 97 through 101 plus ADRs 0045 through 0048.
- Updated wake surface, claim surface, proof obligations, lifecycle gates, and micro-simulation report for rev0012.


## rev0011 `providerpoison-gardenrefusal-churnforge`

- Added `src/i2p_dht_lab/providerpoison.py` for provider-plane poison pressure: false providers, wrong content, silence, graceful refusal, invalid records, semantic confirmations, family diversity, and order-stable provider batch digests.
- Added `src/i2p_dht_lab/provider_poison.py` for longer-lived local provider memory: probe outcomes, quarantine, useful-refusal backoff, and family-rotated provider selection.
- Added `src/i2p_dht_lab/gardenrefusal.py` for garden useful-refusal/admission scaffolding: signed bounded refusal receipts, fair request ordering, per-family pressure, refusal batch analysis, contradictory-garden detection, and overload/drop separation.
- Added `src/i2p_dht_lab/garden_churn.py` for garden mutable-head/churn lookup behavior: latest/stale/refusing/drop events and bounded refusal backoff.
- Added `src/i2p_dht_lab/churnforge.py` for path-family churn frontier selection, captured-fast-window detection, and stable transcript digests.
- Added `tests/test_rev0011_providerpoison_gardenrefusal.py`, `tests/test_rev0011_provider_garden_churn.py`, and `tests/test_rev0011_churnforge.py`.
- Added docs `88` through `93` and ADRs `0041` through `0044`.
- Updated micro-simulation evidence to include provider poison, garden refusal, and churn-frontier pressure.

## rev0010 `seedcapture-witnesspoison-pathpressure`

- Added `src/i2p_dht_lab/pathpressure.py` for path-family-aware mutable lookup pressure, post-hoc stale detection, and conservative continuation decisions.
- Added `src/i2p_dht_lab/witnesspoison.py` for receipt validity, family diversity, and contradictory-witness analysis.
- Added `src/i2p_dht_lab/seedcapture.py` for seed-portfolio capture pressure and diversity-biased bootstrap selection.
- Added `src/i2p_dht_lab/revocation_pressure.py` for history-aware revocation-head rollback/fork memory and cumulative revoked-hash preservation.
- Added `src/i2p_dht_lab/succession.py` for co-signed key succession records and rollback/fork detection.
- Added `tests/test_rev0010_risk_first.py` with 12 hard-guess tests.
- Added docs `80` through `87` and ADRs `0036` through `0040`.
- Updated micro-simulation evidence to include path pressure, seed capture, revocation rollback, witness analysis, and succession forks.

## rev0009 `forkwatch-capgrant-chaosloom`

- Added `src/i2p_dht_lab/forkwatch.py` for local mutable-head history, same-sequence fork detection, rollback/stale detection, and signed witness receipts.
- Added `src/i2p_dht_lab/capgrant.py` for scoped delegated capability grants, resource/audience/verb checks, revocation heads, and mutable revocation-head wrappers.
- Added/extended `src/i2p_dht_lab/chaos.py` for fake adversarial mutable lookup transcripts and seed portfolio capture reports while keeping legacy headlog chaos compatibility.
- Added `tests/test_forkwatch_capgrant_chaos.py` for the new hard-guess pressure lane.
- Added docs `72` through `78` and ADRs `0032` through `0034`.
- Updated proof obligations and lifecycle gates to mark forkwatch, capgrant, and seed-capture as toy-tested.

## rev0009 `forkwatch-capgrant-chaosloom`

- Added `headlog.py` with history-aware mutable head values, local monotonic memory, previous-head digest checks, rollback/fork verdicts, and signed garden witness receipts.
- Added `capability.py` with scoped, expiring, signed capability grants, delegation-chain validation, revocation entries, and revocation mutable heads.
- Added `chaos.py` with deterministic fake mutable-head lookup transcripts for honest/stale/fork/empty responders.
- Added `tests/test_headlog_capability_chaos.py` covering rollback, same-sequence forks, previous-link mismatches, witness receipts, capability chains, revocation heads, and fake lookup chaos.
- Added docs 72–79 and ADRs 0032–0035.
- Updated the micro-simulation and assurance surface to include rev0009 risk-first mutability evidence.

## rev0007 `soverseed-bridgeban-mutualaid`

- Added signed contact cards as the proposed DHT entrance atom: I2P Destination, DHT public key, derived node id, capabilities, hints, expiry, and signature.
- Added `src/i2p_dht_lab/sovereignty.py` for entrance channels, participation modes, contact-card validation, entrance cache, and I2P-only readiness.
- Added `src/i2p_dht_lab/bridge.py` for localhost/private/public classic-client bridge modes, bridge budgets, operation planning, and gateway guardrails.
- Added `src/i2p_dht_lab/governance.py` for scoped subjective policy capsules and key-ban decisions that affect official surfaces without claiming DHT truth.
- Added `tests/test_sovereignty_governance_bridge.py` for contact cards, readiness, policy decisions, and bridge refusals.
- Added docs `56` through `64` covering sovereignty seeding, contact cards, default-off I2P-only mode, classic bridgeback, subjective key bans, mutual-aid economics, research notes, Python surface, and wake notes.
- Added ADRs 0023-0027 for legacy clients as entrance distributors, I2P-only readiness, classic bridge as garden service, scoped key bans, and mutable control plane for policy/seed records.
- Updated micro-simulation evidence to include contact-card entrance cache, I2P-only readiness, policy capsule refusal, and bridge refusal.

## rev0006 `mutasync-gardenlog-flossresilio`

- Added mutable sync as a first-class DHT design pressure while keeping the cube DHT-only.
- Added `src/i2p_dht_lab/mutasync.py` with collection ids, writer grants, per-writer feed entries, snapshot manifests, mutable sync heads, conflict guesses, and garden sync service planning.
- Added `tests/test_mutasync.py` for grants, feed chaining, snapshot heads, roster heads, conflict preservation, and sync garden budgets.
- Added docs `48` through `55` covering mutasync dream, record algebra, garden sync services, conflict/capability threats, research notes, wire sketch, Python surface, and wake notes.
- Added ADRs 0020-0022 for DHT-as-control-plane, per-writer feeds, and garden sync non-authority.
- Updated micro-simulation evidence to include mutable sync feed and snapshot heads.

## rev0005 `gardennode-autocuration-supergive`

- Promoted garden nodes to a first-class DHT design role: voluntary giving supernodes rather than protocol authorities.
- Added docs for garden-node service functions, local autocuration, supernode guardrails, and protocol sketches.
- Added `src/i2p_dht_lab/garden.py` with resource budgets, garden service offers, local encounter salience, receipts, and guardrails.
- Added `tests/test_garden.py` for budget planning, metadata ceilings, salience ranking, reciprocal benefits, receipts, and contact capability decoration.
- Updated the micro-simulation evidence lane to include garden planning and non-authority guardrails.

## rev0004 — `powerloom-hotpath-quorumdream`

- Refocused on deep DHT design guesses for a generic DHT over I2P.
- Added disjoint lookup planning and quorum decision scaffolding.
- Added provider/mutable reannounce sweep scheduling by keyspace region.
- Added canonical-plus-sloppy replica placement for hot keys and lookup-path breadcrumbs.
- Added power-user contribution role/profile hints.
- Added adversarial observation readout seed.
- Added mutable slot family scaffolding.
- Added docs for power-user future posture, hot-key/provider sweeps, I2P latency, mutable families, and Sybil/eclipse chaos hypotheses.

## rev0003 — `kadmelia-mutaplane-substratecore`

- DHT-only reset; future applications became consumers, not design drivers.
- Added generic identity, routing, mutable record, provider record, immutable record, replication, RPC, and in-memory simulation scaffolding.

## rev0002

- Added BEP44/BEP46-style mutable slots and i2pd-bundle-first posture.

## rev0001

- Initial baby datacube foundation and research surface.


## rev0008 — mutahead-seedforge-policydream

- Added `mutable_future.py` with open-question and mutability-dream registers.
- Added seed portfolio mutable-head scaffold.
- Added policy portfolio mutable-head scaffold.
- Added local head observation analysis for stale/rollback and same-sequence fork detection.
- Added docs 65–71 and ADRs 0028–0031.
- Kept scope speculative and DHT-first: no live I2P/SAM, no production DHT, no production application integration.

- Folded duplicate active rev0028 test into `artifacts/branchlets/rev0028_duplicate_active_tests/` after pinning the canonical active test.

## rev0046 — moderationquarantine-redresslane-bridgeledger

rev0046 adds moderationquarantine, redresslane, bridgeledger, and moderationfold. Allegations remain local pressure; redress is explicit; public bridge ledger advance requires current policy, shadow-fire, moderation, redress, and stale-announcement evidence to agree.

## rev0060 — livesendgate-deliverywitness-fenceaudit

- Added live-send gate, delivery witness, send fence, and fenceaudit fold.
- Preserved rev0059 settlementstore/tomb/canary predecessor history.


## rev0062 — ackrepair-liveegress-retryfence

- Folded deliveryrepair/rollbackprobe/liveegress branchlet into active source.
- Added ACK/repair join, retry fence, repair prune guard, and egressrepairfold audit.

## rev0063 — lateack-retrysettle-egressjournal

- Added late ACK after retry fence evidence.
- Added retry/withdraw settlement and withdraw repair publication memory.
- Added egress journal compaction that preserves contradictions.
- Added lateackfold audit/refactor surface.


## rev0064 — retrypublish-idempotencymesh-deliveryrepair

- Added `retrypublish.py` for retry/withdraw publication staging after retry settlement and egress journal agreement.
- Added `idempotencymesh.py` for original ACK / retry settlement / retry publication / contradiction lineage.
- Added `deliveryrepairmesh.py` for remote witness pressure before duplicate delivery is treated as benign or repairable.
- Added `retrypublishfold.py` audit/refactor surface and rev0064 docs/tests.

## rev0066 — repairpublish-ackclosure-duplicatefinality

- Added `repairpublishgate.py` for no-network repair publication permission after repair outbox and conflict cooldown.
- Added `repairackledger.py` for ACK/NACK/absence memory after repair publication readiness.
- Added `duplicateclosure.py` for local duplicate-conflict closure while preserving contradiction memory.
- Added `repairpublishfold.py` and current fold/registry/surface-ledger entries for rev0066.
- Updated evidence scripts for rev0066 micro-simulation and cube audit.

## rev0068 — archivejournal-prunereplay-closureaudit

- Added `archivejournal.py` for restart-journaled local memory after repair prune.
- Added `prunereplay.py` for restart-generation replay resistance after prune.
- Added `closureaudit.py` for joined closure audit across settlement/archive/prune/journal/replay.
- Added `archivejournalfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, and evidence scripts.
- Verified surface check, micro-simulation, full pytest, compile check, compileall, cube audit, fold audits, and zip integrity.

## rev0070 — exportreceipt-retentiongc-closurehandoff

- Added `exportreceipt.py` for exact-boundary redacted export receipt restart memory.
- Added `retentiongc.py` so post-export cleanup cannot drop contradiction or hard-negative memory.
- Added `closurehandoff.py` for redacted operator/garden/public-summary handoff packets.
- Added `exporthandofffold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, and evidence scripts.
- Verification: surface check, micro-simulation, targeted rev0070 tests, full pytest, compile check, cube audit, fold map, fold registry, and predecessor fold passed.

## rev0072 — summaryreceipt-importarchive-lineageprune

- Added `summaryreceipt.py` for explicit summary ACK/refusal memory after redacted summary lineage.
- Added `importarchive.py` for restart-sticky import/archive markers after accepted summary receipt.
- Added `lineageprune.py` for protected lineage-prune permission that preserves contradiction/import/archive memory.
- Added `summaryreceiptfold.py` and updated fold map, fold registry, surface ledger, docs index, public pointers, and evidence scripts.
- Verification: surface check, micro-simulation, targeted rev0072 tests, full pytest, compile check, compileall, cube audit, fold map, fold registry, predecessor fold, and zip integrity.

## rev0073 — summarypublish-redactionwitness-importpruneaudit

- Added `summarypublish.py`, `redactionwitness.py`, `importpruneaudit.py`, and `summarypublishfold.py`.
- Added tests for publication readiness, redaction witness receipts, and import-prune audit after redacted summary receipt/archive/prune.
- Audit/refactor: updated fold map, fold registry, active surface ledger, docs index, public pointers, evidence scripts, and current wake-from-amnesia path.
- Verification: surface check, micro-simulation, targeted rev0073 tests, full pytest, compile check, compileall, cube audit, fold map, fold registry, predecessor fold, and zip integrity.

## rev0074 — summaryoutbox-redactionarchive-publishfence

- Added `summaryoutbox.py` for no-network redacted summary outbox staging after publication/redaction/audit agreement.
- Added `redactionarchive.py` for restart-sticky redaction evidence that preserves contradiction memory.
- Added `publishfence.py` for the exact-boundary fence before any future live/public summary write.
- Added `summaryoutboxfold.py` and updated fold map, fold registry, active surface ledger, docs index, public pointers, and evidence scripts.

## rev0076 — summarydrain-deliverywitness-settlementfence

- Added `summarydrain.py` for no-network outbox drain readiness after summary-send canary acceptance.
- Added `summarydeliverywitness.py` for typed ACK / useful-refusal / missing-ACK / NACK / payload-mismatch evidence.
- Added `settlementfence.py` to join canary, drain, delivery witness, redaction GC, redaction memory, and contradiction memory.
- Added `summarydeliveryfold.py` and updated fold map, fold registry, active surface ledger, docs index, public pointers, evidence scripts, and current wake-from-amnesia path.

## rev0078 — summaryreplay-ackclosure-exportfence

- Added `summaryreplay.py` for restart replay after summary ACK/archive/prune evidence.
- Added `ackclosure.py` for exact-boundary terminal local ACK closure.
- Added `summaryexportfence.py` for no-network redacted-summary export fencing.
- Added `summaryreplayfold.py` and rev0078 docs/tests/audit metadata.

## rev0080 — importsettlement-archive-retentionseal

- Added `summaryimportsettlement.py`, `importarchiveledger.py`, `importretentionseal.py`, and `importsettlementfold.py`.
- Added tests for import settlement after gate/receipt/retention, restart-sticky import archive, and retention seal.
- Audit/refactor: moved the active fold head to `importsettlementfold.py` while preserving rev0079 predecessor history.

## rev0081 — nativeboundary-gccffi-hotpath

- Answers the GCC question: use GCC-compiled C only for narrow, deterministic, side-effect-free leaf kernels while Python keeps the protocol semantics.
- Adds `nativeboundary.py`, `gccffi.py`, `nativehotpaths.py`, and `native/gcc/xor_distance.c`.
- Adds tests that compile the optional XOR-distance C kernel with GCC when present and compare it against the Python reference.
- Adds `nativeboundaryfold.py` to pin the audit/refactor path and preserve rev0080 predecessor history.

## rev0082 — nativeparity-abiguard-fallbackseal

- Added `nativeparity.py` to compare optional GCC-native XOR leaf results against the Python reference before native selection.
- Added `abiguard.py` to bind native artifact loading to ABI version, symbol set, source/object/flag digests, input bounds, and fallback availability.
- Added `fallbackseal.py` so missing or quarantined native leaves route to Python fallback instead of becoming accidental authority.
- Added `nativeparityfold.py` and current-path docs/tests while preserving rev0081 native-boundary predecessor history.

## rev0084 — parserhold-sanitizerplan-nativebudget

- Added `parserhold.py` so hostile-byte parsing remains Python-owned even as GCC-native leaves exist.
- Added `sanitizerplan.py` to require source audit and development sanitizer evidence before native expansion.
- Added `nativebudget.py` to keep native optimization scarce, fallback-bound, and outside semantic protocol surfaces.
- Added `nativebudgetfold.py` and rev0084 docs/tests/audit metadata.

## rev0089 — nativecoldstart-probecorpus-loadergc

- Added `nativecoldstart.py` so restart-time artifact discovery cannot become dynamic loading or dispatch permission.
- Added `probecorpus.py` to refresh Python-oracle vectors after cold-start, unload, and crash-GC.
- Added `loadergc.py` so loader cleanup preserves tombstone, fallback, crash, and quarantine memory.
- Added `nativecoldfold.py` and updated fold map, fold registry, surface ledger, docs, public pointers, evidence scripts, and current wake-from-amnesia surfaces.

## rev0090 — nativehandoff-relaunchgate-loaderseal

- Added native handoff from cold-start/probe/loader-GC evidence into a fallback-active relaunch candidate while load and dispatch remain forbidden.
- Added relaunch gate requiring prior native lane revalidation before a no-network relaunch plan exists.
- Added loader seal restart memory preserving tombstone/fallback/quarantine/crash evidence for relaunch candidates.
- Added native fold-spine audit refactor covering rev0081 through rev0090 native branch anchors.
- Updated current docs, fold map, fold registry, surface ledger, public pointers, evidence scripts, and revision metadata for rev0090.
## rev0093 — nativeloadloop-callcanary-dispatchfence

- Added `nativeloadloop.py`, `nativecallcanary.py`, and `dispatchfence.py`.
- Added `nativeloadloopfold.py` and extended the native fold spine through rev0093.
- Added rev0093 tests and docs 968-977.
- Refined the GCC/native branch rule: loopback/canary/fence evidence remains Python-oracle evidence, not native permission.


## rev0095 — shadowsettlement-admission-callledger

- Added `nativeshadowsettlement.py` so matching native shadow output can be settled as evidence only.
- Added `nativeadmission.py` so settled native evidence can enter only a held shadow slot with no native call permission.
- Added `nativecallledger.py` so restart memory records that the executed route remains Python fallback.
- Added `nativesettlementfold.py` and extended `nativefoldspine.py` through rev0095.
- Verification recorded through surface check, micro-simulation, targeted rev0094/rev0095 tests, chunked/filewise pytest, compile check, compileall, cube audit, fold map, fold registry, nativefoldspine, and zip integrity.

## rev0096 — callarchive-promotedeny-shadowgc

- Added `nativecallarchive.py` to archive the rev0095 Python-route call ledger without granting native authority.
- Added `nativepromotiondeny.py` to explicitly deny native promotion even after repeated matching shadow results.
- Added `nativeshadowgc.py` so soft shadow-vector compaction preserves fallback, denial, tombstone, quarantine, and crash memory.
- Added `nativearchivefold.py` and extended `nativefoldspine.py` through rev0096.
- Updated docs, fold map, fold registry, surface ledger, public pointers, evidence scripts, and current wake-from-amnesia surfaces.

## rev0098 — nativebranchclose-promotearchive-policyseal

- Added `nativepromotearchive.py` to archive held promotion review as restart-sticky evidence without native permission.
- Added `nativepromotionpolicy.py` to enforce local shadow-only native policy.
- Added `nativebranchclose.py` to close the current native/GCC branch while preserving Python fallback authority and requiring any future promotion to start a new branch.
- Added `nativebranchclosefold.py` and extended the native fold spine through rev0098.
