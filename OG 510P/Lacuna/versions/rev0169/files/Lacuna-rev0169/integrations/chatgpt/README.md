# ChatGPT integration materials

- `PROJECT_INSTRUCTIONS.md` is intended for a ChatGPT Project or custom GPT instruction field.
- `CONVERSATION_STARTERS.md` supplies player and operator starters.
- `../../PLAY_WITH_AN_LLM.md` explains the player entrance.
- `../../docs/operators/CHATGPT.md` gives chat-only, human-bridge, role-context, and connected-host procedures.
- `../../docs/operators/FRESH_NARRATOR.md` gives the clean post-checkpoint continuation procedure.

A Project or uploaded repository provides context, not automatic durable local execution. For governed persistence, use a human or connected host that exposes `play start`, the request-scoped `turn run status/dispatch/accept/recover/commit` protocol, and—when backstage comparison is requested—the managed `checkpoint run begin/status/dispatch/accept/record-failure/recover/commit` protocol.

For role-separated use, render `./lacuna turn run dispatch RUN_PATH --provider chatgpt --format markdown` and paste that self-contained handoff into a fresh or role-dedicated ChatGPT context. It embeds the exact task card, so the worker does not need local path access. Save exactly one JSON object matching the named schema, then execute the generated `turn run accept` command. The parent remains the only accept and commit authority.

For managed checkpoint roles, render `./lacuna checkpoint run dispatch RUN_PATH --format markdown`. The route is fixed at run creation. Save exactly one JSON object, invoke the generated accept command, or record an honest failed attempt; only the parent commits. For the clean post-checkpoint condition, the parent runs `./lacuna checkpoint run next-turn RUN_PATH --player-input-file INPUT --provider chatgpt --format markdown` and gives only that complete continuation dispatch to a new narrator context. Do not use shared Project memory as the isolation boundary.
