# cache_root_option_loses_priority_to_home_discovery

This scenario exists to keep **P-0519** honest about **fallback order**.

The crate claims to accept an explicit cache-root option, but at runtime still probes `$HOME` or project directories before honoring that value.

A worthy authority-surface crate should surface the actual fallback order and make clear that the explicit path is *not* the first authority source.
