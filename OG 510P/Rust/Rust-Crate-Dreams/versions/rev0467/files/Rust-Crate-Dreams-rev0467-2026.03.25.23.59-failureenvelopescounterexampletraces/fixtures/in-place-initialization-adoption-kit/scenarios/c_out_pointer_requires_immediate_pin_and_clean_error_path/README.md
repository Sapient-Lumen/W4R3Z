# Scenario: C out-pointer requires immediate pinning and a clean error path

A C API initializes a value through an out-pointer and the resulting object must not be moved after initialization. Error paths must not leave initialized state behind that later requires cleanup.
