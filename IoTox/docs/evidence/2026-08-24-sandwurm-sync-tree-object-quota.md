# Sandwurm synchronization object-count quota evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same whole-store object-count
refusal gate over observed direct UDP and forced TCP. Both cells used one production binary, stable
reused test identities, the canonical 4 MiB treepack fixture, and the pinned local c-toxcore 0.2.23
bootstrap/relay fixture.

The subscriber begins with four private, valid digest-named one-byte immutable objects. Generation 1
then contributes its artifact and manifest, reaches the configured six-object ceiling exactly, and
activates the six-entry read-only tree. The resulting inventory consumes 4,981,173 bytes under a
33,554,432-byte store ceiling. The complete valid generation-2 artifact and manifest would still fit
under that byte ceiling, so byte pressure cannot explain the refusal.

After the publisher changes one payload byte and signs generation 2, whichever new object completes
first is refused with `sync staged commit would exceed whole-store quotas`. The pull ends failed with
two requested objects and zero committed objects. The subscriber retains exactly the six predecessor
objects, accepted HEAD, activation record, `current` link, visible generation-1 payload, and empty
staging. Generation 2 never acquires acceptance or activation authority.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.1oaa9bzi` | 346,951,034,163 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `1cf6bbc8aa47c10b8a49c3c84c8c89339ef11462da889cdcf933a4acabf187ae` |
| forced TCP | `.sandwurm/exports/pairs/pair.x7dul21w` | 486,061,204,668 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `1bd58a20a60c5d0b04516edd0e79a30f5d344498c4944a029532fa31fa445935` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact pair-manifest/export-manifest SHA-256 pairs are
`ccbcf8d747830eaaf9e0ba8076ed831ef93fd5e1a266048de3ca6062c0d110e8` /
`91c7df64537ab87d4e444b0499013269f5517b4f4830f66eb2aa5f69d8a7533d` for UDP and
`ca811566158d246c5416769c98df8a7b17919f93225c8074adae35e80541094d` /
`6756f85896f6b86c597b5f3e6b84801e4b45064d1f19008682e0d7a6211a288d` for TCP.

Both cells bind these exact revision identities:

| Revision | HEAD record | Artifact SHA-256 | Manifest SHA-256 |
|---|---|---|---|
| generation 1, retained and visible | `ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9` | `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` | `f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7` |
| generation 2, refused by local quota | `a795f7344d7a25750384115ae1f62164d4267078d821f5c233316ead05fd5e12` | `b76a31ded55f958f4e09623d80ce97d281cf8ab0586b7460b4395449c55a82da` | `353725dcf8a878ecee6cf5fd9dd2c53971f2a744f2fbc218f76304734c6b78a4` |

The retained visible payload SHA-256 is
`374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.
The UDP client/device receipt SHA-256 values are
`eeb971fa5e4f725b38339264a52af2befa4b6fabede1026fd7091ebf87ac5d23` and
`bf0f99cd5ef053b5050d6e30673896983ef7fafb3a66be617da70a5d500c47c6`;
the TCP values are
`f7962d2643a684ed2bf14c2e2e3386457240cc1dc677809e60496d39703953b5` and
`eb98f221848fefc3522267357364b7af51671620e27cc986152eacc91876c3bd`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-object-quota
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-object-quota

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.1oaa9bzi \
  --route direct-udp --scenario sync-tree-object-quota
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.x7dul21w \
  --route forced-tcp --scenario sync-tree-object-quota
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, a saturated local whole-store object count, independent
byte headroom, order-independent candidate refusal, failure cleanup, and signed/visible old-state
preservation on this construction kernel. It does not prove automatic eviction, destructive
collection, quota recovery, an independently configurable tree-entry ceiling, read-only storage, a
peak resident-memory ceiling, multi-source or multi-host behavior, arbitrary kernel scheduling,
target-fleet load, content-v2, automatic OTA, or safety-critical actuation. The shared v1
`maximum-objects` meaning and its operational sizing consequence are recorded in ADR 0142.
