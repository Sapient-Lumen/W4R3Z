# rev0321 pedagogy-forward execution refactor

## Refactor target

The first teacher/tutor cycle should require commands and human decisions, not another policy branch.
The hot path is now:

1. `make micro-pilot-pack ... CONCEPT_KIT=equality-one-step OVERWRITE=1`;
2. `make micro-pilot-readiness PACKET=... WRITE=1` to confirm the fresh packet is still `NOT_READY`;
3. optionally run `make micro-pilot-dry-run PACKET=... CONFIRM=synthetic-aggregate-dry-run-not-evidence OVERWRITE=1` to rehearse the positive branch;
4. score the dry-run packet and confirm it returns `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE`;
5. delete or replace the dry-run packet;
6. generate a fresh packet for the real owner cycle;
7. only consider evidence import after a separate real owner-attested route exists.

## Burden removed

The operator no longer has to infer the passing readiness branch by manually editing four packet files.
The dry-run harness centralizes that rehearsal without adding a release validator, schema, public
claim, or service authority.

## Boundary

The dry-run harness and readiness scorecard are local preparation support. They do not prove learning,
safety, access, workload, effectiveness, compliance, custody, or `FT-0181` closure.
