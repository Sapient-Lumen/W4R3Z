# Scenario — resolver v2 host/target split requires unification-risk receipt

Focus: a dependency may be built with one feature set for host/build use and another for the normal target graph under resolver v2.

Feature-surface reading: the crate may still be correct, but downstream users need a compact warning that feature behavior can differ by build context and that `cargo metadata` alone may not tell the whole story.
