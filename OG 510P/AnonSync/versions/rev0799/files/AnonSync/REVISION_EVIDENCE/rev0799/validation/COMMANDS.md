# Rev0799 validation commands

```bash
cmake -S . -B /mnt/data/anonsync-rev0799-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug -DANONSYNC_USE_BUNDLED_SQLITE=ON \
  -DCMAKE_CXX_FLAGS=-Werror
cmake --build /mnt/data/anonsync-rev0799-build --parallel 4
ctest --test-dir /mnt/data/anonsync-rev0799-build \
  --output-on-failure --parallel 4

ctest --test-dir /mnt/data/anonsync-rev0799-build \
  -R '^(anonsync_sqlite_verification_budget_test|anonsync_sqlite_snapshot_geometry_binding_test)$' \
  --repeat until-fail:20 --output-on-failure

for i in $(seq 1 10); do
  /mnt/data/anonsync-rev0799-build/anonsync_core \
    --selftest-ledger-sqlite-readonly-snapshot-verifier
done

cmake -S . -B /mnt/data/anonsync-rev0799-asan -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug -DANONSYNC_USE_BUNDLED_SQLITE=ON \
  -DANONSYNC_ENABLE_SANITIZERS=ON -DCMAKE_CXX_FLAGS=-Werror
cmake --build /mnt/data/anonsync-rev0799-asan --parallel 2 --target \
  anonsync_sqlite_verification_budget_test \
  anonsync_sqlite_snapshot_geometry_binding_test

python3 tools/audit_sqlite_verification_budget.py --root .
python3 tools/audit_ingress_sender_replay_integrity.py --root .
python3 tools/audit_sqlite_replay_ledger_schema_contract.py --root .
python3 tools/audit_sqlite_snapshot_seal.py --root .
python3 tools/audit_sqlite_snapshot_geometry.py --root .
```

Clang strict and GCC optimized lanes directly compiled the focused boundary and
proof with `-Werror`; the Clang lane additionally enabled `-Wconversion`,
`-Wsign-conversion`, `-Wshadow`, and `_GLIBCXX_ASSERTIONS`.
