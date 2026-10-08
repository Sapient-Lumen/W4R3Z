# Proof obligation rev0076

The proof obligation for this revision is local:

```text
A redacted summary can only advance past canary readiness when drain markers,
delivery observations, and settlement-fence markers agree at the same exact
boundary and preserve contradiction/redaction memory.
```

Tests cover the happy path, raw leak rejection, useful-refusal hold, payload-mismatch quarantine, missing-ACK fence hold, contradiction-drop quarantine, and the fold audit.
