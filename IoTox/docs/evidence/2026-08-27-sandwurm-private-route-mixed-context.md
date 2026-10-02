# Sandwurm private-route mixed-context evidence

Date: 2026-08-27

Status: accepted two-guest authority-private native/generic-SOCKS route evidence; not actual Tor

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`9a7389564c99c0b91c8dd912237479d5ef4a977a` and identical IoTox binary SHA-256
`0781b30def613ebfedeaa39e1e1fb4b0e64a7fdf213c95289985e1d5285fd56d`. Each reused the immutable
private test-identity baseline without modifying it and constructed three independently keyed Tox
routes under one stable device principal: a native UDP primary, a native UDP bulk member, and a
strict generic-SOCKS/TCP bulk member.

The complete signed route inventory crossed only the authority-authenticated primary. Each
auxiliary exchanged only its fixed v2 member proof. Both roles reported the mixed context, two ready
bulk members, synchronization authority, accepted HEAD, and explicit activation. The converged
tree contains three directories, three files, and 4,194,389 content bytes. Its payload SHA-256 is
`374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`; artifact and manifest
SHA-256 values are `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` and
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`.

## Packet and proxy observations

The verifier extracts only the first, outermost tshark occurrence before selecting guest egress.
This prevents an inbound ICMP error's embedded original UDP header from masquerading as outbound
traffic.

| Role | IPv4 egress | Native UDP | Native ICMP | Local relay TCP | SOCKS TCP | Unexpected context packets | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---|
| client | 3,493 | 2,832 | 25 | 43 | 593 | 0 | `f553b0725ee4716453b4ccc60695b91807dbcef05b581acb1e932347e134c7d4` |
| device | 3,235 | 2,607 | 14 | 46 | 568 | 0 | `04f4bf21763155f7b9c9a635db7544b2f88a502ccd9f95fe7f506e48445fd1f6` |

Native UDP and its possible ICMP consequences may use public destinations. Every TCP packet was
confined to `10.0.0.1:39050` (strict SOCKS) or `10.0.0.1:33445` (the pinned local TCP relay). The
SOCKS audit admitted four connections, all to `10.0.0.1:33445`, and denied zero; its SHA-256 is
`38df19b5d2d3f5cebe8e54a5bbf02ae6defebffae0d3e4c79afff125df6e4ecb`.

The complete host span, including source-linked image realization, was 389,155,509,158 ns.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.z948jeii`. It allocates 3,727,360
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
and the bootstrap secret. Its source-manifest, compact pair-manifest, containment, and compact-export
SHA-256 values are respectively:

```text
64d2a3769df533d04194250a0ea18eb1452be3f4fc09b5a530f861804c169696
7f92a7427975cc7419166ec30161e6c532341a9dfa7265031ea4146d6b0ea912
509d3eb35a013f6e89194b1874bfb554ce673996279d097f30ab28dbc2ed5375
581c605c2ac408cfcb46a816ff54e4b4bf1c51dceb949c22a1fb798b513b85df
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-tree-route-private-mixed
```

Both raw and compact accepted roots independently returned status `passed` from
`iotox.sandwurm-pair-verification.v0`.

## Exact nonclaims

The Tor-designated workers crossed the repository's numeric allowlisted SOCKS forwarder, not an
actual Tor daemon. This is one construction host, one guest pair, one provider build, one signed
tree, and one finite observation. It does not prove anonymity, public Tor circuits, malicious-proxy
resistance, timing unlinkability, physical-path diversity, cross-context failure recovery,
long-running reliability, I2P, or a production default. The separate operator-Tor evidence proves
one single-IoTox public route; the still-open M8 matrix must join actual Tor to two IoTox peers over
multiple relays/time windows before that wider claim exists.

