# Scenario — stable subcommand tree needs shell-doc coverage and a command-surface receipt

This scenario exists to stop future passes from collapsing these claims into one vague “has a CLI” story:

- command surface is stable enough to be relied on,
- the tool is a subcommand tree rather than one flat command,
- shell-oriented documentation assets exist,
- and value hints are broad enough to improve completion quality.

A parser declaration alone is not yet a downstream support contract.
