# Scenario — usage error and partial success must not share the same exit semantics

This scenario exists to stop future passes from flattening all nonzero outcomes into one fake “failure” class.

A serious CLI often needs to distinguish:

- parse/usage failure,
- partial success with reviewable residue,
- empty-result success or non-success policy,
- and complete success.
