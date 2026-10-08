# Scenario — canvas textbox reports focus but not value or selection

A custom/canvas text field can receive focus and keyboard events, but the authoring-side semantic tree does not expose current value or selection semantics.
This is a common boundary case for Rust GUI stacks that hand-roll text input.

The right output is a **semantic-contract report** that keeps focusability and control presence separate from value/selection semantics, instead of flattening everything into a single "textbox exists" success claim.
