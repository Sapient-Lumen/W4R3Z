# Proof obligation rev0070

The local proof obligations added here are:

1. export receipts must bind to the accepted redacted export and preserve contradiction memory;
2. retention GC must preserve required marker classes before soft material can be reclaimed;
3. closure handoff must be redacted and exact-boundary;
4. fold/audit surfaces must know rev0070 and preserve the rev0069 predecessor path.

The tests intentionally hit raw leakage, sequence forks, contradiction drops, hard-negative drops, and boundary drift.
