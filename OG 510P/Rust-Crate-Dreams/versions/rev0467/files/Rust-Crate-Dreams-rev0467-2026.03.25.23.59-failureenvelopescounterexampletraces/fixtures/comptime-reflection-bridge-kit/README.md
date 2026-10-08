# Comptime Reflection Bridge Kit fixtures

These fixtures support **P-0439 Comptime Reflection Bridge Kit**.

They exist to keep four receiver-facing truths separate:

1. **schema source** — where the export came from and what authority it has;
2. **coverage scope** — whether the export covers declared families, observed monomorphizations, or only a projection;
3. **execution posture** — whether a consumer needs static tables, compile-time adapters, or runtime registry state;
4. **loss accounting** — which metadata classes were preserved, dropped, synthesized, or still need manual review.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “has reflection-like metadata” into one fake reflection-support story.
