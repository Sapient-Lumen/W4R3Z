# serde-reflection format description is not full type-shape authority

This scenario exists to keep format-schema extraction separate from full reflection authority.

`serde_reflection` extracts format descriptions for Serde containers and can support compatibility testing, cross-language generation, and JSON translation.
That is useful neighboring evidence, but a bridge crate should not silently treat it as complete type-shape, doc-comment, or attribute authority.
