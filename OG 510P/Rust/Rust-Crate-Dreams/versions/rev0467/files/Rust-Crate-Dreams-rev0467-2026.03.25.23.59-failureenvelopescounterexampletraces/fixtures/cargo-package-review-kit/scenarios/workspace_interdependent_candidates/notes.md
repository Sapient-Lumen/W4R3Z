# Scenario: workspace interdependent candidates

A workspace packages `core-lib` and `cli-tool` together for review.
`cli-tool` depends on the workspace member `core-lib`, and the capture records the candidate set instead of pretending one package was reviewed in isolation.
