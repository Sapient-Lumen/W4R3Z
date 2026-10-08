# Scenario: local patch and lock anchor the current route but do not make it shared or durable

This fixture keeps an important lifecycle distinction visible:

- a local config patch plus the current checked-in lockfile can keep today’s route working,
- but that does not make the route shared transition policy,
- and it does not prove that a clean checkout or lock refresh will preserve the same posture.
