# Transport and adapter layer

This directory defines how TimeSync semantic objects can be carried by existing mechanisms without defining a new timing protocol.

Files:

```text
adapter-catalog.json   machine-readable adapter patterns
ADAPTER-CATALOG.md     human-readable catalog summary
```

The adapter layer is intentionally small. It names the carrier and the message type, then leaves semantic meaning to the nested payload.

Most important invariant:

```text
Adapter metadata cannot make a TimeState fresher, more traceable, more applicable, or more profile-conformant.
```
