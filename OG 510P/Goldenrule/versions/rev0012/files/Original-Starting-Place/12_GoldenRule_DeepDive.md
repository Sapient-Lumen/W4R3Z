# Golden Rule — Deep Dive (formal lenses, pitfalls, and spec implications)

This document is a **concept map**: it translates “Golden Rule energy” into testable desiderata and world features.

Concord is pluralist: “Golden Rule” is a family of norms. We should expect tensions:
- between mercy and justice,
- between universal rules and context sensitivity,
- between role-reversal and preference diversity,
- between short-run cooperation and long-run resistance to exploitation.

## 12.1 Canonical formulations and what they imply

### (A) Positive Golden Rule (“do unto others…”)
Implication: pro-social action; encourages initiating cooperation.

Engine mapping:
- strategies must be capable of *initiating* cooperation in uncertain worlds (not only reacting).

### (B) Negative / “Silver Rule” (“do not do…”)
Implication: restraint, non-harm; avoids many pathologies of naive role-reversal.

Engine mapping:
- metrics must include harm floors (do not drop the other below a reasonable baseline without justification).

### (C) The “sadist” / preference mismatch objection
If someone likes pain, role-reversal can recommend harming others.
This motivates “negative” formulations, and motivates preference inference.

Engine mapping:
- include a “preference diversity” world suite where what counts as “benefit” differs.
- score strategies on avoiding harmful projection.

## 12.2 Role-reversal is not the same as empathy
“Imagining yourself in another’s shoes” can differ from “extending concern.”
Role-reversal can misfire when preferences differ or are strategically misreported.

Engine mapping:
- include “platinum worlds”: agents have heterogeneous utility and can communicate preferences (truthfully or deceptively).
- evaluate “platinum-mode” ability: infer what the other values, but under security constraints and deception tests.

## 12.3 Universalization: “my maxim, applied to all”
Golden Rule often has universalization flavor: would I endorse a world where this is the rule?

Engine mapping:
- self-play and population-level tests are not just optional; they are core universalization probes.
- add “universalization regret”: how far is the universal outcome from the best universal outcome in the same world.

## 12.4 Contractualism / justifiability (proxy)
A closely related moral idea: actions should be justifiable to others; wrongness tracks principles others could reasonably reject.

Engine mapping:
- add a “complaint score”: how often do you impose losses on cooperative partners beyond a reasonable floor?
- require an auditable reason-trace: actions should be explainable by stable rules.

This is NOT full contractualism. It is a conservative proxy to prevent obviously indefensible strategies.

## 12.5 Restorative justice and “healing the sickness”
A Golden Rule–like practice often aims at repair and reintegration, not only deterrence.

Engine mapping:
- create “restoration worlds” with apology/repentance opportunities.
- measure restoration efficiency: how quickly can mutual cooperation be rebuilt after harm without enabling repeated abuse?
- model “reintegration” mechanics (e.g., reputation repair over time, or after costly apology).

## 12.6 Forgiveness as a dynamic, not forgetting
Past harm should decay in relevance, but not vanish instantly.

Engine mapping:
- implement strategies with a “harm debt” variable that decays (recentness weighting).
- define `grudge_half_life` as a core metric.
- distinguish:
  - *forgiveness* (de-escalation under evidence of change),
  - *naivety* (unconditional reset exploitable by fake contrition).

## 12.7 Justified defection: standing vs image scoring
Indirect reciprocity suggests norms that treat defection differently depending on whether it is justified.

Engine mapping:
- include reputation norms where “justified defection” does not damage standing.
- test strategies’ ability to punish exploiters without becoming “bad” under the norm, under noisy/private info.

## 12.8 Golden Rule is not self-sacrifice
A core constraint: a rule that makes you systematically exploitable is not stable and will not survive adversarial worlds.

Engine mapping:
- include extortion sweeps and “mercy harvesting” opponents in red-team.
- require a security floor vs AlwaysD-like families.

## 12.9 Implications: what we should expect to discover
Under these lenses, “best Golden Rule strategies” are likely to be:
- **nice but not naive**,
- **forgiving but not forgetful**,
- **intention-calibrated** under noise,
- **institution-aware** (reputation, exit, repair channels),
- and **resource-efficient** (bounded compute).

They may look like a hierarchy:
- default cooperative mode (build trust),
- suspicion mode (diagnose noise vs hostility),
- justice mode (proportionate response),
- restoration mode (repair after repentance),
- exit mode (leave persistent exploitation).
