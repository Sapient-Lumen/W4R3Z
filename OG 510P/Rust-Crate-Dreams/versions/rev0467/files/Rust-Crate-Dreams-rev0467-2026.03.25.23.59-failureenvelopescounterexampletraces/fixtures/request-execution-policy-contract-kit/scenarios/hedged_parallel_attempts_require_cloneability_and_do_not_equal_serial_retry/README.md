# Scenario — hedged parallel attempts require cloneability and do not equal serial retry

This scenario captures a hedged request policy.
The important distinction is that replay safety is not enough by itself: the execution topology is parallel, cloneability is required, and loser cancellation becomes part of the contract.
