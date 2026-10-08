# Scenario: a portable bundle keeps context, mobility, and driver liveness separate

This scenario proves that a mature concurrency-support bundle should not flatten:
- broad execution-context legality,
- locality / mobility / affinity,
- and driver-liveness / progress conditions

into one fake “works in async” bit.
