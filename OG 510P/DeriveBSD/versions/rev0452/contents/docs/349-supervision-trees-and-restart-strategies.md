# Erlang/OTP lesson: supervision trees as explicit restart contracts

Erlang/OTP’s reliability story is not magic; it’s *discipline*:
**processes are expected to die**, and the system makes “what happens next?” explicit via a **supervision tree**.

DeriveBSD already wants:
- typed service ownership (`docs/235-process-contracts-and-service-ownership.md`)
- SMF-style lifecycle (`docs/239-service-lifecycle-restarters-and-repo.md`)
- restart budgets + receipts (`docs/342-minix-self-healing-and-reincarnation.md`)

This doc steals the OTP supervisor semantics as a *clean vocabulary* for DeriveBSD’s restarter layer.

## What to steal (tight set)

1) **Tree topology is policy**
- a supervisor owns children
- ownership implies restart authority
- the tree is *the* escalation path

2) **Restart strategy is explicit**
OTP’s classic strategies map cleanly to DeriveBSD:
- **one_for_one**: restart only the failing child
- **rest_for_one**: restart the failing child + the children started after it (dependency order)
- **one_for_all**: restart all siblings when one fails (shared fate)
- **simple_one_for_one / dynamic**: spawn many similar workers under one policy

3) **Maximum restart intensity**
A supervisor defines a *rate limit* (“N restarts in T seconds”).
If exceeded, the supervisor *fails closed* (it terminates), forcing escalation up the tree.

4) **Child restart types**
- **permanent**: always restart
- **transient**: restart only on abnormal exit
- **temporary**: never restart (one-shot jobs)

## DeriveBSD adaptation

### 1) Compiled supervision graphs
A `derive.unit` (or service bundle) should compile into a **supervision graph**:
- supervisors are services with the *authority to restart*
- edges are typed “owns/depends-on” relationships
- each node carries: strategy, intensity, restart type, shutdown timeout, and escalation class

This graph becomes part of the compiled `svcdb` surface (`docs/173-compiled-service-database-bundles.md`).

### 2) Restart as evidence (receipts everywhere)
Every restart attempt should emit a typed receipt:
- why did we restart (exit status, watchdog, health gate)?
- which supervisor authorized it?
- what budget did we spend?
- what state dataset(s) were involved?

This plugs into the evidence spine (`docs/229-evidence-spine-overview.md`).

### 3) Escalation paths that don’t become footguns
When restart intensity is exceeded:
- **default**: mark service as *failed*, stop restarting, emit alarm receipt
- **optional**: restart the supervisor (higher-level decision)
- **never**: infinite flapping without an evidence trail

Escalation actions should themselves be policy decisions (PDRs) (`docs/93-policy-decision-records.md`).

## Concrete contract surface (proposal)

Add a small schema (either in `spec/` or as fields inside `derive.unit` compilation):

- `restart.strategy`: one_for_one | rest_for_one | one_for_all | dynamic
- `restart.intensity`: {max_restarts, period_seconds}
- `restart.type`: permanent | transient | temporary
- `restart.backoff`: {min_ms, max_ms, jitter_pct}
- `restart.escalation`: {quarantine | alarm_only | reboot_domain | reboot_host} (policy-gated)

## Why this matters for DeriveBSD

OTP’s semantics give us:
- a **shared mental model** (no bespoke restarter folklore)
- a **small vocabulary** that can be linted
- a **measurable** flapping story (restart intensity + receipts)
- a coherent bridge from “service supervision” → “authority budgets” (`docs/298-authority-budgets-and-permission-drift-alarms.md`)

## References
- Erlang/OTP design principles: Supervisor Behaviour: https://www.erlang.org/doc/system/sup_princ.html
- Erlang/OTP stdlib: supervisor module reference: https://www.erlang.org/doc/apps/stdlib/supervisor.html
