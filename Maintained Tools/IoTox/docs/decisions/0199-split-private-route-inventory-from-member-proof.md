# ADR 0199: Split private route inventory from member proof

Status: accepted construction codec, 2026-08-27; live policy completed by ADR 0200.

## Context

ADR 0198 selected distinct random Tox identities for native and privacy-routed contexts and forbade
public or friendship-only roster disclosure. Route-binding v1 cannot meet that boundary because its
otherwise sound transcript proof is preceded by the complete signed route set on every auxiliary
session.

The receiver already needs an authority-authenticated primary association before accepting v1. The
missing step is to make that primary association the disclosure channel rather than sending the
roster early and merely refusing to trust it.

## Decision

Allocate feature bit 28, primary message type 26, and auxiliary message type 27 for private route
binding v2. Bit 28 depends on authority-ledger-v1 and route-binding-v1; the latter remains the codec
lineage but its type-19 exchange is not reused.

Send the unchanged stable-device-signed route-set-v1 artifact only on an exact transcript-confirmed,
authority-authenticated primary session. Admission binds the authenticated remote principal,
coordinator key, full artifact digest, route-set generation, primary friend, and online epoch.

On an auxiliary session, send one new fixed 256-byte stable-device-signed member artifact. It binds
the exact member key/policy, auxiliary transcript, and the digest of the complete inventory already
admitted privately. Both creation and verification require the primary authority edge still to be
current and require the auxiliary peer to appear in the remote inventory. The member artifact never
contains sibling route keys.

Keep bit 28 absent from the default and Agent feature masks until bounded one-send/one-receive replay
state, primary delivery, worker handoff, and lifecycle integration are complete. Route-binding v1
remains byte-for-byte frozen and usable only for the existing same-context construction.

## Consequences

- Full roster disclosure now has a precise authority gate and a separately testable codec.
- The complete artifact digest prevents a member proof from floating between same-generation forks
  whose undisclosed budget, expiry, or sibling membership differs.
- A stale primary epoch, changed authority transcript, unauthorized peer, unlisted auxiliary key,
  altered envelope, modified binding, or foreign inventory fails closed before admission.
- The primary-authorized peer still learns the route set, and the chosen auxiliary peer learns the
  stable principal/coordinator/member relationship needed to authenticate its road. This is least
  disclosure for the current coordinator model, not anonymous credentials.
- The remaining work is live orchestration, not a cryptographic-format ambiguity.

ADR 0200 subsequently supplies that live orchestration without changing these wire bytes.
