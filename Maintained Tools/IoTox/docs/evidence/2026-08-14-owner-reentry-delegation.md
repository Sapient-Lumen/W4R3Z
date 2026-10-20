# Genuine owner re-entry and self-delegation evidence — 2026-08-14

Classification: redacted shareable report. The three disposable work directories used while
developing and running this gate were destroyed after the result fields below were extracted. Tox
savedata, stable identity keys, RecallRoot fixture phrases, authority ledgers, command stores,
runtime trees, and raw logs are not evidence artifacts.

## Inputs

```text
product-source-commit=d5b166d874b72fa09b02425c528a438057dc2489
lab-harness-commit=4dacc0a007295b98728ff6346b9ef8b4bf973dfc
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=ec4b8573534a399a3b939fdcd3188f9af0409a580ad2ddf8128b4aad13b42b66
provider=c-toxcore-0.2.23 source-linked
normal-route=tox/native using the pinned default bootstrap/relay catalog
tcp-only-route=tox/native using only the pinned default TCP-relay catalog
```

The binary was built from `product-source-commit`. The later harness commit changes only which
fixture RecallRoot phrase is supplied to the controller CLI: remote re-entry reconstructs the
target device's owner, never the controller's owner.

## Deterministic gates

The warnings-as-errors GCC test suite proves these boundaries without relying on network timing:

- a valid but unknown ordinary device claimant is denied;
- exactly one explicit recovery claimant may replace that denied device proof;
- an authorized first proof remains frozen, and recovery replacement cannot be repeated;
- a later exact-head challenge is accepted as a new authority round in the same Tox session;
- a remote append requires the proven owner, exact device, controller, epoch, sequence, and tail;
- unauthorized application is denied, a valid signed record appends once, exact replay does not
  append, and a stale sequence conflicts;
- closing and reopening the receiver ledger preserves the delegated principal and recognizes the
  exact record as a duplicate.
- remote revocation denies missing, inactive, and owner subjects; applies once to an active
  non-owner; and recognizes exact replay without another sequence transition.

All seven GCC CTest entries passed after these tests were added. The fresh-process Agent/session
stress gate then passed 100/100 runs (`shard=1/130`). GCC Release, Clang 21 warnings-as-errors,
ASan+UBSan, and TSan also passed all seven CTest entries.

## Genuine native result

```text
real-peer-smoke=pass
peer-a-public-key-sha256=ea7132eaeda61cf3e53f381c528209495aa2e42e763a813d477f90a91e15148f
peer-b-public-key-sha256=14b700f15ec68e4853a1636b0d15f73bca18ea46f930c3dc5520acfbf9b14f76
session=canonical-hello-transcript-confirmed-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
transport-mode=udp-and-tcp
initial-convergence-ms=22913
reconnect-convergence-ms=13545
peer-a-rss-kib=8652
peer-b-rss-kib=8872
peer-a-cpu-ticks=203
peer-b-cpu-ticks=52
peer-a-context-switches=2270
peer-b-context-switches=891
peer-a-open-fds=36
peer-b-open-fds=36
protocol-journal-bytes-proxy=12286
persistent-tox-savedata-bytes=11937
```

## Genuine TCP-only result

The exact provider-ABI test independently requires UDP, local discovery, DHT announcements, and
hole punching to be disabled. The same ceremony and full lifecycle then passed over configured TCP
relays only:

```text
real-peer-smoke=pass
peer-a-public-key-sha256=0dada607ce6dc3a4bec544b793ef5823bd924fb6dc316c80b1a30b39cf2fda2e
peer-b-public-key-sha256=3e5148653be03f50c02aecfbc41093dbe12e3f62a5fc9ca59714c4368f325fbc
session=canonical-hello-transcript-confirmed-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
transport-mode=tcp-only
initial-convergence-ms=46988
reconnect-convergence-ms=41339
peer-a-rss-kib=8560
peer-b-rss-kib=8432
peer-a-cpu-ticks=805
peer-b-cpu-ticks=67
peer-a-context-switches=6382
peer-b-context-switches=2488
peer-a-open-fds=34
peer-b-open-fds=34
protocol-journal-bytes-proxy=12254
persistent-tox-savedata-bytes=6402
```

CPU ticks and context switches are cumulative host observations at one sample point. Protocol
journal bytes are an application-frame proxy, not wire-traffic measurement. These values are
observed baselines rather than acceptance budgets.

## Claim boundary

This closes the M4 fresh-controller owner re-entry, self-delegation, and delegated-controller
revocation sub-gates for the official IoTox tool and the named pinned provider. It does not yet
close ownership-epoch transition, phrase-compromise response, controlled packet-loss behavior,
every relay or censorship environment, independent reproduction, or production readiness.
Cross-client compatibility is intentionally outside this repository's acceptance scope.
