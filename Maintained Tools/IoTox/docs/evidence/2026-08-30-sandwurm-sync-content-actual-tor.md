# Sandwurm content-v2 over an exact actual-Tor worker

Date: 2026-08-30

Status: accepted one-source mixed-route qualification

## Accepted claim

Two simultaneous source-linked IoTox KVM guests kept authority, writer proof, and the signed
content-v2 HEAD on their primary direct-UDP sessions while moving availability, object, FileId,
CTA1, and terminal effects through one separately authenticated `tox/tor` worker per guest. The
subscriber invoked `sync-pull FRIEND NAMESPACE fail-closed tox/tor`, converged the exact paged
4 MiB revision in one attempt with zero failures, accepted its HEAD last, and activated only by its
exact local token.

The accepted secret-free compact proof is:

```text
.sandwurm/exports/pairs/pair.fahovlrg
```

It allocates 14,671,872 bytes and passes strict replay with route `direct-udp` and scenario
`sync-content-route-private-actual-tor`. The larger size than an ordinary content proof is the two
retained packet captures and Tor control/circuit evidence; guest disks, identities, bootstrap keys,
Tor datadirs, and runtime state are omitted.

## Exact bindings

```text
source revision                  8ad2fb3516ef5e60e399f5fe181fbeae84bb2f75-dirty
IoTox                            0.45.0 rev0045
c-toxcore                        0.2.23 iotox-file-rr1-tcp-connect120
IoTox binary SHA-256             cc6d986d45c9c371cfab7f8524c5b49680e7f37c48185ebd1e570e936fa84dba
Tor                              0.4.8.11
Tor binary SHA-256               63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2
simultaneous-pair span           397271436681 ns
artifact SHA-256                 844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7
root-manifest SHA-256            f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66
signed-HEAD record SHA-256       5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c
selected Tor carrier SHA-256     0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c
client receipt SHA-256           02ed3d77a165e2d6d80b11d5f319a5cacbb6cdd663b7363a23d33fa9c70439ff
device receipt SHA-256           43944b850e519fdcc28ec555ce78230b0d697a55395857b76f9b64def33939dd
source manifest SHA-256          e14928370aade1b47a75ce41d3301c23fe6d839b3b6eb5c25a16c0637dd0dfc2
compact manifest SHA-256         783f3a01f1205faeeab4cec6356520361b39aff3cd65aa2ceb7034303ea0ea4b
compact export SHA-256           ad9cc10b2253cf352a2ee93284425604acc9f49241edf5bb52d378adcb6fa5fa
```

Both guests report `private_route_primary_network=Tox/native` and
`private_route_auxiliary_network=Tox/Tor`, and both exact auxiliary workers are ready. Only the
subscriber reports the selected payload carrier, as expected for the pulling role. It reports zero
reassignments. The compact completion record binds four chunks, one page, four deduplicated content
objects, the 272-byte root, convergence, activation, and generation 1.

The two guest TAP captures contain both native primary traffic and traffic to their configured Tor
endpoints, with zero unexpected-context packets. Two independent Tor processes built circuits to
the operator-supplied public Tox TCP record. This proves route separation and actual Tor process use;
it does not prove anonymity.

## Failure found by the gate

The first product-complete attempt established primary authority and exact Tor route proofs but
retried the pull until its bounded deadline because every worker reported
`content-negotiated=0`. Agent constructed its `WorkerSupervisor` before it constructed the two
content services, so the worker feature gate was permanently initialized false even though the
primary Agent later advertised bit 29.

The repair retains the fail-closed construction gate. Worker configuration starts false. After both
content services initialize, Agent finalizes the supervisor's content gate before `start()`.
Enabling requires base synchronization support; changing it after startup is refused. Thus the
negotiated feature remains immutable during worker lifetime, but startup order can no longer
silently suppress a service that was actually constructed. The accepted run then completed in one
pull with no retry.

The lab also repaired a strict namespace-policy fixture that emitted an empty line for one-source
content and aligned the runner, verifier, and compact exporter scenario classifiers. Each evidence
tool retains an independent rejection boundary and a self-test for this scenario.

## Reproduction and verification

```sh
python3 tools/run-sandwurm-pair.py direct-udp \
  sync-content-route-private-actual-tor \
  --tor-node IP:TCP_PORT:64_HEX_PUBLIC_KEY

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.fahovlrg \
  --route direct-udp \
  --scenario sync-content-route-private-actual-tor
```

The public node record is an operator input and is not a project dependency. Reproduction should
select a current TCP-capable record rather than assuming the sampled endpoint remains available.

## Exact nonclaims

This evidence does not qualify multiple content sources, multiple simultaneous lanes, byte
striping, automatic or same-job continuation, Tor-process loss during content-v2, I2P content-v2,
forced-TCP primary authority, comparative throughput, anonymity, two physical hosts, arbitrary
filesystem/power faults, or fleet behavior.
