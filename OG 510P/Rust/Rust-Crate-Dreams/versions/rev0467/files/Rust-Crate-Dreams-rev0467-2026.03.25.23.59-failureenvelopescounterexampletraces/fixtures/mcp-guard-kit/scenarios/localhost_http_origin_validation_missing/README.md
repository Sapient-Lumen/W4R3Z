# Scenario: localhost HTTP deployment missing origin validation

This scenario models a local Streamable HTTP MCP server that binds on localhost but does **not** validate the `Origin` header.

The point is to show that “localhost only” is not the same thing as “safe by default” when DNS rebinding protections are absent.
