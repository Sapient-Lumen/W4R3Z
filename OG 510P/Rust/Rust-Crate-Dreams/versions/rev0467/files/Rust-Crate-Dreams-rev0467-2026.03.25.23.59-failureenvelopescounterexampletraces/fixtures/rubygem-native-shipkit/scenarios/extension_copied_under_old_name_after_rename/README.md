# Scenario: extension copied under old name after rename

The gem was renamed from `fast_json_ext` to `fjson`.
The compiled shared object still gets copied under the old basename, while the Ruby require stub expects the new path.
The build succeeds, but runtime load fails or becomes environment-dependent.
