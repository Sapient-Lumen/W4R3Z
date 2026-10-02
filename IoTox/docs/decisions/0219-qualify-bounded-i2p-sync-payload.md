# ADR 0219: Qualify a bounded private-member I2P sync payload

Status: accepted construction evidence, 2026-08-28.

## Context

ADRs 0216–0218 proved a contained two-guest I2P baseline plus router and persistent-service recovery,
but none proved that application payload was assigned to the authenticated I2P member while a native
member was also eligible. Route readiness alone is not payload attribution.

The first exact-payload experiments exposed a second boundary. The auxiliary synchronization protocol
currently permits only complete object request/result records and FileId-bound whole-object transfer;
HEAD, range, activation, and authority frames remain on the primary. When the selected auxiliary
carrier disappears, the safe existing behavior fences the attempt and reassigns the complete missing
object to another ready member. That is correct availability behavior, but it can violate a future
privacy-pinned intent if the replacement member is native.

## Decision

- Add `sync-tree-route-private-actual-i2p-payload` as a distinct Sandwurm cell. Keep the primary and
  fallback member on native UDP, construct the other exact member through the strict actual-I2P
  topology, and require private route-binding v2 on both roles.
- Use fixed selection only after `sync-status` reports both authenticated auxiliary routes for the
  exact remote principal. Status now exposes an aggregate ready-route count and one content-free line
  per eligible route with route-key, worker, friend, epoch, principal, admitted work, and maximum
  work. Aggregate readiness alone is not enough to establish principal-correct eligibility.
- Require the completed job's carrier commitment to equal the expected I2P auxiliary-key commitment,
  exactly one role to retain the payload observation, and the reassignment count to remain zero.
  Signed HEAD acceptance, complete object verification, explicit activation, ordinary topology
  evidence, router/front process continuity, and TAP context containment remain mandatory.
- Freeze this first accepted object at a 128 KiB generated payload: 131,157 content bytes and a
  131,369-byte treepack artifact. This is a lower-bound construction gate, not a product ceiling.
- Do not hide the rejected larger-object result. Both 512 KiB and 4 MiB diagnostic attempts selected
  I2P first and then recorded one authoritative carrier loss and native reassignment while the two
  routers and three fronts remained alive. In the 512 KiB attempt, the busiest captured
  client-to-adapter TCP flow carried about 301 KiB total before its approximately 101-second
  connection ended. Those rejected private roots were deliberately removed after diagnosis and are
  not accepted evidence.
- Keep production `tox/i2p` reserved. Before privacy-sensitive large sync or OTA can depend on this
  route, extend the auxiliary protocol with bounded digest-bound chunk/range work and signed route
  class/failover constraints. Loss of a privacy-required member must fail closed or move only to an
  equally authorized class; ordinary availability policy may retain whole-object cross-class
  reassignment when explicitly selected.

Accepted compact proof `pair.5xjf2n4d` runs clean source commit `a2205b6`, uses identical binary
SHA-256 `1235e79f138f1a2878fffd845db6b541245208e52e1598209c9f639aea76bc77` in both guests, and
binds payload carrier commitment
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c` to the client's exact
`Tox/I2P-construction` auxiliary member. The signed tree converges and activates on the first pull
attempt with zero failures and zero reassignments. Both roles report two ready bulk members.

The two i2pd 2.60.0 routers and all three persistent fronts have zero restarts. The routers own their
SAM listeners and 28/31 established public TCP remotes at attribution. The client/device TAPs contain
1,486/786 packets to `10.0.0.1:39053`, mixed alongside the deliberately retained native context, and
zero packets outside the context rules. Raw and 5,115,904-byte secret-free compact evidence both
pass strict verification.

## Consequences

- The private route-member plus exact sync-payload item is closed for one bounded 128 KiB object and
  one same-host time/record window. It proves scheduler attribution, not byte-by-byte content
  classification, anonymity, independent administration, availability, or production suitability.
- The failure boundary is now part of the architecture: route membership and initial selection do
  not by themselves preserve privacy intent across loss. Route-class authorization must be signed
  independently of the local fixed/adaptive placement heuristic.
- Whole-object auxiliary transfer is adequate for small bounded control artifacts in this observed
  window, but it is the wrong primitive for large privacy-pinned sync and OTA. Chunk/range support is
  the next locally actionable protocol gate; larger exact-I2P repetition follows it.
- Later record/time repetition and product/stewardship policy remain open. No result here enables the
  reserved `tox/i2p` spelling.

ADR 0220 later implements the owner-local fail-closed enforcement prerequisite and makes the I2P
payload cell select it. Signed per-job route classes, auxiliary chunk/range framing, and the genuine
loss gate remain open.

See `docs/evidence/2026-08-28-sandwurm-actual-i2p-private-sync-payload.md`,
`docs/i2p-route-construction.md`, and `docs/multi-route-plan.md`.
