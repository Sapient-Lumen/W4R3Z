# portfolio-envelope-v0 fixture lane

This directory holds **negative fixtures** for the archive's shared portfolio-envelope checker.

Positive examples live in:
- `specimens/portfolio-envelope-v0/`

Negative fixtures live here because the archive now wants to prove not only that honest examples pass, but also that common posture failures are actually rejected.

Current invalid fixtures:
- `invalid/invalid-canonical-pack-lossy.example.json`
- `invalid/invalid-routed-brief-no-escalation.example.json`
- `invalid/invalid-lineage-child-no-parent.example.json`

Review rule:
- if shared role minimums change, refresh the affected invalid fixture in the same revision;
- if a new hard rule is added, add at least one negative fixture that should fail for that reason;
- and do not move positive specimens into this directory unless they are intentionally being turned into failure cases.
