# ADR 0201: Qualify private routes across network contexts

Status: accepted and qualified in two Sandwurm guests, 2026-08-27.

## Context

ADRs 0198 through 0200 separated native/privacy route identities, froze the private v2 inventory
and member-proof formats, and operated them behind an explicit Agent gate. The remaining product
question was whether independently keyed members could use different local network contexts while
retaining one authority-owning coordinator and one signed synchronization transaction.

The first genuine mixed-context attempt also exposed an ordering race. An auxiliary peer can send
its one frozen member proof after its own primary inventory is admitted but before this side admits
the reciprocal inventory. The worker correctly retains that unverifiable frame. The old context
replacement path then cleared it while the sender correctly avoided retransmitting a proof already
accepted by toxcore, leaving one side ready and the other waiting indefinitely.

## Decision

Allow an exact non-primary route key to select a local worker network with repeatable
`--route-worker-network KEY=tox/native` or
`--route-worker-network KEY=tox/tor@NUMERIC_PROXY`. The complete mapping is validated before any
worker starts. Keys must be unique signed auxiliary members; a Tor-designated member must be TCP,
must have an explicit numeric SOCKS endpoint, and inherits no native discovery or fallback. The
signed route set continues to describe member identity, role, connection class, and budgets; local
proxy addresses are deployment policy and do not enter the shared signed artifact.

On private primary-context replacement, cancel all auxiliary effects and regenerate the local proof
as before, but retain one already-received reciprocal proof long enough to verify it against the new
exact context. A valid early proof becomes authenticated under that context. A proof valid only for
the prior inventory is discarded without gaining authority so the peer's fresh proof may arrive.
An invalid proof received after the current context exists remains rejected normally. Primary
withdrawal retains no proof or readiness.

Qualify this policy with scenario `sync-tree-route-private-mixed` in two simultaneous source-linked
Sandwurm guests. Each role owns a native UDP primary, one native UDP bulk member, and one strict
generic-SOCKS/TCP bulk member under independent Tox keys. Both primary sessions must authorize the
remote stable principal, both auxiliary members must become reciprocally ready through v2, and one
signed three-file/three-directory tree containing 4,194,389 bytes must converge and activate.

Packet evidence is interpreted by outermost IPv4 headers. Native Tox may use arbitrary UDP DHT
destinations and the host stack may emit related ICMP. Every TCP packet must instead terminate at
the configured host-local SOCKS endpoint or pinned TCP relay. The SOCKS audit must admit only the
pinned relay target and deny zero requests. This aggregate TAP evidence is joined to exact-key
configuration, per-worker savedata identity, signed membership, and guest receipts; packet capture
alone is not process attribution.

## Consequences

- The authority-private cross-context discovery and generic-SOCKS mixed-operation gate is complete.
- A primary-inventory/member-proof scheduling race is closed without adding retries, accepting an
  unverified proof, changing v2 bytes, or weakening withdrawal.
- The accepted compact proof is `pair.z948jeii`; both roles reached two ready bulk members and
  converged the exact signed 4,194,389-byte tree. Four SOCKS connections were admitted and zero
  denied. Both captures contain native UDP and proxied TCP, with zero TCP outside configured local
  endpoints.
- The generic SOCKS forwarder is not Tor. This decision proves neither actual-Tor two-peer
  operation, anonymity, traffic-correlation resistance, independent physical paths, failover across
  network contexts, nor I2P. Those remain separately named M8 gates.

