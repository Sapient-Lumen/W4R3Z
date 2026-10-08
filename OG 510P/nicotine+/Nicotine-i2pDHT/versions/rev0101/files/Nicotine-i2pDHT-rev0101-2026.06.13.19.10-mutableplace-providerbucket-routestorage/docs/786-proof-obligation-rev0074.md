# Proof obligations rev0074

rev0074 adds obligations for future work:

- prove summary outbox staging is idempotent across restart
- prove redaction archive cannot be compacted into raw-leaking diagnostics
- prove publish fence cannot authorize a different scope/request/payload
- prove later live-send adapters consume fence evidence without dropping contradiction memory
