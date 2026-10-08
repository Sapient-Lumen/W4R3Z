# OpenAPI Schema Object dialect is not plain Draft 2020-12

This scenario exercises the rule that an OpenAPI 3.1 Schema Object should be described as the
**OpenAPI 3.1 Schema Object dialect built on JSON Schema Draft 2020-12**, not as plain JSON Schema folklore.

The point is to stop future tooling passes from claiming "draft-2020-12 support" while silently skipping
OpenAPI-specific dialect assumptions.
