# rev0074 revision summary

## Problem resolved

Rev0074 re-audits PB-01 against the exact current `3.3.x` source and upstream history. The old packet joined direct `PeerInit` replacement and secondary-socket promotion, then selected a blanket established-primary guard because a fixed regression turned green.

That decision was unsafe. The demonstrated secondary is created by a valid locally tokened direct/indirect race. Upstream deliberately retained such connections to repair SoulseekQt compatibility and immediately added promotion when the retained socket carries traffic. A new two-peer test shows the rev0038 guard can make the two peers choose opposite TCP legs.

## Disposition

```text
PB-01A / U-168: observed direct-over-direct replacement remains open protocol-hardening research
PB-01B / U-176: retired as a defect on current evidence
rev0038 patch: superseded experiment
rev0074 origin-aware patch: narrower experiment, not selected
private security route: unsupported
```

## Validation

```text
exact source ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
source invariants: 7/7
classified expectations: 12/12
isolated upstream units: 58 passed, 1 skipped in all three states; i18n excluded because msgfmt is unavailable
```

## Cube refactor

Two duplicated policy-mixed tests (924 lines / 33,838 bytes) were replaced on the active surface by a shared harness and four role-specific tests (436 lines / 12,870 bytes). Originals remain archived. A current packet ledger and deterministic status audit now classify historical “production-ready” and patch-stack artifacts as superseded rather than silently active.

## Boundary

No patch is recommended for upstream use. All material is research-only and must be independently recreated by a human under the project's contribution rules.
