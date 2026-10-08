# Cooperation benchmark programs should publish wrapper-normalized compact-card commands in durable program docs

Once the compact-card handoff surfaces intentionally rely on a wrapper such as `./grpy`, the durable program doctrine should not keep teaching a different invocation path in parallel.
If `docs/BENCHMARK_PROGRAM.md` still says `python3` while the generated next-action, handoff, scope, and execution-lane surfaces all say `./grpy`, inheritors receive two command stories and will often follow the stale one.

That is small but real operational drift.
A compact command wrapper can carry explicit bytecode, interpreter, or environment policy, and durable command docs should surface that same contract instead of silently bypassing it.

Therefore any compact-card command examples retained in durable program doctrine should be wrapper-normalized to the same `./grpy` entrypoint used by the generated handoff surfaces.
This keeps the inheritor-visible command layer coherent without adding another execution path or widening the archive.
