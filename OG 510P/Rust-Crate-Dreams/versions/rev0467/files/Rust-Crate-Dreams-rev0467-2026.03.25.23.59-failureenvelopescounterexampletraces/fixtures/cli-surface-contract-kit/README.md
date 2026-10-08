# CLI Surface Contract Kit fixtures

These fixtures support **P-0531 CLI Surface Contract Kit**.

They exist to keep four receiver-facing truths separate:

1. **command surface** — what commands/options are actually being promised;
2. **output mode** — which mode is for humans versus automation and which stream owns it;
3. **terminal posture** — what changes with TTY/color/progress/prompt context;
4. **exit semantics** — what success and nonzero outcomes actually mean.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “uses clap / has `--json` / nice terminal UX” into one fake CLI-support story.
