# ADR 0233: Qualify late native bounded-range loss

Status: accepted genuine direct-UDP/forced-TCP Sandwurm qualification, 2026-08-29.

## Context

ADRs 0231 and 0232 establish exact-prefix continuation after one and two native auxiliary-carrier
deaths, but their genuine faults occur around the first quarter of a 1 MiB range. Near completion,
the old attempt can race final transport completion, terminal delivery, route retirement, prefix
inspection, and reassignment. That boundary needs its own evidence rather than inference from early
loss.

The first 15/16-threshold run used the ordinary 4 Mbit/s prerequisite rate. It was correctly rejected:
the final 64 KiB completed between qualification observations, so no fault occurred. This showed
that a threshold alone does not make a late event observable.

## Decision

- Add the distinct `sync-file-range-late-route-loss` Sandwurm cell without changing product code or
  frozen framing.
- Select the exact 1,048,576-byte range bundle and arm one fault at 983,040 bytes (15/16). Keep the
  4 MiB basis/prerequisite path at 4 Mbit/s, then shape only the selected range at 256 kbit/s so the
  threshold is observable by the existing default-off fault seam.
- Bind both threshold and rate into the pair manifest. The strict verifier requires a fault position
  at or above 983,040 and strictly below 1,048,576.
- Reuse ADR 0231 unchanged: finish/fence the old signed attempt, hide its FileId, validate the exact
  strict prefix, allocate a fresh attempt/message/FileId on the other authenticated carrier, seek,
  receive only the suffix, and require full digest/HEAD-last/explicit-activation checks.
- Require one loss, reassignment, stale-terminal fence, recovery, retained attempt, and resumed
  attempt; retained bytes equal resumed bytes; discard, fallback, final partials, range retry, and
  qualification request hold remain zero.

## Evidence

Both accepted cells use source revision `5d6358aa23f96cf146aaa18411bfe9b685683df2`, product revision
`rev0045`, and binary SHA-256
`88093a006d9a9e0bedb7af6be5ed3efb47399279a289c7b7c44eb86748257bca`:

| Route | Compact proof | Fault = retained = resumed | Remaining suffix | Span |
|---|---|---:|---:|---:|
| direct UDP | `pair.tev4u3rs` | 984,378 bytes | 64,198 bytes | 438,453,698,922 ns |
| forced TCP | `pair.1z7_d0jn` | 995,346 bytes | 53,230 bytes | 498,230,171,154 ns |

Each cell fetches one exact 1 MiB range, reuses 3 MiB of verified basis, reconstructs the same exact
4 MiB artifact, accepts the linked generation-2 signed HEAD last, explicitly activates it, and
recovers the stopped savedata identity. Both 155,648-byte compact exports pass the strict verifier.

## Consequences

Native available-policy range continuation is now genuinely qualified for one loss both near the
first quarter and after at least 15/16 of the bundle, plus a separate two-loss early/mid-transfer
sequence. Late completion does not require retransmission or weakening stale-attempt fences.

This does not prove a fault in the final transport chunk, a fault after remote completion but before
local terminal processing, repeated late faults, randomized thresholds, process
or guest restart, explicit-new-job prefix reuse, cross-class migration, fail-closed I2P continuation,
Tor-to-Tor continuation, concurrent multi-source striping, two physical hosts, or performance gains.
ADR 0235's separately wired early/mid-transfer three-loss gate does not widen this late-loss claim.
