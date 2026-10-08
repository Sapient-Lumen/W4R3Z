# Jumplist back/forward feedback (rev341)

Micromax-editor's jumplist already worked, and rev333/rev334 already made `goto` / `jump` / `jumppick` report where they landed. The remaining quiet gap was the **return loop itself**: actual jumplist traversal through `JumpBack` / `JumpForward` still just changed state.

Rev341 keeps the change tiny but makes that loop more trustworthy and more usable:

- `JumpBack` / `jumpback` now report `jumpback: name @ line:col` on success
- `JumpForward` / `jumpforward` now report `jumpforward: name @ line:col` on success
- failed traversal is explicit too:
  - `jumpback: no earlier jump`
  - `jumpforward: no later jump`

Why this matters:

- the editor's newer navigation loops already follow a shared rule: **tell the user where you actually landed**
- jumplist traversal is exactly the kind of action where users are recovering context, so silence is unusually costly
- making both key-driven actions and command-bar commands speak the same dialect helps future UIs, future scripts, and future humans keep the model coherent

This is still intentionally small. It does **not** add a richer history browser, cross-buffer global jump history, or new jumplist storage semantics. It just makes the existing back/forward loop more explicit and easier to trust.
