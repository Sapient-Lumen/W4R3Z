# Revision 0981 tests

This record is Linux-cloudtainer evidence. Fresh spawn interpreters are unusually
slow under this instrumented host, so focused isolated families are reported
instead of presenting an aggregate timeout as a complete-suite result.

## Startup lifecycle evidence

- Shared worker lifecycle passed **30/30 in 12.55 s** after the final deadline
  race and gate-recovery additions.
- Coverage includes blocked Process construction, blocked `start()`, one pending
  retry ceiling, late child termination, exact abnormal cleanup, explicit fork
  rejection, start failure after partial launch, full/partial/oversize frames,
  crash, lingering child, one absolute gate-plus-start deadline, and a completion
  timestamp after the boundary.
- `tools/reproduce_process_start_stall.py` observed raw start blocked throughout
  **0.35 s**, bounded caller return in **0.100173 s** for a **0.10 s** startup
  deadline, completed late cleanup, and a successful subsequent worker.

## Caller and product-path evidence

- Atomic write plan passed **8/8 in 0.27 s**.
- Filesystem list passed **10/10 in 10.87 s**; read passed **10/10 in 8.59 s**;
  stat passed **6/6 in 6.30 s**; save-residue identity/cleanup passed **15/15 in
  0.30 s**.
- The three rewritten save-boundary projection regressions passed **3/3 in 0.29
  s**.
- Five real open/save product paths passed **5/5 in 25.31 s**, including bounded
  open, a result larger than the socket buffer, capability-gated open/save,
  ordinary save, and save-as refusal.
- File-write collector, injected multiprocessing regex adapter, plugin-package
  timeout/protocol cases, project worker mapping, and one complete picker journey
  passed **12/12 in 6.49 s**.
- The representative project picker passed in **4.51 s** on the rev0980 tree and
  **4.35 s** on rev0981 pytest reporting; complete command wall time was **6.63
  s** and **6.45 s**, respectively.

## Benchmark evidence

Five ordinary spawn one-shot samples measured:

| Tree | samples (s) | median |
| --- | --- | ---: |
| rev0980 | 1.294824, 0.991448, 0.901987, 0.905803, 0.980162 | 0.980162 s |
| rev0981 | 1.259223, 0.982463, 0.901706, 1.184682, 1.131326 | 1.131326 s |

The samples overlap and are not a throughput proof. Repeated spawn-heavy modules
can exceed coarse aggregate command deadlines in this host even when isolated
families pass; no startup acceleration claim is made.

## Structural and publication evidence

- `python -m compileall -q` passed for `src`, `tools`, and every changed test
  module; `python tools/mxlint.py` reported `mxlint: ok`.
- The portability oracle passed **172/172** cases: 115 kernel and 57 stdlib.
- `python tools/mxaudit.py --check` passed with the new
  `worker-start-deadline=True` boundary; its structural regressions passed
  **4/4 in 8.99 s**.
- `python tools/mxeffects.py --write-help-doc --check-help-doc --check` passed
  with **24** current effect/resource rows.
- Living-doc, revision-index, generated-context, structural-audit, and effect
  contract tests passed **21/21 in 25.39 s**.
- Archive generation/lineage/verifier tests passed **52/52 in 13.13 s**. The
  expected warning is Python `zipfile` reporting the deliberately duplicated
  member in the duplicate-rejection test.
- Installed-package stdlib evidence passed **1/1 in 8.02 s**; reproducible
  release tooling passed **8/8 in 0.14 s**; release-manifest tooling passed
  **17/17 in 0.14 s**.
- Final packaging regenerated `MICROMAX-CONTEXT.json` from the cleaned tree,
  verified the archive's embedded provenance, member CRCs/digests, revision
  lineage, and filename policy, and retested the resulting ZIP with `unzip -t`.

No complete pytest suite, Windows run, frozen executable, process pool, permanent
launcher reclamation, total-memory cap, syscall filter, native-crash boundary,
or hostile-plugin sandbox is claimed.
