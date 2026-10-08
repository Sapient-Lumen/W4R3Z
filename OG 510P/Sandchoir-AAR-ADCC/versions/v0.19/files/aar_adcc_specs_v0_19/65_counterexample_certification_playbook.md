# 65 — Counterexample Certification Playbook (v0.19)

You said: agents should be able to vote on allowing specific counterexamples, and “prove the counterexample” should be strongly weighted.
But tooling varies per project; we need a generic playbook.

Key principle:
A counterexample is only “strong” if it is **replayable** by others with a bounded recipe.

## 1) CE# object (generic)
Fields:
- `claim_ref`: C# / P# / CFG# it refutes
- `witness`: input / scenario / seed / file / minimal repro
- `repro_kind`: test|property|script|proof|build|trace
- `repro_recipe`: verifier name + args OR EXEC# with timeout class
- `expected_signal`: 1–2 lines (e.g., “unit_fast fails at X”)
- `status`: proposed|certified|contested|superseded

## 2) Certification levels (cheap to expensive)
- Level 0: “plausible” (witness exists, recipe described, not run)
- Level 1: “replayed once” (someone ran it, produced E#)
- Level 2: “stable” (replayed by 2 agents or cached, not flaky)
- Level 3: “minimal” (witness minimized, stable, easy to run)

## 3) What counts as “prove the counterexample”
In this system: certification Level >= 1.
Because we can’t assume theorem provers.
If you *do* have a proof engine:
- proof scripts can be a repro_kind too (Level 1 = script checks)

## 4) How CE interacts with votes
Default rule:
- any certified CE automatically promotes to HOT (global)
- patch selection must address certified CE before moving on (Gatekeeper mode)
- integrator must either:
  - apply a patch that resolves it, or
  - explicitly mark it “explained away” with evidence

## 5) “Vote to allow counterexample”
You can interpret this as:
- vote to allocate check budget to certify it (checks vote)
- vote to include it in mandatory view sections
Not as “vote to ignore evidence.” Evidence still moves votes.

## 6) CE minimization as a task
Minimization is a first-class deliverable:
- create T# “minimize CE#”
- success: smaller witness or simpler repro recipe
