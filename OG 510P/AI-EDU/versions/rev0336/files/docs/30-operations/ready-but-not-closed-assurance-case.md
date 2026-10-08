# Ready-but-not-closed assurance case

The archive now supports a precise late-stage claim:

> This release can ship as an internally consistent, handoff-safe,
> ready-but-not-closed archive while preserving `FT-0181` as externally
> gated on real pilot evidence.

This is weaker than completion and stronger than a loose draft. The
assurance case records the argument and the evidence paths that support
that bounded claim.

## Claim structure

| Claim | Supported by | Limit |
|---|---|---|
| release can ship | lint, release candidate, audit manifest | does not close `FT-0181` |
| real import is ready to receive data | request, dictionary, import map, acceptance, closeout workflow | no real packet yet |
| examples are non-evidence | synthetic declaration and no-fake guard | examples may still guide design |
| public summaries are bounded | redaction profiles and render smoke tests | human publication review still required |
| no hidden waiver explains the gap | policy-exception register | future waivers need records |
| handoff is safe | operator handoff and lifecycle records | next maintainer must still review |

## Assurance states

| State | Meaning |
|---|---|
| `AC0` | no assurance case |
| `AC1` | draft argument only |
| `AC2` | evidence paths exist and live queue is named |
| `AC3` | reviewer-checked assurance before real import |
| `AC4` | closure-ready assurance after real import |
| `ACX` | invalidated or overclaiming |

## Evidence discipline

An assurance case should not quote a surface as proof of its own outcome.
For example, a public-summary surface can prove that a notice template
exists; it cannot prove learning, safety, accessibility, or workload
benefit. A schema can prove field shape; it cannot prove truth.

For `FT-0181`, the assurance case must continue to say `externally_gated`
until a source packet is `SRC2+`, reviewer calibration passes, public
renders are safe, lifecycle decisions are made, and closeout-board minutes
permit closure.

## Closeout rule

The assurance case may move from `AC2` to `AC4` only when all of these are
true:

1. `FT-0181` is the only item changing state;
2. an `SRC2+` source packet exists;
3. import-readiness and acceptance records are closure-ready;
4. service records and public summaries pass validation;
5. lifecycle and closeout records permit closure;
6. the decision-delta log explains every field kept, trimmed, or added;
7. no active policy exception bypasses the evidence threshold.
