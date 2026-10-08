# Proof obligation — rev0080

The current baby proof obligation is local and executable:

```text
accepted import settlement requires receipt + gate + retention audit agreement
accepted archive requires settlement + retention + import gate agreement
accepted retention seal requires settlement + archive + retention agreement
all accepted paths preserve redaction and contradiction memory
all accepted paths reject digest drift, boundary drift, raw leaks, replay, rollback, forks, previous-link mismatch, hard negatives, and low diversity
```

The tests are pressure checks, not production security proofs.
