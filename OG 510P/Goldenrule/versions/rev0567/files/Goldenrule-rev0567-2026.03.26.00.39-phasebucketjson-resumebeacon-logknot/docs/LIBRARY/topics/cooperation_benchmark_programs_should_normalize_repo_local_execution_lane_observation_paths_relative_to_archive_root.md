# Cooperation benchmark programs should normalize repo-local execution-lane observation paths relative to archive root

Execution-lane observation surfaces are meant to survive packaging, relocation, and inheritance. When they describe a repo-local path such as the JuNest home inside `.sandworm/`, they should publish that path relative to the archive root rather than leaking the absolute scratch workspace used during one build session.

This keeps the handoff surface portable, avoids stale `/mnt/data/.../Goldenrule-rev...` residues, and lets inheritors compare successive revisions without mistaking container-specific paths for durable program facts.
