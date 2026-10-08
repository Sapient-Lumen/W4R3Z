# Cooperation benchmark programs should publish direct selected fallback command targets and semantics for compact-card next-action surfaces

When a compact-card next-action surface already publishes one selected machine step, it should also publish one direct first fallback command with the same local semantics: target, subject role, intent summary, outcome summary, and effect code.

Why:
- inheritors should not need to scan fallback command arrays just to recover the first honest alternate step;
- the first recovery path should be as locally legible as the preferred step;
- fallback semantics should stay a typed alias of the retained command family rather than becoming hidden builder knowledge.

Compact rule:
- publish only the first distinct fallback command after the selected command;
- keep the fallback witness derived from the same command-to-target/semantics mapping already used for the selected step;
- fail closed to `null` when no distinct fallback command exists.
