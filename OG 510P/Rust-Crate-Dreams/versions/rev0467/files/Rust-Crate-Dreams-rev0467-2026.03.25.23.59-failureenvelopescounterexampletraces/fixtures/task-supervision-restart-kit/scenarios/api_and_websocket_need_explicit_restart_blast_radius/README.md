# Scenario: API and websocket siblings need explicit restart blast radius

A service has an HTTP server and a websocket server that share startup dependencies and should be treated as one subsystem for restart review.
The point is to show that “auto-restart” is not enough; reviewers need explicit topology, dependency ordering, and readiness basis.

