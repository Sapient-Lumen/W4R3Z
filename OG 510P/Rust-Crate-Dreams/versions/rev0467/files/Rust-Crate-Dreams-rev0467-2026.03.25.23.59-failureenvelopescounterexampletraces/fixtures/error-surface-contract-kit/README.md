# Error Surface Contract Kit fixtures

These fixtures support **P-0533 Error Surface Contract Kit**.

They exist to keep four receiver-facing truths separate:

1. **error identity** — what public code/class is actually being promised;
2. **audience mode** — whether the surface is for users, operators, developers, or machines;
3. **remediation surface** — whether a fix/retry/docs path is authoritative or merely suggestive;
4. **sensitivity posture** — whether paths, snippets, backtraces, or attachments are safe to expose.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “uses `thiserror` / has rich reports / has help text” into one fake error-support story.
