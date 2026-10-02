# Sandwurm mutable profile-status evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently granted each other exactly
`write.settings`, proved current remote authority, issued one durable `profile.status.set busy`, and
converged their real c-toxcore presentation state over observed direct UDP and forced TCP. Both roles
retained the exact successful outgoing and incoming command records. Each incoming `IPS1` result
bound desired busy, provider-observed busy, convergence true, and ownership epoch 1.

The guest harness retries only transient pre-admission CLI failure. Once one durable command is
admitted, it follows that exact sender epoch and message identifier to terminal truth; it never
creates a substitute command.

## Accepted compact cells

| Route | Compact proof | Span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.rqrsf6t9` | 297,202,671,180 ns | `45ce1f156debf6b828a5db1f60cc0fa569a99570bbe874be8b648ad57c0b3d0d` | `07dd76d3596f2124b3a0c5d907636ffcad7950c5ab5feca435e993b063713e9d` |
| forced TCP | `.sandwurm/exports/pairs/pair.59kegxle` | 285,458,392,413 ns | `48383c948b132de98fe341dad74026ae8e4a4913580ddf05d96d964ac6c0eb1c` | `8d73b59bcb3962a8a999207703a4c9f7a020cf40e62c531423662f838b9db516` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates
122,880 bytes. Both cells bind production binary
`149038ddde0e62c4d6b1cc2884cc6254c061f6b1d36ea2c3a5c3369575f192aa`.
The pair manifests record `mutable_profile_convergence=true`, two authorized roles, and two
converged roles.

The UDP client/device receipt SHA-256 values are
`93f1bc1815e47386453b356c029d5cfabee26d47c2daf4939e963fbffbceca80` and
`308319e01df009846b3cdfd390ea559e3323947023357701026d72d154f3a66a`;
the TCP values are
`8633cd548369b83753ed56c8179c30e7834b08a2ff32d1493d5a21dab91c69fc` and
`f6e4aabf29bf6d076c9f4a66c8c56ab60218b8bf1cc5bdd32da5f62ca28d60a6`.

Qualification also exposed a fail-closed authority ordering race: a proof already queued for the
bootstrap ledger head could arrive after the immediately following grant invalidated its challenge,
and the verifier previously poisoned the replacement round as malformed. The verifier now rejects
that old-head proof as unavailable while remaining `challenge-ready`; a fresh nonce, message ID, and
exact-head challenge/proof round is required. A deterministic registry gate freezes the behavior,
and both accepted carrier cells exercise the same bootstrap-then-grant schedule.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp mutable-profile-status
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp mutable-profile-status

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.rqrsf6t9 \
  --route direct-udp --scenario mutable-profile-status
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.59kegxle \
  --route forced-tcp --scenario mutable-profile-status
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and removed after the compact exports independently passed. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This is one three-valued Tox presentation mutation in each direction, under ownership epoch 1, on
one construction host and one pinned provider version. It proves remote capability separation,
durable command/result convergence, real provider readback, and both supported carrier modes. The
separate process gate—not these VM cells—proves recovery from the post-effect/pre-savedata window.

It does not prove physical output, representative hardware, media/power-loss durability,
rollback-resistant command storage, permanent presence, target timing, multiple mutations,
two-physical-host behavior, or any safety-critical effect. ADR 0148 freezes the interpretation.
