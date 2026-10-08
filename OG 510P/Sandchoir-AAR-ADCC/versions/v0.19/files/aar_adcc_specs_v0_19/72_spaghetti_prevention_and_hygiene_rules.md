# 72 — Spaghetti Prevention + Hygiene Rules (v0.19)

This doc is not about “security”; it’s about preserving ergonomics under high trust.

## 1) Primary spaghetti sources
- unbounded prose in WS
- ad-hoc commands without pointers or expected signals
- patches applied without checks
- multiple agents editing the same file without leases/integrator
- protocol elections mid-run
- REQ backchannel creep

## 2) Hygiene rules (default)
- WS is structured only; prose goes to ledger.
- Every patch proposal must include verifier intent.
- Canonical apply is integrator-only.
- Ad-hoc exec must be tied to EXEC# and has a timeout class (53_).
- REQ caps + TTLs are enforced.
- Compaction is triggered early, not late.

## 3) Worktree discipline
- Agents do “messy work” in their worktree (54_).
- Export patches; don’t push half-done changes into canonical.
- If repeated conflicts: turn on PatchOnly + rerere (70_).

## 4) MetaLLM role
MetaLLM watches hygiene metrics:
- WS size trends
- unstructured leakage attempts
- exec spam attempts
- evidence density
And nudges:
- mode changes
- compaction
- budget shrink

## 5) The one rule that saves you
If you do only one thing:
- **require CTRLJSON first** and keep views bounded.
Everything else can be refined later.
