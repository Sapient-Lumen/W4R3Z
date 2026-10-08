# rev0839 parent defect witnesses

These files were compiled against the sealed rev0839 source before the API refactor.

- `parent-locale-repro.cpp` installs a grouping locale and invokes the parent heartbeat
  encoder. `parent-locale-invalid-heartbeat.json` contains values such as `7_000`.
  `parent-defect-verification.log` records strict JSON rejection.
- `parent-size-repro.cpp` supplies a 70,000-byte reason.
  `parent-oversize-heartbeat.size` records 73,146 emitted bytes while the parent reader
  ceiling is 65,536. The full output is preserved in
  `parent-oversize-heartbeat.json` despite being self-unreadable by AnonSync.

The witnesses prove concrete behavior in the parent. They do not claim that an ordinary
process locale or ordinary reason string always triggers either defect.
