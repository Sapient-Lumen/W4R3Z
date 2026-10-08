# Scenario — public redaction receipt allows candidate export

This scenario captures an upgrade pack that started with workspace-private notes, local paths, and internal package aliases, but became honestly exportable only after a bounded redaction pass produced its own reviewable receipt.

It proves that:
- `redaction_status: applied` should not float without an exact receipt,
- public export can remain honest when the public surface names the redaction receipt as supporting context,
- and the pack should say which classes of private material were dropped, generalized, or moved to private context.
