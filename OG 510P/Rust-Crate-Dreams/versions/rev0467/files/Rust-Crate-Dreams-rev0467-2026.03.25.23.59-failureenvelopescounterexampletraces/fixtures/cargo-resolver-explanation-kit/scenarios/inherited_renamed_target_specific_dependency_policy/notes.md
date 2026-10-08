# inherited_renamed_target_specific_dependency_policy

Goal: freeze the case where effective dependency policy comes from a mix of workspace inheritance, local rename tokens, and target-specific clauses.

Why it matters:
- resolver answers are not just about edges; they are also about where policy was authored,
- feature tokens may use the local dependency key rather than the original package name,
- and target-specific inheritance can keep a conclusion conservative even when the graph looks simple.
