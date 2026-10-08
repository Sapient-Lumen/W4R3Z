# Scenario: `cargo component` success does not automatically imply a stable interface contract

This scenario exists because the current `cargo component` README explicitly says the tool is experimental and may break existing projects as the Component Model stabilizes.

The receipt therefore keeps these truths separate:

- a project successfully built as a component,
- a WIT package/world exists,
- and the surrounding build tool is still experimental.

That is enough for a strong plugin-interface receipt, but not enough to bluff long-term tooling stability.

