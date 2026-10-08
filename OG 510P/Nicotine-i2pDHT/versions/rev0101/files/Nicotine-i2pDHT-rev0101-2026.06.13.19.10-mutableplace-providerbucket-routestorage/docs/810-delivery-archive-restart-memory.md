# Delivery archive restart memory

`deliveryarchive` records ACK-settlement evidence into restart-sticky local memory.

The archive carries:

- ACK-ledger digest,
- settlement-fence digest,
- accepted ACK and fence marker digests,
- redacted-summary digest,
- restart generation,
- redaction memory,
- contradiction memory.

The archive does not publish anything and does not claim global finality. It only prevents restart or cleanup from forgetting the evidence that made local settlement believable.
