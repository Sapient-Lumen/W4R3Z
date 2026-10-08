# Claude surface profile

- **surface key:** `claude`
- **priority:** reference adapter
- **role in repo:** current best real adapter lane

## First workflow targets
- surface-detect
- receiver-resolve
- composer-read
- composer-write
- turn-submit
- generation-read
- latest-turn-read
- support-capture

## Notes
Claude remains the implementation reference adapter. Future shared state and workflow decisions should extract reusable patterns from Claude without freezing the whole project into Claude-only assumptions.

## Related living record
- `docs/support-records/claude.md`
