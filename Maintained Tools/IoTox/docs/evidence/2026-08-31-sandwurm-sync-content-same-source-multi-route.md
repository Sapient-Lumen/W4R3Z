# Sandwurm same-source content over two exact Tor carriers — 2026-08-31

## Claim

One stable remote principal and one native primary authority/HEAD session distribute a 4 MiB
content-v2 revision across two distinct authenticated `tox/tor` worker carriers. Both paths answer
availability, both commit positive immutable-object bytes, the original signed HEAD is accepted
last, and activation remains explicit.

This is whole-object logical-carrier distribution. It is not byte striping, throughput improvement,
transparent failover, independent circuits/exits/physical paths, anonymity, or availability.

## Construction

Two simultaneous Sandwurm Cloud Hypervisor guests reuse the immutable test-only identity baseline.
Each guest constructs two reciprocal route-worker identities in one signed route set. The primary
Agent session remains direct native UDP and owns v3 authority, writer membership, the signed HEAD,
reconstruction, acceptance, and activation. Only content-v2 availability/object traffic and its
FileId/CTA1/terminal chain use the two auxiliary workers.

The client invokes one routed atomic pull with the same source selector twice. Agent must resolve
those repetitions to distinct exact route keys and worker incarnations before sending HEAD. Both
workers are isolated Tox transports, so each legitimately calls its sole peer `friend=0`; verifier
identity therefore uses the route key, worker ID, and complete carrier tuple rather than requiring
different local friend numbers.

One host Tor 0.4.8.11 process serves each guest. Both target the explicit reviewed Tox TCP record:

```text
205.185.115.131:33445
3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68
```

## Invocation and replay

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-same-source-multi-route-actual-tor \
  205.185.115.131:33445:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.iiuhmhy0 \
  --route direct-udp \
  --scenario sync-content-same-source-multi-route-actual-tor

./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/pair.iiuhmhy0

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.iiuhmhy0 \
  --route direct-udp \
  --scenario sync-content-same-source-multi-route-actual-tor
```

## Accepted observations

- proof `pair.iiuhmhy0`, scenario `sync-content-same-source-multi-route-actual-tor`, route mode
  `direct-udp`, status `passed`;
- one stable principal, primary friend `0`, authority epoch `1`, and authority route
  `6943ACCA12AA95F3F5115584DCBB3AFBDC194CA5C198A2CC28C95C7243B15337`;
- source-path IDs `14559789730237573196` and `2946242742209318164`;
- carrier A route `13E3E4EFA78A92E3A1B41AFF31BE596496903F83383566E1BDD15C02BE7ADC10`,
  worker `96522577892379607`, local friend `0`, one committed object, and 272 fetched bytes;
- carrier B route `478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`,
  worker `5163345934066486877`, local friend `0`, five committed objects, and 4,194,560 fetched bytes;
- carrier-set SHA-256
  `e4cc6e4fb61f9710713cb8201b5ff54c9f04ba830ffb7cad5f3d859bb0f82505`;
- four availability requests and four exact results;
- artifact size 4,194,304, artifact SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`, manifest SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`, and accepted HEAD-record
  digest `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`;
- two actual Tor instances at 100% bootstrap, one per guest, with four successful guest-source
  streams on each side;
- client TAP: 4,782 proxy packets, 2,517 native UDP packets, 53 native relay-TCP packets, and zero
  unexpected-context packets;
- device TAP: 5,473 proxy packets, 2,588 native UDP packets, 53 native relay-TCP packets, and zero
  unexpected-context packets; and
- identical source-linked binary SHA-256
  `ad3ffc663ea0ded7a7d849d73de991af338b8be08b267d4f417ca7818984fa04` in both guest receipts.

## Independent verification and retention

The strict verifier re-parses the custom source-path record, requires one principal and authority
session, requires two distinct route keys/source IDs/worker IDs, accepts route-local friend-number
collision, recomputes the sorted carrier-set digest, requires positive contribution on each path,
checks availability completion, and joins the actual-Tor payload and TAP-containment evidence.

- source revision: `a00147722899300fc5ba76f769c5dad21b6e0a50`;
- compact pair-manifest SHA-256:
  `4b7fe3731e82dd6d6d5f0678f3929bb8ccdcb875fec6527e4d96f022bad3c7c5`;
- compact-export SHA-256:
  `ff46156dcfaa1e89fd007c789e18d80298606d844ec3cc98d154a5c72b5911d4`;
- source-path record SHA-256:
  `43b48936ebcea621149b214194b1bda96dc0ce02fb8500c95c54410658e14a78`;
- client/device receipt SHA-256:
  `8feebf92b9d21bad0454b380af3e4080b8c1c4e6fc4c7d4a5351b094a4a02ef2` /
  `cc3cb6eec00f248b29518bec4096d7d02cf46c369f4d6f4c6cca3158d8ce073f`;
- client/device capture SHA-256:
  `3c9277d10835cb1f713578c308261e7b301d1aa13078b4677a1ae3f061e99a35` /
  `56bc9ea7816222613ac208b0a823cc7498b8a66e18e39e79e11185a7485ecdc8`;
- compact files: 21; allocated bytes: 14,811,136; and
- private guest disks, bootstrap secret, injected identities, and runtime state omitted.

The exporter initially exposed a verifier path-label mistake for the new custom record. Commit
`c00eca6` centralizes the exact confined path; verifier and exporter self-tests pass, and both the
unchanged raw proof and compact export then pass strict replay.

## Diagnostic loss observation

A separate non-accepted run reached two ready same-principal carriers and committed positive bytes
through both. One actual-Tor carrier then went offline. Status recorded four of five objects and
2,097,680 fetched bytes before the entire job failed with
`exact auxiliary content carrier went offline`; it did not accept HEAD, activate, or reassign.
This is useful corroboration of deterministic loss tests, not an accepted retained proof.

## Limits

Both worker pairs use their guest's one Tor process and the same public Tox relay target. The
evidence does not bind one circuit or exit to each content carrier, prove independent bottlenecks,
measure a speedup, or justify an automatic route count. Object assignment is intentionally skewed
in this small graph; only positive contribution, not balance, is required. Default content
concurrency remains one, whole-object loss remains fail-closed, and all peer/local-control framing
is unchanged. See ADR 0269.
