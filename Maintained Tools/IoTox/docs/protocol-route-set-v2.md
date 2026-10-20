# IoTox authenticated route set v2

**Implemented:** stable-device-signed exact network class per route member

**Peer-wire allocation:** none

**Signer:** stable IoTox device identity

**Artifact size:** `156 + 48 * member-count` bytes; 252..924 bytes for 2..16 members

Route-set v2 closes the distinction between an owner-local worker override and the route class that
the stable device principal authorized. It signs only the coarse construction class. Proxy,
bootstrap, relay, router, circuit, and endpoint coordinates remain local deployment policy and are
not disclosed in the artifact.

## Canonical artifact

All integers are unsigned big-endian. The fixed header and member sizes are unchanged from v1.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 8 | ASCII `IOTOXRS2` |
| 8 | 1 | format version, exactly `2` |
| 9 | 1 | minimum route protocol, exactly `1` |
| 10 | 2 | zero |
| 12 | 8 | route-set generation, nonzero |
| 20 | 32 | stable device Ed25519 public key |
| 52 | 32 | coordinator Tox public key |
| 84 | 2 | member count, 2..16 |
| 86 | 6 | zero |
| 92 | `48*N` | canonical member records |
| `92+48*N` | 64 | Ed25519 signature |

Each member record is:

| Member offset | Size | Meaning |
|---:|---:|---|
| 0 | 32 | nonzero Tox public key |
| 32 | 1 | role: `1` protected, `2` bulk |
| 33 | 1 | connection class: `1` TCP, `2` UDP, `3` either |
| 34 | 2 | maximum active work, nonzero |
| 36 | 2 | automatic restart budget |
| 38 | 1 | network class: `1` Tox/native, `2` Tox/Tor, `3` Tox/I2P |
| 39 | 1 | zero |
| 40 | 8 | expiry as Unix milliseconds; zero means no wall-clock expiry |

Members are strictly increasing by Tox public key. V2 additionally requires the coordinator key to
be present and to be the sole protected member. Network class zero and unknown values fail closed.
Every v1 structural, expiry, stable-principal, generation, work-budget, and canonical-order rule
continues to apply.

The signature message is printable ASCII `IOTOX-ROUTE-SET-SIGNATURE-V2` followed immediately by the
complete header and member body. The complete signed artifact continues to use the domain-separated
`iotox-route-set-artifact-v1` digest operation for generation checkpoints and private route binding;
the digest operation's name is historical and does not reinterpret v2 bytes.

## Construction and admission enforcement

An Agent loading v2 compares the protected coordinator member to the exact configured primary
`NetworkStack` before starting its primary transport. Each auxiliary worker derives its class after
applying the exact-key local network/bootstrap/relay overrides and refuses a mismatch before that
worker transport starts. The coordinator independently compares the authenticated worker proof to
the signed member class before it can become ready or receive work.

The supported signed classes are:

```text
tox/native
tox/tor
tox/i2p
```

ADR 0253 promotes the already qualified class-3 construction to canonical `tox/i2p` without
changing its byte. The deprecated `tox/i2p-construction` authoring spelling is accepted and maps to
the same byte, so existing signed artifacts and savedata require no migration. New rendering is
canonical. A class match proves the selected strict IoTox construction policy, not Tor anonymity,
I2P anonymity, endpoint ownership, route availability, or physical path separation.

Private route-binding v2 already commits to the digest of the complete signed route-set artifact.
Consequently a changed network-class byte changes the inventory digest and invalidates an old member
proof; no type-26/type-27 peer frame or feature bit changes.

## Authoring and compatibility

Offline authoring is explicit:

```text
iotox --identity PATH route-set-create-v2 OUTPUT GENERATION COORDINATOR_KEY \
  KEY:protected|bulk:tcp|udp|either:tox/native|tox/tor|tox/i2p:WORK:RESTARTS:EXPIRES_MS ...
```

The command uses an existing stable identity, creates without replacement, signs, canonically
re-verifies, and reports `format=2`. It does not provision Tox savedata or mutate a running Agent.

`route-set-create` remains the v1 authoring command. V1 retains `IOTOXRS1`, its v1 signature domain,
two zero bytes at member offsets 38..39, and an in-memory `network-class=unspecified` projection.
V1 cannot carry a nonzero class; v2 cannot omit one. Decoding selects an exact magic/version/domain
triple, so neither format can be interpreted as the other.
