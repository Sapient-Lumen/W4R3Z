# Scenario: reexport makes a declared-private dependency effectively public

The crate reexports a dependency helper or exposes its types in a visible signature.
The manifest still treats the dependency as private.
The bundle must classify this as **effectively public** and explain the route rather than only echo the manifest.
