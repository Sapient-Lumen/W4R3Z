# Summary prune fence

`summaryprunefence` is a permission boundary before local cleanup after a redacted-summary delivery.

It accepts soft working-set pruning only when proposals explicitly keep:

- ACK-ledger memory,
- delivery-archive memory,
- settlement-fence memory,
- redaction memory,
- contradiction memory,
- hard-negative memory.

This is an audit/refactor pressure point: pruning is a protocol operation, not filesystem housekeeping.
