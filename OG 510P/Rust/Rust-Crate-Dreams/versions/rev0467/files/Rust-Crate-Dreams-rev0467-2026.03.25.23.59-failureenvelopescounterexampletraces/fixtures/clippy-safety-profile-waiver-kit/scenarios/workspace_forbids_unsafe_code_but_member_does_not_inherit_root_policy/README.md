# Scenario: workspace forbids `unsafe_code` but one member does not inherit root policy

The root workspace declares a strict rust lint posture, but one package forgot `[lints] workspace = true`.
A green run on the inherited members must not be presented as evidence for the stray member.
