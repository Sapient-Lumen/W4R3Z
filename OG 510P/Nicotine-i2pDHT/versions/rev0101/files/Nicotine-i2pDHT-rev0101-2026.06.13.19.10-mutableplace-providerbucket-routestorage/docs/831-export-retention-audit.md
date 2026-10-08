# Export retention audit

Export/import readiness can tempt cleanup. This lane treats retention as a protocol boundary.

Retention audit joins:

- summary export receipt
- summary import gate
- summary export fence
- retention policy markers
- redaction memory
- contradiction memory

It allows future soft compaction only when redaction and contradiction memory survive. It quarantines attempts to erase hard negatives, raw leak protections, or contradiction evidence.
