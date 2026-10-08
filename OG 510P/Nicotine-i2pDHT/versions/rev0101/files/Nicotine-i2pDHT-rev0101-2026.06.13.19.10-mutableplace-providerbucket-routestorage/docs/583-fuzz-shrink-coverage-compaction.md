# Fuzz shrink coverage compaction

`fuzzshrink.py` treats test-corpus reduction as a safety boundary. A smaller corpus is useful only if it still preserves the required deliberate mutations and their expected quarantine-style decisions.

The shrink report checks:

- accepted fuzz report and accepted fuzz ledger;
- generator binding;
- required mutation coverage;
- expected decision prefix preservation;
- rejection of watch-only outcomes unless explicitly allowed;
- surface, family, and path diversity;
- payload-unit reduction without pretending compaction is proof of correctness.

The point is not to build a production fuzz engine. The point is to keep coverage evidence durable and small without losing the hard negative cases that taught us something.
