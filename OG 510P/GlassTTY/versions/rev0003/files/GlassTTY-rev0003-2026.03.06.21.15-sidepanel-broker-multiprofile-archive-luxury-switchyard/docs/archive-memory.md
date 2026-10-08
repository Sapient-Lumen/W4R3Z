# Archive memory design

## Why this repo carries memory explicitly

GlassTTY is expected to evolve across many sessions, possibly with different LLMs and different humans in charge.

That means the archive itself must carry:
- current status
- active assumptions
- decisions already made
- the read order for future sessions
- the sharpest next tasks

## Memory layers

### Human-readable
- `README.md`
- `STATUS.md`
- `MEMORY.md`
- `DECISIONS.md`
- `PROJECT_MAP.md`
- `TASK_QUEUE.md`

### Machine-readable
- `ARCHIVE_MANIFEST.json`
- JSONL event logs under `GLASSTTY_HOME/state/`

### Session scaffolding
- `.llm/SESSION_START.md`
- `.llm/SESSION_END.md`

## Rule

Important reasoning should not live only in chat history if it affects how the repo should evolve.
