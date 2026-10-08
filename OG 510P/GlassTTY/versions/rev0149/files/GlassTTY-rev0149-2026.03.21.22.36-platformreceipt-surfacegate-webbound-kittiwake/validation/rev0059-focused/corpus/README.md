# Seeded fixture corpus

These JSON files are deterministic sample fixtures for offline tooling work. They are not evidence from a live browser session.

Use them to:
- exercise index and compare commands
- verify archive tooling after a workspace reset
- give future sessions something concrete to inspect before live-browser proof exists

Refresh with:

```bash
./scripts/seed-fixture-corpus.py fixtures/corpus --force
```
