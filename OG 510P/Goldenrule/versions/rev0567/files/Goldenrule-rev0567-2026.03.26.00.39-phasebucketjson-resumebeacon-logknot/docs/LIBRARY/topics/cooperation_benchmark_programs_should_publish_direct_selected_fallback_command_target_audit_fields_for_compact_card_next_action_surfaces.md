# Cooperation benchmark programs should publish direct selected fallback command target audit fields for compact-card next-action surfaces

If a compact-card archive already emits one direct first fallback command plus that command's target and semantics, it should also publish the fallback target's compact audit fields directly on the next-action witness and next-action surfaces.

Operational implications:

1. publish the first fallback command target's retained `bytes` and `sha256` directly, so inheritors do not have to scan report bindings or manifests just to confirm the recovery target's exact retained identity;
2. publish one tiny fallback-target scale summary directly, so inheritors do not have to open the retained JSON or parse multiple count fields just to judge the local scale of the first recovery step;
3. keep these fields strict aliases of the retained fallback target object and fail closed when the first fallback command cannot be resolved to a known retained report target;
4. treat these audit fields as recovery-step interpretation aids, not as a second fallback-selection policy.

This keeps the first honest recovery step locally auditable without widening cards, receipts, citation surfaces, or handoff packs.
