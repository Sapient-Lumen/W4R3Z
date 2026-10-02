# ADR 0225: Sign exact route network classes

Status: accepted implementation, deterministic gates, and genuine Sandwurm v2 actual-I2P payload
evidence, 2026-08-28.

## Context

ADR 0222 lets an owner pin a synchronization pull to an actual constructed worker class, but the
route set signed only the member key, protected/bulk role, TCP/UDP class, work and restart budgets,
and expiry. The exact-key `--route-worker-network` override remained local configuration. A changed
configuration could therefore construct a native worker for a member the owner intended to be Tor
or I2P while retaining a valid v1 artifact.

The complete private-route inventory is already stable-device-signed and its digest is already
bound into each auxiliary member proof. Extending that artifact is smaller and more coherent than
creating a second signer, mutable route registry, or new peer frame.

## Decision

- Preserve route-set v1 byte-for-byte and add the exact `IOTOXRS2`/format-2/signature-domain tuple.
- Reuse member byte 38, reserved in v1, for one required coarse class:
  `tox/native`, `tox/tor`, or laboratory-only `tox/i2p-construction`. Byte 39 remains zero. Artifact
  size and member count limits do not change.
- Require the v2 coordinator key to name the sole protected member. This makes the primary policy
  unambiguous without changing the v1 compatibility rule.
- Before starting the primary transport, compare its configured network stack with the signed
  protected member. After applying an auxiliary's exact-key override and catalogs, compare that
  constructed stack with its signed member before starting the worker transport. Recheck the class
  in coordinator authentication before readiness and work admission.
- Keep proxy, bootstrap, relay, router, circuit, and endpoint coordinates unsigned and private.
  The class constrains construction; it does not claim path ownership, anonymity, or availability.
- Keep private route inventory/member frame bytes unchanged. Their complete-artifact digest makes a
  changed class a different inventory and invalidates the old proof.
- Add creation-only `route-set-create-v2` with a required network-class member field. Keep
  `route-set-create` as the v1 compatibility author.
- Make new Sandwurm multi-route guests author v2 and fail unless both the protected primary and both
  ready bulk records project the exact signed classes. Add an optional receipt/manifest truth so
  historical compact proofs remain verifiable while new proofs expose the stronger gate.

Unit and integration gates cover canonical v1/v2 separation, missing/unknown classes, coordinator
shape, signature verification, exact coordinator authentication, primary mismatch before toxcore
savedata creation, auxiliary mismatch before worker start, CLI creation, and private binding failure
when only a signed member class changes.

The first genuine attempt reached two exact ready bulk routes per guest and rendered the protected
native, bulk native, and bulk I2P-construction classes exactly as signed. It then
failed before transfer: the five-argument `sync-pull ... fail-closed tox/i2p-construction` CLI chose
local operation 86 but omitted its mandatory failover byte because the encoder recognized an
explicit failover only in the four-argument form. The corrected encoder treats both four- and
five-argument forms as explicit failover. The full Agent route-loss test now enters through the real
CLI in both available and fail-closed cases, rather than constructing operation 86 by hand.

Clean rerun `pair.q2pka1fm` is accepted bounded evidence. Both guests observed the exact three
signed class projections; the subscriber explicitly selected I2P-construction under fail-closed
policy, assigned the 131,369-byte tree once to that member, never reassigned to the ready native
member, and activated the verified tree. Both full and 5,255,168-byte secret-free compact forms pass
the strict verifier. The evidence record owns the exact hashes and nonclaims.

## Consequences

The owner-local per-pull selector can now be joined to stable-device-signed route membership. A
native fallback cannot masquerade as the same authorized Tor or I2P-construction member merely by
reusing its Tox savedata key. V1 remains usable but explicitly projects `unspecified`; it supplies no
signed privacy-class claim.

No IoTox peer-wire, synchronization-wire, Ratox, or Tox bytes change. The next scientific gate is a
genuine two-guest actual-I2P process-loss run using v2: pin the pull fail-closed to
`tox/i2p-construction`, fault the router after positive progress, require zero native reassignment,
then recover the same signed member. Byte resume across an I2P-to-I2P replacement and privacy-class
authorization across distinct remote principals remain later gates.
