# Scenario: tools and sampling enabled without approval or loop limits

This scenario models an MCP deployment that exposes both high-risk tools and sampling, but lacks explicit approval checkpoints and does not impose loop limits on tool-driven sampling chains.

The point is to make **operation guard truth** reviewable rather than assuming the host or model layer will catch it.
