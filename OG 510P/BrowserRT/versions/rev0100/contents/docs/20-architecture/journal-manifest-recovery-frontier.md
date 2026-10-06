# Journal and manifest recovery frontier

Revision: rev0028

## Boundary

BrowserRT recovery is currently a contract sketch plus a fake provider proof. It is not yet a durable storage engine.

## Recovery ladder

```txt
fake journal + fake manifest
  -> Node filesystem recovery
  -> OPFS async block recovery
  -> OPFS sync-worker recovery
  -> browser reload/reopen recovery
  -> quota/failure recovery
  -> multi-tab leader recovery
  -> compaction and checkpoint maintenance
```

Every rung needs its own manifest task.

## Contract shape

A recovery-capable provider should eventually expose:

- append journal record;
- checkpoint manifest;
- read latest valid manifest;
- replay journal records after the checkpoint;
- ignore or reject torn records according to policy;
- report uncommitted operations;
- emit trace events for every recovery decision;
- expose a non-claim boundary for durability and provider-specific failure assumptions.

## Why this comes before OPFS durability

Browser OPFS restart tests are expensive in the cloudtainer. The fake provider lets us design what recovery evidence should look like before spending browser fixture budget.

## Rev0012 slice

`storage:journal-recovery-proof` is the current slice. It should stay cheap and deterministic. It creates vocabulary and trace evidence for future storage providers.

## Non-claims

- No durable OPFS recovery.
- No filesystem crash recovery.
- No fsync or browser `flush` guarantee.
- No quota or eviction guarantee.
- No compaction proof.
- No multi-tab safety.
