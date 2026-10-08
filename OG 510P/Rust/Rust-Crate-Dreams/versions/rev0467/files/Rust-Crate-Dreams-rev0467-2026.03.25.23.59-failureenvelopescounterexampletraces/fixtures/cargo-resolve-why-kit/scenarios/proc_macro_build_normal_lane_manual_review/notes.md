# Scenario — proc-macro helper used from both build and normal lanes

This scenario is intentionally conservative.

The docs say build-dependencies and proc-macros do not share features with normal dependencies, but real issue reports show proc-macro/helper arrangements where the practical feature story is still hard to explain from stable surfaces alone.
The bundle should therefore freeze the lane structure and admit **manual review required** instead of inventing a false exact answer.
