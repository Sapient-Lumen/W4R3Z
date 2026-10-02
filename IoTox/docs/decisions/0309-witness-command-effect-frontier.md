# ADR 0309: Witness the durable mutable-command effect frontier

- Status: accepted and implemented for the opt-in command-effect lane
- Date: 2026-09-02

## Context

IoTox commits an incoming durable command through `RECEIVED`, `ADMITTED`, and `STARTED` before a
mutable provider operation. That ordering makes an ordinary crash recoverable, but a storage
attacker can restore a complete older command journal and erase the durable fact that an effect was
already started. A later authorized recovery could then treat the old request as new.

Witnessing every diagnostic, retry, or result-delivery write would create needless high-churn
external state and still would not name the security event that matters. The boundary is the exact
authorized command identity at `STARTED`, before the provider or update store is touched.

## Decision

Add a separately enrolled `command-effect` witness lane. Its canonical frontier contains every
retained incoming non-read-only command that has crossed `STARTED`. Each entry length-binds the
sender Tox key, sender epoch, message ID, operation, proven application principal, ownership epoch,
authority sequence, and exact canonical request. Sorting is by durable command key. Timestamps,
outcome/result bytes, delivery attempts, and read-only commands do not enter the digest.

`iotox witness-command-effects-enrollment --config PATH` binds the current frontier to position one
or to the exact already signed local checkpoint. It requires an existing authenticated command
store and the complete remote-witness selection. With `--witness-command-effects`, startup verifies
that frontier against the service before startup incarnations or RuntimeTree.

For a live mutable command, the Agent:

1. commits its exact principal, authority head, and `STARTED` lifecycle to the signed command store;
2. recomputes the complete effect frontier;
3. advances that digest through the generic durable-intent and authenticated pending/committed CAS;
4. only after the external commit is resolved, calls `profile.status.set` or `update.stage`; and
5. may change result/delivery state without moving the effect witness.

If the service is unavailable or disagrees, no provider/update effect is attempted. A crash after
the witness commit but before or during the effect retains the existing command recovery rule: only
operations explicitly classified as idempotent desired state may run again. This mechanism does not
claim exactly-once physical effects.

Effect-bearing terminal records are excluded from ordinary bounded-history pruning while the lane
is enabled. This makes whole or selective restoration of an older command journal change the
frontier and fail startup. It also makes the configured command-record ceiling a deliberate lifetime
effect-history ceiling: when no non-effect terminal record can be pruned, new work fails closed.
Compaction requires a future witnessed checkpoint protocol and is not improvised here.

The default checkpoint is `COMMAND_STORE.effect-witness-checkpoint`; its intent is beside it. Both
are part of protected-state closure. Diagnostic structural commitment v6 exposes only whether the
lane is required.

## Consequences

One owned check brings the direct registry to 782. It proves that received/read-only/result churn
does not move the frontier, `STARTED` does, terminal delivery preserves the same digest, and ordinary
pruning retains an effect identity while removing eligible read-only history. The generic policy
witness tests already cover explicit digest advancement, whole-local rollback refusal, both lost-
reply recovery joins, and same-domain refusal. The two-guest service gate enrolls and starts the
source-linked Agent with all six lanes through the actual authenticated TCP service.

The lane protects only durable IoTox command effects. It does not cover direct Ratox shell actions,
local administration outside IoTox, a compromised live process/kernel, or rollback of the witness
service itself. Production still requires a separately administered, rollback-resistant or
independently checkpointed witness. Sync guarded state remains separate; ADR 0311 subsequently
witnesses update policy and lifecycle-state freshness.
