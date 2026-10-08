# audit export redacted boundary

Audit export is still no-network. It prepares a redacted local bundle for an operator, garden witness, or public redacted summary, but it does not publish anything.

The export lane is intentionally suspicious of helpful diagnostics. It rejects raw boundary exposure, raw payload exposure, boundary drift, digest drift, contradiction drops, hard-negative pressure, replay/fork/previous-link pressure, and low family/path diversity.

Export is useful because garden operators need intelligible receipts. Export is dangerous because diagnostics are metadata. rev0069 keeps export behind retention proof and closure seal so summaries cannot become a new authority surface or a raw leak.
