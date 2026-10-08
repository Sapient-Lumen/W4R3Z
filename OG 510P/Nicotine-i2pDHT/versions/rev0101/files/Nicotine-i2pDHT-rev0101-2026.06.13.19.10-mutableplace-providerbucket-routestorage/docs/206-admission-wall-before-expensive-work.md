# Admission wall before expensive work

`admissionwall.py` sits after parse/wire/validator checks and before handler work.

The risk: once a frame parses, verifies, and passes namespace policy, it can still be a denial-of-service shape. A garden node needs a local wall that decides whether to spend streams, bytes, RAM, metadata budget, custody IO, or witness attention.

The first model enforces:

- allowed namespaces;
- stream budget;
- byte budget;
- metadata budget;
- per-family accepted-work cap;
- priority ordering;
- reserve capacity for critical work;
- signed useful-refusal receipts;
- replay quarantine.

Useful refusal remains positive capacity evidence, not payment or reputation.

The hardest implemented test: critical work survives a flood of bulk work while duplicate/replayed valid requests are quarantined instead of merely counted as overload.
