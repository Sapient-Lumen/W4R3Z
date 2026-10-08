# Scenario: delegate package upgrade reorders units and changes the support story

A shared delegate package adds a preflight generator that now runs before the native-probe unit.
The build still succeeds, but the support contract changed because generated headers and metadata now depend on a different order.
