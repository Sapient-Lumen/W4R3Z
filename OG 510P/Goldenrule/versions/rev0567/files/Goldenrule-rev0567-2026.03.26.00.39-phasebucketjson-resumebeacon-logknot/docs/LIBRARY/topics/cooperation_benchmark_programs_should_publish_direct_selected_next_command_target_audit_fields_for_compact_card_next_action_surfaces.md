# Cooperation benchmark programs should publish direct selected-next-command target audit fields for compact-card next-action surfaces

If a compact-card archive already emits one selected next command plus that command's direct target and semantics, it should also publish the selected target's compact audit fields directly on the next-action witness and next-action surfaces.

Operational implications:

1. publish the selected next command target's retained `bytes` and `sha256` directly, so inheritors do not have to scan report bindings or manifests just to confirm the chosen target's exact retained identity;
2. publish one tiny selected-target scale summary directly, so inheritors do not have to open the retained JSON or parse multiple count fields just to judge the chosen target's local report scale;
3. keep these fields strict aliases of the retained target object and fail closed when the selected command cannot be resolved to a known retained report target;
4. treat these audit fields as selected-action interpretation aids, not as a second action-selection policy.

This keeps the selected next step locally auditable without widening cards, receipts, citation surfaces, or handoff packs.
