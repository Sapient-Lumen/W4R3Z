# Repair prune guard

`repairpruneguard.py` joins ACK pruning with retry-fence memory.

The rule:

```text
terminal ACK path -> pruning may be locally allowed
repair path       -> repair debt must be retained
```

This prevents an independent prune lane from deleting the evidence needed to explain why a retry, withdraw, or dead-letter hold exists.

Repair debt is not a log message. It is local protocol memory until a fence, settlement, or terminal contradiction resolves it.

repair prune guard audit needle.
