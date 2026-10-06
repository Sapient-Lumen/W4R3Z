# Storage-lane model oracle frontier

Revision: rev0028

The storage lane now has three layers of evidence:

1. `scheduler:storage-lane-provider-proof` proves one scripted integration path.
2. `scheduler:storage-lane-model-walk-proof` explores deterministic generated operation sequences.
3. `facility:storage-lane-model-contract-audit` checks that the proof, docs, manifest, artifacts, and non-claims remain coherent.

## New validator

`validateStorageLaneExecutorSnapshot(snapshot)` is now the compact shared contract for storage-lane snapshots. It verifies:

- executor pending/result counts are non-negative;
- scheduler validation is present and passing;
- global scheduler queue/in-flight counts match lane totals;
- mailbox queue/pending counts match sequence arrays;
- live block digests are covered by retained/provider block accounting.

This is intentionally small. It is not a full model checker. Its job is to make every future storage-lane proof start from the same shape.

## Model scope

The rev0028 model tracks:

```txt
ready seqs
pending seqs + pending IDs
acked seqs
delivered seqs
payload checksums
```

The generated walk exercises:

```txt
enqueue
dequeue
ack
checkpoint
compact dry-run
compact real
manual health rejection
provider write failure
capacity blocking
dependency deferral
final drain
```

The oracle checks the logical delivery model after every step.

## What this teaches

- Provider failure must not mutate logical delivery state.
- Lane-health rejection must not mutate scheduler/mailbox state.
- Compaction must not mutate logical delivery state.
- Dependency deferral must eventually release when the dependency completes.
- Capacity blocking must leave work queued and not disappear it.
- Final drain must return scheduler and mailbox accounting to zero.

## Next frontier

The next earned steps are:

1. storage-lane retry/admission policy, fake-provider first;
2. OPFS storage-lane provider, single browser slice only;
3. crash/reload simulation with fake persisted provider;
4. retained-ref compaction model walks.


The storage-lane model oracle is a cheap fake-provider reference surface, not a browser or OPFS claim.

Non-claim: No exhaustive model checking.

Keyword guard: storage-lane model. No exhaustive model checking.
