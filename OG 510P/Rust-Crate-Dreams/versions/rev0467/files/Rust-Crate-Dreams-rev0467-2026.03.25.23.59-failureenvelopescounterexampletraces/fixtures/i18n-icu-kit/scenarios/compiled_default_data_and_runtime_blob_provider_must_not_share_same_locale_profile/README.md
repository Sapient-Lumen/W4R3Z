# Scenario: compiled default data and runtime blob provider must not share same locale profile

This scenario keeps two data-posture truths separate:

- a build using ICU4X compiled default data with dead-code elimination and no runtime updates,
- and a build using runtime-loaded blob data whose locale set may expand or refresh after build.

Both can honestly say they use ICU4X, but they do not publish the same locale-data contract.
