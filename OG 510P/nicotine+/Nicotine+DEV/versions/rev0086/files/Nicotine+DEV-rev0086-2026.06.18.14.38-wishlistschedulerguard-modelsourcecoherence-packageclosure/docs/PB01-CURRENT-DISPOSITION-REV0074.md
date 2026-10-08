# PB-01 current disposition — rev0074

## Decision

PB-01 was one label for two different state transitions. They do not survive current review as one defect.

| Split | Current-source observation | Reachability actually demonstrated | rev0074 disposition |
|---|---|---|---|
| PB-01A / U-168 | A later incoming direct `PeerInit` for the same username and P/D type replaces the mapped connection, migrates queued messages, and closes the prior socket. | A peer can send a `PeerInit` claiming that username/type. The protocol supplies no authenticated connection generation in this message. | Keep as public correctness and protocol-hardening research. No selected patch; stronger security impact unproven. |
| PB-01B / U-176 | Post-init traffic on a secondary connection sharing an existing `PeerInit` promotes that socket to primary. | The executable path uses a valid, locally issued indirect token while direct and indirect attempts race. | Retired as a defect on current evidence. It is intentional compatibility/failover behavior in the demonstrated path. |

The old rev0038 blanket established-primary guard is **superseded**, not selected. It turns a reachable simultaneous race into split-brain: one peer can retain the direct leg while the other retains the indirect leg. Passing tests written to enforce that guard did not establish that the policy was correct.

## Exact-current result

```text
source lane: github-branch-3.3.x
source ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
source invariants: 7/7 pass
classified source-state/test-role expectations: 12/12 pass
isolated upstream units: 58 passed, 1 skipped in baseline, rev0038, and origin-aware lanes; the msgfmt-dependent i18n file was excluded because msgfmt is unavailable
selected patch: none
private security route: not supported by current evidence
```

The three source states are deliberately interpreted, rather than ranked by raw pass count:

| State | Current witnesses | Race compatibility | rev0038 counterexample | Origin-aware experiment |
|---|---:|---:|---:|---:|
| Baseline | 2 pass | 1 pass | 1 expected fail | 2 pass / 1 expected fail |
| rev0038 blanket guard | 2 expected fail | 1 expected fail | 1 pass | 1 pass / 2 expected fail |
| rev0074 origin-aware experiment | 1 pass / 1 expected fail | 1 pass | 1 expected fail | 3 pass |

An expected failure is evidence about policy discrimination; it is not a broken gate. The machine-readable matrix is `data/rev0074_pb01_test_matrix.csv`.

## Why PB-01B changes status

The modern protocol attempts direct and indirect peer connections concurrently. A valid `PierceFireWall` response can therefore arrive after a direct socket is established. Current code intentionally keeps that secondary open because some clients send on it. The immediately following upstream change added promotion when the secondary actually carries a message.

The history is unusually probative:

```text
34b442a (2024-01-16): be less aggressive when rejecting indirect connections;
                       explicitly fixes connectivity with some SoulseekQt users,
                       related to issue #2829.
4932ef9 (2024-01-17): replace init socket when necessary;
                       promotes the secondary carrying post-init traffic.
```

The rev0038 suite manufactured the shared-`PeerInit` state but did not prove an arbitrary remote path into it. The actual current path is locally authorized by a token generated for the direct/indirect race. That distinction invalidates the old attacker-only interpretation.

## Why PB-01A remains open

The direct-over-direct transition still deserves design attention: `PeerInit` names the peer, but the message does not establish a cryptographic identity or a connection generation. A blanket “first established wins” guard is not enough:

1. the first claimant is not authenticated by the guard;
2. a stale or half-dead first connection can become sticky;
3. legitimate reconnect and simultaneous-open behavior remains unspecified;
4. queue ownership is migrated before any application-level proof of freshness.

Rev0074 includes a narrower origin-aware experiment that rejects direct-over-established-direct while still allowing a direct connection to supersede an outgoing indirect response. It is a useful executable question, not a selected fix. It has no integration proof for stale sockets, reconnects, mixed-client behavior, or peer identity.

## What would change the disposition

PB-01A can advance only after an explicit election policy is stated and tested. A useful design likely needs a connection origin, request token/generation, liveness, and deterministic tie-breaker rather than a single `is_established` bit.

PB-01B should reopen only if a test demonstrates a harmful secondary promotion outside the valid locally tokened race—for example, a remote path that binds an unrelated socket to the same live `PeerInit` without possession of the outstanding token.

## Research boundary

All generated code, tests, patches, and prose in this cube are research-only. Historical files with names such as `PRODUCTION-READY` or `SELECTED-PATCH` record an earlier cube judgment; they are not current recommendations. `data/current_packet_dispositions.json` is the current machine-readable authority.
