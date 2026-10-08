# Scenario: native wasip2 component still requires host-supplied imports

This scenario models a component built directly with `cargo build --target=wasm32-wasip2` that compiles successfully but still depends on host-supplied imports.

It exists to resist a common false conclusion:

> “Native target build succeeded, therefore the component is closed and ready to hand to another team.”

The expected outcome is a composition-closure report that marks the bundle as host-supplied-open rather than pretending it is fully closed.
