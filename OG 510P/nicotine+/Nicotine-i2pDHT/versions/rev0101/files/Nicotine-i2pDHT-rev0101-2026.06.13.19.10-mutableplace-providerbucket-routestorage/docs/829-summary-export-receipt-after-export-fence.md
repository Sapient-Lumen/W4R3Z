# Summary export receipt after export fence

The summary export receipt lane starts after the export fence from rev0078 says the redacted summary is locally export-ready. This lane says a recipient actually acknowledged or refused that exact redacted export edge.

Receipt markers bind:

- exact action/profile/service/scope/request/payload/idempotency boundary
- summary export fence digest
- accepted export marker digest
- recipient kind
- receipt kind
- redacted summary digest
- redaction and contradiction memory

A recipient refusal is not success. It becomes watch pressure. Raw boundary or payload exposure quarantines.
