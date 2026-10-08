# Scenario: iceberg catalog refresh and static snapshot must not share freshness claims

This scenario exists because current `iceberg_datafusion` explicitly offers two different public surfaces:

- a **catalog-backed provider with automatic metadata refresh**, and
- a **static provider for read-only access to a specific snapshot**.

The fixture keeps future archive passes from collapsing those into one vague “Iceberg table provider” story.
