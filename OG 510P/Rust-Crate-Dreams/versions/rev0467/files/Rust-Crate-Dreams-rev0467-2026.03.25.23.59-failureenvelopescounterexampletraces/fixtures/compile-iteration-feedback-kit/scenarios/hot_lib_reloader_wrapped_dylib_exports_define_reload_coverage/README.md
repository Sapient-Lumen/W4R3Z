# Scenario — hot-lib-reloader coverage is the wrapped dylib export surface, not “the whole crate”

This scenario freezes the fact that hot-lib-reloader requires code in a reloadable dylib and the `hot_module` wrapper defines the usable surface.
Reloading one wrapped export should not masquerade as coverage for generic functions, arbitrary internal routes, or hidden global-state behavior.
