# Sync content-v2 object protocol

Status: frozen and active behind dynamic Agent construction; deterministic auxiliary-carrier,
genuine direct-UDP primary-peer multi-source, genuine native-authority/actual-Tor-worker
multi-source, selected actual-Tor worker-loss, and bounded same-source two-lane direct-UDP/forced-TCP
gates accepted; direct-UDP/forced-TCP 1/2/4/8 lane performance, persistent terminal load, fresh
post-bulk admission, counterbalanced order, cap-two terminal SLA, multi-lane daemon restart, and
same-source exact-worker whole-object distribution accepted; I2P content-v2, Tor/I2P content-daemon
restart, and physical-path multipath qualification pending, 2026-08-31.

## Purpose and activation

This protocol moves one immutable content-v2 root manifest, manifest page, or artifact chunk. It does not select a
revision. One already verified `AcceptedHead` remains frozen for the entire receive coordinator, and
every source is independently admitted against that exact signed-HEAD record under authority-ledger
v3. Friendship, route membership, possession of bytes, or a successful file offer grants no HEAD or
activation authority.

Feature bit 29 is named `state-sync-content-v2`. It depends on feature bit 18, `state-sync-v1`.
Message types 28 and 29 are allocated to `sync_content_object_request` and
`sync_content_object_result`; types 30 and 31 carry exact sparse availability. Bit 29 remains absent
from `kImplementedFeatureMask`. The Agent adds it to its frozen HELLO mask only when an enabled
content-v2 namespace has passed startup recovery and authenticated live-graph validation and both
content services exist. A route worker advertises bit 29 only when its parent constructed both
content services. The active receiver consumes exact sparse availability from explicitly added,
independently authorized primary Tox peers. Before HEAD admission, owner-local policy may bind each
source's content frames and file lane to one exact reciprocally authenticated auxiliary worker. It
does not discover sources, and the worker cannot carry HEAD, activation, or authority records.

## Canonical object request

The request payload is exactly 184 bytes. Integers use big-endian encoding.

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | version, exactly `1` |
| 1 | 1 | kind: `1` manifest page, `2` artifact chunk, `3` root manifest |
| 2 | 1 | namespace length, `1..64` |
| 3 | 5 | zero |
| 8 | 32 | SHA-256 of the frozen canonical signed-HEAD record |
| 40 | 32 | exact root/page/chunk SHA-256 |
| 72 | 32 | caller-selected Tox `FileId` |
| 104 | 8 | logical page/chunk index; exactly zero for a root manifest |
| 112 | 8 | exact object byte length, nonzero |
| 120 | 64 | namespace bytes followed by zero padding |

The containing frame has flags, correlation ID, sequence, and expiry all zero and a nonzero message
ID. The namespace uses the frozen IoTox namespace grammar. HEAD digest, object digest, and FileId
must each be nonzero. Noncanonical padding, sizes, kinds, or envelope fields are protocol errors.

## Canonical object result

The result payload is exactly 120 bytes:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | version, exactly `1` |
| 1 | 1 | status |
| 2 | 1 | echoed object kind |
| 3 | 5 | zero |
| 8 | 32 | echoed frozen signed-HEAD record digest |
| 40 | 32 | echoed object digest |
| 72 | 32 | echoed `FileId` |
| 104 | 8 | echoed logical index |
| 112 | 8 | echoed object byte length |

Statuses are `1 offered`, `2 denied`, `3 stale-head`, `4 object-absent`, and `5 unavailable`. The
frame has a fresh nonzero message ID, correlates the exact request message ID, and otherwise uses a
zero envelope. A successful result is meaningful only when the matching finite-file offer was
admitted on the same authenticated carrier and uses the exact FileId. The result alone is not a byte
commit.

## Publisher admission and replay

Before an offer, the publisher requires all of the following:

1. feature bit 29 was negotiated on the exact peer context;
2. the request frame is canonical and its namespace is a local content-v2 policy;
3. the requester has a current exact authority proof with `sync.subscribe` and appears in the
   namespace subscriber set;
4. the publisher's current signed HEAD hashes to the requested frozen-HEAD digest; and
5. the locally derived kind/index resolves to the requested digest and size, and the digest-named CAS
   object passes size plus SHA-256 verification.

Paths are never accepted from the peer. Root kind resolves only HEAD's exact manifest digest/size at
index zero. The resolver otherwise derives the root manifest and CAS path from local policy, rehashes
the root against HEAD, then resolves page/chunk kind and index through the verified flat or paged
manifest.

The publisher retains a bounded FIFO epoch/carrier/message-ID exact-replay window. An exact retained
replay returns the same result without another offer. Same-ID/different-payload reuse inside the
window is a protocol error, and an authority change refuses retained replay. When the window rolls,
an older identifier is fresh read-only work and must pass current authority, HEAD, object, and quota
validation again before any immutable offer. Peer or carrier loss removes the scoped entries
(ADR 0282).

## Canonical exact availability

The availability request is exactly 120 bytes:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | version, exactly `1` |
| 1 | 1 | page/chunk kind |
| 2 | 1 | namespace length, `1..64` |
| 3 | 1 | zero |
| 4 | 4 | object count, `1..8192` |
| 8 | 32 | frozen signed-HEAD record digest |
| 40 | 8 | first logical object index |
| 48 | 8 | zero |
| 56 | 64 | namespace plus zero padding |

The result begins with 56 fixed bytes followed by exactly `ceil(object_count/8)` availability bytes:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | version, exactly `1` |
| 1 | 1 | status: `1 available`, `2 denied`, `3 stale-head`, `4 unavailable` |
| 2 | 1 | echoed page/chunk kind |
| 3 | 1 | zero |
| 4 | 4 | echoed object count |
| 8 | 32 | echoed frozen signed-HEAD record digest |
| 40 | 8 | echoed first logical index |
| 48 | 4 | bitmap bytes, exactly `ceil(count/8)` |
| 52 | 4 | zero |
| 56 | variable | little-endian membership bits |

Bit zero of byte zero describes `first_object`. Bits beyond the count in the final byte are zero.
The maximum result is 1,080 bytes and fits one IoTox frame. The source requires the same current
subscriber authorization as an object request, verifies the root manifest against HEAD, and
size/digest-verifies every object whose bit it sets. Exact replay returns the retained bitmap without
rescanning. The receiver reapplies source authorization and accepts only its exact current
kind/first/count window; sparse membership expires when the window advances.

## Receiver coordinator

The transport-neutral coordinator embeds the preserved toxsync content fabric. It independently
rehashes the root manifest and checks its artifact, manifest, and size semantics against the frozen
HEAD. Policy bounds cap sources, lanes, outstanding requests, objects, scheduler workspace, windows,
and I/O buffers. Every source needs current exact-v3 proof, `sync.publish`, writer membership, the
same frozen-HEAD digest, and negotiated bit 29.

The subscriber requests or reuses the exact root manifest from the original source before
constructing the coordinator. An early matching FileId offer is retained but remains paused until
its canonical `offered` result arrives. One-source jobs then use the complete-source fast path.
With two or more sources, the subscriber requests the coordinator's exact current window from every
source and waits for one canonical response from each before scheduling. Assignments bind a fresh
request ID, selected source, kind, object digest, size, logical index, and private staging path.
Their object request, FileId, CTA1 record, completion, cancellation, and retirement use that exact
source's authenticated primary-peer context. Page and chunk commits reverify and atomically enter the
digest-named store. A new window causes a new exact availability round. Source loss currently fails
the whole job; it is not treated as empty availability or auxiliary failover. The product subscriber
reconstructs into exact private staging, commits the whole verified artifact to CAS, and advances
accepted HEAD last. Acceptance is still not activation.

ADR 0246 defines the local physical inventory prerequisite. The canonical CAS is exclusively
`content-v2/sha256/<2-lowercase-hex>/<62-lowercase-hex>` beneath a mode-0700 root. A strict scan under
the namespace transaction rejects aliases, links, unsafe ownership/modes, mount crossings, malformed
entries, and quota overflow; an optional pass rehashes every object. Its combined view counts these
objects and the flat immutable store against the same namespace object and byte ceilings. This is an
accounting primitive, not yet a product write, reachability, or deletion path.

ADR 0247 supplies the construction-level product write path. The coordinator accepts only those
derived CAS and staging roots, and completion accepts only the scheduler's exact staging pathname.
Under the namespace transaction, a nonempty mode-0600 owner-owned single-link file must match the
assigned size and fit the prospective combined physical quota. IoTox then copies through SHA-256 into
a no-replace destination and consumes staging only after success. Existing-object retry verifies both
destination and source. No caller may assert that peer-delivered bytes are preverified, and product
commit does not use hard-link ingest. Quota refusal retains the exact active assignment and staging
file without publishing bytes.

ADR 0248 defines the content-specific `CTA1` restart journal. Before transport effect, a signed
record binds the frozen HEAD, page/chunk identity, digest/size, scheduler request/source IDs, exact
FileId, authenticated carrier incarnation, and stable source principal. IDs are burned first; exact
retry is idempotent and active request, FileId, or logical-object aliases are forbidden. The complete
encoding and recovery algorithm are frozen in `sync-content-attempt-journal-v1.md`.

Restart does not resurrect a carrier. An already present exact CAS object is committed truth; an
exact-size private staging object may enter through the ADR 0247 commit; partial or absent work is
fenced for a fresh authorized request. Unsafe or corrupt-complete staging leaves the signed record
intact and fails closed. Only a new signed mutation retires all safely classified records. This is
restart truth, not remote authorization, HEAD acceptance, or activation.

## Local publication ordering

ADR 0249 defines the product-side producer prerequisite. Under one namespace transaction, local
`sync-publish` builds a flat or paged toxsync fabric in an exact private publication workspace,
walks and deduplicates its root/page/chunk identities, prospectively admits the complete set against
scratch and combined flat-plus-CAS quotas, and imports every object through the ADR 0247 commit. The
stable-device-signed content-v2 HEAD is published only after all objects verify in CAS. Failure may
leave unreachable immutable objects but cannot leave a signed incomplete revision. Exact workspace
cleanup is separate from CTA1 network-attempt staging.

ADR 0250 closes the local receiver ordering. Kind `3` bootstraps the exact signed root under CTA1;
root/page/chunk commits precede reconstruction, whole-artifact CAS precedes accepted HEAD, and an
exact retry can reuse artifact CAS after interruption. ADR 0254 extends that service to explicit
primary-peer sources and exact sparse windows while preserving one lane and nonactivation. ADR 0262
later permits bounded page/chunk overlap without changing that order: root remains serial, each live
object owns an exact request/FileId/CTA1/carrier binding, and HEAD still lands only after all lanes
settle and the complete artifact verifies.

## Product gate and remaining claims

ADR 0251 routes HEAD/object packets, exact FileId offers, and terminal events through the live Agent.
The ordinary `sync-pull`, `sync-status`, `sync-cancel`, `sync-activate`, `sync-repair`, and `sync-gc`
controls now select the content engine where appropriate. Startup authenticates the persisted live
graph before advertisement; explicit activation rechecks whole artifact and manifest CAS objects;
repair quarantines digest drift; GC classifies candidates only after a complete signed traversal and
has no purge mode. A deterministic full-Agent/mock-toxcore test converges and activates a paged
revision through those boundaries.

ADR 0252 qualifies that bounded one-source product path through two independent source-linked
Sandwurm guests using genuine c-toxcore. The same paged 4 MiB revision converges in one pull with zero
failure over direct UDP and forced TCP, enters whole-artifact and root-manifest CAS, accepts HEAD
last, and explicitly activates. Strict compact replay retains the exact four-chunk/one-page/four-
object content declaration as well as the common hashes.

ADR 0254 adds local-control v1.40 operation 87 and `sync-source-add JOB_ID FRIEND`. The operation is
owner-local and job-scoped. The original peer remains the only HEAD source; every added peer needs
feature bit 29, current exact-v3 proof, `sync.publish`, and writer membership for the same namespace.
The deterministic product gate splits chunk CAS across two authenticated writers, requires both to
answer exact availability and supply objects, reconstructs the exact artifact, and accepts only the
original frozen HEAD. No added source receives HEAD or activation authority.

ADR 0255 carries that exact multi-source path through three live IoTox agents in two Sandwurm guests
over direct UDP. Both complementary sources answer exact availability and contribute objects before
the subscriber reconstructs, accepts the original HEAD last, and explicitly activates it. Forced TCP
does not qualify after thirteen bounded constructions separated relay count, serialized admission,
ordinary pending acceptance, reusable-key pre-provision, full-address rendezvous, and A/B placement.
The strongest hybrid briefly confirmed the secondary TCP/application session, then lost it for the
entire v3-authority window before object work. Relay connectivity and transient session state are not
durable authenticated-source truth.

ADR 0256 adds local-control v1.41 operation 88 and
`sync-pull-multi PRIMARY NAMESPACE SOURCE [SOURCE...]`. The payload carries one auxiliary count
`u8`, the primary `u32`, 1..15 distinct auxiliary `u32` values, then 1..64 namespace bytes. Every
peer is authenticated before the content job begins; all auxiliaries are registered while the
primary HEAD frame is withheld; only then may that frame dispatch. Any registration or dispatch
failure cancels the newly allocated job. This owner-local transaction changes no content-v2 peer
frame and grants no added source HEAD or activation authority. `sync-source-add` remains a dynamic
job mutation, but does not provide this initial ordering guarantee.

The direct-UDP source-loss gate stops the selected secondary after positive object work. The first
job fails as a whole and fences staging, signed attempt truth, HEAD acceptance, and activation while
leaving already verified immutable CAS prerequisites reusable. The same source identity must return
at a higher authenticated epoch before a distinct explicit atomic pull can recover. The construction
secondary originally had to reinject its valid foreign-writer HEAD after clean startup rather than
place it in its local publication tree.

ADR 0257 replaces that construction seam with local-control v1.42 operation 89 and
`sync-replica-import NAMESPACE SIGNED_HEAD_PATH`. The imported record retains the original writer's
signature inside a fixed device-signed custody envelope under `replica-heads/`. Import requires the
complete verified root/page graph and permits missing artifact chunks. The first import may join an
existing remote generation; later changes must be duplicate or one same-writer exact linked advance.
The publisher falls back to this availability record only when local publication is absent. Primary
HEAD acceptance still requires the authenticated remote writer, so a replica can serve only an
already frozen exact record and cannot publish, accept, activate, or roll it back on the subscriber.
Reachability roots the replica graph bytes that are present, tolerates replica-only missing chunks,
and fails GC closed if root/page traversal is incomplete. The repeated source-loss gate now proves a
true partial-store cold start, absent foreign publication, consistent zero-candidate GC, and recovery
without post-start HEAD injection.

ADR 0258 adds local-control v1.43 operation 90 and
`sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]`. `ROUTE_CLASS` must name
native, Tor, or I2P. Agent proves every primary authority session first, selects one exact ready
content-capable auxiliary worker for each stable source principal, installs all carrier bindings,
then releases the primary's HEAD request over its original session. The same pre-HEAD bind permits
`sync-pull FRIEND NAMESPACE fail-closed ROUTE_CLASS` for one source. HEAD, writer authority, and
activation never move to the worker. Availability/object types 28--31, exact FileId offers, CTA1,
and terminals use the frozen source carrier. Any carrier loss fails the whole content job; no
fallback, rebinding after HEAD, or same-job continuation is implied. The wire framing is unchanged.

The accepted one-source actual-Tor gate keeps the primary authority and HEAD on direct UDP, binds
the source carrier to one exact `tox/tor` worker before HEAD, and converges the paged 4 MiB revision
in one pull with zero failure or reassignment. Worker bit-29 advertisement is finalized from both
constructed content services before supervisor start and cannot change afterward. This qualifies
one routed carrier, not authority over the worker friendship.

ADR 0259 qualifies the complementary-source shape without moving authority. Two native primary
publisher sessions independently prove the same writer HEAD; each source is frozen to a distinct
exact `tox/tor` worker before HEAD dispatch. One atomic pull receives five objects from the primary
store and one from the partial store, verifies the complete paged fabric, accepts the original HEAD
last, and activates explicitly. Owner-private `content-source-job=` records bind every source's
stable principal and authority route to its exact worker route/incarnation. The verifier recomputes
the two-key carrier-set commitment and checks both TAP captures for zero unexpected context packets.
This status surface changes no content-v2 or local-control encoding.

ADR 0260 qualifies the frozen carrier-loss rule. A qualification-only selector stops the second
source's exact Tor worker after positive receive progress. The first content job fails with the exact
auxiliary-carrier-loss reason, cleans transient staging, accepts no HEAD, activates nothing, and
records zero reassignment. Verified CAS objects remain immutable reusable truth, but the failed
FileId/CTA1 attempt and job are never resumed. Recovery consumes one signed worker restart and
creates a new incarnation for the same route only after every affected content job is terminal.
Both native authority epochs remain unchanged, and only a distinct explicit atomic pull may
converge. The selector and its status counters are owner-private qualification machinery; peer and
local-control framing remain unchanged.

ADR 0261 repeats that exact frozen rule through a second public relay record. It also centralizes the
host runner's derived loss-manifest scenario set after independent verification rejected an omitted
head-fenced count. No content-v2 frame, capability, CTA1 field, source-selection rule, carrier-loss
rule, or local-control operation changes; the repetition is evidence about the existing contract.

ADR 0262 activates the already-signed lane budget. `--max-sync-content-lanes N` is a process ceiling
with conservative default `1`; the effective source ceiling is the minimum of that value and the
namespace's `maximum-lanes` plus `maximum-outstanding-requests` quotas. The root manifest is always a
one-lane phase. Only independently digest-addressed manifest pages and artifact chunks may overlap.
Out-of-order terminals settle the exact lane and refill only the free slot. A permanent result,
source/authority change, storage failure, or carrier loss attempts to cancel and durably fence
every sibling before the whole job fails. When the storage transaction itself is unavailable, the
existing durable-attempt recovery boundary owns any conservative residue; no successful cleanup is
claimed. `sync-status` reports `active-lanes` and one owner-private `content-lane-job=` binding per
live object; its compatibility `active-file` fields are empty whenever multiple lanes would make
them ambiguous. No peer or local-control frame changes.

ADR 0269 extends only the owner-local meaning of operation 90. In
`sync-pull-multi-route`, repeating one source friend selector requests another distinct exact ready
worker for that same stable principal and primary authority session. Selection is atomic and fails
when the named class cannot satisfy the full distinct-carrier set. The original primary friend,
online epoch, authority route, writer proof, and HEAD remain identical on every repeated source-path
record; each path has a distinct source ID and auxiliary route/worker incarnation. The ordinary
`sync-pull-multi` form still rejects duplicate friends.

ADR 0296 later makes the already frozen local-control operations 87--88 dispatch tree-v2 jobs as
well. Their content-v2 HEAD, availability-window, auxiliary-route, and loss semantics above are
unchanged; the engine is resolved from the installed namespace before source registration.

All immutable objects are scheduled whole. A page or chunk belongs to exactly one selected carrier;
no object byte range crosses carriers. Every terminal comparison uses the full transfer-carrier
tuple because friend and file numbers are local to one worker transport and may collide across
workers. `content-source-job=` now appends monotonic `requested`, `committed`, and `fetched-bytes`
counters for each path. Exact selected-carrier loss still fails the whole job without replacement.
Operation 90 bytes, content types 28--31, CTA1, HEAD, activation, and feature negotiation are frozen.

The active code and accepted evidence do not yet prove:

- genuine I2P content-v2 or Tor/I2P content-v2 daemon-restart transport behavior;
- byte striping, balanced or faster same-source auxiliary-path use, independent circuits/physical
  paths, or selected-source continuation inside the same live job;
- a confidence interval, physical-host throughput result, or bandwidth-independent Ratox-latency
  budget beyond ADR 0268's bounded native cap-two construction profile;
- a performance win over range-v1; or
- safety under arbitrary filesystem faults, power loss, hostile kernels, multiple physical hosts, or
  a production fleet.

Peers advertise bit 29 for the genuine-provider-qualified one-source path, explicit multi-source
primary-peer path, and construction-complete auxiliary workers. Bit 29 does not claim a particular
carrier topology or recovery policy; topology qualification remains an evidence property. The
accepted actual-Tor receipts are documented in
`evidence/2026-08-30-sandwurm-sync-content-actual-tor.md` and
`evidence/2026-08-30-sandwurm-sync-content-multi-route-actual-tor.md`; the selected-worker-loss
receipt is `evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss.md`; and the same-source lane
proofs are documented in `evidence/2026-08-30-sandwurm-sync-content-same-source-lanes.md`.
The distinct-carrier same-source proof is documented in ADR 0269 and
`evidence/2026-08-31-sandwurm-sync-content-same-source-multi-route.md`.
The stable-session lane-count observations and retained default-one decision are documented in
ADR 0263 and `evidence/2026-08-30-sandwurm-sync-content-lane-science.md`.
The order-balanced recommendations and canonical aggregate report are documented in ADR 0266 and
`evidence/2026-08-31-sandwurm-sync-content-lane-counterbalance.md`.
ADR 0267 qualifies unclean client-daemon restart at explicit caps two and four on direct UDP and
forced TCP. Recovery preserves the exact verified complete CAS inventory, removes only exact private
c-toxcore transport temporaries after journal verification, fences the old active attempt set, and
permits convergence plus activation only through a distinct pull after two-sided recovered
authority. The framing is unchanged. Exact receipts are in
`evidence/2026-08-31-sandwurm-sync-content-restart.md`.
ADR 0268 freezes the missing persistent cap-two construction SLA before measurement and passes it
over both native carriers with one 960-sample Ratox attachment and one Tox epoch. Default one,
manual selection, and all framing remain unchanged. Exact receipts are in
`evidence/2026-08-31-sandwurm-sync-content-ratox-cap-2-sla.md`.
