# Scenario: caller-provided storage for `async fn in dyn Trait` changes the allocation story

The language goal explicitly calls out futures initialized into caller-provided storage. A receipt must therefore distinguish callee-defined construction from caller-owned destination storage.
