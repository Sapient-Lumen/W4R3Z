# Sandwurm multi-source content-v2 evidence

Date: 2026-08-30

Status: accepted direct-UDP qualification; forced-TCP falsification retained as a nonclaim

## Accepted claim

Three independent IoTox agents in two simultaneous source-linked KVM guests converged one frozen
content-v2 revision from two complementary, independently authorized c-toxcore sources over direct
UDP. The original source remained the sole signed-HEAD authority. Exact sparse availability selected
immutable objects from both peers; the subscriber reconstructed canonical whole-artifact CAS,
accepted the original HEAD last, and activated only through the exact local token.

The accepted secret-free compact proof is:

```text
.sandwurm/exports/pairs/pair.u80_yp7r
```

It allocates 163,840 bytes and passes strict verification with route `direct-udp` and scenario
`sync-content-multi-source`.

The proof binds source revision `51f51ba3b206e04a6a4594bbe7dd7e6941f319f7-dirty`, IoTox
`0.45.0 rev0045`, c-toxcore `0.2.23` variant `iotox-file-rr1-tcp-connect120`, libsodium `1.0.22`,
and Argon2 `20190702`.

## Exact bindings

```text
whole-VM rendezvous span       421254591741 ns
IoTox binary SHA-256          6c1a973b455eab17fcf048aa714ef66aa2e5383c80a8524892208eab43130d65
artifact SHA-256              844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7
root-manifest SHA-256         f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66
signed-HEAD record SHA-256    5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c
secondary Tox-key commitment  359824afea8462049231fd5746a3557ff21493e794228897466e764cf5c37ef3
secondary principal commit    2188011de0f5f522dcd5b4758f53fd7ace8ff2e8d71f9222c8062b79224d4d80
client receipt SHA-256        51ab4de8122ebd1ab801779525efd46a1ab678306f0acd7f24e2906e43c1caf6
device receipt SHA-256        226926af9e042e70c4c80444519ed2ed9c6581ddeef186d82474b8a1d1bde892
source manifest SHA-256       a7c4d128bf94a04094076503d6a1afdfe47ad4e0178b2ed99e872b87f976777a
compact manifest SHA-256      bd33492c1b823281eb17fe8d5fa18622101b82e152be25ac06c16545eb44dc1c
compact export SHA-256        b04afa9da54decc9a091c800676668959bd3c8a74f2ca075b0b0d471f500b790
```

The content record binds 4,194,304 artifact bytes, a 272-byte paged root, four logical chunks, one
page, and four content objects. Both sources answered two windows, for four availability requests
and four matching results. The primary supplied three logical chunk occurrences and the secondary
one. Device counters bind five primary object requests and one secondary object request.

The apparent 3/1 logical split is correct. The four logical chunks contain only two distinct physical
chunk digests. The fixture parses the authenticated page, assigns each distinct digest to exactly one
provider, and then counts logical occurrences. It does not infer physical inventory from logical
chunk count.

## Forced-TCP experiment

Forced TCP did not pass, and no forced proof is accepted. The following raw roots were bounded
scientific attempts:

| Raw root | Topology | Exact terminal boundary |
|---|---|---|
| `pair.w5xdce8a` | one bootstrap/relay for all three agents | primary confirmed; secondary never confirmed |
| `pair.yq63hq4o` | client bootstrapped and relayed through A+B; publishers split | primary session failed on both roles |
| `pair.5_ns69s9` | client bootstrapped A and relayed A+B; secondary bootstrapped/relayed B | primary confirmed; secondary session failed on both roles |
| `pair.65pchyu1` | all agents bootstrapped A; client relayed A+B; publishers used A/B | four stable relay sessions and primary confirmation; secondary session failed on both roles |
| `pair.kz_b8aqu` | common bootstrap A; publisher-specific A/B relays; secondary friendship requested only after primary confirmation | five stable relay sessions and primary confirmation; secondary session failed on both roles |
| `pair.e246dutm` | all three identities connected to both A and B; secondary friendship requested only after primary confirmation | six stable relay sessions and primary confirmation; client secondary session failed at generated line 1773 |
| `pair.krdg001v` | instrumented repeat of serialized all-relay mesh | secondary `offline`, `connected=0`, `connection=offline`, zero HELLO sends/receives/attempts |
| `pair.vps8gh0q` | ordinary accept attempted for secondary only | nondeterministic primary failure on both roles; secondary ceremony not reached |
| `pair.wkaoqike` | ordinary one-request/explicit-accept for primary and secondary | device timed out with `primary-request-seen=0`; isolated relays did not deliver a pending request |
| `pair.cmvi_god` | mutual reusable-key pre-provision; all identities on A+B | primary confirmed; secondary remained Tox-offline with zero HELLO attempts |
| `pair.5c2o3ake` | mutual reusable-key pre-provision; subscriber A+B, publishers A/B | primary confirmed; secondary remained Tox-offline with zero HELLO attempts |
| `pair.tc5w6e8k` | device pre-accept plus client full-address request; common bootstrap A, publisher relays A/B | secondary passed initial TCP/confirmed checkpoint, then stayed offline through 300-second authority window |
| `pair.cznfp0_q` | same hybrid, secondary bootstrap+relay confined to B | four exact relay sockets and primary confirmation; secondary remained Tox-offline with zero HELLO attempts |

Each complete forced variant used the same 900-second guest construction deadline. The deadline was
not widened after failure. Host observation distinguished established TCP relay sockets from the
guest's canonical `session state=confirmed` assertion. Instrumented failures distinguish a Tox
carrier from the IoTox transcript: an offline secondary records `connected=0`, `connection=offline`,
and zero HELLO activity. Serializing friendship admission, adding relay sockets, all-relay mesh,
mutual no-request pre-provision, ordinary pending-request acceptance, and strict B-only secondary
placement are falsified as sufficient fixes.

The most informative hybrid run was `pair.tc5w6e8k`. The subscriber requested the full Tox address
only after the device had pre-accepted its reviewed reusable key. The secondary crossed the exact
initial `connection=tcp` plus `state=confirmed` assertions, then returned to `offline` before v3
authority converged. Both roles sampled that state for the complete 300-second authority subwindow;
no content pull began. This narrows the bottleneck to durability of the second friend/application
session in this rendezvous construction rather than content scheduling, FileId, CTA1, or bulk
throughput.

This does not prove a universal c-toxcore limitation. It proves only that this one-subscriber,
three-agent, two-VM forced-TCP construction does not yet qualify. A later design may need separate
route identities or a different rendezvous construction, but that is not accepted here.

After the boundaries were recorded, the guarded zero-retention cleaner removed every rejected raw
root and the accepted private source root. The first cleanup reclaimed 13.9 GiB; each later bounded
cell reclaimed another approximately 2.3 GiB after its exact terminal assertion was recorded. The
compact accepted direct-UDP proof remains and passed strict replay again; rejected raw roots are
reproducible inputs, not durable accepted evidence.

## Repository validation

- GCC Debug: 664/664 owned checks and 46/46 CTest entries passed in the pinned development shell;
- Clang Debug: warnings-as-errors build plus the same 664/664 and 46/46 passed;
- five cgroup process entries were expected skips in both compiler lanes because the shell lacked a
  delegated writable cgroup subtree;
- Sandwurm runner, verifier, and exporter self-tests passed;
- strict replay distinguishes the original non-atomic ADR 0255 completion shape from ADR 0256's
  later atomic source-admission shape. Historical `pair.u80_yp7r` and current durable-replica/loss
  proof `pair.w_ws202c` both passed after this compatibility boundary was locked into the verifier;
- `toxBootstrapSecondary` built with its exact port-33446 patch, and both forced-TCP guest closures
  evaluated; and
- `nix flake check` passed, including the IoTox package, provider-upgrade fixture, and bootstrap
  NixOS service VM test.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-content-multi-source
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.u80_yp7r sync-content-multi-source

# Retained fail-closed research gate; currently expected not to qualify.
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-content-multi-source
```

## Exact nonclaims

This evidence does not qualify forced-TCP multi-source operation, source disappearance or
reassignment, simultaneous content lanes, striping, daemon/guest restart, comparative speedup,
arbitrary topology, two physical hosts, hostile kernels/filesystems, power loss, fleet behavior, or
unattended update safety.
