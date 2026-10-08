# custom_profile_changes_benchmark_story

A crate advertises release-like startup numbers, but the maintainer also uses a custom profile with different debug-symbol, LTO, or codegen-unit settings for profiling or release review.
The fixture exists to force the pack to record that a benchmark story is partly about **which profile** was used, not only about which runner executed.
