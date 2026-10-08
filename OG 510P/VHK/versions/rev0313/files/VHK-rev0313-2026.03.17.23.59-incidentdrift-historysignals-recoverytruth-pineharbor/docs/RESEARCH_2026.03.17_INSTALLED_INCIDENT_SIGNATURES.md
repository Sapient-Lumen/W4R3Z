# Research note — installed incident signatures

## What Linux tooling is teaching here

- `ExecCondition=` is a skip/failure hybrid: exit codes 1–254 skip the rest of
  startup without marking the unit failed, while abnormal/255 failures do count
  as failures.
- `systemctl show` is the structured surface for unit state, including
  `Result`, `ConditionResult`, `NRestarts`, and related state that support
  lightweight classification.
- `journalctl -o json` gives machine-readable recent journal entries, which is a
  better fit for status/support artifacts than scraping human-oriented output.

## Design consequence for VHK

VHK should not collapse every bad-looking installed-lane state into "service
failed". The installed status surface should preserve a compact incident class
plus a short journal sample when possible, then let heavier dossier/rehearsal
paths collect more evidence later.
