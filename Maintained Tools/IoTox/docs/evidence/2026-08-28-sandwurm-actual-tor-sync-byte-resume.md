# Sandwurm actual-Tor synchronization byte-resume evidence

Date: 2026-08-28

Status: accepted bounded actual-Tor process-loss/resume/recovery evidence

## Claim

Two simultaneous source-linked IoTox guests combined a native UDP primary with two separately keyed
authority-private v2 bulk members. Stable-key order assigned the client lane-1 member to an
independently supervised Tor process and left the second auxiliary available over native UDP. The
subscriber began a genuine 16 MiB signed-tree pull on the Tor member.

After 75,405 observed artifact bytes and authenticated Tor process/control/circuit capture, the host
sent `SIGKILL` only to the client Tor process group. IoTox observed authoritative loss after
27,750,415,228 ns, retained two concurrently positive whole-object prefixes totaling 102,825 bytes,
and reassigned the job once to the native auxiliary. Fresh attempts and FileIds inherited both
prefixes; resumed attempts and bytes matched retained attempts and bytes exactly. No retention
fallback occurred, no partial remained, and the IoTox route-worker restart count stayed zero.

The complete artifact and manifest passed their immutable digests, accepted HEAD committed last,
and activation completed. Two stale old-carrier terminals were fenced. The host then restarted the
same Tor 0.4.8.11 binary, configuration, and private data directory; bootstrap reached 100 after
2,338,796,178 ns, and IoTox counted exactly one carrier recovery under the same member identity.

## Accepted compact cell

Compact proof `.sandwurm/exports/pairs/pair.3u5cjbci` allocates 12,652,544 bytes, reports
`contains_secrets=false`, and omits guest disks, injected identities, runtime state, bootstrap
secret, and Tor data directories. It independently verifies from clean source revision
`de020dc2d1f9453e1a89122024c1d6787f6b358b`, binary
`97ccac9341c6e87709645be22533395526159fd739b47bcef357026991801a19`, and Tor binary
`63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`.
The complete host/VMM span is 685,079,485,549 ns.

The compact pair manifest, compact index, and actual-Tor process-loss record SHA-256 values are:

```text
57759c6dfd311e05b842f0b7fec678e2d72506ee30ee9acff686135008bdfe0d
cdbbc1191ecee6c996920f2f9a251063797579e47e217f90dc244d95234bc223
630bb3965aa23ea2bdb20b74301d47a0d6fc363ba42383bb6184ff78356832b4
```

The client/device guest receipt hashes are
`88ac61dbea32ead3bd33fdb3f610069c63a14b7dce90874ebec11350830e248f` and
`e6fb6f31d5ed806df3b7b7f4b6ed3fddf526a90bb547a499d03f895b4682a26b`.
The tree artifact, manifest, HEAD, and payload SHA-256 values are respectively
`e3a25daf0e29c4ce25bd87a55a7d5437863a367f804ac551f7c1fe47a877c4a4`,
`ecaaea48dde740c466f550d20ec30f8267008d646326ff37e8b23c9c13f012ad`,
`009d592db7c4f9ea2a6296a279307ca8c2ad81cbf64158e56a70e129933facfd`, and
`4d4d1b014a00448e56f14a5638b05494326003ae805cdd124ab1d55be0a73b97`.
It has three directories, three files, and 16,777,301 content bytes.

Three independently authenticated Tor phases—client before loss, client after recovery, and the
continuous device process—each reached bootstrap 100 and bound the configured public Tox target to a
three-hop linked-Conflux application circuit. Client pre-loss, client recovered, and continuous
device circuit-path commitments are
`cc56fc0570be82f7bfd65854814e8035e1fe659b60cf27c7f908cc6756d5e7c5`,
`5880e95481dd4fe1e0bdfbf166e958c38c77b709ed58b8d6a2b630a4834c8d14`, and
`442d2abc192100ac024df592c1bc6dfb9d47533efef95c3b30fd63a9832ed2d1`.

The client/device TAP captures contain 5,902/8,392 IPv4 packets, 889/1,359 packets to their exact
local Tor endpoints, and zero unexpected-context packets. All guest TCP is confined to the configured
local relay or Tor endpoint. Their capture SHA-256 values are
`71de721de2bbca05c5e370b93cfb0334cf2fd3bdadd92037991334ddeff56211` and
`c21070516cc5308e792aa44a450cbc3a2fc9ee47cea63311eb856666498ebde9`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-loss \
  144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.3u5cjbci \
  sync-tree-route-private-actual-tor-loss
```

The verifier binds the public node, Tor binary/configuration/control observations, three circuit
phases, `SIGKILL` result, stopped and replacement carrier identities, zero worker restart, exact
retained/resumed prefix equality, tree convergence, Tor return, guest chains, and packet containment.

## Exact nonclaims

This is one physical host, two VMs, one public Tox record, one Tor build, one Tor-to-native policy
transition, one signed tree, and one finite time window. It does not claim anonymity, unlinkability,
timing-correlation resistance, physical path independence, permission to cross privacy classes,
Tor-to-Tor continuation, terminal migration, general public-relay reliability, repeated/late loss,
restart continuation, or a production performance bound. The final digest remains authoritative;
prefix retention is only a same-process transfer optimization.
