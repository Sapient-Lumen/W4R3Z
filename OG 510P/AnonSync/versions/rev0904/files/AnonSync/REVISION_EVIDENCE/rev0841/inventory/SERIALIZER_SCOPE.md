# rev0841 serializer scope

- Production C++ lexical `std::ostringstream` occurrences: **61**.
- Explicit classic-locale imbues: **6**.
- `sqlite_replay_ledger.cpp`: **4** remaining streams and **4** classic-locale imbues.
- V3 signed publication owner: **no stream use**; integers use `std::to_chars`.

These are lexical counts, not automatic defect verdicts. File slurps and human diagnostics
have different contracts from signing, persistence, or wire serializers.
