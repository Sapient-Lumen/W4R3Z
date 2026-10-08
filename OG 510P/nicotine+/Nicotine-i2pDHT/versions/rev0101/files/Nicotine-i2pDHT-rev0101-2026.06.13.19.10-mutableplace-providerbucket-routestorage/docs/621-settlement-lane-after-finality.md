# Settlement lane after finality

The settlement lane records what kind of effect is locally being carried after effect reconciliation:

- terminal commit,
- terminal abort,
- retry held,
- dead-letter held.

The important risk is laundering: a retry-held effect must not drop dead-letter memory just because some other component is ready to retry. The lane keeps `dead_letter_required` and `retry_required` as explicit state and rejects entries that claim retry while silently erasing dead-letter pressure.

This is intentionally local memory, not consensus. It makes a node harder to confuse after restart or branch merge.
