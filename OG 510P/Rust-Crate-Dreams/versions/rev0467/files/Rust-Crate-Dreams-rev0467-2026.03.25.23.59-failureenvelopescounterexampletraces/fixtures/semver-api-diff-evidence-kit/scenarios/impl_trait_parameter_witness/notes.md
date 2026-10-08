# Scenario: `impl_trait_parameter_witness`

A function parameter changes from a concrete type to a more complex `impl Trait` surface.
The bundle should preserve that this case was escalated to witness compilation instead of pretending syntax alone was decisive.
