# TimeSync — rev0001

## What this is

This first revision is intentionally small.

It does **not** define the full TimeSync system.
It does **not** assume TimeSync should be a new wire protocol.
It does **not** lock in a final ontology or architecture.

Instead, it creates a minimal foundation for asking the question:
**what should TimeSync actually be?**

This bundle is a research-grounded starting point for a longer design process.

## What this revision tries to do

1. Frame the problem honestly.
2. Capture the strongest external signals from current standards and practice.
3. Record only the smallest set of decisions that already seem justified.
4. Preserve a live frontier of unanswered questions.
5. Leave room for TimeSync to become the right thing, rather than forcing it too early into the wrong shape.

## Current best guess

After initial research, TimeSync looks less like "a replacement for NTP/PTP" and more like a system for making time synchronization:

- legible,
- risk-bounded,
- provenance-aware,
- uncertainty-bearing,
- and governable across multiple underlying mechanisms.

That is a direction, not yet a verdict.

## Fast path

Open these first:

- `START_HERE.md`
- `PROBLEM-LANDSCAPE.md`
- `DECISION-MEMO.md`
- `OPEN-QUESTIONS.md`
- `frontier-ticket.json`

## Revision theme

**problem frame before protocol**
