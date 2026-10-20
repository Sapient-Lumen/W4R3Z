# Reusable and fresh genuine-test identity evidence — 2026-08-15

Classification: redacted shareable report. The reusable baseline remains local private test
material under the ignored `.cache/` tree; it is not an evidence artifact. Every run used a fresh
work directory, and the harness destroyed all copied keys, ledgers, command stores, runtimes, files,
and logs on exit. The fixed, non-production RecallRoot phrases remain ordinary public fixture text
in the harness.

## Inputs

```text
product-source-commit=531d74d46a3fe6477b5b9633c960cf8b0fe5e98b
genuine-harness-sha256=6773031b06014372d1f32ea472dd59a8fd78c0a8137fb3f06b1a90f9aa3f782b
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=cb448346b8f58d3f25d8305a61955029bb7879fd1beee080790988056203b5ca
provider=c-toxcore-0.2.23 source-linked
route=tox/native using the pinned default bootstrap/relay catalog
timeout-seconds=240
```

The binary was built immediately before the named product-source commit; the later commits changed
evidence and repository tooling rather than compiled product source. The harness hash names the
exact uncommitted-at-execution script that this evidence accompanies.

## Cache preparation and at-rest reuse

`./tools/run-real-peer-smoke.sh --prepare-keys` provisioned two distinct peers and published exactly
four private baseline files. A second preparation returned ready without modifying any byte. Both
the initial and repeated validation observed owned `0700` directories and nonsymlink, nonempty
`0600` files. No authority ledger, command store, runtime, or friend/request projection was admitted
to the cache.

Private file digests are intentionally omitted from this shareable record. The harness retained an
aggregate digest in process and verified it again only after each reused-key lifecycle.

## Reused-key result, run 1

```text
real-peer-smoke=pass
key-mode=reuse
key-lifecycle=reused-immutable-clean-baseline
peer-a-public-key-sha256=cde58bc4372848354e741e855fe02d98981eccf5ca88fa4e065c7ac1f349558f
peer-b-public-key-sha256=477a8e972bdb38fb8c9339250c112827924ba02fad1ef6cba5097c0a111cbcc9
initial-convergence-ms=22016
reconnect-convergence-ms=18898
```

## Fresh-key result

```text
real-peer-smoke=pass
key-mode=fresh
key-lifecycle=fresh-generated-disposable
peer-a-public-key-sha256=2b3748af8b20efad6d97d1b4ccd3b72baa0dfca8713d439654209971d85ad76d
peer-b-public-key-sha256=b16003836a4e3f979630e28cb3091ba2e7b045ba0d16dcfafb267e8f7a70ee01
initial-convergence-ms=15091
reconnect-convergence-ms=24825
```

## Reused-key result, run 2

```text
real-peer-smoke=pass
key-mode=reuse
key-lifecycle=reused-immutable-clean-baseline
peer-a-public-key-sha256=cde58bc4372848354e741e855fe02d98981eccf5ca88fa4e065c7ac1f349558f
peer-b-public-key-sha256=477a8e972bdb38fb8c9339250c112827924ba02fad1ef6cba5097c0a111cbcc9
initial-convergence-ms=30530
reconnect-convergence-ms=38492
```

Both reused runs reported the same two public-key hashes; the intervening fresh run reported a
different pair. All three runs independently passed:

```text
canonical HELLO transcript confirmation in both directions
stable-principal proof and mutual read-telemetry authority
denied device followed by recalled-owner re-entry
owner-role denial, self-delegation, exact duplicate handling
remote revocation, restart replay, and re-delegation
successor nomination, ownership epoch transition, and retired-owner denial
live text, device.describe, system.summary, and exact finite-file completion
bilateral friendship removal/re-add and fresh session/authority proof
Tox and stable-device identity preservation across process restart
```

## Claim boundary

This establishes that the founding bare-metal harness can reuse one clean test-only identity pair
across complete genuine network runs without persisting lifecycle state, and can still complete the
same lifecycle from newly generated keys. It does not make the local cache a backup or release
artifact, authorize production-key use, prove concurrent multi-host use of one identity, establish
controlled packet-loss behavior, or replace independent provider/target qualification.
