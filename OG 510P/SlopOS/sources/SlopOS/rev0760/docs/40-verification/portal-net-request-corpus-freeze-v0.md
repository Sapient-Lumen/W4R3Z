# Portal.net request corpus freeze v0

Purpose: stop further growth of the named checkpoint/resume/truncation/append corpus suffix ladder and redirect work into parameterized model/proof artifacts.

## Frozen pattern

The archive has enough E1 corpus evidence to show the shape of accepted-history binding, checkpoint/resume replay, truncation, append-after-truncation, recheckpointing, and malformed-envelope rejection for `portal.net.request`.

Future releases should not add a new `portal-net-request-linearization-chain-checkpoint-resume-truncation-append-...` named variant unless it replaces the ladder with a parameterized generator or closes a specific bug found by the model/proof work.

## Allowed follow-up work

- Generalize scenarios into a compact history/recovery DSL.
- Emit the same scenarios from `crates/portal_net_model/` or a proof-assistant extraction.
- Add Kani/Verus/proof-assistant harnesses for a bounded transition relation.
- Replace repeated corpus suffixes with content-addressed scenario manifests.
- Add dashboard rows showing evidence maturity movement.

## Not allowed by default

- Adding another manually named suffix that only composes existing words.
- Treating a larger corpus as a substitute for a state-machine theorem.
- Adding fresh boundary prose without explaining how it moves MVP-A2.
