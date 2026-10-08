# rev0320 pedagogy-forward execution refactor

## Refactor target

The first teacher/tutor cycle should require commands and human decisions, not another policy branch.
The hot path is now:

1. `make micro-pilot-pack ... CONCEPT_KIT=equality-one-step OVERWRITE=1`;
2. local owner completes plan, aggregate session rows, final eight-row readout, and decision memo;
3. `make micro-pilot-readiness PACKET=scratch/pedagogy/teacher-tutor-micro-pilot/equality-one-step WRITE=1`;
4. use the scorecard's next actions;
5. only consider evidence import after a separate real owner-attested route exists.

## Burden removed

The operator no longer has to infer readiness by manually comparing seven packet files against the
run card. The scorecard centralizes that inspection without adding a release validator, schema,
public claim, or service authority.

## Boundary

The scorecard is local preparation support. It does not prove learning, safety, access, workload,
effectiveness, compliance, custody, or `FT-0181` closure.
