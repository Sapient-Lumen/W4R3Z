# CELL-161 — Native Audit and Build Hygiene

Priority: **P0**  
Status: **candidate-with-runnable-audit**

## Question

Can the cube stay openable and reproducible while carrying compiled probes?

## Cheap first run

Runnable native audit emits REV0013_NATIVE_PROBE_AUDIT.json/md.

## Metrics

- audit pass/fail
- compiled probe count
- binary absence
- JSON output presence

## Stop condition

If native artifacts make the cube brittle or opaque, restrict to source-only notes.
