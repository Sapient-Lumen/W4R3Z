# Proof obligation rev0075

The local proof obligation is to show that rev0075 surfaces reject drift and contradiction drops before accepting summary-send readiness or outbox settlement.

The included tests exercise happy path, raw leak, frame digest drift, redaction-GC contradiction drop, redaction-GC component drift, prepared-only hold, terminal phase conflict, and current fold audit.
