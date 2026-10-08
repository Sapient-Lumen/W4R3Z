# Tokio cancellation semantics are lane-specific

This scenario freezes another common mistake:
“cancel safe” is not one crate-wide or runtime-wide bit.

Different surfaces may document queue-place loss, partial progress, or stronger cancellation guarantees.
