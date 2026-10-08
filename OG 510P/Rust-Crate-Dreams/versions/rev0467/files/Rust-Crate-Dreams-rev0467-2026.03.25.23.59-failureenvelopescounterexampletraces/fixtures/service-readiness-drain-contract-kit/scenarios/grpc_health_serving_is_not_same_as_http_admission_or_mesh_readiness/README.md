# gRPC health is not automatically the whole service readiness contract

This scenario keeps **gRPC health** separate from **HTTP admission** and **mesh/load-balancer readiness**.
The crate should let maintainers state these surfaces separately instead of pretending one status bit covers them all.
