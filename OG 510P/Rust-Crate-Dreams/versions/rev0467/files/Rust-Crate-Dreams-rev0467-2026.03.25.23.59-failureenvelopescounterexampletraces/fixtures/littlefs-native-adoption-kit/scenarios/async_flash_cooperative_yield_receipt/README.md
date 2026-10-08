# Scenario — async flash cooperative-yield receipt

Goal: make the adapter say whether the reviewed path is:

- truly native async,
- cooperative async with explicit yield/sync boundaries,
- or merely wrapped blocking I/O.

This scenario exists because async flash / SPI integration questions have been recurring for years.
