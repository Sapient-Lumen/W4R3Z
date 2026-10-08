# Risk register rev0075

Risks under test:

- fenced summary outbox mistaken for live-send permission,
- redaction GC dropping contradiction evidence,
- prepared-only outbox state being treated as terminal,
- terminal abort/suppression conflicts,
- frame/session/endpoint digest drift hidden behind valid components,
- fold/audit drift hiding active revision surfaces.
