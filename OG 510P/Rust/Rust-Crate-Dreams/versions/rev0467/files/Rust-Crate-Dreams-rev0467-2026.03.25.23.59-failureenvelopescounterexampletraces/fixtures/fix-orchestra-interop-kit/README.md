# FIX + Orchestra Interop Kit fixture sketch

Suggested contents for a `*.fixbundle.zip`:

- `orchestra.xml` — machine-readable rules of engagement snapshot
- `profile.toml` — counterparty policy overrides and timing assumptions
- `transcript.fixlog` — raw FIX/FIXT message stream
- `canonical.jsonl` — normalized event stream for diff/replay
- `verdicts.json` — spec/profile/session results
- `redaction-map.json` — tokenization mapping (optional, private)
- `notes.md` — human triage notes
