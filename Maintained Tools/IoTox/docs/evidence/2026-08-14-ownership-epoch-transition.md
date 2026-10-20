# Genuine ownership-epoch transition evidence — 2026-08-14

Classification: redacted shareable report. Four disposable work directories were used across the
bounded diagnostic and final runs. All were destroyed after the fields below were extracted. Tox
savedata, stable identity keys, RecallRoot fixture phrases, authority ledgers, command stores,
runtime trees, and raw logs are not evidence artifacts.

## Inputs

```text
genuine-product-source-commit=fa8f871986f3d38e3fedad0b67941c9752ddccc2
lab-harness-commit=aa450adc4b7fa40be762c20357404a653c551830
final-validation-source-commit=178e1d56f12765b70158c0b2f7a24daeeee24923
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=729663ea43d4212fcef60ae198743c64d0cf71b777595c28dfccc9bd171e3876
provider=c-toxcore-0.2.23 source-linked
normal-route=tox/native using the pinned default bootstrap/relay catalog
tcp-only-route=tox/native using only the pinned default TCP-relay catalog
```

The standalone verifier passed and showed c-toxcore, libsodium, and Argon2 linked into the binary.
The current and successor fixture phrases were supplied only to separate short-lived CLI processes.
The controller and both daemons received public keys, exact prepared bodies, signed records, and
correlated results—not either phrase, RecallRoot, seed, or secret signing key.

## Deterministic and process gates

The warnings-as-errors suite proves:

- transition without an immediately preceding successor nomination is rejected;
- any intervening mutation consumes the nomination adjacency;
- skipped epoch, non-reset sequence, altered prior tail, wrong current claimant, same-owner
  nomination, and inactive or already-owner subjects fail closed;
- the current owner signs only the nomination, while the nominated successor signs the transition;
- transition advances the epoch once, resets sequence to 1, preserves the global record count and
  cross-epoch digest chain, and leaves exactly the successor owner live;
- old owners and delegates are unauthorized after the cut;
- exact nomination/transition replay does not append or advance the epoch;
- ledger replay reconstructs epoch 2 and its sole owner after restart;
- a claimant accepts a lexicographically newer `(ownership epoch, sequence)` challenge when the
  sequence legitimately resets to 1.

GCC debug, GCC Release, GCC with linked system Argon2, Clang 21 warnings-as-errors, ASan+UBSan with
leak detection, and TSan with race/deadlock halting passed all eight product CTest entries. The
Mutorr preservation configuration passed all ten entries and its combined 144-check registry.
Clang libFuzzer completed 5,000 executions on each of the frame, session, local-control, command,
and authority targets under ASan+UBSan. The fresh-process Agent/session stress gate passed 100/100
runs (`shard=1/131`).

The eighth process gate drives the real `iotox` CLI across a private control socket for remote
self-delegation, revocation, successor nomination, and successor-signed transition. It verifies each
returned signature independently against its reconstructed issuer and requires the signed record
body to equal the prepared body byte-for-byte. The final maintained-product coverage gate measured
70.3% lines (12,625/17,964), 87.5% functions, and 38.9% branches, satisfying the enforced 70% line
floor. The coverage tool now also rejects a disabled-instrumentation cache or missing matching
`gcov`; the narrowly ignored GCC 15 condition is its known negative branch-hit parse defect, not a
coverage exclusion.

## Diagnostic finding

The first bounded genuine run applied and replayed the exact transition at epoch 2 sequence 1, then
timed out awaiting the controller's new proof. Read-only projected-state inspection showed the
receiver correctly awaiting a proof while the claimant had rejected the new challenge as a
conflict. Its freshness rule required the same epoch and an increasing sequence, which excluded the
specified epoch increment plus sequence reset.

Commit `fa8f871` changed claimant freshness to compare `(ownership epoch, sequence)`
lexicographically and added the regression above. The diagnostic processes and private worktree
were then destroyed. Both complete genuine modes below passed with that correction.

The expanded final matrix also exposed an unrelated pre-existing observable-state race: concurrent
runtime snapshot publishers could capture generations in order and replace the status file in the
opposite order. A live incoming-request directory could therefore coexist with a stale
`pending-request-count=0` until another event. Commit `4595102` serializes snapshot capture and
projection and publishes the request count before journal I/O. The formerly intermittent full
144-check Mutorr runner then passed 20 consecutive executions, followed by TSan and the complete
matrix (`final-source-matrix=pass`).

After adding the CLI ceremony gate, commit `178e1d5` repeated the complete matrix on 2026-08-15:
all six product configurations passed 8/8 entries, Mutorr passed 10/10, every fuzzer completed its
5,000 executions, the coverage floor passed, and the exclusive Agent/session audit passed 100/100.

## Genuine native result

```text
real-peer-smoke=pass
peer-a-public-key-sha256=9fe1811f49220d1e3d16b7984c3517d8d422c67d95e927821caa640f414ecac8
peer-b-public-key-sha256=9eab8d78165ee73e29e9925d79b212f223ac57afba05f064f1f24836b289b289
session=canonical-hello-transcript-confirmed-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
ownership-epoch=successor-nominated-transitioned-exact-duplicate-replayed-at-epoch-2
phrase-compromise-cut=old-owner-denied-successor-reentered-and-redelegated
transport-mode=udp-and-tcp
initial-convergence-ms=15946
reconnect-convergence-ms=12010
peer-a-rss-kib=8764
peer-b-rss-kib=8744
peer-a-cpu-ticks=391
peer-b-cpu-ticks=79
peer-a-context-switches=2787
peer-b-context-switches=998
peer-a-open-fds=35
peer-b-open-fds=35
protocol-journal-bytes-proxy=12220
persistent-tox-savedata-bytes=11823
```

## Genuine TCP-only result

The exact provider-ABI gate independently requires UDP, local discovery, DHT announcements, and
hole punching to be disabled. The same complete ceremony passed through configured TCP relays only:

```text
real-peer-smoke=pass
peer-a-public-key-sha256=bf9a91ce4db3b3ab46bcc7e3d189ee4b308037f9b53ba389cd2fe8dc1857261d
peer-b-public-key-sha256=bb07d66c57014d2a390886995f4c066eb925f383bf4459426b17d6006baeb4f3
session=canonical-hello-transcript-confirmed-both-directions
owner-reentry=denied-device-then-recalled-owner-proof
self-delegation=owner-role-denied-applied-exact-duplicate
remote-revocation=applied-exact-duplicate-and-inactive-after-restart
delegation-restart=revoked-controller-recalled-and-redelegated-at-sequence-4
ownership-epoch=successor-nominated-transitioned-exact-duplicate-replayed-at-epoch-2
phrase-compromise-cut=old-owner-denied-successor-reentered-and-redelegated
transport-mode=tcp-only
initial-convergence-ms=56782
reconnect-convergence-ms=84081
peer-a-rss-kib=8540
peer-b-rss-kib=8180
peer-a-cpu-ticks=1500
peer-b-cpu-ticks=70
peer-a-context-switches=12915
peer-b-context-switches=4156
peer-a-open-fds=34
peer-b-open-fds=34
protocol-journal-bytes-proxy=12104
persistent-tox-savedata-bytes=6402
```

CPU ticks and context switches are cumulative host observations at one sample point. Protocol
journal bytes are an application-frame proxy, not wire-traffic measurement. These values are
observed baselines rather than acceptance budgets.

## Claim boundary

This closes M4 owner re-entry, delegation, delegated-controller revocation, planned transfer, and
successor-signed ownership-epoch transition for the official IoTox tool and named pinned provider.
A completed cut blocks future authority from the retired phrase and every old-epoch delegate. It
does not undo prior effects, defeat a pre-cut race by another holder of a compromised current
phrase, detect rollback to an older complete valid ledger, recover after every owner secret is lost,
provide remembered route discovery, cover every relay/censorship environment, establish independent
reproduction, or imply production readiness. Cross-client compatibility is intentionally outside
this repository's acceptance scope.
