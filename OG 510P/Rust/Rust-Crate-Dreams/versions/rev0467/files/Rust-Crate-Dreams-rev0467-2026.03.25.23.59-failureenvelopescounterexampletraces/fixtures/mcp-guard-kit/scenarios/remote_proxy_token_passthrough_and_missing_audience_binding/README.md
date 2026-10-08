# Scenario: remote proxy accepts token passthrough and skips audience binding

This scenario models a remote MCP proxy that forwards upstream bearer tokens to a downstream API without validating that the tokens were issued for the MCP server itself.

The point is to make **token passthrough** and missing **audience/resource binding** visible as first-class auth-boundary failures.
