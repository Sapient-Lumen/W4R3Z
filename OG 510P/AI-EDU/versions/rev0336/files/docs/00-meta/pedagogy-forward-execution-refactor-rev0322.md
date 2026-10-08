# rev0322 pedagogy-forward execution refactor

## Refactor target

The first teacher/tutor cycle should be driven by commands and human decisions, not another policy
branch. The hot path is now:

1. `make micro-pilot-next WRITE=1` to learn whether a packet exists;
2. `make micro-pilot-pack ... CONCEPT_KIT=equality-one-step OVERWRITE=1` when the router says to prepare;
3. `make micro-pilot-next PACKET=... WRITE=1` to route the fresh packet state;
4. optionally run `make micro-pilot-dry-run PACKET=... CONFIRM=synthetic-aggregate-dry-run-not-evidence OVERWRITE=1` once to rehearse the positive branch;
5. `make micro-pilot-next PACKET=... WRITE=1` again and follow `DISCARD_SYNTHETIC_AND_REGENERATE`;
6. delete or replace the dry-run packet;
7. generate a fresh packet for the real owner cycle;
8. stop at local owner review unless a separate real owner-attested evidence route exists.

## Burden removed

The operator no longer has to infer next state by opening the packet manifest, dry-run trace,
readiness JSON, run card, and startup docs. The router centralizes that decision without adding a
release validator, schema, public claim, or service authority.

## Boundary

The next-action router, dry-run harness, and readiness scorecard are local preparation support. They
do not prove learning, safety, access, workload, effectiveness, compliance, custody, or `FT-0181`
closure.
