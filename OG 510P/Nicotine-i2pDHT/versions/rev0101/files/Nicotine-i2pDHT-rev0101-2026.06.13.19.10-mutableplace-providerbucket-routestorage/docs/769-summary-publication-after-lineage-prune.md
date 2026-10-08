# Summary publication after lineage prune

`summarypublish.py` models a no-network publication-ready marker for redacted summary material.

It joins:

- summary receipt
- import archive
- lineage prune guard
- redacted summary digest
- previous-linked publication intents
- family/path diversity
- contradiction memory

The risky guess is that publication-looking summaries are a new public edge even when the content is redacted. A summary can be useful for operator/garden/public surfaces while still becoming a metadata side channel if raw boundary or payload material sneaks through.

The lane rejects raw leaks, boundary drift, component digest drift, replay, rollback, same-sequence forks, previous-link mismatch, hard-negative pressure, and contradiction-memory drops.

Audit needle: summary publication.
