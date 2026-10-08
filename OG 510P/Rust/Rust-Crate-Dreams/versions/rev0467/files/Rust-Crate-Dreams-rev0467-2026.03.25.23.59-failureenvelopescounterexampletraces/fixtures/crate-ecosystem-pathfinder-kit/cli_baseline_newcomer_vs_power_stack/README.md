# CLI baseline with newcomer-vs-power-stack tension

Simulates a teaching or internal-tools team choosing a CLI baseline where first-success ergonomics and long-term extensibility may disagree.
The pathfinder result should not pretend those are the same optimization target.

Why this matters:
- many Rust users still learn through docs and code, so the starter stack itself becomes part of the language’s learning surface;
- the most featureful choice is not always the best onboarding choice, and the simplest choice is not always the least painful later.

What this scenario should force:
- a task profile that distinguishes teaching fit from long-term extensibility
- a decision-axis report with separate `teaching_fit`, `task_fit`, and `migration_friction` values
- a summary that says whether the chosen starter set is “teaching default”, “production default”, or still unresolved
