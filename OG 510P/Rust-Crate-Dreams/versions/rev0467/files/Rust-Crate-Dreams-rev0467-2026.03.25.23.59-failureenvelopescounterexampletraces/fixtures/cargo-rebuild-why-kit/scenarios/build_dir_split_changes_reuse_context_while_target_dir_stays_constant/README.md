# Scenario — build-dir split changes reuse context while target-dir stays constant

The project keeps the same visible `target-dir` for final artifacts but begins routing intermediate artifacts into a distinct `build-dir`.
A rebuild bundle must preserve that route drift explicitly instead of implying that the final output path alone defines reuse expectations.
