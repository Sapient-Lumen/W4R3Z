# Sandwurm route-set-v2 actual-I2P payload evidence

Date: 2026-08-28

Status: accepted bounded signed-class actual-I2P payload evidence

## Claim

Two simultaneous source-linked IoTox guests each constructed a native UDP protected route, a
native UDP bulk route, and an independently keyed laboratory-only `tox/i2p-construction` bulk
route through its own i2pd router. Each guest authored route-set v2 and refused startup unless the
protected coordinator and both auxiliary workers matched the exact network classes signed for
their member keys.

The subscriber explicitly selected `fail-closed tox/i2p-construction` for one signed 131,369-byte
tree. Private route-binding admitted the exact actual-I2P member belonging to the remote stable
principal. The job selected that member once, never reassigned to the simultaneously ready native
bulk route, fetched and verified the artifact and manifest, accepted the signed HEAD last, and
activated the exact tree. Both guest receipts independently report that all signed route network
classes were observed.

This closes the positive-path route-set-v2 prerequisite. It does not close route loss, same-class
recovery, byte continuation, or production `tox/i2p`.

## Accepted compact cell

Compact proof `.sandwurm/exports/pairs/pair.q2pka1fm` allocates 5,255,168 bytes, reports
`contains_secrets=false`, and omits guest disks, injected identities, runtime state, bootstrap
secret, and i2pd data directories. It independently verifies from clean source revision
`0dcbf43894b9429fd50bd1486dc9990d45770a25`, source-linked binary
`d0021c91efad9c0cf5a6e5e6be247ae7811dc7722a9eb434e411bd603ee6c05d`, and node-set commitment
`cf040c3bc97197477a2b5e16e10a101c2b6505939924c04adfefd3de3bca9cc3`.
The complete host/VMM span is 502,536,121,415 ns.

The compact manifest and retained full pair-manifest SHA-256 values are:

```text
655e6c81fa2ce2ce846daab96cd6260fa9169ff36b27409f9232775a77e92a83
744a8d9fb117db4ff17a044ccc02d8bd0f29e805ec3d4caa6b37859428bc1c46
```

The client/device guest receipt SHA-256 values are
`0c6750425f505c7b7d5b0e8d0509f937b0a85e248105354c80cfb48d85448073` and
`dc5d4595393ae7e3a82f3e822343d536f7cbe4535e94d3500972359f03377d98`.
The tree artifact, manifest, HEAD, and payload SHA-256 values are respectively
`1561fd522b8dae36ba428a6c4a4decb12636bc9118d781ff5f58ff82349baf16`,
`0e8cf5710cd6c7145281252f9f9b0c9971d0e0e84d8eba64d011fc6f95b7e2cf`,
`a918fa4320008a845322d396f7169fe2687c268af06f5dbda1af9358a0a709d6`, and
`e00495e384dd69c9ad5a850cbde4be69c277e074ae3b17f56942a2681feb7ffe`.

The manifest requires two roles with signed route-class observation, two ready bulk routes per
role, exactly one initial pull selection, zero pull failures, and one actual-I2P payload observer.
Both TAP captures report zero packets outside their permitted network contexts. The client capture
contains 5,047 packets, including 1,274 to its proxy endpoint; the device capture contains 4,785,
including 1,082 to its proxy endpoint. The final topology commitment is
`006969e953b52dbf6fad9bda4ad7437da1a2a6711bd839959bd95fe6c5f08ad4`.

## Defect found before acceptance

The first genuine route-set-v2 attempt reached all signed route projections but never started the
pull. The five-argument CLI form selected local operation 86 yet omitted its required failover byte,
because explicit failover had been recognized only for the older four-argument form. The encoder
now treats every four-or-more-argument form as explicit. The full Agent route-loss test now enters
both available and fail-closed cases through the real CLI instead of hand-constructing a correct
operation-86 packet. The accepted cell above is a clean rerun after that repair.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-i2p-payload \
  205.185.115.131:443:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68 \
  139.162.110.188:443:F76A11284547163889DDC89A7738CF271797BF5E5E220643E97AD3C7E7903D55 \
  172.104.215.182:443:DA2BD927E01CD05EBCC2574EBE5BEBB10FF59AE0B2105A7D1E2B40E49BB20239
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.q2pka1fm \
  sync-tree-route-private-actual-i2p-payload
```

The verifier binds the clean source/binary, guest receipt chains, exact network-class observations,
stable-principal private membership, fail-closed class selection, zero reassignment, immutable tree
convergence, router/front audits, and packet-context containment.

## Exact nonclaims

This is one physical host, two VMs, one finite run, three reviewed public Tox records, two i2pd
2.60.0 routers, one small tree, and a laboratory construction route. It does not claim anonymity,
unlinkability, timing-correlation resistance, physical path independence, production I2P support,
availability, loss recovery, byte resume, repeated behavior, or a performance bound. The signed
class constrains local construction and authenticated membership; it does not attest the external
path.
