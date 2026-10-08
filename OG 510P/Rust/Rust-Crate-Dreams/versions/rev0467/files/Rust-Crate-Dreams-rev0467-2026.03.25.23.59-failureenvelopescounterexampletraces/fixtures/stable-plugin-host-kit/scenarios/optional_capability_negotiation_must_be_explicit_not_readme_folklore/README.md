# optional capability negotiation must be explicit

This scenario captures a plugin host where optional capabilities (for example, background indexing or advanced render hooks) are probed at load time.
The important truth is that the active surface may be a downgraded subset, and that needs a receipt.

What the receipt should prove:

- which capabilities are required,
- which are optional,
- how the downgrade is performed,
- and whether missing optional features reject the plugin or activate a subset.
