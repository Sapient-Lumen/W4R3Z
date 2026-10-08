# Case-contract and route-test-harness routing

## Question in one sentence

When a golden case names an expected route, how does the archive prove that the route, axes, remedy profile, flags, and prohibited shortcuts are all still connected after later edits?[S21][S27][S59][S594]

## Rule

A golden case is not merely an example. It is a contract for the cube answer. Each case must be reducible to a machine-readable obligation:

1. **Route obligation** — the case must name the route records that should fire.
2. **Axis obligation** — any raw case axes must use values that exist in the cube schema.
3. **Flag obligation** — expected flags should be route-backed anti-patterns, review triggers, proof postures, burden mechanics, remedy types, or floor risks rather than decorative prose.
4. **Remedy obligation** — each expected route must have a remedy profile so the case can test the corrective move, not only the classification label.
5. **Negative-answer obligation** — each case must say what an answer must not do, so regression review catches tempting shortcuts.

This pass sits after route selection and before final prose. If the route fires but the answer loses the axis, remedy, flag, or forbidden-shortcut obligations, the answer is not contract-compliant.

## Ordering rule

Use the case-contract pass after the ordinary decision procedure has selected candidate routes. The pass does not replace moral judgment. It gives the archive a regression surface: when a future edit changes route IDs, flags, source posture, or remedy profiles, the golden case fails visibly rather than drifting silently.

## Contract families

| Contract surface | What it tests | Failure mode |
|---|---|---|
| expected routes | whether the correct route records fire | answer chooses a nearby route and misses the seam |
| raw axes | whether case facts are expressible in the cube schema | prose uses terms the machine layer cannot validate |
| expected flags | whether the flagged harm is visible in route semantics | case says `hidden tax` while the route only says generic risk |
| remedy profiles | whether a route can say what corrective move follows | route classification survives but remedy disappears |
| must-not answers | whether common bad answers are blocked | answer repeats the exact shortcut the case was written to prevent |

## Machine surface

The companion machine layer is [`../00-meta/case-contracts.json`](../00-meta/case-contracts.json), validated by [`../../tools/audit_case_contracts.py`](../../tools/audit_case_contracts.py). The contract layer is intentionally separate from `golden-cases.json`: the prose case states the scenario, while the contract states the obligations an answer must satisfy.

## Source IDs only

[S21][S27][S59][S594]

[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S59]: ../../SOURCES.md#S59
[S594]: ../../SOURCES.md#S594
