# Toxic compatibility bridge live proof

Date: 2026-09-19; forced-TCP addendum 2026-09-20

Status: passed on the founding workstation.

This gate uses stock Toxic as a normal external Tox client and source-linked
IoTox as the device agent. It is deliberately not an IoTox-to-IoTox mock. The
test starts both clients from fresh private state, drives Toxic through its TUI,
and proves the normal-Tox edge before exercising the signed IoTox bridge layer.

Replay:

```sh
tools/run-toxic-compat-bridge-lab.py
```

The harness auto-builds the source-linked IoTox package from a clean git
archive when `--iotox` is omitted, and builds pinned Toxic from Nixpkgs
`50ab793786d9de88ee30ec4e4c24fb4236fc2674` when `--toxic` is omitted. The
successful retained run used:

```sh
tools/run-toxic-compat-bridge-lab.py \
  --iotox /nix/store/5ddccv1n62qq20ydrj45nakxnfjis2c2-iotox-source-linked-0.51.0-rev0051/bin/iotox
```

The default-route successful run produced `iotox-toxic-compat-live-proof-v1` with nonce
`d63ff6f615` in `/tmp/iotox-toxic-live-lab-im7umpv9/proof-summary.json`.
That lab directory is intentionally not committed because it contains fresh
private Tox savedata.

The forced-TCP retained run used:

```sh
tools/run-toxic-compat-bridge-lab.py \
  --toxic-force-tcp \
  --iotox /nix/store/5ddccv1n62qq20ydrj45nakxnfjis2c2-iotox-source-linked-0.51.0-rev0051/bin/iotox
```

It produced `iotox-toxic-compat-live-proof-v1` with nonce `b98087803d` in
`/tmp/iotox-toxic-live-lab-oxmppg3x/proof-summary.json` and
`toxic_force_tcp=true`.

What passed:

- Toxic generated a fresh normal Tox identity.
- Toxic sent `/add IOTOX_ADDRESS toxic-compat-lab-...`.
- IoTox observed the Toxic friend request and accepted Toxic's public key.
- IoTox sent ordinary normal Tox text `iotox-to-toxic-d63ff6f615`.
- Toxic displayed/logged that normal Tox text.
- Toxic sent ordinary normal Tox text `toxic-to-iotox-d63ff6f615`.
- IoTox recorded that text in `peer-messages`.
- IoTox created a self roster, public person card, and delegated sender record.
- IoTox wrapped the Toxic inbound text as a signed
  `iotox-person-tox-bridge-plan-v1` payload under the delegated self device.
- The inbound/outbound plan path printed a `--bridge-store` local commit
  command for owner review.
- `person tox-bridge-receive` committed the bridge observation once.
- Replaying the same bridge payload reported `duplicate=1 mutated=0`.
- `person tox-bridge-status` reported `entries=1`, `inbound=1`,
  `outbound=0`, and `content-free=1`.
- `person tox-bridge-plan-out-delegated` printed a normal-Tox
  `iotox message-hex key:TOXIC_KEY ...` command targeting the actual Toxic
  public key from the run.

What additionally passed under forced TCP:

- Toxic was launched with `-t` and a lab-local single-line `DHTnodes.json`
  formatted for Toxic 0.15.x's exact no-whitespace parser.
- IoTox was launched with `--native-tcp-only`.
- IoTox sent a normal friend request to Toxic's full Tox address.
- Toxic listed the request with `/requests` and accepted it with stock
  `/accept 0`.
- IoTox sent ordinary normal Tox text `iotox-to-toxic-b98087803d`.
- Toxic displayed/logged that normal Tox text.
- Toxic sent ordinary normal Tox text `toxic-to-iotox-b98087803d`.
- IoTox recorded that text in `peer-messages`.
- The same delegated bridge-store proof passed with duplicate idempotence and
  an outbound plan targeting the actual forced-TCP Toxic public key.

This proves the current one-to-one normal Tox compatibility bridge with Toxic:
ordinary Toxic messages can cross the outer Tox friendship edge, and IoTox can
turn the observed normal-Tox event into the signed multidevice compatibility
record that other self devices can verify.

Nonclaims:

- This is not a normal Tox group/conference bridge.
- This does not make Toxic's public key an IoTox person key.
- This does not make Tox read receipts into person/all-device receipts.
- Toxic is the supported compatibility target. Other clients are intentionally
  outside this gate unless we choose to add them later.
- This does not prove NAT-hostile, Tor, I2P, long-haul, or lossy-network
  behavior. Forced TCP now has founding-workstation evidence through public
  Tox TCP relays, but not a broad network matrix.
- The live lab keeps private savedata in its retained evidence directory; only
  content-free summaries belong in git.

## Multidevice Toxic bridge proof

Status: passed on the founding workstation.

Replay:

```sh
tools/run-toxic-multidevice-bridge-lab.py
```

The stronger gate starts three independent source-linked IoTox device agents
and one stock Toxic profile. The accepted committed-state replay used:

```sh
tools/run-toxic-multidevice-bridge-lab.py \
  --iotox /nix/store/5ddccv1n62qq20ydrj45nakxnfjis2c2-iotox-source-linked-0.51.0-rev0051/bin/iotox
```

The accepted committed-state replay produced
`iotox-toxic-multidevice-compat-live-proof-v1` with nonce `e85f1aed46` in
`/tmp/iotox-toxic-multidev-lab-3camoswk/proof-summary.json`.
That lab directory is intentionally not committed because it contains four
fresh private Tox savedata profiles.

The forced-TCP retained run used:

```sh
tools/run-toxic-multidevice-bridge-lab.py \
  --toxic-force-tcp \
  --iotox /nix/store/5ddccv1n62qq20ydrj45nakxnfjis2c2-iotox-source-linked-0.51.0-rev0051/bin/iotox
```

It produced `iotox-toxic-multidevice-compat-live-proof-v1` with nonce
`556d130f26` in
`/tmp/iotox-toxic-multidev-lab-v1s6aeyu/proof-summary.json` and
`toxic_force_tcp=true`.

What passed:

- Toxic generated one fresh normal Tox identity.
- Three IoTox devices generated distinct Tox route keys and distinct stable
  device principals.
- Toxic friended all three IoTox devices through normal `/add` requests.
- Each IoTox device sent a normal probe to Toxic and received Toxic read
  receipt plus Toxic-side log/display evidence.
- Toxic sent one ordinary normal Tox text to bridge device A.
- Device A recorded that Toxic text in `peer-messages`.
- The three IoTox devices formed a full self-route Tox mesh: A↔B, A↔C, B↔C.
- IoTox created one private self roster, one public person card with three
  routes, and delegated sender records for A, B, and C.
- Device A ran live `person tox-bridge-fanout-in-delegated`, skipped its own
  current route, committed its local bridge store through `--bridge-store`,
  and sent the signed inbound bridge observation to B and C.
- A, B, and C all committed that inbound bridge observation.
- Devices A, B, and C each ran live
  `person tox-bridge-send-out-delegated` to Toxic with `--bridge-store`.
- Toxic read-receipted and logged/displayed all three outbound normal Tox
  messages.
- Each outbound bridge observation self-fanned to the other two IoTox devices.
- Each live bridge sender committed its own local bridge store during the
  successful bridge command.
- Final `tox-bridge-status` on A, B, and C reported `entries=4`,
  `inbound=1`, `outbound=3`, and `content-free=1`.

What additionally passed under forced TCP:

- Toxic was launched with `-t` and the compact lab-local Toxic nodes file.
- All three IoTox devices were launched with `--native-tcp-only`.
- Devices A, B, and C each initiated friendship to the one Toxic identity, and
  Toxic accepted each request with its stock `/accept` command.
- All three device routes proved normal text delivery to Toxic with Toxic-side
  receipt/log evidence.
- Toxic sent one ordinary inbound normal text to device A.
- The full A↔B↔C self-route mesh, inbound bridge fanout, three outbound bridge
  sends, and final `entries=4`, `inbound=1`, `outbound=3`,
  `content-free=1` bridge-store status passed over forced TCP.

This proves the current one-person/three-device normal Toxic compatibility
shape: a normal Toxic contact can talk to one IoTox bridge route; that
observation can reach the other self devices; and any self device can send
normal Toxic text back while the other self devices receive the signed outbound
observation.

Additional nonclaims:

- This is still not a normal Tox conference/group bridge.
- This is not automatic background routing across arbitrary offline devices.
- Toxic is the compatibility target for this proof. Other clients are
  intentionally outside this gate unless we choose to add them later.
- This does not prove Tor, I2P, NAT-hostile, long-haul, or lossy-network
  behavior for multidevice Toxic compatibility. Forced TCP now has
  founding-workstation evidence through public Tox TCP relays, but not a broad
  network matrix.
- The bridge observation says a delegated IoTox device observed/sent normal
  Tox text; the external Toxic key still did not sign an IoTox person message.

## Long-loop addendum

The 2026-09-29 massive soak campaign kept both multidevice Toxic bridge loops
running for an elapsed day with `--keep-going`; see
[`2026-09-29-massive-soak-campaign.md`](2026-09-29-massive-soak-campaign.md).
The default/native route produced 539 passing iterations and 16 failed
iterations, a pass rate of about 97.1%. The forced-TCP route produced 116
passing iterations and 90 failed iterations, a pass rate of about 56.3%.

That addendum changes the confidence shape: default/native Toxic compatibility
has strong long-loop evidence with rare lab flakes, while forced-TCP is proven
to work repeatedly but remains degraded and should not be described as a smooth
daily-driver bridge route yet.

## Harness hardening after the long loop

The long-loop failure distribution showed that much of the forced-TCP pain was
at the Toxic PTY/control boundary, not in the signed bridge semantics. The
harness now accepts Toxic request rows rendered next to the `/requests` command
echo, writes richer failure dossiers for IoTox request waits, and treats
retry-created outbound bridge records as expected local state. Until a fresh
soak proves otherwise, the built-in route label is
`default-qualified-forced-tcp-degraded`.

The 2026-09-30 follow-up narrowed another harness weakness: friendship setup
was a one-shot action even though fresh public Tox routes can take minutes to
propagate, especially under forced TCP. The single-device and multidevice
Toxic labs now retry Toxic `/add`, IoTox `transport-peer-request`, and the
IoTox self-mesh `transport-peer-request` during the existing request timeout.
For IoTox-originated retries, the harness first removes the pending peer by
exact `key:...` selector, then sends a fresh request; otherwise toxcore keeps
the first pending friend and rejects later duplicate requests without actually
re-sending. Duplicate/pending retry errors are kept as diagnostics instead of
ending the wait. The lab-local Toxic bootstrap file was also refreshed from the
official `nodes.tox.chat` JSON to a numeric-only set of current TCP-capable
nodes so forced-TCP tests do not depend on stale relays or DNS. Fresh
one-iteration default and forced-TCP multidevice Toxic smokes passed after the
first hardening pass, but forced-TCP remains degraded until a long follow-up
soak is boring.
