# Scenario — Chaud reload completion does not bound old-route retirement

Chaud documents that hot-reloaded code only becomes active once a `#[chaud::hot]` function is called.
It also documents that function pointers and trait objects can keep older code alive after a hot reload.
So a completed reload is not an honest retirement boundary for all routes.
