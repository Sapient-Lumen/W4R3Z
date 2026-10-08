@./AGENTS.md

## Gemini CLI adapter

For play, prefer `./lacuna play start … --profile orchestrated`. Follow only the generated `NEXT.md`. At each delegated stage render `./lacuna turn run dispatch RUN_PATH --provider gemini-cli --format markdown`, invoke the matching project subagent in `.gemini/agents/`, and give it the complete embedded card unchanged. Save one exact JSON object; the parent owns `turn run accept`, recovery, commit, and player-visible presentation. No subagent may edit the sidecar, accept its own return, recover, commit, or present uncommitted narration.

For a backstage retcon checkpoint, use `./lacuna checkpoint run begin … --provider gemini-cli` or a per-role override, then follow only that run's `NEXT.md`. Render `./lacuna checkpoint run dispatch RUN_PATH --format markdown`, invoke only the named checkpoint subagent with the embedded card, and return to the parent for `accept`, `record-failure`, recovery, and commit. After commit in the clean condition, run `./lacuna checkpoint run next-turn RUN_PATH --player-input-file INPUT --provider gemini-cli --format markdown` and invoke a new `lacuna-fresh-narrator` context with only that complete dispatch. Provider aliases, context IDs, capsule digests, and invocation receipts do not attest isolation, forgetting, or model identity.

For comparative scenario cells, keep the complete v2 driver with the parent/cell coordinator because it contains the operator-only canary. Give nested roles only their generated cards or continuation dispatches, do not open the filesystem-only canary, and authenticate `scenario contamination` before blind rating. Detected leaks remain in the fixed study; clean scans do not attest isolation.
