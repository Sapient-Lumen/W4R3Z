# latest_only_registry_check_must_not_masquerade_as_transitive_history_guarantee

A registry-backed compatibility check passed for the latest registered subject version only.
That is useful, but it is not the same guarantee as a transitive all-history check across every prior subject version.

This scenario exists to keep “registry compatibility passed” from silently reading as “all historical versions are still compatible”.
