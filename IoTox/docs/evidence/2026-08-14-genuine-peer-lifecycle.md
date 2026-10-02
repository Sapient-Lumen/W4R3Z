# Genuine-peer lifecycle evidence — 2026-08-14

Classification: redacted shareable report. The disposable work directory, Tox savedata, stable
device identities, RecallRoot fixture phrases, authority ledgers, command stores, runtime trees, and
logs were destroyed by the harness and are not evidence artifacts.

## Inputs

```text
product-source-commit=7a62a9905c35c1802176e33f619393f885817238
lab-harness-commit=c08df7c6736aba6be5ca1efe3e18ee5775dd790b
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=20d634505bd3fe257937f0042cd06738a8d2504339d9165245afad8fa08d8c87
provider=c-toxcore-0.2.23 source-linked
route=tox/native using the pinned default bootstrap/relay catalog
timeout-seconds=240
```

The binary was built before the harness-only commit; that commit changed no compiled source. The
product source tree used by the binary is therefore named separately and exactly above.

## Redacted result

```text
real-peer-smoke=pass
peer-a-public-key-sha256=e69260a9c5a92b7dba6bc1e039ef1402420c0fae7413a046535109b1db943c88
peer-b-public-key-sha256=5f41b2cb7e16300648cc4b1735cc7417d4c07b1de3eb5b30b805715506b6efc6
session=canonical-hello-transcript-confirmed-both-directions
authority=stable-principal-proof-and-read-telemetry-grant-both-directions
message=delivered-to-peer-journal
command=device.describe-received-succeeded-and-durably-reloaded
summary=system.summary-received-succeeded-and-typed
file=finite-exact-bytes-completed
friendship=removed-both-directions-and-readded-with-fresh-session-proof
restart-identity=tox-and-stable-device-preserved
```

## Claim boundary

This establishes one successful two-genuine-peer native-Tox lifecycle on the founding bare-metal
host. It does not establish a controlled bootstrap topology, relay-only routing, packet-loss
behavior, resource budgets, cross-client compatibility, independent reproduction, or production
readiness. Those remain M3 gates.
