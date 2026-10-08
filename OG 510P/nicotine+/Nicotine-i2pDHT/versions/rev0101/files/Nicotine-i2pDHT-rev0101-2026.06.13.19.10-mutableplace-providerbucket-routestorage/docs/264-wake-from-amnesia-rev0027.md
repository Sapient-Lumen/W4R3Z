# Wake from amnesia — rev0027

You are inside a Python-first DHT design cube for an application-agnostic DHT that may later live above I2P. Do not start with Nicotine integration. The design center remains mutable records, local evidence, garden nodes, provider truth pressure, path diversity, and auditability.

rev0027 did two things:

1. folded a parallel rev0026 lineage/workmeter branchlet into the spoken schedjoin branch;
2. implemented three explicit debts: persistence/reload pressure, malformed wire/parser fixtures, and refusal laundering across windows.

The strongest current sentence:

```text
Local memory is a protocol boundary after restart, not a cache.
```

Run:

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Start reading:

1. `docs/258-rev0027-branchmerge-persistfuzz-refusalloop.md`
2. `docs/259-persist-lane-crash-reload-pressure.md`
3. `docs/260-fuzzwire-generated-malformed-fixtures.md`
4. `docs/261-refusal-loop-across-garden-windows.md`
5. `docs/262-branchmergefold-audit-refactor.md`
6. `tests/test_rev0027_persist_fuzz_refusal_branchmerge.py`
