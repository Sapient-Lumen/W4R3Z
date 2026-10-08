# codspeed_unknown_environment_checks_suite_without_measurement

A crate reuses an existing Criterion-compatible benchmark suite through a CodSpeed compatibility layer, but the run happens in an environment where CodSpeed reports that no performance measurement will be made.

The fixture exists to force the pack to record:

- that the suite ran,
- that the environment still matters,
- and that execution intent should downgrade to sanity/imported evidence rather than silently claiming authoritative measurement.
